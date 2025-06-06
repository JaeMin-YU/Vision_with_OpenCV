import cv2
import os
import json
import numpy as np

# 타이틀 변수와 경로 설정
base_dir = os.getcwd()
guide_folder = os.path.join(base_dir, 'Vision', 'guide')

image_folder = guide_folder
output_txt = os.path.join(guide_folder, 'guide_line_patterns.txt')
debug_img_dir = os.path.join(guide_folder, 'detectGuideImage')

os.makedirs(os.path.dirname(output_txt), exist_ok=True)
os.makedirs(debug_img_dir, exist_ok=True)

# 가이드라인 윤곽선 추출 함수 (복수 2개 윤곽 추출)
def extract_multiple_contours_and_debug(image_path, save_debug_path):
    img = cv2.imread(image_path)
    debug_img = img.copy()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return []

    # 면적 기준으로 큰 contour 2개만 선택 (양손 가이드라인)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    top2_contours = contours[:2]  # 최대 2개

    # 디버그 이미지에 윤곽 그리기
    cv2.drawContours(debug_img, top2_contours, -1, (0, 255, 0), 2)
    cv2.imwrite(save_debug_path, debug_img)

    return top2_contours  # 리스트 반환

# main.py에서 저장된 윤곽 데이터를 불러오는 함수
def load_saved_contours():
    with open(output_txt, 'r') as f:
        data = json.load(f)

    contours = {}
    for label, point_list in data.items():
        contour_array = np.array(point_list, dtype=np.int32).reshape((-1, 1, 2))
        contours[label] = contour_array
    return contours

def generate_and_save_all_guide_contours():
    guide_data = {}
    raw_contour_data = {}

    image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg'))]

    def sort_key(filename):
        name = filename.split('.')[0]
        return (0, int(name)) if name.isdigit() else (1, name)

    for filename in sorted(image_files, key=sort_key):
        label = filename.split('.')[0]
        image_path = os.path.join(image_folder, filename)
        debug_save_path = os.path.join(debug_img_dir, f"{label}_debug.png")

        contours = extract_multiple_contours_and_debug(image_path, debug_save_path)

        if contours:
            for i, contour in enumerate(contours):
                label_i = f"{label}_hand{i+1}"  # ex: "fullHand_hand1", "fullHand_hand2"
                raw_contour_data[label_i] = contour
                guide_data[label_i] = contour[:, 0, :].tolist()
                print(f"{filename} → 윤곽 {i+1} 저장 완료")
        else:
            print(f"{filename} → 윤곽 없음")

    # JSON 파일로 저장 (모든 라벨 저장)
    with open(output_txt, 'w') as f:
        json.dump(guide_data, f)

    print(f"\n 총 {len(guide_data)}개의 가이드라인 윤곽 데이터가 저장되었습니다 → {output_txt}")

# 진입점 보호
if __name__ == "__main__":
    generate_and_save_all_guide_contours()