from pptx.enum.dml import MSO_COLOR_TYPE
from pptx.dml.color import RGBColor

def get_run_color(run) -> str | None:
    """Run 객체에서 색상 정보를 추출하여 hex 문자열 또는 테마 문자열로 반환"""
    color = run.font.color
    
    # 색상 타입 확인
    if color.type == MSO_COLOR_TYPE.RGB:
        return str(color.rgb)  # 'FF0000' 형태
    elif color.type == MSO_COLOR_TYPE.SCHEME:
        return f"SCHEME_{color.theme_color}"
    
    # 색상이 명시적으로 지정되지 않은 경우 (기본 텍스트 색상)
    return None

def set_run_color(run, hex_color_str: str):
    """Run 객체의 색상을 hex 색상으로 변경"""
    # hex_color_str은 'FF0000' 형태의 문자열이어야 함
    hex_color_str = hex_color_str.lstrip('#')
    if len(hex_color_str) == 6:
        r = int(hex_color_str[0:2], 16)
        g = int(hex_color_str[2:4], 16)
        b = int(hex_color_str[4:6], 16)
        run.font.color.rgb = RGBColor(r, g, b)
    else:
        raise ValueError(f"Invalid hex color string: {hex_color_str}")
