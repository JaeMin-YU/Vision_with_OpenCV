# ready.py (색상 추출 단계)

def run_ready():
    import cv2
    import numpy as np
    import time

    from guide_line import get_guide_contours
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

    # 가이드라인 윤곽 불러오기
    guide_contours_raw = get_guide_contours()

    guide_contours = []
    for contour in guide_contours_raw:
        # guide contour를 ROI 크기에 맞게 스케일 조정
        scaled = contour.astype(np.float32)
        scaled[:, :, 0] *= ROI_WIDTH / 606
        scaled[:, :, 1] *= ROI_HEIGHT / 396
        guide_contours.append(scaled.astype(np.int32))

    # 초기 상태 설정
    color_sampled = False
    sampling_start_time = None
    sampling_duration = 2.0  # 2초 동안 유지 시 색상 샘플링

    # 아시아인 피부색 HSV 범위 (초기값)
    lower_asian_skin = np.array([0, 20, 70])
    upper_asian_skin = np.array([25, 180, 255])

    # 가이드 내부에서 평균 색상 샘플링 함수 정의
    def sample_hand_color(hsv_img, guide_mask, margin=40):
        hsv_values = hsv_img[guide_mask > 0]
        if len(hsv_values) == 0:
            return None, None

        mean_hsv = np.median(hsv_values, axis=0)
        h, s, v = mean_hsv

        lower = np.array([max(h - margin, 0), max(s - margin, 50), max(v - margin, 50)])
        upper = np.array([min(h + margin, 179), min(s + margin, 255), min(v + margin, 255)])

        return lower, upper

    lower_color_list, upper_color_list = [None, None], [None, None]

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))

        # ROI 영역 추출
        roi = frame[ROI_TOP_LEFT[1]:ROI_BOTTOM_RIGHT[1], ROI_TOP_LEFT[0]:ROI_BOTTOM_RIGHT[0]]

        # ROI 영역에 사각형 그리기
        cv2.rectangle(frame, ROI_TOP_LEFT, ROI_BOTTOM_RIGHT, (100, 100, 255), 2)
        cv2.putText(frame, "Place your hands in the box", (130, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        guide_masks = []
        skin_ratios = []

        # ROI 영역 HSV 변환 후 skin mask 생성
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        skin_mask = cv2.inRange(hsv_roi, lower_asian_skin, upper_asian_skin)

        # 각 가이드 contour 별로 처리
        for contour in guide_contours:
            cv2.drawContours(roi, [contour], -1, (100, 100, 255), 2)

            # 가이드 영역 마스크 생성
            guide_mask = np.zeros((ROI_HEIGHT, ROI_WIDTH), dtype=np.uint8)
            cv2.drawContours(guide_mask, [contour], -1, 255, -1)
            guide_masks.append(guide_mask)

            # 가이드 내부의 skin 비율 계산
            skin_in_guide = cv2.bitwise_and(skin_mask, skin_mask, mask=guide_mask)

            skin_area = cv2.countNonZero(skin_in_guide)
            total_area = cv2.countNonZero(guide_mask)
            skin_ratio = skin_area / total_area if total_area > 0 else 0
            skin_ratios.append(skin_ratio)

        # 색상 샘플링 시작 조건 확인
        if not color_sampled:
            # 모든 가이드 영역에서 skin 비율이 70% 이상일 때만 진행
            if all(ratio > 0.7 for ratio in skin_ratios):
                if sampling_start_time is None:
                    sampling_start_time = time.time()  # 처음 시작 시간 기록
                else:
                    elapsed_time = time.time() - sampling_start_time
                    progress = min(elapsed_time / sampling_duration, 1.0)

                    # 진행 표시 바 그리기
                    bar_x = 160
                    bar_y = 420
                    bar_width = 320
                    bar_height = 20

                    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), (255, 255, 255), 2)
                    cv2.rectangle(frame, (bar_x, bar_y), (bar_x + int(bar_width * progress), bar_y + bar_height), (0, 255, 0), -1)

                    # 2초 동안 유지 시 색상 샘플링 수행
                    if elapsed_time >= sampling_duration:
                        for i, guide_mask in enumerate(guide_masks):
                            lower, upper = sample_hand_color(hsv_roi, guide_mask)
                            lower_color_list[i] = lower
                            upper_color_list[i] = upper

                        color_sampled = True
                        sampling_start_time = None

                        print("Color ranges sampled.")
                        for i in range(len(guide_masks)):
                            print(f"Hand {i+1} → Lower: {lower_color_list[i]}, Upper: {upper_color_list[i]}")

                        break  # 샘플링 완료 시 루프 탈출
            else:
                # 조건 미충족 시 타이머 초기화
                sampling_start_time = None

        # 화면 출력
        cv2.imshow("Hand Color Ready", frame)

        # 키 입력 처리
        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC 키 누르면 종료
            break
        elif key == ord('s'):  # s 키 누르면 샘플링 다시 시작
            color_sampled = False
            sampling_start_time = None

    # 자원 해제
    cap.release()
    cv2.destroyAllWindows()

    # 색상 범위 평균값 계산 후 반환
    lower_color = np.mean(lower_color_list, axis=0).astype(np.int32)
    upper_color = np.mean(upper_color_list, axis=0).astype(np.int32)

    return lower_color, upper_color
