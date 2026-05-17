# PPT Color Changer 시스템 아키텍처 정의서 (ARCHITECTURE)
## 확장 가능한 고품격 레이어드 패러다임 • 버전 v4.0

본 문서는 PPT Color Changer 프로그램의 계층적 아키텍처 및 내부 모듈 간의 유기적 흐름과 결합도 최소화 전략을 설명합니다.

---

## 1. 아키텍처 개요 (SoC)

프로그램은 **관심사 분리(Separation of Concerns, SoC)** 원칙을 엄격하게 준수하여 설계되었습니다.
어떠한 경우에도 화면 표시(GUI) 객체가 비즈니스 데이터 및 핵심 PPT 변환 알고리즘에 직접 관여하지 않으며, 단방향 흐름으로 위임됩니다.

```plaintext
   [ UI Layer (app_ui.py) ]  ◀─── 스레드 안전 UI 갱신 (.after 스케줄러)
            │ (이벤트 수집)
            ▼
 [ Controller Layer (app_controller.py) ] (중앙 상태 관리 및 작업 위임)
            │
            ▼
  [ Service Layer (ppt_service.py) ] (비즈니스 워크플로우 오케스트레이션)
            │
            ▼
    [ Core Facade (ppt_reader.py) ] (핵심 엔진 단일 창구)
            │
     ┌──────┴──────┬──────────────┐
     ▼             ▼              ▼
ppt_scanner.py  text_color_replacer.py  image_replacer.py (image_processor.py)
```

---

## 2. 계층별 상세 역할 및 구조

### 2-1. UI Layer (View)
- **메인 쉘 (`ui/app_ui.py`)**: 각 위젯 카드를 격리된 컴포넌트로 선언하고 격자 배치하는 레이아웃 코디네이터 역할만 수행합니다. (코드 분량 약 150줄 내외 극단적 경량화)
- **컴포넌트 패널 (`ui/components/`)**:
  - `file_selector.py`: 파일 로딩 카드 UI 담당.
  - `color_chips_panel.py`: 가로 스크롤 색상 칩 렌더링 및 하이라이트 테두리 관리.
  - `options_panel.py`: 변경 대상(글자/이미지) 토글 체크박스 및 유사도 조절 슬라이더 상태 조작 관리.
  - `preview_panel.py`: Before/After 변환 색상 칩 가독성 보정 매칭 뷰 및 실시간 변경수 안내 라벨 피드백.
  - `progress_panel.py`: 진행 상태 표시, 프로그레스 바 작동 및 최종 실행 실행 버튼 상태 관리.

### 2-2. Controller Layer
- **상태 관리자 (`controllers/app_controller.py`)**: 
  - 앱의 활성 상태 변수(`current_ppt_path`, `selected_target_color`, `selected_new_color`, `extracted_colors`)를 중앙 집중식으로 보존하는 상태 저장소입니다.
  - 백그라운드 멀티스레드(`threading.Thread`)를 스폰하여 무거운 작업을 실행하고, 스레드 중복 방지를 위한 `_count_thread_lock` 동기화 락을 관리합니다.
  - 백그라운드 워커 스레드가 작업 완료 시, GUI 비정상 죽음을 막기 위해 반드시 **Tkinter의 `.after()` 메인 스레드 예약 함수**를 통해서만 UI를 조작하게 스케줄링합니다.

### 2-3. Service Layer
- **오케스트레이터 (`services/ppt_service.py`)**:
  - 컨트롤러와 Core 비즈니스 로직 사이의 결합도를 낮추는 미들웨어 서비스 레이어입니다.
  - 컨트롤러는 저수준의 `core` 라이브러리를 직접 임포트하지 않으며, 오직 `PPTService`가 제공하는 고수준 인터페이스(`extract_ppt_colors`, `count_occurrences`, `execute_replacement`)만 호출합니다.

### 2-4. Core Layer (비즈니스 연산 엔진)
- **Facade (`core/ppt_reader.py`)**: 하위 핵심 세부 연산 모듈을 취합하여 하위 호환성을 유지시키는 일괄 관문 역할을 수행합니다.
- **Scanner (`core/ppt_scanner.py`)**: 도형(Shape), 그룹 내부 도형(Group Shapes), 표(Table Cell)를 재귀적으로 돌며 텍스트의 유효 색상셋을 수집하고, 타겟 색상 매칭 빈도를 사전 계산하는 탐색 엔진입니다.
- **Text Replacer (`core/text_color_replacer.py`)**: PPT 내 일반 도형 및 표 내부 Run 단위 글꼴 색상을 치환하는 텍스트 전담 모듈입니다.
- **Image Replacer (`core/image_replacer.py`)**: `python-pptx`가 제공하지 않는 이미지 수정 한계를 저수준 XML 트리 조작(`shape._element.remove()`)을 통해 원본의 위치와 치수를 그대로 보존하면서 덮어씌워 강제 교체하는 이미지 치환 전담 모듈입니다.
- **Image Processor (`core/image_processor.py`)**: OpenCV를 사용하여 이미지 내 타겟 색상 영역을 dynamic HSV 범위로 검출하고 치환(Hue, Saturation, Value 조절)하는 영상 처리 전문 엔진입니다.

---

## 3. 스레딩 및 스레드 세이프 안정성 규칙

1. **GUI 비결합 원칙**: 백그라운드 스레드 내부에서 직접 UI 컴포넌트나 Tkinter 위젯을 생성, 소멸, 갱신해서는 안 됩니다.
2. **동기화 락**: 사전 카운팅 작업은 사용자가 연속해서 조작(체크박스 토글 후 즉시 슬라이더 드래그 등)할 수 있으므로, `threading.Lock`을 통해 선행 스레드 완료 대기를 보장하고, 변경된 타겟 색상 검증을 거쳐 최종 유효 데이터만 화면에 반환시킵니다.
3. **Tkinter 스레드 안전 콜백**:
   ```python
   # 백그라운드 스레드 연산 완료 후 UI 반영 예시
   self.ui.after(0, self._on_success_callback, results)
   ```
