import time


class CmdProgressBar:
    """Displays a simple progress bar in the console. No other prints should be used as this relies in '\r'"""
    def __init__(self, upper=1, str_units="", bar_len=30):
        """Class constructor

        :param upper: Upper limit for progress value
        :param str_units: String appended before progress numbers
        :param bar_len: Bar width in characters
        """
        self.upper = upper
        self.str_units = str_units
        self.bar_len = bar_len

        self.min_update_ell_time = 1 / 60  # 1/frame_rate.

        self.start_time = time.perf_counter()
        self.last_update = self.start_time - 1  # To force the first print

        self.update(0)

    def update(self, value_in):
        """Redraws the progress bar

        :param value_in: Progress value
        """
        # Frame rate is limited to not slowdown the program. The last iteration is always drawn
        if time.perf_counter() - self.last_update > self.min_update_ell_time or value_in == self.upper:
            self.last_update = time.perf_counter()

            # Compute percentage completed and use it to draw the corresponding bar
            perc_completed = value_in / self.upper
            char_completed = round(self.bar_len * perc_completed)
            char_not_completed = self.bar_len - char_completed

            str_out = "%s: %d/%d (%0.2f%%) " % (self.str_units, value_in, self.upper, perc_completed * 100) \
                      + "[" + "#" * char_completed + " " * char_not_completed + "] " \
                      + "Tiempo transcurrido: %0.2fs" % (time.perf_counter() - self.start_time)
            print('\r' + str_out, end="")
            # Print a line break in the last iteration
            if value_in == self.upper:
                print("")
