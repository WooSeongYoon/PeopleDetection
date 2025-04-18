import cv2
import threading
import time

cv2.namedWindow("Real-Time Stream", cv2.WINDOW_NORMAL)

class RealTimeViewer(threading.Thread):
    def __init__(self, main, show_window=True):
        threading.Thread.__init__(self)
        self.main = main
        self.is_stopped = False
        self.show_window = show_window

        self.cached_results = []
        self.last_result_ts = 0

    def run(self):
        try:
            while not self.is_stopped:
                frame = self.main.latest_frame
                if frame is not None:
                    # 결과가 갱신되었는지 확인
                    if self.main.result_timestamp > self.last_result_ts:
                        self.cached_results = self.main.results
                        self.last_result_ts = self.main.result_timestamp

                    # 이전 or 최신 결과를 사용하여 표시
                    for label, conf, (x, y, w, h) in self.cached_results:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (100, 0, 255), 3)
                        cv2.putText(frame, f"{label}: {conf:.2f}", (x, y-10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 0, 255), 1)

                    if self.show_window:
                        cv2.imshow("Real-Time Stream", frame)
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break

                time.sleep(0.01)  # GPU 과부하 방지용

        except Exception as e:
            print(f"[Viewer] 오류 발생: {e}")
        finally:
            self.stop()

    def stop(self):
        self.is_stopped = True
        cv2.destroyAllWindows()