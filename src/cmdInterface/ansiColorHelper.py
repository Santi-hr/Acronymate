import ctypes


class AnsiColorCode:
    """Enum with several ANSI color and format codes"""
    GRAY = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'

    DEFAULT = '\033[39m'
    DARK_CYAN = '\033[36m'
    DARK_YELLOW = '\033[33m'

    BACK_BLACK = '\033[40m'
    BACK_RED = '\033[41m'
    BACK_GREEN = '\033[42m'
    BACK_YELLOW = '\033[43m'
    BACK_BLUE = '\033[44m'
    BACK_MAGENTA = '\033[45m'
    BACK_CYAN = '\033[46m'
    BACK_WHITE = '\033[47m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def highlight_substr(str_in, span, highlight_color):
    """Highlights a substring by inserting a color code and its end code after and before the input span

    :param str_in: Input string
    :param span: Tuple with the start and end of the highlight
    :param highlight_color: AnsiColorCode
    :return: String with part highlighted
    """
    str_out = str_in[:span[0]] + highlight_color + str_in[span[0]:span[1]] + AnsiColorCode.END + str_in[span[1]:]
    return str_out


def color_str(str_in, highlight_color):
    """ Adds the color code and end code to a string

    :param str_in: Input string
    :param highlight_color: AnsiColorCode
    :return: String with color and end codes
    """
    str_out = highlight_color + str_in + AnsiColorCode.END
    return str_out


def enable_ansi_in_windows_cmd():
    """Enables ENABLE_VIRTUAL_TERMINAL_PROCESSING in the Windows 10 console"""
    # Windows 10 added support for ANSI escape sequences
    # Using ctypes to enable them by using SetConsoleMode Windows API with the ENABLE_VIRTUAL_TERMINAL_PROCESSING
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
