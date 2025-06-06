👋 OpenCV 기반 수어(손 제스처) 인식 시스템

🔄 프로젝트 개요

본 프로젝트는 웹캠을 이용한 실시간 수어(손 제스처) 인식 시스템입니다. 사용자의 손 제스처를 사전 등록된 패턴과 비교하여 화면에 해당 수어를 표시합니다.

OpenCV 기반 실시간 영상 처리

자동 손 색상 범위 학습

저장된 손 제스처 패턴과 형태 매칭

사용자 친화적인 실시간 피드백 인터페이스 제공

🔄 시스템 흐름

1️⃣ 준비 단계 - 손 윤곽 및 가이드라인 등록

autoHandMeans.py: 학습용 손 이미지에서 손 윤곽을 추출하여 sign_patterns.txt에 저장

only_guideline.py: 가이드 이미지에서 양손 가이드라인 윤곽 2개를 추출하여 guide_line_patterns.txt에 저장

2️⃣ 실시간 인식 흐름 (main.py)

main.py
  |
  |-- run_ready()  # 준비 단계 실행
  |
  |-- run_recognize()  # 인식 단계 실행

3️⃣ 준비 단계 (ready.py)

목적: 사용자의 손 색상 범위를 자동으로 학습

웹캠 활성화

사용자가 중앙 ROI 박스에 손을 위치

가이드라인 영역의 70% 이상에서 피부 영역 감지 시:

손 위치를 2초 동안 유지

평균 HSV 색상 범위 자동 샘플링

lower_color, upper_color 값을 반환하여 인식 단계에서 활용

4️⃣ 인식 단계 (recognize.py)

목적: 실시간 손 제스처를 저장된 패턴과 매칭하여 인식

웹캠 활성화

프레임에서 ROI 영역 추출

학습한 색상 범위로 피부 마스크 생성

마스크에서 가장 큰 윤곽 추출

저장된 패턴과 cv2.matchShapes를 이용하여 매칭 수행

가장 유사한 패턴 레이블과 score를 화면에 표시

5️⃣ 공통 유틸리티 (utils.py)

connectedCam.txt에서 카메라 index 읽기

프레임 크기 및 ROI 영역 상수 정의

📅 전체 흐름 요약

손 & 가이드 패턴 등록 ➔ 손 색상 자동 학습 ➔ 실시간 손 제스처 인식 ➔ 매칭 결과 출력

💡 프로젝트 구조

main.py
 ├─ ready.py
 │   └─ guide_line.py (가이드라인 윤곽)
 │   └─ utils.py (공통 설정)
 │
 └─ recognize.py
     └─ autoHandMeans.py (저장된 손 제스처 패턴)
     └─ utils.py

💡 사용 방법

# Step 1: 손 제스처 패턴 등록
python autoHandMeans.py

# Step 2: 가이드라인 패턴 등록
python only_guideline.py

# Step 3: 메인 프로그램 실행 (실시간 인식)
python main.py

🎉 사용 라이브러리

본 프로젝트는 다음 기술을 사용합니다:

Python

OpenCV

기본 형태 매칭 기법

🚀 향후 개선 사항

윤곽 매칭 정확도 향상

다중 제스처 인식 지원

인식된 제스처에 대한 음성 출력 기능 추가