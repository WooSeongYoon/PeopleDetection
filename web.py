from flask import Flask, Response, render_template
from flask_cors import CORS
import cv2
import threading
import os
import time
from main import Main

app = Flask(__name__)
CORS(app)

# 시스템 초기화
URL = '영상 주소'
main_controller = Main(stream_url=URL, show_window=False)

# 백그라운드에서 Main 스레드 실행
def start_main():
    main_controller.start()

main_thread = threading.Thread(target=start_main)
main_thread.daemon = True
main_thread.start()

# 프레임 스트리밍 생성기
def gen():
    while True:
        frame = main_controller.latest_frame
        if frame is None:
            time.sleep(0.01)
            continue

        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

# 메인 페이지
@app.route('/')
def index():
    return render_template('index.html')  # templates/index.html 필요

# 영상 스트림 엔드포인트
@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 종료 처리
@app.route('/exit')
def exit():
    main_controller.stop()
    os._exit(0)

if __name__ == '__main__':
    app.run(host='host 번호', port=5000)
