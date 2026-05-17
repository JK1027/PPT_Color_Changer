import customtkinter as ctk

class FileSelector(ctk.CTkFrame):
    """
    PPT 파일을 열고 선택된 파일명을 표시하는 카드형 UI 컴포넌트입니다.
    """
    def __init__(self, parent, controller, on_load_click):
        super().__init__(parent, fg_color="#1e1e1e", corner_radius=12, border_width=1, border_color="#2c2c2c")
        self.controller = controller
        
        self.lbl_file = ctk.CTkLabel(
            self, 
            text="📂 선택된 파워포인트 파일이 없습니다.", 
            anchor="w", 
            font=("Malgun Gothic", 12)
        )
        self.lbl_file.pack(side="left", padx=15, pady=15, fill="x", expand=True)
        
        self.btn_load = ctk.CTkButton(
            self, 
            text="PPT 열기", 
            fg_color="#00a8ff", 
            hover_color="#0088cc", 
            font=("Malgun Gothic", 12, "bold"), 
            command=on_load_click
        )
        self.btn_load.pack(side="right", padx=15, pady=15)
        
    def update_file_path(self, text: str) -> None:
        """선택된 파일 경로 업데이트"""
        self.lbl_file.configure(text=text)
        
    def set_loading_state(self, is_loading: bool) -> None:
        """분석/처리 중 버튼 잠금 상태 변환"""
        if is_loading:
            self.btn_load.configure(state="disabled")
        else:
            self.btn_load.configure(state="normal")
