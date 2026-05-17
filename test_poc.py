import os
from core.ppt_reader import extract_all_colors, replace_color

def test_poc():
    input_path = os.path.join("test_data", "test_sample.pptx")
    output_path = os.path.join("test_data", "test_sample_modified.pptx")

    if not os.path.exists(input_path):
        print(f"Error: {input_path} 가 없습니다. generate_test_ppt.py를 먼저 실행하세요.")
        return

    # 1. 색상 추출 테스트
    print("--- 1. 색상 추출 테스트 ---")
    colors = extract_all_colors(input_path)
    print(f"발견된 색상: {colors}")
    
    # 2. 색상 변경 테스트 (빨간색 -> 보라색)
    target_color = "FF0000" # 빨간색
    new_color = "800080"    # 보라색 (Purple)
    
    if target_color in colors:
        print(f"\n--- 2. 색상 변경 테스트 ({target_color} -> {new_color}) ---")
        changed = replace_color(input_path, target_color, new_color, output_path)
        print(f"총 {changed}개의 텍스트(Run) 색상이 변경되었습니다.")
        
        # 3. 변경 결과 확인 (새로 저장된 파일에서 색상 다시 추출)
        new_colors = extract_all_colors(output_path)
        print(f"변경 후 파일의 색상 목록: {new_colors}")
        print(f"저장 완료: {output_path}")
    else:
        print(f"\n대상 색상 {target_color}이(가) 파일에 없습니다.")

if __name__ == '__main__':
    test_poc()
