# main.py

# 모듈 import
import ready
import recognize

if __name__ == "__main__":

    # 색상 탐지 단계 실행 → 색상 범위 받아오기
    lower_color, upper_color = ready.run_ready()

    # 인식 단계 실행 → 받아온 색상값으로 진행
    recognize.run_recognize(lower_color, upper_color)
