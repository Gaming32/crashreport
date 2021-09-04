import crashreport

crashreport.inject_excepthook()


def main_div_by_0():
    print(1 / 0)


def main_recursion():
    x = 5
    main_recursion()


if __name__ == '__main__':
    main_recursion()
