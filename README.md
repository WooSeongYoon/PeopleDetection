# PeopleDetection
Darknet을 이용한 사람 식별 프로그램
필요 프로그램: https://github.com/AlexeyAB/darknet.git

주요 기능
- 실시간 영상에서 사람 감지
- 탐지 결과를 웹 또는 cv2창에서 실시간 확인

- 변경점 -
lib/darknet.py 파일의 라이브러리 로드 부분을 자신의 위치로 수정하기
main.py 파일에 실시간 영상 주소 변경
web.py 파일에 실시간 영상 주소와 host주소 변경

- 실행 파일 -
main.py -> cv2창을 열어서 프로그램 결과 확인
weeb.py -> 웹 페이지를 열어서 프로그램 결과 확인
