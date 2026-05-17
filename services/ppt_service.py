import logging
from typing import Set, Dict
from core.ppt_scanner import extract_all_colors, count_target_color_occurrences
from core.ppt_reader import replace_color

logger = logging.getLogger("ppt_color_changer")

class PPTService:
    """
    PowerPoint 관련 비즈니스 서비스(색상 추출, 사전 빈도수 계산, 색상 치환)를 
    통합적으로 처리하여 컨트롤러에 제공하는 서비스 레이어 클래스입니다.
    """
    def extract_ppt_colors(self, ppt_path: str) -> Set[str]:
        logger.info(f"Service: Extracting colors from {ppt_path}")
        try:
            return extract_all_colors(ppt_path)
        except Exception as e:
            logger.error(f"Service: Failed to extract colors: {e}", exc_info=True)
            raise
            
    def count_occurrences(
        self, 
        ppt_path: str, 
        target_color: str, 
        change_text: bool, 
        change_image: bool, 
        tolerance: int
    ) -> Dict[str, int]:
        logger.info(f"Service: Pre-counting color occurrences for '{target_color}' (Tolerance: {tolerance})")
        try:
            return count_target_color_occurrences(
                ppt_path, target_color, change_text, change_image, tolerance
            )
        except Exception as e:
            logger.error(f"Service: Failed to pre-count occurrences: {e}", exc_info=True)
            return {"text_count": 0, "image_count": 0}
            
    def execute_replacement(
        self, 
        ppt_path: str, 
        target_color: str, 
        new_color_hex: str, 
        output_path: str, 
        change_text: bool, 
        change_image: bool, 
        tolerance: int
    ) -> int:
        logger.info(f"Service: Starting color replacement: {target_color} -> {new_color_hex}")
        try:
            return replace_color(
                ppt_path, target_color, new_color_hex, output_path, change_text, change_image, tolerance
            )
        except Exception as e:
            logger.error(f"Service: Color replacement execution failed: {e}", exc_info=True)
            raise
