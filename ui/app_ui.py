import os
import threading
import logging
from tkinter import filedialog, colorchooser, messagebox
import customtkinter as ctk
from core.ppt_reader import extract_all_colors, replace_color

# 로깅 설정 (앱 중단 방지 및 에러 추적)
logging.basicConfig(filename='app.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class PPTColorChangerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("PPT Text Color Changer")
        self.geometry("680x550")
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#1a1a1a") # 다크 모드 배경
        
        # 상태 변수
        self.current_ppt_path = None
        self.extracted_colors = []
        self.selected_target_color = None
        self.selected_new_color = None
        self.color_chip_buttons = {}
        
        self._build_ui()
        
    def _build_ui(self):
        # 상단 패널: 파일 선택 (카드형 UI)
        self.frame_top = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        self.frame_top.pack(pady=15, padx=20, fill="x")
        
        self.lbl_file = ctk.CTkLabel(self.frame_top, text="선택된 파일 없음", width=450, anchor="w", font=("", 13))
        self.lbl_file.pack(side="left", padx=15, pady=15)
        
        self.btn_load = ctk.CTkButton(self.frame_top, text="PPT 열기", font=("", 13, "bold"), command=self.on_load_ppt)
        self.btn_load.pack(side="right", padx=15, pady=15)
        
        # 중단 패널: 색상 선택 및 매핑
        self.frame_middle = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        self.frame_middle.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.lbl_colors = ctk.CTkLabel(self.frame_middle, text="🎨 추출된 색상 목록 (클릭하여 대상 색상 선택)", font=("", 15, "bold"))
        self.lbl_colors.pack(pady=15)
        
        # 색상칩 렌더링 영역
        self.color_chips_frame = ctk.CTkScrollableFrame(self.frame_middle, orientation="horizontal", height=90, fg_color="#1a1a1a", corner_radius=10)
        self.color_chips_frame.pack(pady=5, padx=15, fill="x")
        
        # 선택 상태 표시
        self.frame_selection = ctk.CTkFrame(self.frame_middle, fg_color="transparent")
        self.frame_selection.pack(pady=20, fill="x")
        
        self.lbl_target = ctk.CTkLabel(self.frame_selection, text="대상 색상: 없음", width=150, anchor="w", font=("", 13, "bold"))
        self.lbl_target.pack(side="left", padx=20)
        
        self.btn_new_color = ctk.CTkButton(self.frame_selection, text="🖌️ 새 색상 선택 (Color Picker)", state="disabled", font=("", 13, "bold"), command=self.on_select_new_color)
        self.btn_new_color.pack(side="left", padx=20)
        
        self.lbl_new = ctk.CTkLabel(self.frame_selection, text="새 색상: 없음", width=150, anchor="w", font=("", 13, "bold"))
        self.lbl_new.pack(side="left", padx=20)
        
        # 변환 대상 선택 (체크박스) (v2.2 추가)
        self.frame_options = ctk.CTkFrame(self.frame_middle, fg_color="transparent")
        self.frame_options.pack(pady=5, fill="x")
        
        self.var_change_text = ctk.BooleanVar(value=True)
        self.chk_text = ctk.CTkCheckBox(self.frame_options, text="텍스트(글자) 색상 변경", variable=self.var_change_text, font=("", 13, "bold"))
        self.chk_text.pack(side="left", padx=50)
        
        self.var_change_image = ctk.BooleanVar(value=True)
        self.chk_image = ctk.CTkCheckBox(self.frame_options, text="이미지 내 색상 변경", variable=self.var_change_image, font=("", 13, "bold"))
        self.chk_image.pack(side="left", padx=50)
        
        # 하단 패널: 실행 및 프로그레스 (카드형 UI)
        self.frame_bottom = ctk.CTkFrame(self, fg_color="#2b2b2b", corner_radius=15)
        self.frame_bottom.pack(pady=15, padx=20, fill="x")
        
        self.lbl_status = ctk.CTkLabel(self.frame_bottom, text="대기 중...")
        self.lbl_status.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.frame_bottom, mode="indeterminate")
        self.progress_bar.pack(pady=5, padx=10, fill="x")
        self.progress_bar.set(0)
        
        self.btn_run = ctk.CTkButton(self.frame_bottom, text="색상 일괄 변경 실행", state="disabled", fg_color="green", hover_color="darkgreen", command=self.on_run_conversion)
        self.btn_run.pack(pady=10)
        
    def _update_status(self, text):
        self.lbl_status.configure(text=text)

    def on_load_ppt(self):
        file_path = filedialog.askopenfilename(filetypes=[("PowerPoint Files", "*.pptx")])
        if not file_path:
            return
            
        self.current_ppt_path = file_path
        self.lbl_file.configure(text=os.path.basename(file_path))
        
        # UI Freezing 방지: 백그라운드 스레드에서 파일 분석
        self.btn_load.configure(state="disabled")
        self._update_status("PPT 파일 분석 및 색상 추출 중...")
        self.progress_bar.start()
        
        threading.Thread(target=self._extract_colors_thread, args=(file_path,), daemon=True).start()

    def _extract_colors_thread(self, file_path):
        try:
            colors = extract_all_colors(file_path)
            # 메인 스레드로 UI 업데이트 위임 (thread safety)
            self.after(0, self._on_extract_success, colors)
        except Exception as e:
            logging.error(f"Error extracting colors: {str(e)}", exc_info=True)
            self.after(0, self._on_extract_error, str(e))
            
    def _on_extract_success(self, colors):
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.btn_load.configure(state="normal")
        self._update_status("색상 추출 완료.")
        
        self.extracted_colors = list(colors)
        self._render_color_chips()
        
        # 선택 초기화
        self.selected_target_color = None
        self.lbl_target.configure(text="대상 색상: 없음")
        self.btn_new_color.configure(state="disabled")
        self._check_run_state()
        
    def _on_extract_error(self, error_msg):
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.btn_load.configure(state="normal")
        self._update_status("색상 추출 실패!")
        messagebox.showerror("오류", f"파일을 읽는 중 문제가 발생했습니다.\n\n{error_msg}")

    def _render_color_chips(self):
        for widget in self.color_chips_frame.winfo_children():
            widget.destroy()
        self.color_chip_buttons.clear()
            
        if not self.extracted_colors:
            ctk.CTkLabel(self.color_chips_frame, text="추출된 색상이 없습니다.").pack()
            return
            
        for color in self.extracted_colors:
            display_text = color
            bg_color = "transparent"
            if len(color) == 6 and all(c in '0123456789ABCDEFabcdef' for c in color):
                bg_color = f"#{color}"
            
            hover_c = "#444" if bg_color == "transparent" else bg_color
            
            btn = ctk.CTkButton(self.color_chips_frame, text=display_text, width=110, height=55, 
                                corner_radius=8, border_width=3, border_color="#1a1a1a",
                                font=("", 13, "bold"),
                                fg_color=bg_color if bg_color != "transparent" else ["#444", "#555"],
                                text_color="black" if bg_color != "transparent" else "white",
                                hover_color=hover_c,
                                command=lambda c=color: self.on_target_color_select(c))
            btn.pack(side="left", padx=8, pady=5)
            self.color_chip_buttons[color] = btn

    def on_target_color_select(self, color):
        self.selected_target_color = color
        self.lbl_target.configure(text=f"대상 색상: {color}")
        self.btn_new_color.configure(state="normal")
        
        # 선택된 칩에 파란색 테두리 강조
        for c, btn in self.color_chip_buttons.items():
            if c == color:
                btn.configure(border_color="#00a8ff") # Highlight
            else:
                btn.configure(border_color="#1a1a1a") # Hidden
                
        self._check_run_state()

    def on_select_new_color(self):
        color_code = colorchooser.askcolor(title="새 색상 선택")[1]
        if color_code:
            hex_color = color_code.lstrip('#').upper()
            self.selected_new_color = hex_color
            self.lbl_new.configure(text=f"새 색상: #{hex_color}")
            self._check_run_state()

    def _check_run_state(self):
        if self.selected_target_color and self.selected_new_color:
            self.btn_run.configure(state="normal")
        else:
            self.btn_run.configure(state="disabled")

    def on_run_conversion(self):
        if not self.current_ppt_path or not self.selected_target_color or not self.selected_new_color:
            return
            
        change_text = self.var_change_text.get()
        change_image = self.var_change_image.get()
        
        # 둘 다 체크 해제한 경우 방어 코드
        if not change_text and not change_image:
            messagebox.showwarning("경고", "텍스트와 이미지 중 최소 하나는 선택해야 합니다.")
            return
            
        base, ext = os.path.splitext(self.current_ppt_path)
        output_path = f"{base}_modified{ext}"
        
        self.btn_run.configure(state="disabled")
        self._update_status("색상 변경 및 저장 중...")
        self.progress_bar.start()
        
        threading.Thread(target=self._run_conversion_thread, 
                         args=(self.current_ppt_path, self.selected_target_color, self.selected_new_color, output_path, change_text, change_image), 
                         daemon=True).start()

    def _run_conversion_thread(self, input_path, target_color, new_color, output_path, change_text, change_image):
        try:
            change_count = replace_color(input_path, target_color, new_color, output_path, change_text, change_image)
            self.after(0, self._on_convert_success, change_count, output_path)
        except PermissionError:
            logging.error("PermissionError during save.", exc_info=True)
            self.after(0, self._on_convert_error, "PPT 파일이 다른 프로그램(파워포인트 등)에서 열려있습니다.\n파일을 닫은 후 다시 시도해주세요.")
        except Exception as e:
            logging.error(f"Error during conversion: {str(e)}", exc_info=True)
            self.after(0, self._on_convert_error, str(e))

    def _on_convert_success(self, change_count, output_path):
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.btn_run.configure(state="normal")
        self._update_status("작업 완료!")
        messagebox.showinfo("성공", f"총 {change_count}개의 객체 색상이 변경되었습니다.\n\n저장 경로:\n{output_path}")

    def _on_convert_error(self, error_msg):
        self.progress_bar.stop()
        self.progress_bar.set(0)
        self.btn_run.configure(state="normal")
        self._update_status("작업 실패!")
        messagebox.showerror("오류", f"처리 중 오류가 발생했습니다.\n\n{error_msg}")
