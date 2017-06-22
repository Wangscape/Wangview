
# coding: utf-8
from time import perf_counter, sleep

class FPSLimiter:
    """
    Allows framerates to be throttled and measured.
    """
    def __init__(self, max_fps = 60):
        self._frame_count = 0
        self._fps = 0
        self.set_max_fps(max_fps)
        self._previous_time = perf_counter()
        self._start_of_second = self._previous_time
    def set_max_fps(self, max_fps):
        """
        Changes the FPSLimiter's maximum framerate to max_fps.
        """
        self._max_fps = max_fps
        self._interval = 1./max_fps
    def wait(self):
        """
        When called every frame, prevents the maximum framerate from being
        exceeded by calling time.sleep() with an appropriate interval.
        """
        t = perf_counter()
        self._frame_count += 1
        if t - self._start_of_second >= 1.:
            self._fps = self._frame_count
            self._frame_count = 0
            self._start_of_second = t
        dt = t - self._previous_time
        if(dt < self._interval):
            sleep_interval = self._interval - dt
            correct_sleep_interval  = min(self._interval, sleep_interval)
            sleep(correct_sleep_interval)
        self._previous_time = perf_counter()
    def get_fps(self):
        """
        Returns the number of times wait() was called in the last completed second.
        """
        return self._fps
