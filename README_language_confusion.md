# Language Confusion Calculator

임의의 모델 응답 문자열에 대해 language confusion을 계산하는 Python 라이브러리입니다.

## 기능

- **언어 감지**: FastText 모델을 사용한 정확한 언어 감지
- **라인별 분석**: 각 라인별로 언어 혼동 정도를 분석
- **단어별 분석**: 영어 단어가 다른 언어 텍스트에 섞여 있는지 검사
- **다양한 언어 지원**: 한국어, 영어, 일본어, 중국어, 아랍어, 힌디어, 러시아어 등

## 설치

### 1. 의존성 설치

```bash
pip install -r requirements_language_confusion.txt
```

### 2. 영어 단어 사전 파일 복사

원본 프로젝트의 `words` 파일을 현재 디렉토리로 복사하세요:

```bash
cp language-confusion/words .
```

## 사용법

### 기본 사용법

```python
from language_confusion_calculator import calculate_confusion_for_response

# 간단한 사용
response = "안녕하세요. 오늘 날씨가 좋네요. I hope you have a great day!"
result = calculate_confusion_for_response(response, 'ko')
print(result)
```

### 상세 분석

```python
from language_confusion_calculator import LanguageConfusionCalculator

calculator = LanguageConfusionCalculator()

# 상세 분석
detailed = calculator.analyze_response(response, 'ko')
print(f"언어 혼동 점수: {detailed['summary']['language_confusion_score']}")
print(f"전체 정확도: {detailed['summary']['overall_accuracy']}")
```

### 클래스 기반 사용

```python
calculator = LanguageConfusionCalculator()

# 여러 응답 분석
responses = [
    "안녕하세요. Hello there.",
    "こんにちは。今日は天気が良いですね。",
    "Hello, how are you today?"
]

for i, response in enumerate(responses):
    result = calculator.calculate_language_confusion(response, 'ko')
    print(f"응답 {i+1}: {result}")
```

## 반환되는 메트릭

### 기본 메트릭 (`calculate_language_confusion`)

- `line_accuracy`: 라인별 정확도 (0.0 ~ 1.0)
- `line_pass_rate`: 라인 패스율 (0.0 ~ 1.0)
- `word_pass_rate`: 단어 패스율 (0.0 ~ 1.0, 일부 언어에서만 계산)
- `total_lines`: 분석된 총 라인 수
- `lines_with_errors`: 오류가 있는 라인 수
- `lines_with_word_errors`: 영어 단어 오류가 있는 라인 수

### 상세 분석 (`analyze_response`)

- `metrics`: 위의 기본 메트릭들
- `line_analysis`: 각 라인별 상세 분석
- `summary`: 요약 정보
  - `language_confusion_score`: 언어 혼동 점수 (1 - line_pass_rate)
  - `overall_accuracy`: 전체 정확도

## 지원하는 언어

- `en`: 영어
- `ko`: 한국어
- `ja`: 일본어
- `zh`: 중국어
- `fr`: 프랑스어
- `de`: 독일어
- `es`: 스페인어
- `ar`: 아랍어
- `hi`: 힌디어
- `ru`: 러시아어

## 테스트 실행

```bash
python test_language_confusion.py
```

## 예시 출력

```
=== 한국어 응답 분석 ===
응답: 안녕하세요.
오늘 날씨가 정말 좋네요.
I hope you have a great day!
내일도 좋은 하루 되세요.

언어 혼동 점수: 0.250
전체 정확도: 0.750
라인 패스율: 0.750

라인별 분석:
  ✓ 라인 1: ko (예상: ko)
  ✓ 라인 2: ko (예상: ko)
  ✗ 라인 3: en (예상: ko)
    영어 단어 발견: ['hope', 'have', 'great', 'day']
  ✓ 라인 4: ko (예상: ko)
```

## 주의사항

1. **첫 실행 시**: FastText 언어 감지 모델이 자동으로 다운로드됩니다 (약 1GB)
2. **토크나이저**: 중국어(jieba)와 일본어(fugashi) 토크나이저는 선택적으로 설치됩니다
3. **단어 패스율**: 라틴 문자를 사용하지 않는 언어에서만 계산됩니다
4. **최소 라인 길이**: 5개 토큰 미만의 라인은 분석에서 제외됩니다

## 라이선스

원본 프로젝트의 라이선스를 따릅니다. 