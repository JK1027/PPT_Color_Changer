import os
import io
from typing import Set
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from core.color_extractor import get_run_color, set_run_color
from core.image_processor import process_image_blob

def extract_all_colors(ppt_path: str) -> Set[str]:
    """PPT 내의 모든 텍스트 색상을 추출 (테이블, 그룹 도형 포함 재귀 탐색)"""
    prs = Presentation(ppt_path)
    colors = set()
    
    for slide in prs.slides:
        for shape in slide.shapes:
            _extract_colors_from_shape(shape, colors)
            
    return colors

def _extract_colors_from_shape(shape, colors: Set[str]):
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

def replace_color(ppt_path: str, target_color: str, new_color_hex: str, output_path: str, change_text: bool = True, change_image: bool = True) -> int:
    """
    특정 색상을 새 색상으로 일괄 변경하고 저장 
    (텍스트 및 이미지 색상 치환 선택적 포함)
    (원본 보존 원칙: 무조건 새로운 output_path로 저장)
    """
    if os.path.abspath(ppt_path) == os.path.abspath(output_path):
        raise ValueError("원본 데이터 보존을 위해 output_path는 ppt_path와 동일할 수 없습니다.")

    prs = Presentation(ppt_path)
    change_count = 0
    
    for slide in prs.slides:
        # slide.shapes를 리스트로 복사하여 순회해야 shape 삭제/추가 시 인덱스 에러가 안남
        for shape in list(slide.shapes):
            change_count += _replace_color_in_shape(shape, slide, target_color, new_color_hex, change_text, change_image)
            
    prs.save(output_path)
    return change_count

def _replace_color_in_shape(shape, slide, target_color: str, new_color_hex: str, change_text: bool, change_image: bool) -> int:
    """재귀적으로 shape 탐색하여 색상 변경 후 변경 횟수 반환"""
    change_count = 0
    
    # 1. 일반 텍스트 프레임이 있는 경우
    if shape.has_text_frame and change_text:
        for paragraph in shape.text_frame.paragraphs:
            for run in paragraph.runs:
                if get_run_color(run) == target_color:
                    set_run_color(run, new_color_hex)
                    change_count += 1
                    
    # 2. 그룹 도형인 경우 재귀 탐색 (텍스트/이미지 옵션을 하위 도형에 그대로 위임)
    elif shape.shape_type == MSO_SHAPE_TYPE.GROUP:
        for child_shape in shape.shapes:
            change_count += _replace_color_in_shape(child_shape, slide, target_color, new_color_hex, change_text, change_image)
            
    # 3. 테이블인 경우 셀 내부 텍스트 프레임 탐색
    elif shape.has_table and change_text:
        for row in shape.table.rows:
            for cell in row.cells:
                if cell.text_frame:
                    for paragraph in cell.text_frame.paragraphs:
                        for run in paragraph.runs:
                            if get_run_color(run) == target_color:
                                set_run_color(run, new_color_hex)
                                change_count += 1
                                
    # 4. 이미지인 경우 색상 치환 후 교체
    elif shape.shape_type == MSO_SHAPE_TYPE.PICTURE and change_image:
        try:
            image_blob = shape.image.blob
            # 이미지 프로세서를 거쳐 색상 치환된 바이너리 획득
            new_blob = process_image_blob(image_blob, target_color, new_color_hex)
            
            # 바이너리가 달라졌다면 (실제 색상 치환이 일어났다면) 이미지 교체
            if new_blob != image_blob:
                image_stream = io.BytesIO(new_blob)
                # 동일한 위치와 크기(left, top, width, height)로 새 이미지 추가
                slide.shapes.add_picture(image_stream, shape.left, shape.top, shape.width, shape.height)
                
                # 기존 원본 이미지 제거
                sp = shape._element
                sp.getparent().remove(sp)
                change_count += 1
        except Exception as e:
            print(f"이미지 shape 치환 중 에러 발생: {e}")
                                
    return change_count
