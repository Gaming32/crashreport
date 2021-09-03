import sys

import crashreport


old_exc_handler = sys.excepthook

def exc_handler(etype, value, tb):
    if issubclass(etype, Exception):
        dest = crashreport.dump_report(etype, value, tb)
        print('Dumped crash report to', dest)
        sys.exit(1)
    old_exc_handler(etype, value, tb)


sys.excepthook = exc_handler


def main_div_by_0():
    print(1 / 0)


def main_recursion():
    x = 5
    main_recursion()


if __name__ == '__main__':
    main_recursion()
