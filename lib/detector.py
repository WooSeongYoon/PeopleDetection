import threading
import time
from collections import deque
from lib.darknet import *

class Detector(threading.Thread):
    def __init__(self, main):
        super().__init__()
        self.main = main
        self.buffer = deque()
        self.model = None
        self.thresh = 0.5
        self.detections = []
        self.dtection_buffer = 50

        try:
            self.model = self.load_model()
        except Exception as e:
            print(f"모델 로딩 중 오류 발생: {e}")
            if self.main:
                self.main.is_running = False

    def load_model(self):
        config_path = "./PeopleDetector/model/yolov4-tiny.cfg"
        weight_path = "./PeopleDetector/model/yolov4-tiny_best.weights"
        names_path = "./PeopleDetector/model/names.names"
        return DarknetWrapper(config_path, weight_path, names_path)

    def push(self, frame):
        self.buffer.append(frame)

    def run(self):
        if self.model is None:
            print("모델이 로드되지 않았습니다.")
            return

        while True if self.main is None else self.main.is_running:
            if len(self.buffer) > self.dtection_buffer:
                try:
                    latest = self.buffer[-1]
                    self.buffer.clear()
                    self.buffer.append(latest)
                except IndexError:
                    pass

            if self.buffer:
                try:
                    frame = self.buffer.popleft()

                    results = self.model.detect(frame, self.thresh)
                    current_detections = []
                    for label, conf, (x, y, w, h) in results:
                        x1 = int(x - w/2)
                        y1 = int(y - h/2)
                        current_detections.append((label, conf, (x1, y1, int(w), int(h))))

                    if self.main:
                        self.main.results = current_detections

                except IndexError:
                    pass
                except Exception as e:
                    print(f"객체 감지 중 오류 발생: {e}")

            time.sleep(0.01)

        print("[Detector] 스레드 종료.")
