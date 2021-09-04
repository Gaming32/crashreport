import io
import os
import pprint
import sys
import time
import traceback
from types import FrameType, TracebackType
from typing import IO, Any, List, Optional, Type, Union


def _get_main_name() -> str:
    import __main__
    return os.path.splitext(os.path.basename(__main__.__file__))[0]


def _write_separator(f: IO) -> int:
    return f.write('\n\n' + '='*75 + '\n\n')


def _exhaustive_vars(obj: Any) -> dict[str, Any]:
    return {name: getattr(obj, name) for name in dir(obj)}


def _variable_summary(f: IO, vars: dict[str, Any]) -> None:
    for (name, value) in vars.items():
        label = f'{name} => '
        indent = len(label)
        formatted = pprint.pformat(value)
        formatted = formatted.replace('\n', '\n' + ' '*indent)
        f.write(f'{label}{formatted}\n')


_RECURSIVE_CUTOFF = 3
def _trace_exchaustive(result: IO, tb: TracebackType) -> None:
    last_file = None
    last_line = None
    last_name = None
    count = 0
    frame: FrameType
    for (frame, lineno) in traceback.walk_tb(tb):
        co = frame.f_code
        filename = co.co_filename
        name = co.co_name
        summary = traceback.FrameSummary(filename, lineno, name, lookup_line=True)
        if (last_file is None or last_file != filename or
            last_line is None or last_line != lineno or
            last_name is None or last_name != name):
            if count > _RECURSIVE_CUTOFF:
                count -= _RECURSIVE_CUTOFF
                result.write(
                    f'  [Previous frame repeated {count} more '
                    f'time{"s" if count > 1 else ""}]\n'
                )
            last_file = filename
            last_line = lineno
            last_name = name
            count = 0
        count += 1
        if count > _RECURSIVE_CUTOFF:
            _write_separator(result)
            frame = frame.f_back
            continue
        result.write(f'File "{filename}", line {lineno}, in {name}\n')
        if summary.line:
            result.write(f'--->  {summary.line.strip()}\n\n')
        if frame.f_locals:
            _variable_summary(result, frame.f_locals)
        _write_separator(result)
        frame = frame.f_back
    if count > _RECURSIVE_CUTOFF:
        count -= _RECURSIVE_CUTOFF
        result.write(
            f'  [Previous frame repeated {count} more '
            f'time{"s" if count > 1 else ""}]\n'
        )


def dump_report_to_file(file: Union[str, IO], etype: Optional[Type[BaseException]], value: Optional[BaseException], tb: Optional[TracebackType]) -> None:
    if isinstance(file, str):
        with open(file, 'w') as fp:
            dump_report_to_file(fp, etype, value, tb)
            return

    import __main__

    # Write name and date
    file.write(f'"{__main__.__file__}" crashed at {time.strftime("%Y-%m-%dT%H:%M:%S%z")} ({time.strftime("%F %H:%M:%S %Z")})')
    _write_separator(file)

    # Write traceback
    tb_lines = traceback.format_exception(etype, value, tb)
    file.write(''.join(tb_lines))
    _write_separator(file)

    file.write(f'Summary of sys variables:\n')
    _variable_summary(file, _exhaustive_vars(sys))
    _write_separator(file)

    file.write('Following is an exhaustive stack trace (most recent call last)')
    _write_separator(file)

    _trace_exchaustive(file, tb)


def dump_report(etype: Optional[Type[BaseException]], value: Optional[BaseException], tb: Optional[TracebackType]) -> str:
    filename = f'{_get_main_name()}-{time.strftime("%Y-%m-%d-%H-%M-%S")}.dump'
    dump_report_to_file(filename, etype, value, tb)
    return filename


def format_report(etype: Optional[Type[BaseException]], value: Optional[BaseException], tb: Optional[TracebackType]) -> str:
    result = io.StringIO()
    dump_report_to_file(result, etype, value, tb)
    return result.getvalue()
