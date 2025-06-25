# Language Confusion Calculator

임의의 모델 응답 문자열에 대해 language confusion을 계산하는 Python 라이브러리입니다.

## 기능

- **언어 감지**: FastText 모델과 문자 기반 감지를 결합한 정확한 언어 감지
- **라인별 분석**: 각 라인별로 언어 혼동 정도를 분석
- **단어별 분석**: 영어 단어가 다른 언어 텍스트에 섞여 있는지 검사
- **9가지 언어 지원**: 한국어, 영어, 중국어, 일본어, 스페인어, 프랑스어, 독일어, 이탈리아어, 포르투갈어
- **언어 신뢰도**: 각 라인별 언어 감지 신뢰도 제공

## 지원 언어

| 언어 코드 | 언어명 | 특수 문자 지원 |
|-----------|--------|----------------|
| `ko` | 한국어 | 한글 (가-힣) |
| `en` | 영어 | 라틴 문자 |
| `zh` | 중국어 | 한자 (CJK) |
| `ja` | 일본어 | 히라가나, 가타카나, 한자 |
| `es` | 스페인어 | 라틴 문자 + 액센트 |
| `fr` | 프랑스어 | 라틴 문자 + 액센트 |
| `de` | 독일어 | 라틴 문자 + 움라우트 |
| `it` | 이탈리아어 | 라틴 문자 + 액센트 |
| `pt` | 포르투갈어 | 라틴 문자 + 액센트 |

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
print(f"언어 신뢰도: {detailed['summary']['language_confidence']}")
```

### 클래스 기반 사용

```python
calculator = LanguageConfusionCalculator()

# 지원 언어 확인
supported_langs = calculator.get_supported_languages()
print("지원 언어:", supported_langs)

# 여러 응답 분석
responses = [
    "안녕하세요. Hello there.",
    "こんにちは。今日は天気が良いですね。",
    "¡Hola! ¿Cómo estás hoy?",
    "Bonjour! Comment allez-vous?"
]

for i, response in enumerate(responses):
    result = calculator.calculate_language_confusion(response, 'ko')
    print(f"응답 {i+1}: {result}")
```

### 언어 감지 기능

```python
calculator = LanguageConfusionCalculator()

# 언어 감지
text = "안녕하세요"
detected_lang = calculator.detect_language(text)
print(f"감지된 언어: {detected_lang}")

# 문자 분포 분석
char_scores = calculator.detect_language_characters(text)
print(f"문자 분포: {char_scores}")

### 종합 스코어 사용

```python
calculator = LanguageConfusionCalculator()

# 모든 종합 스코어 계산
all_scores = calculator.calculate_all_scores(response, 'ko')
print(f"가중 평균 종합 스코어: {all_scores['comprehensive_score']:.3f}")
print(f"단순 평균 종합 스코어: {all_scores['simple_comprehensive_score']:.3f}")
print(f"최대값 종합 스코어: {all_scores['max_comprehensive_score']:.3f}")

# 개별 스코어 계산
metrics = calculator.calculate_language_confusion(response, 'ko')
comprehensive_score = calculator.calculate_comprehensive_score(metrics, 'ko')
print(f"종합 스코어: {comprehensive_score:.3f}")
```

## 반환되는 메트릭

### 기본 메트릭 (`calculate_language_confusion`)

- `line_accuracy`: 라인별 정확도 (0.0 ~ 1.0)
- `line_pass_rate`: 라인 패스율 (0.0 ~ 1.0)
- `word_pass_rate`: 단어 패스율 (0.0 ~ 1.0, CJK 언어에서만 계산)
- `total_lines`: 분석된 총 라인 수
- `lines_with_errors`: 오류가 있는 라인 수
- `lines_with_word_errors`: 영어 단어 오류가 있는 라인 수
- `language_confidence`: 언어 신뢰도 (0.0 ~ 1.0)

### 상세 분석 (`analyze_response`)

- `metrics`: 위의 기본 메트릭들
- `line_analysis`: 각 라인별 상세 분석
  - `detected_language`: 감지된 언어
  - `is_correct_language`: 올바른 언어인지 여부
  - `language_confidence`: 해당 라인의 언어 신뢰도
  - `english_words_found`: 발견된 영어 단어들
  - `character_distribution`: 문자 분포
- `summary`: 요약 정보
  - `language_confusion_score`: 언어 혼동 점수 (1 - line_pass_rate)
  - `overall_accuracy`: 전체 정확도
  - `language_confidence`: 전체 언어 신뢰도
  - `comprehensive_score`: 가중 평균 기반 종합 스코어
  - `simple_comprehensive_score`: 단순 평균 기반 종합 스코어
  - `max_comprehensive_score`: 최대값 기반 종합 스코어

### 종합 스코어 (`calculate_all_scores`)

모든 종합 스코어를 한 번에 계산하는 기능:

- `comprehensive_score`: 가중 평균 기반 종합 스코어 (권장)
  - Line Accuracy: 40%, Language Confidence: 30%, Line Pass Rate: 20%, Word Pass Rate: 10%
- `simple_comprehensive_score`: 단순 평균 기반 종합 스코어
- `max_comprehensive_score`: 최대값 기반 종합 스코어
- `language_confusion_score`: 기존 혼동 스코어

## 테스트 실행

```bash
python test_language_confusion.py
```

## 예시 출력

```
=== 한국어 (Korean) 응답 분석 ===
응답: 안녕하세요.
오늘 날씨가 정말 좋네요.
I hope you have a great day!
내일도 좋은 하루 되세요.

언어 혼동 점수: 0.250
전체 정확도: 0.750
라인 패스율: 0.750
언어 신뢰도: 0.850

라인별 분석:
  ✓ 라인 1: ko (예상: ko)
    신뢰도: 0.950
  ✓ 라인 2: ko (예상: ko)
    신뢰도: 0.900
  ✗ 라인 3: en (예상: ko)
    신뢰도: 0.200
    영어 단어 발견: ['hope', 'have', 'great', 'day']
  ✓ 라인 4: ko (예상: ko)
    신뢰도: 0.850
```

## 새로운 기능

### 1. 문자 기반 언어 감지
- 각 언어의 특수 문자 패턴을 사용한 정확한 언어 감지
- FastText와 결합하여 더 나은 성능 제공

### 2. 언어 신뢰도
- 각 라인별로 언어 감지의 신뢰도를 계산
- 문자 분포를 기반으로 한 정량적 평가

### 3. 향상된 토크나이징
- CJK 언어: 문자 단위 토크나이징
- 라틴 문자 언어: 공백 기반 토크나이징
- 선택적 고급 토크나이저 지원 (jieba, fugashi)

### 4. 에러 처리
- 지원하지 않는 언어에 대한 명확한 에러 메시지
- 누락된 의존성에 대한 우아한 처리

## 주의사항

1. **첫 실행 시**: FastText 언어 감지 모델이 자동으로 다운로드됩니다 (약 1GB)
2. **토크나이저**: 중국어(jieba)와 일본어(fugashi) 토크나이저는 선택적으로 설치됩니다
3. **단어 패스율**: CJK 언어(한국어, 중국어, 일본어)에서만 계산됩니다
4. **최소 라인 길이**: 3개 토큰 미만의 라인은 분석에서 제외됩니다
5. **언어 제한**: 현재 9가지 언어만 지원됩니다

## 라이선스

원본 프로젝트의 라이선스를 따릅니다. 