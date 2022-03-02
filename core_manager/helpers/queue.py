class Queue:

    sub = "organizer"
    base = "organizer"
    success = "organizer"
    fail = "organizer"
    interval = 0
    is_ok = False
    retry = 0
    counter = 0

    def clear_counter(self):
        self.counter = 0

    def counter_tick(self):
        self.counter += 1

    def set_step(self, sub, base, success, fail, interval=0, is_ok=False, retry=0):
        self.sub = sub
        self.base = base
        self.success = success
        self.fail = fail
        self.interval = interval
        self.is_ok = is_ok
        self.retry = retry
