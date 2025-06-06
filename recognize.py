# recognize.py (인식 단계)

def run_recognize(lower_color, upper_color):
    import cv2
    import numpy as np

    from autoHandMeans import load_saved_contours
    from utils.utils import (
        read_connected_camera_index,
        FRAME_WIDTH, FRAME_HEIGHT,
        ROI_TOP_LEFT, ROI_BOTTOM_RIGHT, ROI_WIDTH, ROI_HEIGHT
    )

    # 카메라 index 읽기
    cam_index = read_connected_camera_index()

    # 카메라 열기
    cap = cv2.VideoCapture(cam_index)
    cap.set(cv2.CAP_PROP_FPS, 30)

    # 저장된 손 윤곽 데이터 불러오기
    saved_contours = load_saved_contours()

    # 손 이미지 전처리 함수
    def preprocess_hand(img_roi, lower, upper):
        hsv = cv2.cvtColor(img_roi, cv2.COLOR_BGR2HSV)

        # 지정된 색상 범위로 마스크 생성
        mask = cv2.inRange(hsv, lower, upper)

        # 마스크 후처리 (블러 + 모폴로지 연산)
        mask = cv2.GaussianBlur(mask, (5, 5), 0)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

        return mask

    # 입력 이미지에서 가장 큰 윤곽 검출 함수
    def get_largest_contour(binary_img):
        contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 윤곽이 있을 경우 가장 큰 것 반환
        if contours:
            return max(contours, key=cv2.contourArea)

        return None

    # 입력 윤곽을 저장된 윤곽들과 매칭
    def match_to_saved_contours(input_contour, saved_contours):
        min_score = float('inf')
        best_label = "Unknown"

        # 모든 저장된 contour와 비교
        for label, saved in saved_contours.items():
            score = cv2.matchShapes(input_contour, saved, 1, 0.0)

            # 최소 score를 갱신
            if score < min_score:
                min_score = score
                best_label = label

        return best_label, min_score

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

        # ROI 영역 추출
        roi = frame[ROI_TOP_LEFT[1]:ROI_BOTTOM_RIGHT[1], ROI_TOP_LEFT[0]:ROI_BOTTOM_RIGHT[0]]

        # ROI 표시용 사각형 그리기
        cv2.rectangle(frame, ROI_TOP_LEFT, ROI_BOTTOM_RIGHT, (100, 100, 255), 2)
        cv2.putText(frame, "Perform your sign gesture", (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # ROI 영역 전처리 (색상 마스킹)
        mask = preprocess_hand(roi, lower_color, upper_color)

        # 디버그용 마스킹 결과 표시
        cv2.imshow("Debug-Mask ROI", mask)

        # 가장 큰 윤곽 검출
        contour = get_largest_contour(mask)

        # 윤곽이 있고 면적이 충분히 크면 처리
        if contour is not None and cv2.contourArea(contour) > 1000:
            # ROI 영역에 윤곽 그리기
            cv2.drawContours(roi, [contour], -1, (0, 255, 0), 2)

            # 저장된 윤곽과 비교하여 best match 찾기
            label, score = match_to_saved_contours(contour, saved_contours)

            # 인식 결과 화면에 출력
            cv2.putText(frame, f"Detected: {label}", (50, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        # 결과 화면 표시
        cv2.imshow("Hand Color Recognize", frame)

        # 키 입력 처리
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC 키 누르면 종료
            break

    # 자원 해제
    cap.release()
    cv2.destroyAllWindows()