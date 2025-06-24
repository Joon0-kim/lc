#!/usr/bin/env python3
import string
import fasttext
import urllib.request
import os
import functools
from typing import Dict, List, Optional

class LanguageConfusionCalculator:
    """
    임의의 모델 응답 문자열에 대해 language confusion을 계산하는 클래스
    """
    
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
    
    @functools.lru_cache(maxsize=2**20)
    def tokenize(self, line: str, lang: str) -> List[str]:
        """
        주어진 언어에 따라 텍스트를 토크나이징합니다.
        
        Args:
            line: 토크나이징할 텍스트
            lang: 언어 코드 ('zh', 'ja', 기타)
            
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
                    return line.split()
            
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
                    return line.split()
            
            return self.ja_tokenizer.parse(line).split()
        
        else:
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
            (label,), score = self.lid_model.predict(text)
            return label.removeprefix('__label__') if score > 0.3 else 'unknown'
        except Exception as e:
            print(f"언어 감지 중 오류 발생: {e}")
            return 'unknown'
    
    def calculate_language_confusion(self, response: str, expected_language: str) -> Dict[str, float]:
        """
        모델 응답의 language confusion을 계산합니다.
        
        Args:
            response: 모델 응답 문자열
            expected_language: 예상되는 언어 코드 (예: 'en', 'ko', 'ja', 'zh', 'fr', 'de', 'es', 'ar', 'hi', 'ru')
            
        Returns:
            계산된 메트릭 딕셔너리:
            - 'line_accuracy': 라인별 정확도 (0.0 ~ 1.0)
            - 'line_pass_rate': 라인 패스율 (0.0 ~ 1.0)
            - 'word_pass_rate': 단어 패스율 (0.0 ~ 1.0, 일부 언어에서만 계산)
            - 'total_lines': 분석된 총 라인 수
            - 'lines_with_errors': 오류가 있는 라인 수
            - 'lines_with_word_errors': 영어 단어 오류가 있는 라인 수
        """
        # 텍스트 정규화
        normalized_response = self.normalize(response)
        lines = normalized_response.split("\n")
        
        # 각 라인을 토크나이징하고 너무 짧은 라인 제거
        line_tokens = [self.tokenize(line, expected_language) for line in lines]
        valid_indices = [i for i, tokens in enumerate(line_tokens) if len(tokens) >= 5]
        
        if not valid_indices:
            return {
                'line_accuracy': 1.0,
                'line_pass_rate': 1.0,
                'word_pass_rate': 1.0 if expected_language in ('ar', 'hi', 'ja', 'ko', 'ru', 'zh') else None,
                'total_lines': 0,
                'lines_with_errors': 0,
                'lines_with_word_errors': 0
            }
        
        valid_lines = [lines[i] for i in valid_indices]
        valid_line_tokens = [line_tokens[i] for i in valid_indices]
        
        # 메트릭 계산
        line_accuracies = []
        lines_with_errors = 0
        lines_with_word_errors = 0
        
        for line, tokens in zip(valid_lines, valid_line_tokens):
            # 언어 감지
            detected_lang = self.detect_language(line)
            line_correct = detected_lang == expected_language
            
            if not line_correct:
                lines_with_errors += 1
            elif self.en_words and any(token.strip() in self.en_words for token in tokens):
                lines_with_word_errors += 1
            
            line_accuracies.append(1.0 if line_correct else 0.0)
        
        total_lines = len(valid_lines)
        
        # 결과 계산
        metrics = {
            'line_accuracy': sum(line_accuracies) / len(line_accuracies) if line_accuracies else 1.0,
            'line_pass_rate': 1 - lines_with_errors / max(1, total_lines),
            'total_lines': total_lines,
            'lines_with_errors': lines_with_errors,
            'lines_with_word_errors': lines_with_word_errors
        }
        
        # WPR은 일부 언어에서만 계산 (라틴 문자를 사용하지 않는 언어)
        if expected_language in ('ar', 'hi', 'ja', 'ko', 'ru', 'zh'):
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
        metrics = self.calculate_language_confusion(response, expected_language)
        
        # 각 라인별 분석
        normalized_response = self.normalize(response)
        lines = normalized_response.split("\n")
        line_analysis = []
        
        for i, line in enumerate(lines):
            if len(line.strip()) >= 5:  # 의미있는 라인만 분석
                detected_lang = self.detect_language(line)
                tokens = self.tokenize(line, expected_language)
                english_words = [token for token in tokens if token.strip() in self.en_words]
                
                line_analysis.append({
                    'line_number': i + 1,
                    'content': line,
                    'detected_language': detected_lang,
                    'is_correct_language': detected_lang == expected_language,
                    'english_words_found': english_words,
                    'has_english_words': len(english_words) > 0
                })
        
        return {
            'metrics': metrics,
            'line_analysis': line_analysis,
            'summary': {
                'expected_language': expected_language,
                'total_lines_analyzed': metrics['total_lines'],
                'language_confusion_score': 1 - metrics['line_pass_rate'],
                'overall_accuracy': metrics['line_accuracy']
            }
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
    
    # 테스트 응답들
    test_responses = {
        'ko': "안녕하세요. 오늘 날씨가 좋네요. I hope you have a great day!",
        'en': "Hello, how are you today? The weather is nice.",
        'ja': "こんにちは。今日は天気が良いですね。I hope you have a great day!"
    }
    
    for lang, response in test_responses.items():
        print(f"\n=== {lang.upper()} 응답 분석 ===")
        print(f"응답: {response}")
        
        result = calculator.calculate_language_confusion(response, lang)
        print(f"결과: {result}")
        
        detailed = calculator.analyze_response(response, lang)
        print(f"언어 혼동 점수: {detailed['summary']['language_confusion_score']:.3f}") 