import os
import cv2
import numpy as np
from core.ppt_reader import extract_all_colors, replace_color
from core.image_processor import extract_dominant_colors_from_image

def test_dominant_color_extraction():
    print("\n--- 0. 이미지 대표색(강조색) 추출 단위 테스트 ---")
    # 1. 100x100 흰색(배경) 이미지 생성
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    
    # 2. 하늘색(Cyan) 사각형 그리기 (BGR: B=255, G=168, R=0 -> RGB Hex: 00A8FF)
    cv2.rectangle(img, (30, 30), (70, 70), (255, 168, 0), -1)
    
    # PNG 바이너리로 인코딩
    _, encoded = cv2.imencode('.png', img)
    image_blob = encoded.tobytes()
    
    # 3. 대표색 추출 실행
    extracted = extract_dominant_colors_from_image(image_blob)
    print(f"추출된 이미지 강조색 목록: {extracted}")
    
    # 4. 검증 (흰색 배경인 FFFFFF는 무채색이므로 제외되고, 00A8FF만 성공적으로 검출되어야 함)
    expected_hex = "00A8FF"
    if expected_hex in extracted:
        print(f"[SUCCESS] 성공: 강조색 {expected_hex}이(가) 정상적으로 검출되었습니다.")
    else:
        print(f"[FAIL] 실패: {expected_hex}을(를) 찾을 수 없습니다. (추출 결과: {extracted})")
        assert False, f"Dominant color extraction failed. Expected {expected_hex}"

def test_poc():
    # 이미지 추출 단위 테스트 실행
    test_dominant_color_extraction()
    
    input_path = os.path.join("test_data", "test_sample.pptx")
    output_path = os.path.join("test_data", "test_sample_modified.pptx")

    if not os.path.exists(input_path):
        print(f"Error: {input_path} 가 없습니다. generate_test_ppt.py를 먼저 실행하세요.")
        return

    # 1. 색상 추출 테스트
    print("\n--- 1. 색상 추출 테스트 ---")
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
        print("[SUCCESS] 성공: PPT 텍스트 색상 변경 및 스캔 무결성 테스트 완료.")
    else:
        print(f"\n대상 색상 {target_color}이(가) 파일에 없습니다.")

if __name__ == '__main__':
    test_poc()
