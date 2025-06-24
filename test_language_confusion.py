#!/usr/bin/env python3
"""
Language Confusion Calculator 테스트 예시
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

def test_detailed_analysis():
    """상세 분석 테스트"""
    print("=== 상세 분석 테스트 ===")
    
    calculator = LanguageConfusionCalculator()
    
    # 다양한 언어의 테스트 케이스들
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
        }
    ]
    
    for case in test_cases:
        print(f"\n--- {case['lang'].upper()} 응답 분석 ---")
        print(f"응답:\n{case['response']}")
        
        # 상세 분석
        detailed = calculator.analyze_response(case['response'], case['lang'])
        
        print(f"언어 혼동 점수: {detailed['summary']['language_confusion_score']:.3f}")
        print(f"전체 정확도: {detailed['summary']['overall_accuracy']:.3f}")
        print(f"라인 패스율: {detailed['metrics']['line_pass_rate']:.3f}")
        
        if detailed['metrics']['word_pass_rate'] is not None:
            print(f"단어 패스율: {detailed['metrics']['word_pass_rate']:.3f}")
        
        # 라인별 분석
        print("\n라인별 분석:")
        for line_info in detailed['line_analysis']:
            status = "✓" if line_info['is_correct_language'] else "✗"
            print(f"  {status} 라인 {line_info['line_number']}: {line_info['detected_language']} (예상: {case['lang']})")
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
        }
    ]
    
    for case in edge_cases:
        print(f"\n--- {case['name']} ---")
        print(f"응답: {case['response']}")
        
        result = calculator.calculate_language_confusion(case['response'], case['lang'])
        print(f"결과: {result}")

if __name__ == "__main__":
    test_basic_usage()
    test_detailed_analysis()
    test_edge_cases() 