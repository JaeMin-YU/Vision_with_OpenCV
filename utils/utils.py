import os

# 칼링 index 읽기 함수
def read_connected_camera_index():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cam_file = os.path.join(base_dir, 'connectedCam.txt')

    try:
        with open(cam_file, 'r') as f:
            cam_index = int(f.read().strip())
    except Exception as e:
        print(f"[ERROR] Failed to read connectedCam.txt: {e}")
        print("[INFO] Using default camera index 0.")
        cam_index = 0

    return cam_index

# ===============================
# 공통 Frame / ROI 설정
# ===============================

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

ROI_TOP_LEFT = (160, 120)
ROI_BOTTOM_RIGHT = (480, 360)

ROI_WIDTH = ROI_BOTTOM_RIGHT[0] - ROI_TOP_LEFT[0]
ROI_HEIGHT = ROI_BOTTOM_RIGHT[1] - ROI_TOP_LEFT[1]