import cv2
import threading
import time


class StreamGrabber(threading.Thread):
    def __init__(self, out, url, on_state, on_frame, module='opencv', options={}):
        threading.Thread.__init__(self)
        self.out = out
        self.url = url
        self.on_state = on_state
        self.on_frame = on_frame
        self.module = module

        self.is_stopped = False
        self.is_play = False
        self.dt_reconn = time.time()
        self.reconn_delay = 1
        self.RECONN_SECONDS = 10

        self.cap = None
        self.frame = None
        self.frame_cnt = 0
        self.grab_cnt = 1
        self.width = -1
        self.height = -1
        self.frame_w, self.frame_h = 0, 0

    def run(self):
        self.clear()
        self.play()

        while not self.is_stopped:
            if self.is_play:
                # 최신 프레임만 유지하기 위해 grab() 반복 후 마지막 retrieve()
                for _ in range(5):
                    self.cap.grab()
                r, frame = self.cap.retrieve()

                if r and frame is not None:
                    self.frame_cnt += 1
                    self.grab_cnt += 1
                    self.frame_w, self.frame_h = frame.shape[1], frame.shape[0]
                    self.on_frame((frame, self.frame_cnt, self.grab_cnt))
                else:
                    self.on_frame((None, self.frame_cnt, self.grab_cnt), True)
                    break  # 재시도 루프로 빠짐

            else:
                # 재연결 시도 루프
                if time.time() - self.dt_reconn >= self.reconn_delay:
                    self.clear()
                    self.play()
                    if self.is_play:
                        self.reconn_delay = 1
                    else:
                        self.reconn_delay = min(self.reconn_delay * 2, self.RECONN_SECONDS)

                time.sleep(0.001)

    def play(self):
        self.dt_reconn = time.time()
        try:
            self.cap = cv2.VideoCapture(self.url)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)  # 버퍼 제거 시도

            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            if not self.cap.isOpened():
                raise RuntimeError("[Grabber] 스트림 열기 실패")

            self.is_play = True
            print(f"[Grabber] 연결 성공: {self.url} ({self.width}x{self.height})")
        except Exception as e:
            print(f"[Grabber] 연결 오류: {e}")
            self.is_play = False

        self.on_state(is_play=self.is_play)

    def clear(self):
        self.is_play = False
        self.frame = None
        self.frame_cnt = 0
        self.on_state(is_play=self.is_play)

    def stop(self):
        self.is_stopped = True
        if self.cap:
            self.cap.release()
'''
import cv2
import threading
import time

class StreamGrabber(threading.Thread):
    def __init__(self, out, url, on_state, on_frame, module='opencv', options={}):
        threading.Thread.__init__(self)
        self.out = out
        self.url = url
        self.on_state = on_state
        self.on_frame = on_frame
        self.module = module

        self.is_play = False
        self.is_stopped = False
        self.dt_reconn = time.time()
        self.reconn_delay = 1
        self.RECONN_SECONDS = 10

        self.cap = None
        self.frame_cnt = 0
        self.grab_cnt = 1
        self.fps = 15  # 기본 fps
        self.width = -1
        self.height = -1
        self.frame_w, self.frame_h = 0, 0

    def run(self):
        self.clear()
        self.play()

        while not self.is_stopped:
            if self.is_play:
                # 최신 프레임만 유지 (과거 프레임 버리기)
                for _ in range(5):  # 버퍼 날리기
                    self.cap.grab()

                r, frame = self.cap.retrieve()
                if r and frame is not None:
                    self.frame_cnt += 1
                    self.frame_w, self.frame_h = frame.shape[1], frame.shape[0]
                    self.on_frame((frame, self.frame_cnt, self.grab_cnt))
                else:
                    self.on_frame((None, self.frame_cnt, self.grab_cnt), True)
                    break

                time.sleep(1 / self.fps)

            else:
                if time.time() - self.dt_reconn >= self.reconn_delay:
                    self.clear()
                    self.play()
                    self.reconn_delay = 1 if self.is_play else min(self.reconn_delay * 2, self.RECONN_SECONDS)

                time.sleep(0.001)

    def play(self):
        self.dt_reconn = time.time()
        try:
            self.cap = cv2.VideoCapture(self.url)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 0)  # 내부 버퍼 비활성화 (가능한 경우)
            self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            if self.fps <= 0 or self.fps > 60:
                self.fps = 15  # 안전한 기본값

            self.is_play = True
            print(f"[Grabber] RTSP 연결 성공: {self.width}x{self.height} @ {self.fps:.1f}fps")

        except Exception as e:
            print(f"[Grabber] 연결 오류: {e}")
            self.is_play = False

        self.on_state(is_play=self.is_play)

    def stop(self):
        self.is_stopped = True
        if self.cap:
            self.cap.release()

    def clear(self):
        self.is_play = False
        self.frame_cnt = 0
        self.on_state(is_play=self.is_play)
'''