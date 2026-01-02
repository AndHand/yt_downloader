import threading
import time

class RateLimiter():
    def __init__(self, interval=30, per_interval=3, stop_event=None):
        self.executions_per_interval = per_interval
        self.time_interval = interval
        self.executions = [0] * self.executions_per_interval
        self.next_execution = 0
        self.lock = threading.Lock()
        self.stop_event = stop_event

    def get_execution_time(self):
        with self.lock:
            execution_num = self.next_execution
            execution_time = self.executions[execution_num]
            if time.time() < execution_time:
                self.executions[execution_num] += self.time_interval
            else:
                self.executions[execution_num] = time.time() + self.time_interval
            self.next_execution  = (self.next_execution + 1) % self.executions_per_interval
            return execution_time

    def execute(self, func):
        execution_time = self.get_execution_time()
        if time.time() < execution_time:
            wait_time = execution_time - time.time()
            print("waiting " + "{:.2f}".format(wait_time) + " seconds")
            wait_time_left = wait_time
            wait_step = 2
            while wait_time_left > 0:
                #don't wait all at once in case we want to interrupt the program
                current_wait = min(wait_step, wait_time_left)
                time.sleep(current_wait)
                wait_time_left -= current_wait
                if self.stop_event != None and self.stop_event.is_set():
                    return
        func()