import cv2
import os
import json
import numpy as np

# 경로 설정
base_dir = os.getcwd()
image_folder = os.path.join(base_dir, 'Vision', 'hand_image')
output_txt = os.path.join(base_dir, 'Vision', 'handMeanImage', 'sign_patterns.txt')
debug_img_dir = os.path.join(base_dir, 'Vision', 'detectHandImage')

os.makedirs(os.path.dirname(output_txt), exist_ok=True)
os.makedirs(debug_img_dir, exist_ok=True)

# 손 윤곽 추출 함수
def extract_contour_and_debug(image_path, save_debug_path):
    img = cv2.imread(image_path)
    debug_img = img.copy()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    main_contour = max(contours, key=cv2.contourArea)

    # 디버그 이미지에 윤곽 그리기
    cv2.drawContours(debug_img, [main_contour], -1, (0, 255, 0), 2)
    cv2.imwrite(save_debug_path, debug_img)

    # 윤곽선을 numpy array로 반환
    return main_contour

# main.py에서 불러오기 위한 함수
def load_saved_contours():
    with open(output_txt, 'r') as f:
        data = json.load(f)

    contours = {}
    for label, point_list in data.items():
        contour_array = np.array(point_list, dtype=np.int32).reshape((-1, 1, 2))
        contours[label] = contour_array
    return contours

def generate_and_save_all_hand_contours():
    gesture_data = {}
    raw_contour_data = {}

    image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg'))]

    def sort_key(filename):
        name = filename.split('.')[0]
        return (0, int(name)) if name.isdigit() else (1, name)

    for filename in sorted(image_files, key=sort_key):
        label = filename.split('.')[0]

        image_path = os.path.join(image_folder, filename)
        debug_save_path = os.path.join(debug_img_dir, f"{label}_debug.png")

        contour = extract_contour_and_debug(image_path, debug_save_path)

        if contour is not None:
            raw_contour_data[label] = contour
            gesture_data[label] = contour[:, 0, :].tolist()
            print(f"{filename} → 윤곽 추출 & 디버그 저장 완료")
        else:
            print(f"{filename} → 윤곽 없음")

    # JSON 파일로 저장 (모든 라벨 저장)
    with open(output_txt, 'w') as f:
        json.dump(gesture_data, f)

    print(f"\n 현재 저장된 손 윤곽 데이터: {len(gesture_data)} 개 → {output_txt}")

# 진입점 보호
if __name__ == "__main__":
    generate_and_save_all_hand_contours()
