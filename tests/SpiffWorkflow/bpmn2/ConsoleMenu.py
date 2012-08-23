#I stole this code from here: http://www.daniweb.com/software-development/python/code/309413/console-application-menu-module
# Don't think the author minds.
#
# It's not my code, so don't judge me

import string
from textwrap import wrap
try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

class Console_App_Menu():

    """Console Application Menu module.
It implements basic menu and dialogs on a console window."""
    def __init__(self, title='Console Application Menu', size=(80, 25), border='#', log_title='Log Output:'):
        """The class initialization takes as optional arguments:
            - title: title text of the menu
            - size: the size in characteres of the console window menu
            - border: character to be printed as border for the menu and dialogs
            - log_title: title text of the log window"""

        self.__width = size[0]
        self.__height = size[1] - 1
        self.__line = lambda(x): x * self.__width
        self.__ruler = lambda((x, l)): (x / 2) - (l / 2)
        self.__content = StringIO()
        self.__content.write((' ' * self.__width) * self.__height)
        self.__border = border[0]
        self.__log_title = log_title
        self.__log = ['', '', '', '']
        self.__draw_border()
        self.__writeline(3, title)
        self.__log_box()

    def __draw_border(self):
        self.__content.seek(0)
        self.__content.write(self.__border * self.__width)
        for i in range (1, self.__height):
            self.__content.seek(self.__line(i))
            self.__content.write(self.__border)
            self.__content.seek(self.__line(i + 1) - 1)
            self.__content.write(self.__border)
        self.__content.seek(self.__line(i))
        self.__content.write(self.__border * self.__width)

    def __writeline(self, line_n, text):
        self.__content.seek(self.__line(line_n) + self.__ruler((self.__width, len(text))))
        self.__content.write(text)

    def __log_box(self):
        self.__content.seek(self.__line(self.__height - 8) + 10)
        self.__content.write(self.__border + self.__border + self.__log_title)
        self.__content.write(self.__border * (self.__width - 22 - len(self.__log_title)))
        for i in reversed(range(4, 8)):
            self.__content.seek(self.__line(self.__height - i) + 10)
            self.__content.write(self.__border)
            self.__content.seek(self.__line(self.__height - (i - 1)) - 11)
            self.__content.write(self.__border)
        self.__content.seek(self.__line(self.__height - 3) + 10)
        self.__content.write(self.__border * (self.__width - 20))

    def __update_display(self):
        v = self.__content.getvalue()
        for i in range(0,self.__height):
            print v[i*self.__width:(i+1)*self.__width]
        #print self.__question

    def __log_write(self, output):
        for i in range(len(self.__log)):
            if self.__log[i] == '':
                self.__log[i] = output
                break
        else:
            self.__log.pop(0)
            self.__log.append(output)
        ylines = 7
        self.__content.seek(self.__line(self.__height - ylines) + 12)
        for i in range(len(self.__log)):
            self.__content.write(self.__log[i] + (' ' * (self.__width - 24 - len(self.__log[i]))))
            ylines -= 1
            self.__content.seek(self.__line(self.__height - ylines) + 12)

    def __dialog(self, dlg_type, dlg_text):
        scr_buffer = self.__content.getvalue()
        dlg_types = 'error', 'info', 'query_str', 'query_int', 'query_bool'
        dlg_titles = 'Error:', 'Information:', 'Question:', 'Question:', 'Question:'
        line = (self.__height / 2) - 3
        self.__content.seek(self.__line(line) + (self.__width / 4) - 1)
        self.__content.write(' ' * ((self.__width / 2) + 2))
        line += 1
        self.__content.seek(self.__line(line) + (self.__width / 4) - 1)
        self.__content.write(' ' + self.__border + self.__border + dlg_titles[dlg_types.index(dlg_type)])
        self.__content.write(self.__border * ((self.__width / 2) - len(dlg_titles[dlg_types.index(dlg_type)])) + ' ')
        for i in range(1, 4):
            self.__content.seek(self.__line(line + i) + (self.__width / 4) - 1)
            self.__content.write(' ' + self.__border + (' ' * (self.__width / 2) + self.__border + ' '))
        self.__content.seek(self.__line(line + 4) + (self.__width / 4) - 1)
        self.__content.write(' ' + (self.__border * ((self.__width / 2) + 2)) + ' ')
        self.__content.seek(self.__line(line + 2) + (self.__width / 4) + 1)
        self.__content.write((' ' * ((self.__width / 4) - (len(dlg_text) / 2) - 1)) + dlg_text  + (' ' * ((self.__width / 4) - (len(dlg_text) / 2))))
        #print self.__content.getvalue(),
        if dlg_type in ('error', 'info'):
            raw_input('Press Enter to continue... ')
            self.__content.seek(0)
            self.__content.write(scr_buffer)
            self.__update_display()
        elif dlg_type == 'query_str':
            value = raw_input('Enter string: ')
            self.__content.seek(0)
            self.__content.write(scr_buffer)
            return value
        elif dlg_type == 'query_int':
            while True:
                value = raw_input('Enter number: ')
                try:
                    value = int(value)
                    self.__content.seek(0)
                    self.__content.write(scr_buffer)
                    return value
                except:
                    self.__content.seek(0)
                    self.__content.write(scr_buffer)
                    return self.__dialog(dlg_type, dlg_text)
        elif dlg_type == 'query_bool':
            while True:
                value = raw_input('Enter \'Y(y)...\' or \'N(n)...\': ')
                if value:
                    if value[0].lower() == 'y':
                        self.__content.seek(0)
                        self.__content.write(scr_buffer)
                        return True
                    elif value[0].lower() == 'n':
                        self.__content.seek(0)
                        self.__content.write(scr_buffer)
                        return None
                self.__content.seek(0)
                self.__content.write(scr_buffer)
                return self.__dialog(dlg_type, dlg_text)

    def set_options(self, index_type, options_list, separator=') ', question='Insert option: '):
        """Sets menu options. It takes as arguments:
            - index type: 'numbers', 'low' and  'caps'
            - options: list of menu options
            and as optional arguments:
            - separator: characteres between the index and option
            - question: text following the menu
            Usage: Console_App_Menu.set_options(index, options)"""
        self.__separator = separator
        self.__question = question
        lenght = len(options_list)
        start = self.__ruler((self.__height - (self.__height / 4), lenght))
        string_size = max([len(item) for item in options_list])
        self.__options_list = [string.ljust(item, string_size) for item in options_list]
        if index_type == 'numbers':
            self.__indexs = string.digits
        elif index_type == 'low':
            self.__indexs = string.lowercase
        elif index_type == 'caps':
            self.__indexs = string.uppercase
        else:
            print 'Invalid Index Type'
        self.__valids = []
        index = 0
        for i in range(start, start + lenght):
            self.__writeline(i, self.__indexs[index] + self.__separator + self.__options_list[index])
            self.__valids.append(self.__indexs[index])
            index += 1

    def option(self):
        """Returns user selected menu option as a tuple containing:
            - the option index order
            - the option index character
            - the option text
            Usage: option = Console_App_Menu.option()"""
        #print self.__content.getvalue(),
        selected = raw_input(self.__question)
        if selected not in self.__valids:
            self.__dialog('error', 'Invalid Option Selected!!!')
            return self.option()
        else:
            return (self.__valids.index(selected), selected, self.__options_list[self.__valids.index(selected)].strip())

    def log(self, output):
        """Prints given text to the log window.
            Usage: Console_App_Menu.log(text)"""

        if len(output) > 56:
            list_output = wrap(output, 56)
            for output in list_output:
                self.__log_write(output)
            self.__update_display()
        else:
            self.__log_write(output)
            self.__update_display()

    def info(self, text):
        """Displays a information dialog with the given text.
            Usage: Console_App_Menu.info(text)"""

        self.__dialog('info', text[0:37])

    def error(self, text):
        """Displays a error dialog with the given text.
            Usage: Console_App_Menu.error(text)"""
        self.__dialog('error', text[0:37])

    def query(self, input_type, text):
        """Displays a query dialog with the given text and can return
            three different types of data:
                - an integer: Console_App_Menu.query('int', text)
                - a string: Console_App_Menu.query('str', text)
                - a boolean: Console_App_Menu.query('bool', text)
            Usage: input = Console_App_Menu.query(type, text)"""

        if input_type in ('int', 'str', 'bool'):
            return self.__dialog('query_' + input_type, text[0:37])

if __name__ == '__main__':
    menu = Console_App_Menu(title='Console Application Menu Calculator Demo')
    menu.set_options('low', ('Add x to y', 'Subtract x to y', 'Multiply x by y', 'Divide x by y', 'Help', 'Exit'))
    menu.log('Welcome, please select an option to continue...')
    exit_flag = None
    while not exit_flag:
        selected = menu.option()
        if selected == (0, 'a', 'Add x to y'):
            x = menu.query('int', 'Insert number x')
            y = menu.query('int', 'Insert number y')
            menu.log('The result of adding %s to %s is %s.' % (x, y, (x + y)))
        elif selected[0] == 1:
            x = menu.query('int', 'Insert number x')
            y = menu.query('int', 'Insert number y')
            menu.log('The result of subtracting %s to %s is %s.' % (x, y, (y - x)))
        elif selected[1] == 'c':
            x = menu.query('int', 'Insert number x')
            y = menu.query('int', 'Insert number y')
            menu.log('The result of multiplying %s by %s is %s.' % (x, y, (x * y)))
        elif selected[0] == 3:
            x = menu.query('int', 'Insert number x')
            y = menu.query('int', 'Insert number y')
            menu.log('The result of dividing %s by %s is %s.' % (x, y, (x / y)))
        elif selected[2] == 'Help':
            menu.log('Select a calculation option. The numbers will be asked, the calculation is done and the result will be displayed on this log window.')
        elif selected[2] == 'Exit':
            exit_flag = True
