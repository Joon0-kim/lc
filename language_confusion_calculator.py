#!/usr/bin/env python3
import string
import fasttext
import urllib.request
import os
import functools
import re
from typing import Dict, List, Optional

class LanguageConfusionCalculator:
    """
    임의의 모델 응답 문자열에 대해 language confusion을 계산하는 클래스
    지원 언어: ko, en, zh, ja, es, fr, de, it, pt
    """
    
    # 지원하는 언어 목록
    SUPPORTED_LANGUAGES = {
        'ko': 'Korean',
        'en': 'English', 
        'zh': 'Chinese',
        'ja': 'Japanese',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese'
    }
    
    # 언어별 특수 문자 패턴
    LANGUAGE_PATTERNS = {
        'ko': re.compile(r'[가-힣]'),
        'zh': re.compile(r'[\u4e00-\u9fff]'),
        'ja': re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]'),
        'en': re.compile(r'[a-zA-Z]'),
        'es': re.compile(r'[a-zA-ZáéíóúñüÁÉÍÓÚÑÜ]'),
        'fr': re.compile(r'[a-zA-ZàâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]'),
        'de': re.compile(r'[a-zA-ZäöüßÄÖÜ]'),
        'it': re.compile(r'[a-zA-ZàèéìíîòóùÀÈÉÌÍÎÒÓÙ]'),
        'pt': re.compile(r'[a-zA-ZàáâãçéêíóôõúÀÁÂÃÇÉÊÍÓÔÕÚ]')
    }
    
    def __init__(self, words_file_path: str = None):
        """
        초기화: 필요한 모델과 데이터를 로드
        
        Args:
            words_file_path: 영어 단어 사전 파일 경로 (기본값: 'words')
        """
        self.lid_url = 'https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin'
        self.lid_path = 'lid.176.bin'
        self.words_path = words_file_path or 'words'
        
        # 영어 단어 사전 로드
        self._load_english_words()
        
        # 언어 감지 모델 로드
        self._load_language_model()
        
        # 토크나이저 초기화
        self.ja_tokenizer = None
        self.zh_tokenizer = None
        self.ko_tokenizer = None
    
    def _load_english_words(self):
        """영어 단어 사전을 로드합니다."""
        try:
            with open(self.words_path, 'r', encoding='utf-8') as f:
                en_words = [line.strip() for line in f]
            self.en_words = {word for word in en_words if word.islower() and len(word) > 3}
        except FileNotFoundError:
            print(f"Warning: {self.words_path} 파일을 찾을 수 없습니다. 영어 단어 검사가 비활성화됩니다.")
            self.en_words = set()
    
    def _load_language_model(self):
        """FastText 언어 감지 모델을 로드합니다."""
        if not os.path.exists(self.lid_path):
            print(f"언어 감지 모델을 다운로드 중... ({self.lid_url})")
            urllib.request.urlretrieve(self.lid_url, self.lid_path)
        
        self.lid_model = fasttext.load_model(self.lid_path)
    
    def normalize(self, text: str) -> str:
        """
        텍스트를 정규화합니다.
        
        Args:
            text: 정규화할 텍스트
            
        Returns:
            정규화된 텍스트
        """
        text = text.split('\nQ:')[0].strip()
        text = text.translate(str.maketrans("", "", string.punctuation))
        text = text.replace("—", " ")
        text = text.replace("،", "")
        return text
    
    def detect_language_characters(self, text: str) -> Dict[str, float]:
        """
        텍스트에서 각 언어의 문자 비율을 계산합니다.
        
        Args:
            text: 분석할 텍스트
            
        Returns:
            각 언어별 문자 비율 딕셔너리
        """
        if not text.strip():
            return {}
        
        total_chars = len(text)
        language_scores = {}
        
        for lang, pattern in self.LANGUAGE_PATTERNS.items():
            matches = len(pattern.findall(text))
            if total_chars > 0:
                language_scores[lang] = matches / total_chars
        
        return language_scores
    
    @functools.lru_cache(maxsize=2**20)
    def tokenize(self, line: str, lang: str) -> List[str]:
        """
        주어진 언어에 따라 텍스트를 토크나이징합니다.
        
        Args:
            line: 토크나이징할 텍스트
            lang: 언어 코드
            
        Returns:
            토큰화된 단어 리스트
        """
        if lang == 'zh':
            if self.zh_tokenizer is None:
                try:
                    import jieba
                    self.zh_tokenizer = jieba
                    self.zh_tokenizer.initialize()
                except ImportError:
                    print("Warning: jieba가 설치되지 않았습니다. 중국어 토크나이징이 비활성화됩니다.")
                    return self._simple_tokenize(line, lang)
            
            return list(self.zh_tokenizer.cut(line))
        
        elif lang == 'ja':
            if self.ja_tokenizer is None:
                try:
                    from fugashi import Tagger
                    try:
                        self.ja_tokenizer = Tagger("-O wakati -b 50000")
                    except RuntimeError:
                        import unidic.download
                        unidic.download.download_version()
                        self.ja_tokenizer = Tagger("-O wakati -b 50000")
                except ImportError:
                    print("Warning: fugashi가 설치되지 않았습니다. 일본어 토크나이징이 비활성화됩니다.")
                    return self._simple_tokenize(line, lang)
            
            return self.ja_tokenizer.parse(line).split()
        
        elif lang == 'ko':
            return self._simple_tokenize(line, lang)
        
        else:
            return self._simple_tokenize(line, lang)
    
    def _simple_tokenize(self, line: str, lang: str) -> List[str]:
        """
        간단한 토크나이징 (jieba나 fugashi가 없을 때 사용)
        
        Args:
            line: 토크나이징할 텍스트
            lang: 언어 코드
            
        Returns:
            토큰화된 단어 리스트
        """
        if lang in ['ko', 'zh', 'ja']:
            # CJK 언어는 문자 단위로 분리
            return list(line.strip())
        else:
            # 라틴 문자 언어는 공백으로 분리
            return line.split()
    
    def detect_language(self, text: str) -> str:
        """
        텍스트의 언어를 감지합니다.
        
        Args:
            text: 언어를 감지할 텍스트
            
        Returns:
            감지된 언어 코드 또는 'unknown'
        """
        try:
            # FastText 언어 감지
            (label,), score = self.lid_model.predict(text)
            fasttext_lang = label.removeprefix('__label__') if score > 0.3 else 'unknown'
            
            # 문자 기반 언어 감지 (백업)
            char_scores = self.detect_language_characters(text)
            if char_scores:
                char_lang = max(char_scores.items(), key=lambda x: x[1])[0]
                char_score = char_scores[char_lang]
                
                # 문자 기반 점수가 높으면 그것을 우선 사용
                if char_score > 0.5:
                    return char_lang
            
            return fasttext_lang
            
        except Exception as e:
            print(f"언어 감지 중 오류 발생: {e}")
            return 'unknown'
    
    def calculate_language_confusion(self, response: str, expected_language: str) -> Dict[str, float]:
        """
        모델 응답의 language confusion을 계산합니다.
        
        Args:
            response: 모델 응답 문자열
            expected_language: 예상되는 언어 코드
            
        Returns:
            계산된 메트릭 딕셔너리
        """
        if expected_language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"지원하지 않는 언어입니다: {expected_language}. 지원 언어: {list(self.SUPPORTED_LANGUAGES.keys())}")
        
        # 텍스트 정규화
        normalized_response = self.normalize(response)
        lines = normalized_response.split("\n")
        
        # 각 라인을 토크나이징하고 너무 짧은 라인 제거
        line_tokens = [self.tokenize(line, expected_language) for line in lines]
        valid_indices = [i for i, tokens in enumerate(line_tokens) if len(tokens) >= 3]  # 최소 토큰 수를 3으로 줄임
        
        if not valid_indices:
            return {
                'line_accuracy': 1.0,
                'line_pass_rate': 1.0,
                'word_pass_rate': 1.0 if expected_language in ('ko', 'zh', 'ja') else None,
                'total_lines': 0,
                'lines_with_errors': 0,
                'lines_with_word_errors': 0,
                'language_confidence': 1.0
            }
        
        valid_lines = [lines[i] for i in valid_indices]
        valid_line_tokens = [line_tokens[i] for i in valid_indices]
        
        # 메트릭 계산
        line_accuracies = []
        lines_with_errors = 0
        lines_with_word_errors = 0
        language_confidences = []
        
        for line, tokens in zip(valid_lines, valid_line_tokens):
            # 언어 감지
            detected_lang = self.detect_language(line)
            line_correct = detected_lang == expected_language
            
            # 언어 신뢰도 계산
            char_scores = self.detect_language_characters(line)
            confidence = char_scores.get(expected_language, 0.0)
            language_confidences.append(confidence)
            
            if not line_correct:
                lines_with_errors += 1
            elif self.en_words and expected_language in ('ko', 'zh', 'ja') and any(token.strip() in self.en_words for token in tokens):
                lines_with_word_errors += 1
            
            line_accuracies.append(1.0 if line_correct else 0.0)
        
        total_lines = len(valid_lines)
        
        # 결과 계산
        metrics = {
            'line_accuracy': sum(line_accuracies) / len(line_accuracies) if line_accuracies else 1.0,
            'line_pass_rate': 1 - lines_with_errors / max(1, total_lines),
            'total_lines': total_lines,
            'lines_with_errors': lines_with_errors,
            'lines_with_word_errors': lines_with_word_errors,
            'language_confidence': sum(language_confidences) / len(language_confidences) if language_confidences else 1.0
        }
        
        # WPR은 CJK 언어에서만 계산
        if expected_language in ('ko', 'zh', 'ja'):
            metrics['word_pass_rate'] = 1 - lines_with_word_errors / max(1, total_lines - lines_with_errors)
        else:
            metrics['word_pass_rate'] = None
        
        return metrics
    
    def analyze_response(self, response: str, expected_language: str) -> Dict:
        """
        응답을 분석하고 상세한 결과를 반환합니다.
        
        Args:
            response: 분석할 모델 응답
            expected_language: 예상되는 언어
            
        Returns:
            상세한 분석 결과
        """
        if expected_language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"지원하지 않는 언어입니다: {expected_language}. 지원 언어: {list(self.SUPPORTED_LANGUAGES.keys())}")
        
        metrics = self.calculate_language_confusion(response, expected_language)
        
        # 각 라인별 분석
        normalized_response = self.normalize(response)
        lines = normalized_response.split("\n")
        line_analysis = []
        
        for i, line in enumerate(lines):
            if len(line.strip()) >= 3:  # 의미있는 라인만 분석
                detected_lang = self.detect_language(line)
                tokens = self.tokenize(line, expected_language)
                char_scores = self.detect_language_characters(line)
                
                english_words = []
                if expected_language in ('ko', 'zh', 'ja') and self.en_words:
                    english_words = [token for token in tokens if token.strip() in self.en_words]
                
                line_analysis.append({
                    'line_number': i + 1,
                    'content': line,
                    'detected_language': detected_lang,
                    'is_correct_language': detected_lang == expected_language,
                    'language_confidence': char_scores.get(expected_language, 0.0),
                    'english_words_found': english_words,
                    'has_english_words': len(english_words) > 0,
                    'character_distribution': char_scores
                })
        
        return {
            'metrics': metrics,
            'line_analysis': line_analysis,
            'summary': {
                'expected_language': expected_language,
                'language_name': self.SUPPORTED_LANGUAGES[expected_language],
                'total_lines_analyzed': metrics['total_lines'],
                'language_confusion_score': 1 - metrics['line_pass_rate'],
                'overall_accuracy': metrics['line_accuracy'],
                'language_confidence': metrics['language_confidence'],
                'comprehensive_score': self.calculate_comprehensive_score(metrics, expected_language),
                'simple_comprehensive_score': self.calculate_simple_comprehensive_score(metrics),
                'max_comprehensive_score': self.calculate_max_comprehensive_score(metrics)
            }
        }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        지원하는 언어 목록을 반환합니다.
        
        Returns:
            언어 코드와 언어명 딕셔너리
        """
        return self.SUPPORTED_LANGUAGES.copy()
    
    def calculate_comprehensive_score(self, metrics: Dict[str, float], expected_language: str) -> float:
        """
        가중 평균 기반 종합 언어 혼동 스코어를 계산합니다.
        
        Args:
            metrics: calculate_language_confusion에서 반환된 메트릭
            expected_language: 예상되는 언어
            
        Returns:
            종합 스코어 (0.0 ~ 1.0, 높을수록 혼동이 심함)
        """
        # 기본 가중치
        weights = {
            'line_accuracy': 0.4,      # 라인별 정확도 (가장 중요)
            'language_confidence': 0.3, # 언어 신뢰도
            'line_pass_rate': 0.2,     # 라인 패스율
            'word_pass_rate': 0.1      # 단어 패스율 (CJK 언어에서만)
        }
        
        # CJK 언어가 아닌 경우 word_pass_rate 가중치를 다른 항목에 재분배
        if expected_language not in ('ko', 'zh', 'ja') or metrics['word_pass_rate'] is None:
            weights['line_accuracy'] += weights['word_pass_rate'] * 0.6
            weights['language_confidence'] += weights['word_pass_rate'] * 0.4
            weights['word_pass_rate'] = 0.0
        
        # 종합 스코어 계산 (혼동이 심할수록 높은 값)
        comprehensive_score = (
            (1 - metrics['line_accuracy']) * weights['line_accuracy'] +
            (1 - metrics['language_confidence']) * weights['language_confidence'] +
            (1 - metrics['line_pass_rate']) * weights['line_pass_rate'] +
            (0 if metrics['word_pass_rate'] is None else (1 - metrics['word_pass_rate'])) * weights['word_pass_rate']
        )
        
        return comprehensive_score
    
    def calculate_simple_comprehensive_score(self, metrics: Dict[str, float]) -> float:
        """
        단순 평균 기반 종합 스코어를 계산합니다.
        
        Args:
            metrics: calculate_language_confusion에서 반환된 메트릭
            
        Returns:
            종합 스코어 (0.0 ~ 1.0, 높을수록 혼동이 심함)
        """
        scores = [
            1 - metrics['line_accuracy'],
            1 - metrics['language_confidence'],
            1 - metrics['line_pass_rate']
        ]
        
        if metrics['word_pass_rate'] is not None:
            scores.append(1 - metrics['word_pass_rate'])
        
        return sum(scores) / len(scores)
    
    def calculate_max_comprehensive_score(self, metrics: Dict[str, float]) -> float:
        """
        최대값 기반 종합 스코어를 계산합니다 (가장 심한 혼동을 반영).
        
        Args:
            metrics: calculate_language_confusion에서 반환된 메트릭
            
        Returns:
            종합 스코어 (0.0 ~ 1.0, 높을수록 혼동이 심함)
        """
        scores = [
            1 - metrics['line_accuracy'],
            1 - metrics['language_confidence'],
            1 - metrics['line_pass_rate']
        ]
        
        if metrics['word_pass_rate'] is not None:
            scores.append(1 - metrics['word_pass_rate'])
        
        return max(scores)
    
    def calculate_all_scores(self, response: str, expected_language: str) -> Dict[str, float]:
        """
        모든 종합 스코어를 한 번에 계산합니다.
        
        Args:
            response: 모델 응답 문자열
            expected_language: 예상되는 언어 코드
            
        Returns:
            모든 스코어를 포함한 딕셔너리
        """
        metrics = self.calculate_language_confusion(response, expected_language)
        
        return {
            'metrics': metrics,
            'comprehensive_score': self.calculate_comprehensive_score(metrics, expected_language),
            'simple_comprehensive_score': self.calculate_simple_comprehensive_score(metrics),
            'max_comprehensive_score': self.calculate_max_comprehensive_score(metrics),
            'language_confusion_score': 1 - metrics['line_pass_rate']  # 기존 스코어
        }


# 사용 예시 함수
def calculate_confusion_for_response(response: str, expected_language: str) -> Dict:
    """
    간단한 사용을 위한 헬퍼 함수
    
    Args:
        response: 모델 응답 문자열
        expected_language: 예상되는 언어 코드
        
    Returns:
        language confusion 메트릭
    """
    calculator = LanguageConfusionCalculator()
    return calculator.calculate_language_confusion(response, expected_language)


if __name__ == "__main__":
    # 사용 예시
    calculator = LanguageConfusionCalculator()
    
    print("지원하는 언어:")
    for code, name in calculator.get_supported_languages().items():
        print(f"  {code}: {name}")
    
    # 테스트 응답들
    test_responses = {
        'ko': "안녕하세요. 오늘 날씨가 좋네요. I hope you have a great day!",
        'en': "Hello, how are you today? The weather is nice.",
        'ja': "こんにちは。今日は天気が良いですね。I hope you have a great day!",
        'zh': "你好！今天天气很好。I hope you have a great day!",
        'es': "¡Hola! ¿Cómo estás hoy? El tiempo está muy bien.",
        'fr': "Bonjour! Comment allez-vous aujourd'hui? Le temps est très beau.",
        'de': "Hallo! Wie geht es dir heute? Das Wetter ist sehr schön.",
        'it': "Ciao! Come stai oggi? Il tempo è molto bello.",
        'pt': "Olá! Como você está hoje? O tempo está muito bom."
    }
    
    for lang, response in test_responses.items():
        print(f"\n=== {lang.upper()} ({calculator.SUPPORTED_LANGUAGES[lang]}) 응답 분석 ===")
        print(f"응답: {response}")
        
        result = calculator.calculate_language_confusion(response, lang)
        print(f"결과: {result}")
        
        detailed = calculator.analyze_response(response, lang)
        print(f"언어 혼동 점수: {detailed['summary']['language_confusion_score']:.3f}")
        print(f"언어 신뢰도: {detailed['summary']['language_confidence']:.3f}") 