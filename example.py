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


def main():
    print(1 / 0)


if __name__ == '__main__':
    main()
