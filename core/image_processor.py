import cv2
import numpy as np
import logging
from typing import Tuple

# 로거 설정
logger = logging.getLogger("ppt_color_changer")

def hex_to_hsv(hex_color: str) -> np.ndarray:
    """Hex 색상(예: 'FF0000' 또는 '#FF0000')을 OpenCV HSV 배열로 변환"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
        
    b: int = int(hex_color[4:6], 16)
    g: int = int(hex_color[2:4], 16)
    r: int = int(hex_color[0:2], 16)
    
    # BGR to HSV
    bgr = np.uint8([[[b, g, r]]])
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    return hsv[0][0]

def image_contains_color(image_blob: bytes, target_hex: str, tolerance: int = 20) -> bool:
    """이미지 내에 target_hex 색상이 tolerance 내에 존재하는지 검사"""
    try:
        # Byte 배열을 OpenCV BGR 이미지로 디코딩
        nparr = np.frombuffer(image_blob, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return False
            
        target_hsv = hex_to_hsv(target_hex)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        h, s, v = target_hsv
        lower_h = max(0, h - tolerance)
        upper_h = min(179, h + tolerance)
        
        # S, V 하한 설정을 통해 너무 어둡거나 밝은 영역 배제
        lower_bound = np.array([lower_h, 30, 30])
        upper_bound = np.array([upper_h, 255, 255])
        
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        # 빨간색(Hue 0/179 부근) Wrap-around 처리
        if h < tolerance:
            lower_bound2 = np.array([180 + (h - tolerance), 30, 30])
            upper_bound2 = np.array([179, 255, 255])
            mask2 = cv2.inRange(hsv, lower_bound2, upper_bound2)
            mask = cv2.bitwise_or(mask, mask2)
        elif h > 179 - tolerance:
            lower_bound2 = np.array([0, 30, 30])
            upper_bound2 = np.array[(h + tolerance) - 180, 255, 255]
            mask2 = cv2.inRange(hsv, lower_bound2, upper_bound2)
            mask = cv2.bitwise_or(mask, mask2)
            
        return bool(np.any(mask > 0))
    except Exception as e:
        logger.error(f"Error checking color presence in image: {e}", exc_info=True)
        return False

def process_image_blob(image_blob: bytes, target_hex: str, new_hex: str, tolerance: int = 20) -> bytes:
    """PPT 이미지 바이너리를 받아 색상을 치환한 후 새 바이너리로 반환"""
    try:
        # 1. Byte 배열을 OpenCV BGR 이미지로 디코딩
        nparr = np.frombuffer(image_blob, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return image_blob # 디코딩 실패 시 원본 그대로 반환
            
        target_hsv = hex_to_hsv(target_hex)
        new_hsv = hex_to_hsv(new_hex)
        
        # BGR을 HSV로 변환
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 2. 동적 마스크 생성 (Hue 기준 오차 허용)
        h, s, v = target_hsv
        
        lower_h = max(0, h - tolerance)
        upper_h = min(179, h + tolerance)
        
        lower_bound = np.array([lower_h, 30, 30])
        upper_bound = np.array([upper_h, 255, 255])
        
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        
        # 빨간색(Hue가 0 부근) Wrap-around 처리
        if h < tolerance:
            lower_bound2 = np.array([180 + (h - tolerance), 30, 30])
            upper_bound2 = np.array([179, 255, 255])
            mask2 = cv2.inRange(hsv, lower_bound2, upper_bound2)
            mask = cv2.bitwise_or(mask, mask2)
        elif h > 179 - tolerance:
            lower_bound2 = np.array([0, 30, 30])
            upper_bound2 = np.array[(h + tolerance) - 180, 255, 255]
            mask2 = cv2.inRange(hsv, lower_bound2, upper_bound2)
            mask = cv2.bitwise_or(mask, mask2)
            
        # 3. 색상 치환
        if np.any(mask > 0):
            # 대상 픽셀의 Hue 값을 새 색상의 Hue 값으로 통일
            hsv[mask > 0, 0] = new_hsv[0]
            
            # 채도(Saturation) 보정 로직 적용 (질감 보존)
            s_channel = hsv[mask > 0, 1].astype(np.int16)
            s_channel = np.clip(s_channel + 40, 0, 255)
            hsv[mask > 0, 1] = s_channel.astype(np.uint8)
            
            # 4. 결과 인코딩 (PNG로 압축하여 반환)
            result_bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
            success, encoded_img = cv2.imencode('.png', result_bgr)
            
            if success:
                return encoded_img.tobytes()
                
    except Exception as e:
        logger.error(f"Error transforming image colors: {e}", exc_info=True)
        
    return image_blob # 예외 발생 시 안전하게 원본 반환
