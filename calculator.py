try:
    import tkinter
except ImportError:  # Python 2
    import Tkinter as tkinter
import tkinter.font
import math
import re


class Settings:
    def __init__(self, angles='degrees', fix_sci='fix', fix_sci_digits=8, norm=1):
        self.angles = angles
        self.fix_sci = [fix_sci, fix_sci_digits]
        self.norm = norm

    def sig_fig(self, number):
        return round(number, self.fix_sci[1]-int(math.floor(math.log10(abs(number)))) - 1)

    def angle_calc(self, angle):
        if self.angles == 'degrees':
            return math.degrees(angle)
        elif self.angles == 'radians':
            return angle


class Memory:
    def __init__(self):
        self.screen = []
        self.output = []

    def add(self, screen_input, result):
        self.screen.insert(0, screen_input)
        self.output.insert(0, result)


class Coordinates:
    def __init__(self, x: float, y: float, pol_rec: str):
        self.x = x
        self.y = y
        self.type = pol_rec

    def pol(self):
        r = math.sqrt(self.x ** 2 + self.y ** 2)
        theta = settings.angle_calc(math.atan2(self.y, self.x))
        return r, theta

    def rec(self):
        if settings.angles == 'degrees':
            x = self.x * math.cos(math.radians(self.y))
            y = self.x * math.sin(math.radians(self.y))
        else:
            x = self.x * math.cos(self.y)
            y = self.x * math.sin(self.y)
        return x, y


def change_state(new_state: str):
    global state
    if state == new_state:
        state = 'normal'
    else:
        state = new_state
    build_buttons()


def fact(n):
    if n == 0:
        return 1
    else:
        return n * fact(n - 1)


def add_text(symbol):
    global screen
    global state
    global output
    global screen_mode
    global clear_option
    global setup_option
    if screen_mode == 'normal':
        output['text'] = ''
        expression.append(str(symbol))
        screen['text'] = ''.join(expression)
        if state != 'normal':
            state = 'normal'
            build_buttons()
    elif screen_mode == 'clear':
        clear_option = None
        options = {1: "Setup", 2: "Memory", 3: "All"}
        if symbol in (1, 2, 3):
            screen['text'] = f"Reset {options[symbol]}?\n" \
                             f"[=]: Yes   [AC]: Cancel"
            clear_option = symbol
    elif screen_mode == 'setup':
        setup_option = None
        if symbol in (1, 2, 3, 4, 5):
            if symbol == 1:
                settings.angles = 'degrees'
                ac()
            elif symbol == 2:
                settings.angles = 'radians'
                ac()
            elif symbol == 3:
                screen['text'] = 'Fix 0 - 9'
                settings.fix_sci[0] = 'Fix'
                screen_mode = 'FixSci'
            elif symbol == 4:
                screen['text'] = 'Sci 0 - 9'
                settings.fix_sci[0] = 'Sci'
                screen_mode = 'FixSci'
            elif symbol == 5:
                screen['text'] = 'Norm 1 - 2'
                screen_mode = 'Norm'
    elif screen_mode == 'FixSci':
        if symbol in [x for x in range(0, 10)]:
            settings.fix_sci[1] = symbol
            ac()
    elif screen_mode == 'Norm':
        if symbol in (1, 2):
            settings.norm = symbol
            ac()


def ac():
    global screen
    global expression
    global screen_mode
    screen_mode = 'normal'
    screen['text'] = ''
    output['text'] = ''
    expression = []


def delete():
    global screen
    global expression
    if expression:
        expression.pop()
        screen['text'] = ''.join(expression)


def clear():
    global screen_mode
    global state
    screen_mode = 'clear'
    screen['text'] = "Clear?\n" \
                     "1: Setup   2: Memory   3: All"
    output['text'] = ''
    state = 'normal'
    build_buttons()


def setup():
    global screen_mode
    global state
    screen_mode = 'setup'
    screen['text'] = f"1: Deg   2: Rad\n" \
                     f"3: Fix   4: Sci\n" \
                     f"5: Norm"
    output['text'] = ''
    state = 'normal'
    build_buttons()


def solve_expression(expression_list):
    global co_ords
    while any(item in ['Pol(', 'Rec(', '('] for item in expression_list):
        # re.match(r"\((.+)\)", expression_list).group(1)
        for index, term in enumerate(expression_list):
            # if term in ['Pol(', 'Rec(', '(']:
            #     new_list = []
            #     for i in range(index + 1, len(expression_list)):
            #         print(expression_list)
            #         while expression_list[index + 1] != ')':
            #             new_list.append(expression_list.pop(index))
            #     expression_list.pop(index + 1)
            #     expression_list[index] = solve_expression(new_list)
            #     print(expression_list)

            if term in ('Pol(', 'Rec('):
                x, y = float(expression_list.pop(index + 1)), \
                       float(expression_list.pop(index + 2))
                if expression_list.pop(index + 1) != ',' or expression_list.pop(index + 1) != ')':
                    raise ValueError
                if term == 'Pol(':
                    number = Coordinates(x, y, 'Rec').pol()
                    co_ords = Coordinates(number[0], number[1], 'Pol')
                elif term == 'Rec(':
                    number = Coordinates(x, y, 'Pol').rec()
                    co_ords = Coordinates(number[0], number[1], 'Rec')
                expression_list[index] = str(number[0])
    while any(item in ['(×10)', 'P', 'C'] for item in expression_list):
        for index, term in enumerate(expression_list):
            if term in ['(×10)', 'P', 'C']:
                if term == '(×10)':
                    number = float(expression_list.pop(index - 1)) * \
                             (10 ** float(expression_list.pop(index)))
                elif term in ('P', 'C'):
                    n, r = float(expression_list.pop(index - 1)), float(expression_list.pop(index))
                    if term == 'P':
                        number = fact(n) / fact(n - r)
                    elif term == 'C':
                        number = fact(n) / (fact(r) * fact(n - r))

                expression_list[index - 1] = str(number)
    while any(item in ('×', '÷') for item in expression_list):
        for index, term in enumerate(expression_list):
            if term in ('×', '÷'):
                if term == '×':
                    number = float(expression_list.pop(index - 1)) * float(expression_list.pop(index))
                elif term == '÷':
                    number = float(expression_list.pop(index - 1)) / float(expression_list.pop(index))
                expression_list[index - 1] = number
    if expression_list[0] == '-':
        expression_list[0] += expression_list.pop(1)
    result = float(expression_list[0])
    for index, term in enumerate(expression_list):
        if term == '+':
            result += float(expression_list[index + 1])
        elif term == '-':
            result -= float(expression_list[index + 1])

    if str(expression_list[-1]) in '+-×÷':
        raise ValueError

    return result


def equals():
    global ans
    global screen
    global output
    global expression
    global clear_option
    global co_ords
    if screen_mode == 'normal':
        number = ''
        interpreted_string = []
        if expression:
            try:
                for index, term in enumerate(expression):
                    if (index == 0 or not expression[index - 1].isdigit()) and term == '-':
                        number += term
                    elif term.isdigit() or term == '.':
                        number += term
                    elif term == 'Ans':
                        if number:
                            number = str(float(number) * float(ans))
                        else:
                            number = ans
                    else:
                        if number:
                            interpreted_string.append(number)
                        number = ''
                        interpreted_string.append(term)
                if number:
                    interpreted_string.append(number)
                result = solve_expression(interpreted_string)
                # while any(item in ['Pol(', 'Rec('] for item in interpreted_string):
                #     for index, term in enumerate(interpreted_string):
                #         if term in ('Pol(', 'Rec('):
                #             x, y = float(interpreted_string.pop(index + 1)), \
                #                 float(interpreted_string.pop(index + 2))
                #             if interpreted_string.pop(index + 1) != ',' or interpreted_string.pop(index + 1) != ')':
                #                 raise ValueError
                #             if term == 'Pol(':
                #                 number = Coordinates(x, y, 'Rec').pol()
                #                 co_ords = Coordinates(number[0], number[1], 'Pol')
                #             elif term == 'Rec(':
                #                 number = Coordinates(x, y, 'Pol').rec()
                #                 co_ords = Coordinates(number[0], number[1], 'Rec')
                #             interpreted_string[index] = str(number[0])
                # while any(item in ['(×10)', 'P', 'C'] for item in interpreted_string):
                #     for index, term in enumerate(interpreted_string):
                #         if term in ['(×10)', 'P', 'C']:
                #             if term == '(×10)':
                #                 number = float(interpreted_string.pop(index - 1)) * \
                #                          (10 ** float(interpreted_string.pop(index)))
                #             elif term in ('P', 'C'):
                #                 n, r = float(interpreted_string.pop(index - 1)), float(interpreted_string.pop(index))
                #                 if term == 'P':
                #                     number = fact(n) / fact(n - r)
                #                 elif term == 'C':
                #                     number = fact(n) / (fact(r) * fact(n - r))
                #
                #             interpreted_string[index - 1] = str(number)
                # while any(item in ('×', '÷') for item in interpreted_string):
                #     for index, term in enumerate(interpreted_string):
                #         if term in ('×', '÷'):
                #             if term == '×':
                #                 number = float(interpreted_string.pop(index - 1)) * float(interpreted_string.pop(index))
                #             elif term == '÷':
                #                 number = float(interpreted_string.pop(index - 1)) / float(interpreted_string.pop(index))
                #             interpreted_string[index - 1] = number
                # if interpreted_string[0] == '-':
                #     interpreted_string[0] += interpreted_string.pop(1)
                # result = float(interpreted_string[0])
                # for index, term in enumerate(interpreted_string):
                #     if term == '+':
                #         result += float(interpreted_string[index + 1])
                #     elif term == '-':
                #         result -= float(interpreted_string[index + 1])
                #
                # if str(interpreted_string[-1]) in '+-×÷':
                #     raise ValueError
            except (ValueError, TypeError) as e:
                screen['text'] = 'Syntax Error'
            except (ZeroDivisionError, RecursionError):
                screen['text'] = 'Maths Error'
            else:
                if co_ords and result == co_ords.x:
                    if co_ords.type == 'Pol':
                        output['text'] = f"r: {co_ords.x}, \u03B8: {co_ords.y}"
                    elif co_ords.type == 'Rec':
                        output['text'] = f"x: {co_ords.x}, y: {co_ords.y}"
                    ans = str(co_ords.x)
                else:
                    if settings.fix_sci[0] == 'fix':
                        output['text'] = round(result, settings.fix_sci[1])
                    elif settings.fix_sci[0] == 'sci':
                        output['text'] = settings.sig_fig(result)
                    ans = str(result)
                memory.add(expression, output['text'])
            expression = []
    elif screen_mode == 'clear':
        if clear_option:
            if clear_option in (1, 3):
                settings.__init__()
            if clear_option in (2, 3):
                memory.__init__()
            screen['text'] = "Complete\n" \
                             "Press [AC] key to continue"


def build_buttons():
    for i in range(len(function_buttons[state])):
        for j in range(len(function_buttons[state][i])):
            name = function_buttons[state][i][j]
            if name:
                if button_commands[name]:
                    button = tkinter.Button(function_frame, text=name, width=6, command=button_commands[name])
                else:
                    button = tkinter.Button(function_frame, text=name, width=6)
                    # TODO: remove this if statement once all functions implemented
                button.grid(row=i, column=j, sticky='ns', padx=1, pady=4)
                button['font'] = tkinter.font.Font(size=10)
            if name == 'SHIFT':
                button['fg'] = 'blue'
            elif name == 'ALPHA':
                button['fg'] = 'red'
            if name != function_buttons['normal'][i][j]:
                if state == 'shift':
                    button['fg'] = 'blue'
                elif state == 'alpha':
                    button['fg'] = 'red'
            if i == 0:
                button['bg'] = 'grey'

    for i in range(len(number_buttons[state])):
        for j in range(len(number_buttons[state][i])):
            name = number_buttons[state][i][j]
            if button_commands[name]:
                button = tkinter.Button(number_frame, text=name, width=7, command=button_commands[name])
            else:
                button = tkinter.Button(number_frame, text=name, width=7)
                # TODO: remove this if statement once all functions implemented
            button.grid(row=i, column=j, sticky='ns', padx=3, pady=4)
            if i == 0 and j in (3, 4):
                button['bg'] = 'orange'
            if name != number_buttons['normal'][i][j]:
                if state == 'shift':
                    button['fg'] = 'blue'
                elif state == 'alpha':
                    button['fg'] = 'red'


if __name__ == '__main__':
    main_window = tkinter.Tk()
    main_window.title('Scientific Calculator')
    main_window['padx'] = 10
    main_window['pady'] = 10
    main_window.rowconfigure(0, weight=3)
    main_window.rowconfigure(5, weight=4)

    # TODO Add a Label to display the current settings
    screen = tkinter.Label(main_window, bg='white', relief='sunken')
    screen.grid(row=0, column=0, sticky='nsew', rowspan=2, ipady=35)
    expression = []
    output = tkinter.Label(main_window, bg='white', relief='sunken')
    output.grid(row=3, column=0, sticky='nsew', pady=10)

    function_frame = tkinter.Frame(main_window)
    function_frame.grid(row=4, column=0, sticky='nsew', pady=10)

    number_frame = tkinter.Frame(main_window)
    number_frame.grid(row=5, column=0, sticky='nsew', pady=0)

    # Create the buttons
    state = screen_mode = 'normal'
    ans, clear_option, co_ords, setup_option = '0', None, None, None
    settings = Settings()
    memory = Memory()

    button_commands = {"SHIFT": lambda: change_state('shift'), "ALPHA": lambda: change_state('alpha'), "MODE": None,
                       "ON": None, "Abs": None, "x\u00b3": None, 'x\u207B\u00b9': None, 'log\u2099()': None,
                       '()/()': None, '√()': None, 'x\u00b2': None, 'x\u207f': None, 'log': None, 'ln': None,
                       '(-)': None, '., ,,': None, 'hyp': None, 'sin': None, 'cos': None, 'tan': None, 'RCL': None,
                       'ENG': None, '(': lambda: add_text('('), ')': lambda: add_text(')'), 'S<=>D': None, 'M+': None,
                       'SETUP': setup, 'x!': None, '() ()/()': None, '\u00b3√()': None, '(\u0305)\u0305': None,
                       '\u207f√()': None, '10\u207f': None, 'e\u207f': None, 'FACT': None, 'sin\u207B\u00b9': None,
                       'cos\u207B\u00b9': None, 'tan\u207B\u00b9':  None, 'STO': None, '<-': None, '%': None,
                       ',': lambda: add_text(','), 'a b/c': None, 'M-': None, ':': None, 'A': None, 'B': None,
                       'C': None, 'D': None, 'E': None, 'F': None, 'X': None, 'Y': None, 'M': None,
                       '7': lambda: add_text(7), '8': lambda: add_text(8), '9': lambda: add_text(9), 'DEL': delete,
                       'AC': ac, '4': lambda: add_text(4), '5': lambda: add_text(5), '6': lambda: add_text(6),
                       '×': lambda: add_text('×'), '÷': lambda: add_text('÷'), '1': lambda: add_text(1),
                       '2': lambda: add_text(2), '3': lambda: add_text(3), '+': lambda: add_text('+'),
                       '-': lambda: add_text('-'), '0': lambda: add_text(0), '.': lambda: add_text('.'),
                       '×10\u207f': lambda: add_text('(×10)'), 'Ans': lambda: add_text('Ans'), '=': equals,
                       'CLR': clear, 'INS': None, 'OFF': main_window.destroy, 'nPr': lambda: add_text('P'),
                       'nCr': lambda: add_text('C'), 'STAT': None, 'VERIFY': None, 'Pol': lambda: add_text('Pol('),
                       'Rec': lambda: add_text('Rec('), 'Rnd': lambda: add_text('Rnd('),
                       'Ran#': lambda: add_text('Ran#'), '\u03C0': lambda: add_text('\u03C0'),
                       'DRG>': None, 'RanInt': lambda: add_text('RanInt#('), 'e': lambda: add_text('e')}

    function_buttons = {
        'normal': (('SHIFT', 'ALPHA', None, None, 'MODE', 'ON'),
                   ('Abs', 'x\u00b3', None, None, 'x\u207B\u00b9', 'log\u2099()'),
                   ('()/()', '√()', 'x\u00b2', 'x\u207f', 'log', 'ln'),
                   ('(-)', '., ,,', 'hyp', 'sin', 'cos', 'tan'),
                   ('RCL', 'ENG', '(', ')', 'S<=>D', 'M+')),
        'shift': (('SHIFT', 'ALPHA', None, None, 'SETUP', 'ON'),
                  ('Abs', 'x\u00b3', None, None, 'x!', 'log\u2099()'),
                  ('() ()/()', '\u00b3√()', '(\u0305)\u0305', '\u207f√()', '10\u207f', 'e\u207f'),
                  ('(-)', 'FACT', 'hyp', 'sin\u207B\u00b9', 'cos\u207B\u00b9', 'tan\u207B\u00b9'),
                  ('STO', '<-', '%', ',', 'a b/c', 'M-')),
        'alpha': (('SHIFT', 'ALPHA', None, None, 'MODE', 'ON'),
                  ('Abs', ':', None, None, 'x\u207B\u00b9', 'log\u2099()'),
                  ('()/()', '√()', 'x\u00b2', 'x\u207f', 'log', 'ln'),
                  ('A', 'B', 'C', 'D', 'E', 'F'),
                  ('RCL', 'ENG', '(', 'X', 'Y', 'M'))
    }

    number_buttons = {
        'normal': (('7', '8', '9', 'DEL', 'AC'),
                   ('4', '5', '6', '×', '÷'),
                   ('1', '2', '3', '+', '-'),
                   ('0', '.', '×10\u207f', 'Ans', '=')),
        'shift': (('7', '8', 'CLR', 'INS', 'OFF'),
                  ('4', '5', '6', 'nPr', 'nCr'),
                  ('STAT', 'VERIFY', '3', 'Pol', 'Rec'),
                  ('Rnd', 'Ran#', '\u03C0', 'DRG>', '=')),
        'alpha': (('7', '8', '9', 'DEL', 'AC'),
                  ('4', '5', '6', '×', '÷'),
                  ('1', '2', '3', '+', '-'),
                  ('0', 'RanInt', 'e', 'Ans', '='))
    }

    build_buttons()

    main_window.update()
    main_window.minsize(main_window.winfo_width(), main_window.winfo_height())
    main_window.maxsize(main_window.winfo_width(), main_window.winfo_height())
    main_window.mainloop()
