from threading import Timer


class Periodic(object):
    def __init__(self, bumper):
        self.timer = None
        self.bumper = bumper
        self.delay = bumper.delay * 1
        self.is_running = False
        self.start()

    def run(self):
        self.is_running = False
        self.start()
        self.bumper.test()

    def start(self):
        if not self.is_running:
            self.timer = Timer(self.delay, self.run)
            self.timer.start()
            self.is_running = True

    def stop(self):
        self.timer.cancel()
        self.is_running = False
