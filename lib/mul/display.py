import cv2
import threading
import time

class RealTimeViewer(threading.Thread):
    def __init__(self, main, show_window=True):
        threading.Thread.__init__(self)
        self.main = main
        self.cam_id = getattr(main, 'cam_id', 0)
        self.is_stopped = False
        self.show_window = show_window
        self.cached_results = []
        self.last_result_ts = 0

        self.window_name = f"Camera-{self.cam_id}"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)

    def run(self):
        try:
            while not self.is_stopped:
                frame = self.main.latest_frame
                if frame is not None:
                    if self.main.result_timestamp > self.last_result_ts:
                        self.cached_results = self.main.results
                        self.last_result_ts = self.main.result_timestamp

                    for label, conf, (x, y, w, h) in self.cached_results:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (100, 0, 255), 3)
                        cv2.putText(frame, f"{label}: {conf:.2f}", (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 0, 255), 1)

                    if self.show_window:
                        cv2.imshow(self.window_name, frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

                time.sleep(0.01)
        except Exception as e:
            print(f"[Viewer-{self.cam_id}] 오류: {e}")
        finally:
            self.stop()

    def stop(self):
        self.is_stopped = True
        cv2.destroyWindow(self.window_name)