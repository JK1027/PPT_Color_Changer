# PPT Text Color Changer - 개발 일지 (Dev Log)

## 📌 프로젝트 정보
- **목표**: PPT 문서 내 특정 글자색 및 이미지 속 특정 색상을 빠르게 탐지하고 일괄 변경하는 업무 자동화 도구 개발
- **주요 기술**: Python 3.12, `python-pptx`, `CustomTkinter`, `opencv-python`, `numpy`
- **핵심 가치**: 원본 레이아웃 보존, 그룹/표/이미지 객체 내부 재귀 탐색 및 변환 완전성 확보, 안정성

---

## 📅 [2026-05-17] 개발 시작 및 1단계(PoC) 착수

### 1. 수행 내역
- PRD (v1.1) 검토 및 최종 업데이트 완료 (표 탐색 로직, 예외 처리, 프로그레스 바 추가)
- 프로젝트 폴더 구조화 (`core/`, `test_data/` 디렉터리 생성)
- `python-pptx` 의존성 설치
- [진행 중] `core/ppt_reader.py` (재귀 탐색 엔진) 구현
- [진행 중] `core/color_extractor.py` (색상 추출 엔진) 구현

### 2. 기술적 결정 사항 (Architecture Decisions)
- **관심사 분리 (SoC)**: UI 코드 작성 전 비즈니스 로직(PPT 파일 처리)을 `core` 폴더에 완벽히 분리하여 먼저 개발 및 테스트 진행.
- **테스트 주도 데이터 구성**: 알고리즘 검증을 위해 그룹 도형, 표, 일반 텍스트, 테마 색상이 혼합된 `test_sample.pptx`를 코드로 자동 생성하여 엣지 케이스를 먼저 확보하기로 결정.
- **상태 무결성**: 파일 쓰기 시 항상 `_modified.pptx` 형태로만 저장 (원본 덮어쓰기 원천 차단).

### 3. 다음 할 일 (To-Do)
- [x] `generate_test_ppt.py` 작성 및 테스트용 PPT 생성
- [x] `core/color_extractor.py` 구현 (RGB 및 테마 색상 추출 로직)
- [x] `core/ppt_reader.py` 구현 (Shape 재귀 탐색 알고리즘)
- [x] 터미널 상에서 색상 변경 PoC (Proof of Concept) 테스트 통과
  - *결과: 그룹, 표, 일반 텍스트 및 테마 색상 모두 탐지 성공.*

## 📅 [2026-05-17] 2단계(기능 통합 및 UI 구성) 진행
### 1. 수행 내역
- `customtkinter` 라이브러리 설치
- `ui/app_ui.py` 생성 및 메인 창 디자인 (파일 선택, 색상칩, 프로그레스 바)
- UI Freezing 방지를 위한 `threading` 도입 (파일 분석 및 변환 작업을 백그라운드 처리)
- 스레드 세이프티를 위한 `self.after()` 방식의 UI 업데이트 패턴 적용
- `PermissionError`(파일 잠김 현상)에 대한 예외 처리 및 팝업 안내 적용
- `app.log` 로깅 시스템 도입

### 2. 다음 할 일 (To-Do)
- [x] 데스크톱 환경에서 GUI 실행 및 동작 테스트 (수동 테스트 필요)
- [x] 추출된 색상칩 Hover 효과 등 UX 개선 (3단계 완료)

## 📅 [2026-05-17] 3단계(옷 입히기 - 미적 개선 및 UX) 완료
### 1. 수행 내역
- 메인 윈도우 배경색과 패널 간 대비를 통한 카드형(Rounded Card) 레이아웃 적용
- 색상 칩 선택 시 테두리(Border) 강조 애니메이션(색상 전환) 구현
- 폰트 사이즈 상향 및 가독성 높은 이모지(🎨, 🖌️) 추가로 데스크톱 앱 퀄리티 확보

## 📅 [2026-05-17] 사용자 피드백 통합 (v2.2): 이미지 내 특정 색상 치환 및 옵션 분리
### 1. 수행 내역
- **OpenCV 기반 이미지 색상 치환 엔진 (`core/image_processor.py`)**: 
  - 사용자 제공 이미지 색상 치환 원리를 동적 Hex-to-HSV 변환 방식으로 일반화 구현.
  - 지정 색상 기준 오차 범위(Tolerance=20) 설정 및 레드(Red) 계열 Hue 값 랩어라운드(Wrap-around) 예외 처리.
  - 입체감 및 질감 보존을 위해 채도(Saturation)를 보정(clip + 40)하는 로직 적용.
- **PPT 이미지 교체 메커니즘 (`core/ppt_reader.py`)**:
  - `shape.shape_type == MSO_SHAPE_TYPE.PICTURE`를 감지하여 원본 이미지의 크기/위치(left, top, width, height)를 획득.
  - OpenCV 처리를 거친 새 이미지를 동일 위치에 삽입(`add_picture`) 후 기존 이미지 삭제(`_element.remove()`) 기법 적용.
- **변환 대상 체크박스 선택 옵션 (`ui/app_ui.py`)**:
  - 텍스트와 이미지 중 변경을 원하는 대상만 선택 가능하도록 UI 체크박스 위젯(`CTkCheckBox`) 및 상태 변수 연동.
  - 텍스트/이미지 변환 플래그를 백엔드 스레드로 전달해 선택적 변환 수행 구현.
- **가상환경 및 라이브러리 정리**: 
  - Windows CMD 환경용 가상환경 활성화 매뉴얼 가이드 (`activate.bat`).
  - `requirements.txt`에 `opencv-python` 및 `numpy` 추가 반영 완료.

### 2. 다음 할 일 (To-Do) - 4단계(안정화 및 테스트)
- [x] 사용자 수동 테스트 진행 (텍스트/이미지 선택 옵션 및 대용량 교안 검증 완료)
- [x] (테스트 완료 후) `PyInstaller`를 활용하여 무설치 `.exe` 파일 빌드 완료 (`dist/main.exe`)
- [x] 최종 사용자 전달을 위한 패키징 완료
