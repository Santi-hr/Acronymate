import time
from src.cmdInterface import ansiColorHelper as ach


class CmdProgressBar:
    """Displays a simple progress bar in the console. No other prints with \n should be used as this relies in '\r'"""
    def __init__(self, upper=1, str_units="", bar_len=30):
        """Class constructor

        :param upper: Int value associated with 100% progress
        :param str_units: String appended before progress numbers
        :param bar_len: Bar width in characters
        """
        self.upper = max(upper, 1)  # The use of max prevents divisions by zero and negative values.
        self.str_units = str_units
        self.bar_len = bar_len

        self.min_update_ell_time = 1 / 30  # 1/frame_rate.

        self.start_time = time.perf_counter()
        self.last_update = self.start_time - 1  # To force the first print

    def update(self, value_in):
        """Redraws the progress bar

        :param value_in: Int progress value. Should be between 0 and upper.
        """
        # Frame rate is limited to not slowdown the program. The last iteration is always drawn
        if time.perf_counter() - self.last_update > self.min_update_ell_time or value_in == self.upper:
            self.last_update = time.perf_counter()

            # Compute percentage completed and use it to draw the corresponding bar
            perc_completed = min(1, max(0, value_in / self.upper)) #Constrained between [0,1]
            char_completed = round(self.bar_len * perc_completed)
            char_not_completed = self.bar_len - char_completed

            str_out = "%s: %d/%d (%0.2f%%) " % (self.str_units, value_in, self.upper, perc_completed * 100) \
                      + "[" + ach.AnsiColorCode.DARK_GREEN \
                      + "#" * char_completed + " " * char_not_completed \
                      + ach.AnsiColorCode.END + "] " \
                      + _("Tiempo transcurrido:") + " %0.2fs" % (time.perf_counter() - self.start_time)
            print('\r' + str_out, end="")
            # Print a line break in the last iteration
            if value_in >= self.upper:
                print("")
