
import time
from lib.detector import Detector
from lib.display import RealTimeViewer
from lib.grabber import StreamGrabber

class Main:
    def __init__(self, stream_url, show_window):
        self.stream_url = stream_url
        self.is_running = True
        self.latest_frame = None
        self.results = []               # 최신 감지 결과
        self.result_timestamp = 0       # 결과가 업데이트된 시간
        self.show_window = show_window

        self.detector = Detector(main=self)
        self.viewer = RealTimeViewer(main=self, show_window=self.show_window)

        self.grabber = StreamGrabber(
            out=None,
            url=self.stream_url,
            on_state=self.on_state,
            on_frame=self.on_frame
        )

    def on_state(self, is_play):
        print(f"[Main] Grabber 상태: {'재생 중' if is_play else '중지됨'}")

    def on_frame(self, args, is_stop=False):
        if is_stop:
            self.is_running = False
            return
        frame, frame_cnt, grab_cnt = args
        self.latest_frame = frame

    def start(self):
        print("[Main] 시스템 시작")
        self.grabber.start()
        self.detector.start()
        self.viewer.start()

        # 하는 이유: 메인 스레드가 종료되지 않도록 하기 위해
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        print("[Main] 시스템 종료 요청")
        self.is_running = False
        self.grabber.stop()
        self.viewer.stop()

if __name__ == "__main__":
    URL = '영상 주소'
    main = Main(stream_url=URL, show_window=True)
    main.start()
