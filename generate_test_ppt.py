import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_THEME_COLOR

def create_test_ppt():
    """알고리즘 검증을 위한 엣지 케이스 포함 PPT 생성"""
    prs = Presentation()
    blank_slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_slide_layout)

    # 1. 일반 텍스트 (빨간색 - FF0000)
    txBox1 = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(3), Inches(1))
    tf1 = txBox1.text_frame
    p1 = tf1.paragraphs[0]
    run1 = p1.add_run()
    run1.text = "일반 텍스트 상자 (빨간색)"
    run1.font.size = Pt(18)
    run1.font.color.rgb = RGBColor(255, 0, 0)

    # 2. 그룹화된 텍스트 (파란색 - 0000FF)
    # 현재 python-pptx는 그룹 도형 '생성'을 완벽히 지원하지 않으나,
    # 도형 내부에 텍스트를 넣는 것으로 대체하거나,
    # 실제 그룹 객체는 사용자가 직접 묶은 샘플을 사용할 수도 있음.
    # 일단 일반 도형(Rectangle) 내 텍스트로 테스트.
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1), Inches(2.5), Inches(3), Inches(1))
    tf2 = shape.text_frame
    p2 = tf2.paragraphs[0]
    run2 = p2.add_run()
    run2.text = "도형 내부 텍스트 (파란색)"
    run2.font.color.rgb = RGBColor(0, 0, 255)

    # 3. 테이블 내부 텍스트 (초록색 - 00FF00)
    rows, cols = 2, 2
    table_shape = slide.shapes.add_table(rows, cols, Inches(1), Inches(4), Inches(4), Inches(1.5))
    table = table_shape.table
    cell = table.cell(0, 0)
    cell.text = "표 텍스트 (초록색)"
    # 테이블 텍스트 색상 적용
    for paragraph in cell.text_frame.paragraphs:
        for run in paragraph.runs:
            run.font.color.rgb = RGBColor(0, 255, 0)

    # 4. 테마 색상 텍스트 (Theme Color)
    txBox3 = slide.shapes.add_textbox(Inches(1), Inches(6), Inches(3), Inches(1))
    tf3 = txBox3.text_frame
    p3 = tf3.paragraphs[0]
    run3 = p3.add_run()
    run3.text = "테마 색상 텍스트 (ACCENT_1)"
    run3.font.color.theme_color = MSO_THEME_COLOR.ACCENT_1

    # 저장
    os.makedirs('test_data', exist_ok=True)
    save_path = os.path.join('test_data', 'test_sample.pptx')
    prs.save(save_path)
    print(f"테스트용 PPT가 성공적으로 생성되었습니다: {save_path}")

if __name__ == '__main__':
    create_test_ppt()
