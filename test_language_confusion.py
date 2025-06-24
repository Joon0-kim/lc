#!/usr/bin/env python3
"""
Language Confusion Calculator 테스트 예시
9가지 언어 지원: ko, en, zh, ja, es, fr, de, it, pt
"""

from language_confusion_calculator import LanguageConfusionCalculator, calculate_confusion_for_response

def test_basic_usage():
    """기본 사용법 테스트"""
    print("=== 기본 사용법 테스트 ===")
    
    # 간단한 헬퍼 함수 사용
    response = "안녕하세요. 오늘 날씨가 좋네요. I hope you have a great day!"
    result = calculate_confusion_for_response(response, 'ko')
    print(f"응답: {response}")
    print(f"결과: {result}")
    print()

def test_supported_languages():
    """지원 언어 확인 테스트"""
    print("=== 지원 언어 확인 ===")
    calculator = LanguageConfusionCalculator()
    supported_langs = calculator.get_supported_languages()
    
    print("지원하는 언어:")
    for code, name in supported_langs.items():
        print(f"  {code}: {name}")
    print()

def test_detailed_analysis():
    """상세 분석 테스트"""
    print("=== 상세 분석 테스트 ===")
    
    calculator = LanguageConfusionCalculator()
    
    # 9가지 언어의 테스트 케이스들
    test_cases = [
        {
            'lang': 'ko',
            'response': "안녕하세요.\n오늘 날씨가 정말 좋네요.\nI hope you have a great day!\n내일도 좋은 하루 되세요."
        },
        {
            'lang': 'en',
            'response': "Hello there!\nThe weather is beautiful today.\nI hope you have a wonderful day.\nSee you tomorrow!"
        },
        {
            'lang': 'ja',
            'response': "こんにちは。\n今日は天気が良いですね。\nI hope you have a great day!\n明日も良い一日を。"
        },
        {
            'lang': 'zh',
            'response': "你好！\n今天天气很好。\nI hope you have a great day!\n明天见！"
        },
        {
            'lang': 'es',
            'response': "¡Hola!\n¿Cómo estás hoy?\nEl tiempo está muy bien.\n¡Hasta mañana!"
        },
        {
            'lang': 'fr',
            'response': "Bonjour!\nComment allez-vous aujourd'hui?\nLe temps est très beau.\nÀ demain!"
        },
        {
            'lang': 'de',
            'response': "Hallo!\nWie geht es dir heute?\nDas Wetter ist sehr schön.\nBis morgen!"
        },
        {
            'lang': 'it',
            'response': "Ciao!\nCome stai oggi?\nIl tempo è molto bello.\nA domani!"
        },
        {
            'lang': 'pt',
            'response': "Olá!\nComo você está hoje?\nO tempo está muito bom.\nAté amanhã!"
        }
    ]
    
    for case in test_cases:
        print(f"\n--- {case['lang'].upper()} ({calculator.SUPPORTED_LANGUAGES[case['lang']]}) 응답 분석 ---")
        print(f"응답:\n{case['response']}")
        
        # 상세 분석
        detailed = calculator.analyze_response(case['response'], case['lang'])
        
        print(f"언어 혼동 점수: {detailed['summary']['language_confusion_score']:.3f}")
        print(f"전체 정확도: {detailed['summary']['overall_accuracy']:.3f}")
        print(f"라인 패스율: {detailed['metrics']['line_pass_rate']:.3f}")
        print(f"언어 신뢰도: {detailed['summary']['language_confidence']:.3f}")
        
        if detailed['metrics']['word_pass_rate'] is not None:
            print(f"단어 패스율: {detailed['metrics']['word_pass_rate']:.3f}")
        
        # 라인별 분석
        print("\n라인별 분석:")
        for line_info in detailed['line_analysis']:
            status = "✓" if line_info['is_correct_language'] else "✗"
            print(f"  {status} 라인 {line_info['line_number']}: {line_info['detected_language']} (예상: {case['lang']})")
            print(f"    신뢰도: {line_info['language_confidence']:.3f}")
            if line_info['english_words_found']:
                print(f"    영어 단어 발견: {line_info['english_words_found']}")

def test_edge_cases():
    """엣지 케이스 테스트"""
    print("\n=== 엣지 케이스 테스트 ===")
    
    calculator = LanguageConfusionCalculator()
    
    edge_cases = [
        {
            'name': '빈 응답',
            'response': '',
            'lang': 'ko'
        },
        {
            'name': '매우 짧은 응답',
            'response': 'Hi',
            'lang': 'en'
        },
        {
            'name': '긴 영어 문장',
            'response': 'This is a very long English sentence that should be detected correctly as English language.',
            'lang': 'en'
        },
        {
            'name': '혼합 언어 (한국어 + 영어)',
            'response': '안녕하세요. Hello there. 오늘 날씨가 좋네요. How are you?',
            'lang': 'ko'
        },
        {
            'name': '지원하지 않는 언어',
            'response': 'Привет! Как дела?',
            'lang': 'ru'
        }
    ]
    
    for case in edge_cases:
        print(f"\n--- {case['name']} ---")
        print(f"응답: {case['response']}")
        
        try:
            result = calculator.calculate_language_confusion(case['response'], case['lang'])
            print(f"결과: {result}")
        except ValueError as e:
            print(f"오류: {e}")

def test_language_detection():
    """언어 감지 기능 테스트"""
    print("\n=== 언어 감지 기능 테스트 ===")
    
    calculator = LanguageConfusionCalculator()
    
    test_texts = [
        ("안녕하세요", "ko"),
        ("Hello world", "en"),
        ("你好世界", "zh"),
        ("こんにちは世界", "ja"),
        ("¡Hola mundo!", "es"),
        ("Bonjour le monde!", "fr"),
        ("Hallo Welt!", "de"),
        ("Ciao mondo!", "it"),
        ("Olá mundo!", "pt")
    ]
    
    for text, expected in test_texts:
        detected = calculator.detect_language(text)
        char_scores = calculator.detect_language_characters(text)
        print(f"텍스트: '{text}'")
        print(f"  감지된 언어: {detected} (예상: {expected})")
        print(f"  문자 분포: {char_scores}")
        print()

def test_character_detection():
    """문자 감지 기능 테스트"""
    print("\n=== 문자 감지 기능 테스트 ===")
    
    calculator = LanguageConfusionCalculator()
    
    mixed_text = "안녕하세요 Hello 你好 こんにちは ¡Hola! Bonjour! Hallo! Ciao! Olá!"
    char_scores = calculator.detect_language_characters(mixed_text)
    
    print(f"혼합 텍스트: {mixed_text}")
    print("문자 분포:")
    for lang, score in sorted(char_scores.items(), key=lambda x: x[1], reverse=True):
        if score > 0:
            print(f"  {lang}: {score:.3f}")

if __name__ == "__main__":
    test_basic_usage()
    test_supported_languages()
    test_detailed_analysis()
    test_edge_cases()
    test_language_detection()
    test_character_detection() 