import time
import threading

class TimerPool:

    def __init__(self):
        self.running = None
        self.timer_list = []
        self.timer_lock = threading.Condition()

    def add_timer(self, timer):
        self.timer_list.append(timer)

    def run(self):
        self.running = True

        while self.running:
            # print('NGRJTGQDYR TimerPool.tick')
            now_sec = time.time()

            active_timer_sec_idx_timer_list = []
            for i,timer in enumerate(self.timer_list):
                next_sec = timer.next_sec(now_sec=now_sec)
                if next_sec is None: continue
                if next_sec > now_sec: continue
                active_timer_sec_idx_timer_list.append((next_sec,i,timer))
            active_timer_sec_idx_timer_list.sort()

            for _,_,timer in active_timer_sec_idx_timer_list:
                timer.tick(now_sec=now_sec)

            if not self.running: break

            now_sec = time.time()
            next_sec = self.timer_list
            next_sec = map(lambda i:i.next_sec(now_sec=now_sec),next_sec)
            next_sec = filter(lambda i:i!=None,next_sec)
            next_sec = list(next_sec)
            next_sec = min(next_sec) if len(next_sec)>0 else None
            now_sec = time.time()
            
            timeout_sec = None if next_sec is None else max(next_sec-now_sec,0)
            #time.sleep(max(next_sec-now_sec,0))
            with self.timer_lock:
                if not self.running: break
                self.timer_lock.wait(timeout=timeout_sec)

    def notify(self):
        with self.timer_lock:
            self.timer_lock.notify_all()

    def stop(self):
        self.running = False
        self.notify()
