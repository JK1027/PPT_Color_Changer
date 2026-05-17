import customtkinter as ctk

class ProgressPanel(ctk.CTkFrame):
    """
    작업진행 상태 출력(status), 로딩 바(ProgressBar), 
    그리고 최종 실행(Run) 버튼의 렌더링 및 제어를 총괄하는 UI 컴포넌트입니다.
    """
    def __init__(self, parent, controller, on_run_click):
        super().__init__(parent, fg_color="#1e1e1e", corner_radius=12, border_width=1, border_color="#2c2c2c")
        self.controller = controller
        
        self.lbl_status = ctk.CTkLabel(
            self, 
            text="대기 중...", 
            font=("Malgun Gothic", 11), 
            text_color="#888888"
        )
        self.lbl_status.pack(pady=(8, 2))
        
        self.progress_bar = ctk.CTkProgressBar(
            self, 
            mode="indeterminate", 
            height=6, 
            progress_color="#00a8ff"
        )
        self.progress_bar.pack(pady=5, padx=15, fill="x")
        self.progress_bar.set(0)
        
        self.btn_run = ctk.CTkButton(
            self, 
            text="색상 일괄 변경 실행 (백업 자동 생성)", 
            state="disabled", 
            fg_color="#27ae60", 
            hover_color="#219653", 
            font=("Malgun Gothic", 13, "bold"), 
            command=on_run_click
        )
        self.btn_run.pack(pady=(5, 12))
        
    def update_status(self, text: str) -> None:
        """현재 하단 진행 상태 문구 갱신"""
        self.lbl_status.configure(text=text)
        
    def set_loading_state(self, is_loading: bool) -> None:
        """스캐닝 분석 작업 시 프로그레스 바 상태 제어"""
        if is_loading:
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            self.progress_bar.set(0)
            
    def set_running_state(self, is_running: bool) -> None:
        """색상 치환 연산 작업 시 프로그레스 바 및 실행 버튼 제어"""
        if is_running:
            self.btn_run.configure(state="disabled")
            self.progress_bar.start()
        else:
            self.progress_bar.stop()
            self.progress_bar.set(0)
            
    def set_run_button_state(self, state: str) -> None:
        """실행 버튼의 활성화(normal) / 비활성화(disabled) 설정"""
        self.btn_run.configure(state=state)
