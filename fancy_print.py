'''
    Paul Smith
    
    A collection of functions for printing to the command line with added
    formatting.
    
'''

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

def pause():
    input("Press 'Enter' to continue")

def progress_bar(percent:float, label:str='', formatting:str = 'Obt'):
    bar = '=' * int(percent * 20) + '-' * int((1 - percent + 0.04) * 20)
    fprint(bar + label, formatting)

def download_progress(content_remaining, file_size) -> None:
    progress = file_size - content_remaining
    percentage = progress / file_size
    progress_string = f' {round(progress/1048576, 2)}MB / {round(file_size/1048576, 2)}MB'
    progress_bar(percentage, progress_string, 'Ogt')
