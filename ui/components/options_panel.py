import customtkinter as ctk

class OptionsPanel(ctk.CTkFrame):
    """
    변환 옵션(텍스트/이미지 체크박스) 및 유사도 슬라이더 위젯군을 묶은 UI 컴포넌트입니다.
    """
    def __init__(self, parent, controller, on_option_change, on_slider_move, on_slider_release):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller
        self.on_option_change = on_option_change
        
        # 1. 체크박스 패널
        self.frame_checks = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_checks.pack(pady=5, fill="x")
        
        self.var_change_text = ctk.BooleanVar(value=True)
        self.chk_text = ctk.CTkCheckBox(
            self.frame_checks, 
            text="텍스트(글자) 색상 변경", 
            variable=self.var_change_text, 
            font=("Malgun Gothic", 12, "bold"), 
            command=self._on_check_toggle
        )
        self.chk_text.pack(side="left", padx=40)
        
        self.var_change_image = ctk.BooleanVar(value=True)
        self.chk_image = ctk.CTkCheckBox(
            self.frame_checks, 
            text="이미지 내 색상 치환", 
            variable=self.var_change_image, 
            font=("Malgun Gothic", 12, "bold"), 
            command=self._on_check_toggle
        )
        self.chk_image.pack(side="left", padx=40)
        
        # 2. 이미지 치환 오차율 슬라이더 (Tolerance)
        self.frame_tolerance = ctk.CTkFrame(
            self, 
            fg_color="#181818", 
            corner_radius=8, 
            border_width=1, 
            border_color="#252525"
        )
        self.frame_tolerance.pack(pady=10, fill="x")
        
        self.lbl_tolerance = ctk.CTkLabel(
            self.frame_tolerance, 
            text="이미지 색상 치환 유사도(Tolerance): 20 (기본값)", 
            font=("Malgun Gothic", 11), 
            text_color="#aaaaaa"
        )
        self.lbl_tolerance.pack(anchor="w", padx=15, pady=(8, 2))
        
        self.slider_tolerance = ctk.CTkSlider(
            self.frame_tolerance, 
            from_=0, 
            to=80, 
            number_of_steps=80, 
            fg_color="#2b2b2b", 
            progress_color="#00a8ff", 
            button_color="#00a8ff", 
            command=on_slider_move
        )
        self.slider_tolerance.set(20)
        self.slider_tolerance.pack(fill="x", padx=15, pady=(2, 8))
        self.slider_tolerance.bind("<ButtonRelease-1>", on_slider_release)
        
    def _on_check_toggle(self) -> None:
        """체크박스 변경 시 이미지 슬라이더의 잠금/해제 상태 제어"""
        change_image = self.var_change_image.get()
        if change_image:
            self.slider_tolerance.configure(state="normal")
            self.lbl_tolerance.configure(text=f"이미지 색상 치환 유사도(Tolerance): {int(self.slider_tolerance.get())}")
        else:
            self.slider_tolerance.configure(state="disabled")
            self.lbl_tolerance.configure(text="이미지 색상 치환 비활성화됨")
        
        self.on_option_change()
        
    def update_tolerance_label(self, val: int) -> None:
        """슬라이더 드래그 중인 임시 값을 표시"""
        self.lbl_tolerance.configure(text=f"이미지 색상 치환 유사도(Tolerance): {val}")
        
    def get_change_text(self) -> bool:
        return self.var_change_text.get()
        
    def get_change_image(self) -> bool:
        return self.var_change_image.get()
        
    def get_tolerance(self) -> int:
        return int(self.slider_tolerance.get())
        
    def set_state(self, is_running: bool) -> None:
        """변환 작업 실행에 따른 상태 Lock/Unlock"""
        if is_running:
            self.chk_text.configure(state="disabled")
            self.chk_image.configure(state="disabled")
            self.slider_tolerance.configure(state="disabled")
        else:
            self.chk_text.configure(state="normal")
            self.chk_image.configure(state="normal")
            self.slider_tolerance.configure(state="normal" if self.var_change_image.get() else "disabled")
