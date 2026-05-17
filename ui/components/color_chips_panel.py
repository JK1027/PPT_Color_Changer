import customtkinter as ctk

def get_readable_text_color(hex_str: str) -> str:
    """배경색의 밝기(Luminance)에 따라 가독성이 뛰어난 텍스트 색상(검정/흰색) 반환"""
    try:
        hex_str = hex_str.lstrip('#')
        if len(hex_str) != 6:
            return "white"
        r = int(hex_str[0:2], 16)
        g = int(hex_str[2:4], 16)
        b = int(hex_str[4:6], 16)
        # YIQ 공식을 이용한 밝기 계산
        brightness = (r * 299 + g * 587 + b * 114) / 1000
        return "#121212" if brightness > 128 else "#FFFFFF"
    except Exception:
        return "white"

class ColorChipsPanel(ctk.CTkFrame):
    """
    추출된 텍스트 색상 목록을 가로 스크롤 가능한 칩 형태로 렌더링하고 선택을 관리하는 UI 컴포넌트입니다.
    """
    def __init__(self, parent, controller, on_chip_click):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.on_chip_click = on_chip_click
        self.color_chip_buttons = {}
        
        self.lbl_colors = ctk.CTkLabel(
            self, 
            text="🎨 추출된 텍스트 색상 목록 (칩 클릭 시 대상 지정)", 
            font=("Malgun Gothic", 13, "bold"), 
            text_color="#e0e0e0"
        )
        self.lbl_colors.pack(pady=(0, 5))
        
        # 색상칩 가로 스크롤 컨테이너
        self.color_chips_frame = ctk.CTkScrollableFrame(
            self, 
            orientation="horizontal", 
            height=80, 
            fg_color="#151515", 
            corner_radius=8
        )
        self.color_chips_frame.pack(pady=5, fill="x")
        
    def display_colors(self, colors_list: list) -> None:
        """가로 칩 프레임에 색상 버튼 렌더링"""
        for widget in self.color_chips_frame.winfo_children():
            widget.destroy()
        self.color_chip_buttons.clear()
        
        if not colors_list:
            ctk.CTkLabel(
                self.color_chips_frame, 
                text="추출된 유효 색상이 존재하지 않습니다.", 
                text_color="#888888", 
                font=("Malgun Gothic", 11)
            ).pack(pady=20)
            return
            
        for color in colors_list:
            display_text = color
            bg_color = "transparent"
            
            # 파워포인트 테마색 처리
            if color.startswith("SCHEME_"):
                display_text = color.replace("SCHEME_", "Theme ")
                bg_color = "#3a3a3a"
                text_c = "white"
            else:
                bg_color = f"#{color}"
                text_c = get_readable_text_color(color)
            
            hover_c = "#444" if bg_color == "transparent" else bg_color
            
            btn = ctk.CTkButton(
                self.color_chips_frame, 
                text=display_text, 
                width=110, 
                height=50, 
                corner_radius=6, 
                border_width=2, 
                border_color="#121212",
                font=("Segoe UI", 11, "bold"),
                fg_color=bg_color,
                text_color=text_c,
                hover_color=hover_c,
                command=lambda c=color: self.on_chip_click(c)
            )
            btn.pack(side="left", padx=6, pady=5)
            self.color_chip_buttons[color] = btn
            
    def highlight_chip(self, selected_color: str) -> None:
        """선택한 색상 칩 테두리 강조 처리"""
        for c, btn in self.color_chip_buttons.items():
            if c == selected_color:
                btn.configure(border_color="#00a8ff") # 파란색 테두리 하이라이트
            else:
                btn.configure(border_color="#121212") # 초기화
                
    def clear(self) -> None:
        """색상 목록 프레임 비우기"""
        for widget in self.color_chips_frame.winfo_children():
            widget.destroy()
        self.color_chip_buttons.clear()
