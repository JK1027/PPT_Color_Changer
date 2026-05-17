import logging
from core.color_extractor import get_run_color, set_run_color

logger = logging.getLogger("ppt_color_changer")

def replace_text_color_in_shape(shape, target_color: str, new_color_hex: str) -> int:
    """
    도형(일반 및 테이블) 내의 텍스트 색상을 target_color에서 new_color_hex로 교체하고 변경 횟수 반환
    """
    change_count = 0
    
    # 1. 일반 텍스트 프레임이 있는 경우
    if shape.has_text_frame:
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                if get_run_color(run) == target_color:
                    set_run_color(run, new_color_hex)
                    change_count += 1
                    
    # 2. 테이블인 경우 셀 내부 텍스트 프레임 탐색
    elif shape.has_table:
        for row in shape.table.rows:
            for cell in row.cells:
                if cell.text_frame:
                    for paragraph in cell.text_frame.paragraphs:
                        for run in paragraph.runs:
                            if get_run_color(run) == target_color:
                                set_run_color(run, new_color_hex)
                                change_count += 1
                                
    return change_count
