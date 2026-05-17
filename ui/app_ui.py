import os
import logging
from tkinter import filedialog, colorchooser, messagebox
import customtkinter as ctk
from controllers.app_controller import PPTColorChangerController

# 모듈화된 UI 컴포넌트 임포트
from ui.components.file_selector import FileSelector
from ui.components.color_chips_panel import ColorChipsPanel
from ui.components.options_panel import OptionsPanel
from ui.components.preview_panel import PreviewPanel
from ui.components.progress_panel import ProgressPanel

logger = logging.getLogger("ppt_color_changer")

class PPTColorChangerApp(ctk.CTk):
    """
    애플리케이션의 메인 윈도우 쉘(View) 클래스.
    각 독립된 UI 컴포넌트들을 조립하고 연결하여 전체 레이아웃을 형성합니다.
    """
    def __init__(self):
        super().__init__()
        self.title("PPT Color Changer (Premium Modular Edition)")
        self.geometry("720x720")
        
        # 기본 스타일 및 테마 적용
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#121212")
        
        # 컨트롤러 초기화 (View 인스턴스 위임)
        self.controller = PPTColorChangerController(self)
        
        # 컴포넌트 레이아웃 구성
        self._build_ui()
        
    def _build_ui(self):
        # 타이틀 헤더
        self.lbl_main_title = ctk.CTkLabel(
            self, 
            text="⚡ PPT Color Changer (Modular)", 
            font=("Segoe UI", 20, "bold"), 
            text_color="#00a8ff"
        )
        self.lbl_main_title.pack(pady=(15, 5))
        
        # 1. 파일 선택 카드 컴포넌트
        self.file_selector = FileSelector(self, self.controller, self.on_load_ppt)
        self.file_selector.pack(pady=10, padx=20, fill="x")
        
        # 메인 컨테이너 카드
        self.frame_middle_container = ctk.CTkFrame(
            self, 
            fg_color="#1e1e1e", 
            corner_radius=12, 
            border_width=1, 
            border_color="#2c2c2c"
        )
        self.frame_middle_container.pack(pady=10, padx=20, fill="both", expand=True)
        
        # 2. 색상 칩 목록 패널 컴포넌트
        self.color_chips_panel = ColorChipsPanel(
            self.frame_middle_container, 
            self.controller, 
            self.on_target_color_click
        )
        self.color_chips_panel.pack(pady=15, padx=15, fill="x")
        
        # 구분선
        self.separator = ctk.CTkFrame(self.frame_middle_container, height=1, fg_color="#2c2c2c")
        self.separator.pack(fill="x", padx=20, pady=5)
        
        # 3. 변환 옵션 및 유사도 슬라이더 컴포넌트
        self.options_panel = OptionsPanel(
            self.frame_middle_container, 
            self.controller, 
            self.on_option_changed, 
            self.on_slider_move, 
            self.on_slider_released
        )
        self.options_panel.pack(pady=10, padx=15, fill="x")
        
        # 4. 변환 미리보기 및 실시간 개수 분석 컴포넌트
        self.preview_panel = PreviewPanel(self, self.controller, self.on_select_new_color)
        self.preview_panel.pack(pady=5, padx=20, fill="x")
        
        # 5. 하단 실행 및 프로그레스 제어 컴포넌트
        self.progress_panel = ProgressPanel(self, self.controller, self.on_run_conversion)
        self.progress_panel.pack(pady=10, padx=20, fill="x")
        
        # 도움말 툴팁 영역
        self.frame_tooltip = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_tooltip.pack(pady=(0, 10), padx=20, fill="x")
        self.lbl_tooltip = ctk.CTkLabel(
            self.frame_tooltip, 
            text="💡 안내: 'SCHEME_' 색상은 PPT 기본 테마 색상 Accent 계열입니다.\n해당 테마 폰트가 대입된 개체만 안전하게 텍스트 색상이 변경됩니다.", 
            font=("Malgun Gothic", 10), 
            text_color="#777777", 
            justify="left"
        )
        self.lbl_tooltip.pack()

    # --- Controller -> View 업데이트 인터페이스 위임 구현 ---
    
    def set_loading_state(self, is_loading: bool) -> None:
        self.file_selector.set_loading_state(is_loading)
        self.progress_panel.set_loading_state(is_loading)

    def set_running_state(self, is_running: bool) -> None:
        self.file_selector.set_loading_state(is_running)
        self.options_panel.set_state(is_running)
        self.preview_panel.set_state(is_running)
        self.progress_panel.set_running_state(is_running)
        self.check_run_state()

    def update_status(self, text: str) -> None:
        self.progress_panel.update_status(text)

    def display_colors(self, colors_list: list) -> None:
        self.color_chips_panel.display_colors(colors_list)

    def update_target_color_display(self, color: str) -> None:
        self.preview_panel.update_target_color_display(color)
        self.color_chips_panel.highlight_chip(color)

    def update_new_color_display(self, hex_color: str) -> None:
        self.preview_panel.update_new_color_display(hex_color)

    def update_live_counts_display(self, loading: bool, text_count: int = 0, image_count: int = 0) -> None:
        self.preview_panel.update_live_counts_display(loading, text_count, image_count)

    def reset_selection(self) -> None:
        self.preview_panel.reset()
        self.progress_panel.set_run_button_state("disabled")

    def check_run_state(self) -> None:
        if self.controller.selected_target_color and self.controller.selected_new_color:
            self.progress_panel.set_run_button_state("normal")
        else:
            self.progress_panel.set_run_button_state("disabled")

    def show_error_dialog(self, title: str, msg: str) -> None:
        messagebox.showerror(title, msg)

    def show_success_dialog(self, title: str, msg: str, output_path: str) -> None:
        res = messagebox.askyesno(title, f"{msg}\n\n폴더를 열어 파일을 확인하시겠습니까?")
        if res:
            try:
                os.startfile(os.path.dirname(output_path))
            except Exception as e:
                logger.error(f"Failed to open directory: {e}")

    # --- 컴포넌트 이벤트 라우팅 (Controller로 요청 위임) ---

    def on_load_ppt(self) -> None:
        file_path = filedialog.askopenfilename(filetypes=[("PowerPoint Files", "*.pptx")])
        if file_path:
            self.file_selector.update_file_path(os.path.basename(file_path))
            self.controller.load_ppt(file_path)

    def on_target_color_click(self, color: str) -> None:
        change_text = self.options_panel.get_change_text()
        change_image = self.options_panel.get_change_image()
        tolerance = self.options_panel.get_tolerance()
        
        self.controller.select_target_color(color, change_text, change_image, tolerance)

    def on_select_new_color(self) -> None:
        color_code = colorchooser.askcolor(title="새 색상 선택")[1]
        if color_code:
            hex_color = color_code.lstrip('#').upper()
            self.controller.select_new_color(hex_color)

    def on_option_changed(self) -> None:
        if self.controller.selected_target_color:
            change_text = self.options_panel.get_change_text()
            change_image = self.options_panel.get_change_image()
            tolerance = self.options_panel.get_tolerance()
            self.controller.trigger_live_count(change_text, change_image, tolerance)

    def on_slider_move(self, val) -> None:
        self.options_panel.update_tolerance_label(int(val))

    def on_slider_released(self, event) -> None:
        if self.controller.selected_target_color:
            change_text = self.options_panel.get_change_text()
            change_image = self.options_panel.get_change_image()
            tolerance = self.options_panel.get_tolerance()
            self.controller.trigger_live_count(change_text, change_image, tolerance)

    def on_run_conversion(self) -> None:
        change_text = self.options_panel.get_change_text()
        change_image = self.options_panel.get_change_image()
        tolerance = self.options_panel.get_tolerance()
        
        if not change_text and not change_image:
            self.show_error_dialog("경고", "텍스트 또는 이미지 중 최소 하나는 치환 대상으로 선택하셔야 합니다.")
            return
            
        self.controller.run_conversion(change_text, change_image, tolerance)
