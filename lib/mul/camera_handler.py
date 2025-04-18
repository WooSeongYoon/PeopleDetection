# lib/camera_handler.py
from lib.grabber import StreamGrabber
from lib.detector import Detector
from lib.display import RealTimeViewer

class CameraHandler:
    def __init__(self, cam_id, stream_url):
        self.cam_id = cam_id
        self.stream_url = stream_url
        self.latest_frame = None
        self.results = []
        self.result_timestamp = 0
        self.is_running = True

        self.detector = Detector(main=self)
        self.viewer = RealTimeViewer(main=self, show_window=True)
        self.grabber = StreamGrabber(
            out=None,
            url=self.stream_url,
            on_state=self.on_state,
            on_frame=self.on_frame
        )

    def on_state(self, is_play):
        print(f"[Camera-{self.cam_id}] Grabber 상태: {'재생 중' if is_play else '중지됨'}")

    def on_frame(self, args, is_stop=False):
        if is_stop:
            self.is_running = False
            return
        frame, frame_cnt, grab_cnt = args
        self.latest_frame = frame

    def start(self):
        print(f"[Camera-{self.cam_id}] 실행 시작")
        self.grabber.start()
        self.detector.start()
        self.viewer.start()

    def stop(self):
        print(f"[Camera-{self.cam_id}] 정지 요청")
        self.is_running = False
        self.grabber.stop()
        self.viewer.stop()
