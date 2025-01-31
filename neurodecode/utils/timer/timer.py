import time


class Timer:
    """
    Timer class.

    if autoreset=True, timer is reset after any member function call
    """

    def __init__(self, autoreset=False):
        self.autoreset = autoreset
        self.reset()

    def sec(self):
        """
        Provide the time since reset in seconds.
        """
        read = time.time() - self.ref
        if self.autoreset:
            self.reset()
        return read

    def msec(self):
        """
        Provide the time since reset in milliseconds.

        Returns
        -------
        float : The timing
        """
        return self.sec() * 1000.0

    def reset(self):
        """
        Reset the timer to zero.
        """
        self.ref = time.time()

    def sleep_atleast(self, sec):
        """
        Sleep up to sec seconds.

        It's more convenient if autoreset=True

        Parameters
        ----------
        sec : float
            The time to sleep in seconds.
        """
        timer_sec = self.sec()

        if timer_sec < sec:
            time.sleep(sec - timer_sec)
            if self.autoreset:
                self.reset()
