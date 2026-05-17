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

## 📅 [2026-05-17] 사용자 피드백 반영 및 대규모 아키텍처 리팩토링 (v3.0) 완료

### 1. 수행 내역
- **MVC (Layered) 아키텍처 전환 완료**:
  - `ui/app_ui.py`를 순수 View 객체로 전환하여 화면 렌더링에만 집중시킴.
  - `controllers/app_controller.py`를 신설하여 상태 정보 보관, 백그라운드 멀티스레드 제어, UI 스레드 스케줄링(after) 통합 관리.
  - `core/` 비즈니스 엔진에서 UI 의존성 및 로깅 결합 요소를 완벽 제거.
- **비즈니스 엔진 모듈 분할 및 Facade 패턴 도입**:
  - `core/ppt_scanner.py`: PPT 형태소 순회 및 색상 빈도 사전 카운팅을 책임짐.
  - `core/text_color_replacer.py`: 텍스트 Paragraph 및 Table Cell 색상 일괄 치환 격리.
  - `core/image_replacer.py`: python-pptx 한계를 우회하는 저수준 XML 이미지 치환 우회 로직을 완벽 격리하고 예외 격리.
  - `core/image_processor.py`: OpenCV 관련 로직 분할 및 유사 색상 검출(`image_contains_color`) 함수 추가.
- **Premium UX 기능 추가**:
  - **Before/After 색상 변환 미리보기**: 선택한 변경 대상 색상과 Picker 색상을 시각화 카드로 대조 표출.
  - **실시간 사전 카운팅**: 색상칩 및 텍스트/이미지 옵션 선택 시 변경 예상 개수("텍스트 X개, 이미지 Y개")를 백그라운드 스레드에서 실시간 분석하여 화면에 표출.
  - **이미지 색상 치환 오차율(Tolerance) 조절 슬라이더**: 0~80 슬라이더를 통해 드래그 중지 시 실시간 개수 계산 및 dynamic HSV 범위 대입.
  - **테마색(SCHEME_*) 안내**: 사용자 이해를 돕기 위한 하단 툴팁 정보창 구성.
- **OpenCV 최적화 및 경량 빌드**:
  - `opencv-python`을 `opencv-python-headless`로 대체하여 윈도우 환경 컴파일 호환성 확보 및 EXE 크기 경량화 달성.
  - `print` 디버깅 함수를 Python 기본 `logging` 모듈로 통합.
  - 모든 리팩토링 요소의 PoC 테스트 및 PyInstaller 실행 빌드 통과 완료.

### 2. 다음 할 일 (To-Do)
- [x] 실제 교안 파일에 대한 최종 성능 및 엣지 케이스 확인
- [ ] 다중 색상 동시 변경(Batch Color Change) 기능 검토

## 📅 [2026-05-17] 아키텍처 극대화: Service 계층 및 UI 컴포넌트화 완료 (v4.0)

### 1. 수행 내역
- **Service Layer (`services/`) 도입 완료**:
  - `services/ppt_service.py`를 신설하여 비즈니스 로직(스캔, 색상 매칭 분석, 치환 연산)의 오케스트레이션을 완벽 분리.
  - `controllers/app_controller.py`가 더 이상 `core/` 모듈을 직접 참조하지 않도록 의존성을 격리하여 "God Object" 조짐을 원천 타파.
- **UI 컴포넌트 (`ui/components/`) 디렉토리 분할 및 위젯화 완료**:
  - `ui/components/file_selector.py`: 파일 열기 카드 UI 모듈화.
  - `ui/components/color_chips_panel.py`: 색상칩 목록 렌더링 및 하이라이트 제어 위젯 모듈화.
  - `ui/components/options_panel.py`: 체크박스 및 유사도 조절 슬라이더 상태 제어 위젯 모듈화.
  - `ui/components/preview_panel.py`: Before/After 변환 색상칩 대조 및 실시간 갯수 안내 위젯 모듈화.
  - `ui/components/progress_panel.py`: 작업 진행률 및 상태 텍스트, 실행 버튼 제어 위젯 모듈화.
  - 이로써 `ui/app_ui.py`는 단 150줄 가량의 극단적으로 얇고 명확한 **컴포넌트 레이아웃 조립 쉘**로 축소되어 유지보수성이 극대화되었습니다.
- **프로젝트 무결성 유지 및 재빌드 완료**:
  - 리팩토링된 전체 아키텍처 상태에서 PoC 단독 테스트를 완벽 통과했습니다.
  - `PyInstaller`를 활용하여 의존성이 누락되거나 에러 없이 최적화된 새로운 standalone `.exe` (`dist/main.exe`) 빌드를 최종 완료했습니다.

### 2. 다음 할 일 (To-Do)
- [ ] 사용자 실사용 피드백 수집 및 최적 유사도(Tolerance) 분석
- [ ] 다중 색상 동시 변경(Batch) 기능 상세 설계서 검토

## 📅 [2026-05-17] 차기 기능 설계: 이미지 도미넌트(강조색) 색상 추출 계획 수립 (v4.1 예정)

### 1. 수행 내역
- **이미지 색상 분석 및 추출 고도화 기획 수립 완료**:
  - `core/image_processor.py`에 `extract_dominant_colors_from_image` 기능을 추가하여 이미지 내 핵심 하이라이트 유채색(강조색)을 도출하는 정교한 추출 필터 설계.
  - 가로/세로 100픽셀 수준으로 Downscaling하여 스캐닝 속도를 비약적으로 향상시키고 UI 프리징 방지.
  - HSV 색공간 기반 필터링(Value < 40 저명도 흑색 제외, Value > 220 및 Saturation < 35 고명도 종이 배경 백색 제외, Saturation < 40 회색선 제외)을 통해 교과서 스캔 노이즈 완벽 차단 기획.
  - `core/ppt_scanner.py` 내부 재귀 도형 순회 중 `MSO_SHAPE_TYPE.PICTURE` 발생 시 이미지 바이너리를 뽑아 추출기에 투입하고 `unique_colors`에 자동 병합하는 핵심 연동 흐름 구상.
- **문서화 규격 구축**:
  - `PRD.md`, `ARCHITECTURE.md`, `CURRENT_STATUS.md`, `RULES.md`를 신설하여 최상위 아키텍처 상태를 영구 기록하고 협업 가이드라인 규칙 완비.



