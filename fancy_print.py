from colorama import Back, Fore, Style




FORE = {'k': Fore.BLACK,
        'r': Fore.RED,
        'g': Fore.GREEN,
        'y': Fore.YELLOW,
        'b': Fore.BLUE,
        'c': Fore.CYAN,
        'w': Fore.WHITE,}
BACK = {'K': Back.BLACK,
        'R': Back.RED,
        'G': Back.GREEN,
        'Y': Back.YELLOW,
        'B': Back.BLUE,
        'C': Back.CYAN,
        'W': Back.WHITE}
STYLE = {'d': Style.DIM,
         'n': Style.NORMAL,
         't': Style.BRIGHT}
LINE_UP = '\033[1A'
LINE_CLEAR = '\x1b[2K'


def fprint(string, formatting=None):
        fore, back, style, overwrite = '', '', '', False
        if formatting is None:
            formatting = ''
        for cha in formatting:
            if cha.islower():
                if cha in 'dnt':
                    style = STYLE.get(cha, "")
                else:
                    fore = FORE.get(cha, "")
            if cha.isupper():
                if cha == "O":
                    overwrite = True
                else:
                    back = BACK.get(cha, "")
        print_str = fore +\
                    back +\
                    style +\
                    string
        if overwrite:
            print(LINE_UP, end=LINE_CLEAR)
            print(print_str, Style.RESET_ALL)
        else:
            print(print_str, Style.RESET_ALL)

def clear(lines: int=50) -> None:
    print((LINE_UP + LINE_CLEAR) * lines, end=LINE_CLEAR)

def progress_bar(percent:float, label:str='', formatting:str = 'Obt'):
    fprint('=' * int(percent * 20) + '-' * int((1 - percent + 0.04) * 20) + label, 'Obt')
