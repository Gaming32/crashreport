import crashreport

crashreport.inject_excepthook(lambda dest: print('Dumped crash report to', dest))


def main_div_by_0():
    a = 3
    print(a / 0)


def main_double():
    try:
        main_div_by_0()
    except Exception:
        cause = None
        try:
            5 + 's'
        except TypeError as e:
            cause = e
        raise ValueError('exception raised') from cause


def main_recursion():
    x = 5
    main_recursion()


if __name__ == '__main__':
    main_double()
