import customtkinter as ctk
from ui.components.color_chips_panel import get_readable_text_color

class PreviewPanel(ctk.CTkFrame):
    """
    선택된 대상 색상과 치환될 새 색상을 카드 형태로 대조하여 시각화하고,
    실시간으로 계산된 변환 가능 갯수를 안내해주는 미리보기 UI 컴포넌트입니다.
    """
    def __init__(self, parent, controller, on_picker_click):
        super().__init__(parent, fg_color="#1e1e1e", corner_radius=12, border_width=1, border_color="#2c2c2c")
        self.controller = controller
        
        self.lbl_preview_title = ctk.CTkLabel(
            self, 
            text="🔍 변환 미리보기", 
            font=("Malgun Gothic", 12, "bold"), 
            text_color="#aaaaaa"
        )
        self.lbl_preview_title.pack(anchor="w", padx=15, pady=(8, 0))
        
        self.flow_preview = ctk.CTkFrame(self, fg_color="transparent")
        self.flow_preview.pack(pady=10, fill="x")
        
        # Target chip (Before)
        self.preview_target = ctk.CTkLabel(
            self.flow_preview, 
            text="선택안됨", 
            width=120, 
            height=35, 
            corner_radius=6, 
            fg_color="#2c2c2c", 
            text_color="#888", 
            font=("Malgun Gothic", 11, "bold")
        )
        self.preview_target.pack(side="left", padx=(25, 10))
        
        self.arrow = ctk.CTkLabel(
            self.flow_preview, 
            text="→ 🎨 →", 
            font=("Malgun Gothic", 14, "bold"), 
            text_color="#00a8ff"
        )
        self.arrow.pack(side="left", padx=10)
        
        # Color Picker Button
        self.btn_new_color = ctk.CTkButton(
            self.flow_preview, 
            text="새 색상 선택 (Color Picker)", 
            width=180, 
            height=35, 
            state="disabled", 
            fg_color="#333", 
            hover_color="#444", 
            font=("Malgun Gothic", 11, "bold"), 
            command=on_picker_click
        )
        self.btn_new_color.pack(side="left", padx=10)
        
        # New Chip (After)
        self.preview_new = ctk.CTkLabel(
            self.flow_preview, 
            text="선택안됨", 
            width=120, 
            height=35, 
            corner_radius=6, 
            fg_color="#2c2c2c", 
            text_color="#888", 
            font=("Malgun Gothic", 11, "bold")
        )
        self.preview_new.pack(side="left", padx=(10, 25))
        
        # 실시간 변경 카운팅 라벨
        self.lbl_live_counts = ctk.CTkLabel(
            self, 
            text="색상을 선택하면 변경 예정 개수를 분석합니다.", 
            font=("Malgun Gothic", 12, "bold"), 
            text_color="#00a8ff"
        )
        self.lbl_live_counts.pack(pady=(0, 10))
        
    def update_target_color_display(self, color: str) -> None:
        """선택한 대상 색상 칩과 텍스트 동기화"""
        bg_color = "#3a3a3a" if color.startswith("SCHEME_") else f"#{color}"
        text_color = "white" if color.startswith("SCHEME_") else get_readable_text_color(color)
        display_text = color.replace("SCHEME_", "Theme ") if color.startswith("SCHEME_") else f"#{color}"
        
        self.preview_target.configure(
            text=display_text,
            fg_color=bg_color,
            text_color=text_color
        )
        # Picker 버튼 활성화
        self.btn_new_color.configure(state="normal", fg_color="#00a8ff", hover_color="#0088cc", text_color="white")
        
    def update_new_color_display(self, hex_color: str) -> None:
        """선택된 신규 치환 RGB 칩 및 텍스트 동기화"""
        bg_color = f"#{hex_color}"
        text_color = get_readable_text_color(hex_color)
        
        self.preview_new.configure(
            text=f"#{hex_color}",
            fg_color=bg_color,
            text_color=text_color
        )
        
    def update_live_counts_display(self, loading: bool, text_count: int = 0, image_count: int = 0) -> None:
        """계산된 변경 가능한 객체 정보 실시간 피드백"""
        if loading:
            self.lbl_live_counts.configure(text="⏳ 변경 가능한 개수 파악 중...", text_color="#00a8ff")
        else:
            total = text_count + image_count
            self.lbl_live_counts.configure(
                text=f"📊 변경 예상 개수: 텍스트 {text_count}개 | 이미지 {image_count}개",
                text_color="#2ecc71" if total > 0 else "#e74c3c"
            )
            
    def reset(self) -> None:
        """선택 내역 전체 비우기"""
        self.preview_target.configure(text="선택안됨", fg_color="#2c2c2c", text_color="#888")
        self.preview_new.configure(text="선택안됨", fg_color="#2c2c2c", text_color="#888")
        self.lbl_live_counts.configure(text="색상을 선택하면 변경 예정 개수를 분석합니다.", text_color="#00a8ff")
        self.btn_new_color.configure(state="disabled", fg_color="#333", text_color="#888")
        
    def set_state(self, is_running: bool) -> None:
        """실행 시 picker 제어 잠금"""
        if is_running:
            self.btn_new_color.configure(state="disabled")
        else:
            self.btn_new_color.configure(state="normal" if self.controller.selected_target_color else "disabled")
