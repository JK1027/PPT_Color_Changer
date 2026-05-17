import os
import threading
import logging
from services.ppt_service import PPTService

logger = logging.getLogger("ppt_color_changer")

class PPTColorChangerController:
    """
    비즈니스 서비스(PPTService)와 UI(View) 간의 흐름을 조율하는 컨트롤러 클래스.
    모든 데이터 조작 및 비즈니스 연산 요청은 PPTService로 전달되며, 
    thread-safe한 방식으로 결과를 UI에 반영합니다.
    """
    def __init__(self, ui):
        self.ui = ui
        
        # 서비스 계층 초기화
        self.ppt_service = PPTService()
        
        # 상태 변수
        self.current_ppt_path = None
        self.extracted_colors = []
        self.selected_target_color = None
        self.selected_new_color = None
        
        # 실시간 변경 카운팅 스레드 동기화용 락
        self._count_thread_lock = threading.Lock()
        
    def load_ppt(self, file_path: str) -> None:
        """PPT 파일을 로드하고 백그라운드 스레드에서 색상 추출 실행"""
        if not file_path:
            return
            
        self.current_ppt_path = file_path
        self.selected_target_color = None
        self.selected_new_color = None
        
        self.ui.set_loading_state(True)
        self.ui.update_status("PPT 파일 분석 및 색상 추출 중...")
        
        # 백그라운드 스레드에서 파일 분석 실행
        threading.Thread(target=self._load_ppt_thread, args=(file_path,), daemon=True).start()
        
    def _load_ppt_thread(self, file_path: str) -> None:
        try:
            # 서비스 계층 호출
            colors = self.ppt_service.extract_ppt_colors(file_path)
            # 스레드 안전하게 메인 UI 스레드로 성공 핸들러 위임
            self.ui.after(0, self._on_load_success, colors)
        except Exception as e:
            logger.error(f"Error in loading ppt thread: {e}", exc_info=True)
            self.ui.after(0, self._on_load_error, str(e))
            
    def _on_load_success(self, colors) -> None:
        self.extracted_colors = sorted(list(colors))
        self.ui.set_loading_state(False)
        self.ui.update_status("색상 추출 완료.")
        self.ui.display_colors(self.extracted_colors)
        self.ui.reset_selection()
        
    def _on_load_error(self, error_msg: str) -> None:
        self.ui.set_loading_state(False)
        self.ui.update_status("색상 추출 실패!")
        self.ui.show_error_dialog("오류", f"PPT 파일을 분석하는 중 오류가 발생했습니다.\n\n{error_msg}")
        
    def select_target_color(self, color: str, change_text: bool, change_image: bool, tolerance: int) -> None:
        """대상 색상이 선택되었을 때 상태를 업데이트하고 사전 카운트 수행"""
        self.selected_target_color = color
        self.ui.update_target_color_display(color)
        self.trigger_live_count(change_text, change_image, tolerance)
        self.ui.check_run_state()
        
    def select_new_color(self, hex_color: str) -> None:
        """새로운 교체 색상이 선택되었을 때 상태 업데이트"""
        self.selected_new_color = hex_color
        self.ui.update_new_color_display(hex_color)
        self.ui.check_run_state()
        
    def trigger_live_count(self, change_text: bool, change_image: bool, tolerance: int) -> None:
        """선택된 색상의 실시간 발생 빈도를 계산하는 스레드 구동"""
        if not self.current_ppt_path or not self.selected_target_color:
            return
            
        self.ui.update_live_counts_display(loading=True)
        
        threading.Thread(
            target=self._live_count_thread, 
            args=(self.current_ppt_path, self.selected_target_color, change_text, change_image, tolerance),
            daemon=True
        ).start()
        
    def _live_count_thread(self, ppt_path: str, target_color: str, change_text: bool, change_image: bool, tolerance: int) -> None:
        with self._count_thread_lock:
            # 서비스 계층 호출
            counts = self.ppt_service.count_occurrences(
                ppt_path, target_color, change_text, change_image, tolerance
            )
            # 스레드 연산 도중 사용자가 다른 색상으로 선택을 변경했다면 무시
            if self.selected_target_color == target_color:
                self.ui.after(0, self._on_live_count_success, counts)
                
    def _on_live_count_success(self, counts: dict) -> None:
        self.ui.update_live_counts_display(
            loading=False, 
            text_count=counts.get("text_count", 0), 
            image_count=counts.get("image_count", 0)
        )
        
    def run_conversion(self, change_text: bool, change_image: bool, tolerance: int) -> None:
        """백그라운드에서 색상 일괄 변경 실행"""
        if not self.current_ppt_path or not self.selected_target_color or not self.selected_new_color:
            return
            
        base, ext = os.path.splitext(self.current_ppt_path)
        output_path = f"{base}_modified{ext}"
        
        self.ui.set_running_state(True)
        self.ui.update_status("색상 변경 및 저장 중...")
        
        threading.Thread(
            target=self._run_conversion_thread,
            args=(self.current_ppt_path, self.selected_target_color, self.selected_new_color, output_path, change_text, change_image, tolerance),
            daemon=True
        ).start()
        
    def _run_conversion_thread(self, input_path: str, target_color: str, new_color: str, output_path: str, change_text: bool, change_image: bool, tolerance: int) -> None:
        try:
            # 서비스 계층 호출
            change_count = self.ppt_service.execute_replacement(
                input_path, target_color, new_color, output_path, change_text, change_image, tolerance
            )
            self.ui.after(0, self._on_convert_success, change_count, output_path)
        except PermissionError:
            logger.error("Permission error during replacement - file locked.", exc_info=True)
            self.ui.after(0, self._on_convert_error, "PPT 파일이 다른 프로그램(파워포인트 등)에서 열려있습니다.\n파일을 닫은 후 다시 시도해주세요.")
        except Exception as e:
            logger.error(f"Error during color replacement execution: {e}", exc_info=True)
            self.ui.after(0, self._on_convert_error, str(e))
            
    def _on_convert_success(self, change_count: int, output_path: str) -> None:
        self.ui.set_running_state(False)
        self.ui.update_status("작업 완료!")
        self.ui.show_success_dialog(
            "성공", 
            f"총 {change_count}개의 객체 색상이 성공적으로 변경되었습니다.\n\n저장 경로:\n{output_path}",
            output_path
        )
        
    def _on_convert_error(self, error_msg: str) -> None:
        self.ui.set_running_state(False)
        self.ui.update_status("작업 실패!")
        self.ui.show_error_dialog("오류", f"처리 중 오류가 발생했습니다.\n\n{error_msg}")
