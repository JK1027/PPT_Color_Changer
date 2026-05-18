import logging
from typing import Set, Dict, Tuple
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from core.color_extractor import get_run_color
from core.image_processor import image_contains_color, extract_dominant_colors_from_image

logger = logging.getLogger("ppt_color_changer")

def extract_all_colors(ppt_path: str) -> Set[str]:
    """PPT 내의 모든 텍스트 색상을 추출 (테이블, 그룹 도형 포함 재귀 탐색)"""
    try:
        prs = Presentation(ppt_path)
        colors: Set[str] = set()
        
        for slide in prs.slides:
            for shape in slide.shapes:
                _extract_colors_from_shape(shape, colors)
                
        return colors
    except Exception as e:
        logger.error(f"Error extracting colors from {ppt_path}: {e}", exc_info=True)
        raise

def _extract_colors_from_shape(shape, colors: Set[str]) -> None:
    """재귀적으로 shape 탐색하여 색상 추출"""
    # 1. 일반 텍스트 프레임이 있는 경우
    if shape.has_text_frame:
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                c = get_run_color(run)
                if c:
                    colors.add(c)
                    
    # 2. 그룹 도형인 경우 재귀 탐색
    elif shape.shape_type == MSO_SHAPE_TYPE.GROUP:
        for child_shape in shape.shapes:
            _extract_colors_from_shape(child_shape, colors)
            
    # 3. 테이블인 경우 셀 내부 텍스트 프레임 탐색
    elif shape.has_table:
        for row in shape.table.rows:
            for cell in row.cells:
                if cell.text_frame:
                    for paragraph in cell.text_frame.paragraphs:
                        for run in paragraph.runs:
                            c = get_run_color(run)
                            if c:
                                colors.add(c)

    # 4. 이미지인 경우 대표 유채색 추출
    elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
        try:
            image_blob = shape.image.blob
            img_colors = extract_dominant_colors_from_image(image_blob)
            for c in img_colors:
                colors.add(c)
        except Exception as e:
            logger.error(f"Error extracting dominant colors from shape: {e}")

def count_target_color_occurrences(
    ppt_path: str, 
    target_color: str, 
    change_text: bool = True, 
    change_image: bool = True, 
    tolerance: int = 20
) -> Dict[str, int]:
    """
    대상 색상이 텍스트와 이미지 각각에서 변경될 수 있는 개수를 반환
    """
    try:
        prs = Presentation(ppt_path)
        text_count = 0
        image_count = 0
        
        for slide in prs.slides:
            for shape in slide.shapes:
                tc, ic = _count_in_shape(shape, target_color, change_text, change_image, tolerance)
                text_count += tc
                image_count += ic
                
        return {"text_count": text_count, "image_count": image_count}
    except Exception as e:
        logger.error(f"Error counting occurrences for color {target_color}: {e}", exc_info=True)
        return {"text_count": 0, "image_count": 0}

def _count_in_shape(
    shape, 
    target_color: str, 
    change_text: bool, 
    change_image: bool, 
    tolerance: int
) -> Tuple[int, int]:
    """재귀적으로 shape 탐색하여 대상 색상의 매칭 개수(텍스트, 이미지) 반환"""
    text_count = 0
    image_count = 0
    
    # 1. 일반 텍스트 프레임
    if shape.has_text_frame and change_text:
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                if get_run_color(run) == target_color:
                    text_count += 1
                    
    # 2. 그룹 도형 재귀
    elif shape.shape_type == MSO_SHAPE_TYPE.GROUP:
        for child_shape in shape.shapes:
            tc, ic = _count_in_shape(child_shape, target_color, change_text, change_image, tolerance)
            text_count += tc
            image_count += ic
            
    # 3. 테이블
    elif shape.has_table and change_text:
        for row in shape.table.rows:
            for cell in row.cells:
                if cell.text_frame:
                    for paragraph in cell.text_frame.paragraphs:
                        for run in paragraph.runs:
                            if get_run_color(run) == target_color:
                                text_count += 1
                                
    # 4. 이미지
    elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE and change_image:
        try:
            image_blob = shape.image.blob
            if image_contains_color(image_blob, target_color, tolerance):
                image_count += 1
        except Exception:
            # 예외 발생 시 무시 (도형 형식이 예외를 부르는 경우 등 방지)
            pass
            
    return text_count, image_count
