class FPSCounter:

    def __init__(self):
        # fps data
        self.time_between_updates_s = 0.10
        self.nr_samples = 60
        self.buffer = [0] * self.nr_samples
        self.index = 0
        self.last_update = 0
        self.fps = None
        self.avg_rendering_time = 0
        pass

    def update(self, current_time, delta_time):
        self.buffer[self.index] = delta_time
        self.index = 0 if self.index == self.nr_samples - 1 else self.index + 1
        # print("index={} current_time={} delta_time={}".format(self.index, current_time, delta_time))

        if (current_time - self.last_update > self.time_between_updates_s or self.fps is None):
            self.avg_rendering_time = sum(self.buffer) / self.nr_samples
            if (self.avg_rendering_time != 0):
                self.fps = 1 / self.avg_rendering_time
            self.last_update = current_time





