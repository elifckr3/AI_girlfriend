import math
import time
import timeit
import inspect
import logging
import traceback
import typing as tp
from enum import Enum


"""
USAGE

import utils.timeit as timeit

> 1) within a block of code

```
with timeit.Timer() as t:
    time.sleep(1)
```

> 2) for a function looped over to get average time

 ``` timeit.nice_timeit(lambda: my_function(data)) ```


> 3) decorating a function to profile it's execution time

- PROFILE: line by line profiling
- CPROFILE: function call profiling

``` @timeit.PROFILE
    def my_function():
        pass
```
- or -

``` @timeit.CPROFILE
    def my_function():
        pass
```

> 4) decorating a function for elapsed time

``` @timeit.timeit
    def my_function():
        pass
```

"""


class LogLevel(Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


TermColors_T = tp.Literal[
    "HEADER",
    "OKBLUE",
    "OKCYAN",
    "OKGREEN",
    "WARNING",
    "FAIL",
    "BOLD",
    "UNDERLINE",
]

endc = "\033[0m"

term_map: dict[TermColors_T, str] = {
    "HEADER": "\033[95m",
    "OKBLUE": "\033[94m",
    "OKCYAN": "\033[96m",
    "OKGREEN": "\033[92m",
    "WARNING": "\033[93m",
    "FAIL": "\033[91m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
}


def format_exception(e: Exception) -> str:
    return "".join(traceback.format_exception(e))


class TermStr:
    """Terminal string output helper, currently just for color."""

    contents: str

    def __init__(self):
        self.active = None
        self.contents = ""

    def _format(self, text: str, color: TermColors_T | None) -> tp.Self:
        if color:
            self.contents += term_map[color] + text + endc

        self.contents += text
        return self

    def build(self) -> str:
        return self.contents

    def print(self) -> None:
        print(self.contents)

    def normal(self, text: str) -> tp.Self:
        return self._format(text, None)

    def blue(self, text: str) -> tp.Self:
        return self._format(text, "OKBLUE")

    def cyan(self, text: str) -> tp.Self:
        return self._format(text, "OKCYAN")

    def green(self, text: str) -> tp.Self:
        return self._format(text, "OKGREEN")

    def success(self, text: str) -> tp.Self:
        return self._format(text, "OKGREEN")

    def yellow(self, text: str) -> tp.Self:
        return self._format(text, "WARNING")

    def warning(self, text: str) -> tp.Self:
        return self._format(text, "WARNING")

    def red(self, text: str) -> tp.Self:
        return self._format(text, "FAIL")

    def fail(self, text: str) -> tp.Self:
        return self._format(text, "FAIL")

    def bold(self, text: str) -> tp.Self:
        return self._format(text, "BOLD")

    def underline(self, text: str) -> tp.Self:
        return self._format(text, "UNDERLINE")


def print_c(
    text: str,
    color: TermColors_T,
):
    print(TermStr()._format(text, color).build())


def _format_time(timespan, precision=3):
    """Formats the timespan in a human readable form"""
    units = ["s", "ms", "\xb5s", "ns"]
    scaling = [1, 1e3, 1e6, 1e9]
    if timespan > 0.0:
        order = min(-int(math.floor(math.log10(timespan)) // 3), 3)
    else:
        order = 3
    scaled_time = timespan * scaling[order]
    unit = units[order]
    return f"{scaled_time:.{precision}g} {unit}"


class TimeitResult:
    """
    Object returned by the timeit magic with info about the run.

    Contains the following attributes :

    loops: (int) number of loops done per measurement
    repeat: (int) number of times the measurement has been repeated
    best: (float) best execution time / number
    all_runs: (list of float) execution time of each run (in s)
    compile_time: (float) time of statement compilation (s)
    """

    def __init__(self, loops, repeat, best, worst, all_runs, compile_time, precision):
        self.loops = loops
        self.repeat = repeat
        self.best = best
        self.worst = worst
        self.all_runs = all_runs
        self.compile_time = compile_time
        self._precision = precision
        self.timings = [dt / self.loops for dt in all_runs]

    @property
    def average(self):
        return math.fsum(self.timings) / len(self.timings)

    @property
    def stdev(self):
        mean = self.average
        return (
            math.fsum([(x - mean) ** 2 for x in self.timings]) / len(self.timings)
        ) ** 0.5

    def __str__(self):
        return "{mean} {pm} {std} per loop (mean {pm} std. dev. of {runs} run{run_plural}, {loops} loop{loop_plural} each)".format(
            pm="+-",
            runs=self.repeat,
            loops=self.loops,
            loop_plural="" if self.loops == 1 else "s",
            run_plural="" if self.repeat == 1 else "s",
            mean=_format_time(self.average, self._precision),
            std=_format_time(self.stdev, self._precision),
        )


def nice_timeit(
    stmt="pass",
    setup="pass",
    number=0,
    repeat=None,
    precision=3,
    timer_func=timeit.default_timer,
):
    """Time execution of a Python statement or expression."""

    if repeat is None:
        repeat = 7 if timeit.default_repeat < 7 else timeit.default_repeat  # type: ignore[attr-defined]

    timer = timeit.Timer(stmt, setup, timer=timer_func, globals=None)

    # Get compile time
    compile_time_start = timer_func()
    compile(timer.src, "<timeit>", "exec")  # type: ignore[attr-defined]
    total_compile_time = timer_func() - compile_time_start

    # This is used to check if there is a huge difference between the
    # best and worst timings.
    # Issue: https://github.com/ipython/ipython/issues/6471
    if number == 0:
        # determine number so that 0.2 <= total time < 2.0
        for index in range(10):
            number = 10**index
            time_number = timer.timeit(number)
            if time_number >= 0.2:
                break

    all_runs = timer.repeat(repeat, number)
    best = min(all_runs) / number
    worst = max(all_runs) / number
    timeit_result = TimeitResult(
        number,
        repeat,
        best,
        worst,
        all_runs,
        total_compile_time,
        precision,
    )

    # Check best timing is greater than zero to avoid a
    # ZeroDivisionError.
    # In cases where the slowest timing is lesser than a microsecond
    # we assume that it does not really matter if the fastest
    # timing is 4 times faster than the slowest timing or not.
    if worst > 4 * best and best > 0 and worst > 1e-6:
        print_c(
            f"The slowest run took {worst / best:.2f} times longer than the fastest. This could mean that an intermediate result is being cached.",
            "BOLD",
        )

    print_c(str(timeit_result), "BOLD")

    if total_compile_time > 0.1:
        print_c(f"Compiler time: {total_compile_time:.2f} s", "BOLD")
    return timeit_result


class Timer:
    def __init__(
        self,
        desc: str = "Elapsed time",
        log_level: LogLevel = LogLevel.DEBUG,
    ):
        self.desc = desc
        self.elapsed: float = 0
        self.log_level = log_level

    def log(self, msg: str):
        if self.log_level:
            match self.log_level:
                case LogLevel.ERROR:
                    logging.error(msg)
                case LogLevel.WARNING:
                    logging.warning(msg)
                case LogLevel.INFO:
                    logging.info(msg)
                case LogLevel.DEBUG:
                    logging.debug(msg)
                case _:
                    tp.assert_never(self.log_level)

    def __enter__(self):
        self.log(f"Start: {self.desc}")

        self._time_start = time.perf_counter()
        return self

    def __exit__(self, exit_type, value, traceback):
        self.elapsed = time.perf_counter() - self._time_start

        elapsed_readout_part = f": {self.elapsed:.4f} seconds"
        self.readout = f"{self.desc}{elapsed_readout_part}"
        self.log(f"Finish: {self.desc}{elapsed_readout_part}")


def timeit(self, func):
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        filename = func.__module__.split(".")[-1]
        self.warning(
            f"Function '{func.__name__}' in '{filename}.py' executed in {format_time(execution_time)}",
        )
        return result

    return wrapper


def format_time(duration):
    if duration < 1e-6:
        return f"{duration * 1e9:.2f} ns"
    elif duration < 1e-3:
        return f"{duration * 1e6:.2f} µs"
    elif duration < 1:
        return f"{duration * 1e3:.2f} ms"
    else:
        return f"{duration:.4f} s"


def PROFILE(fn):
    if not _is_enabled():
        return fn

    import line_profiler

    def inner(*args, **kwargs):
        lp = line_profiler.LineProfiler()
        lp_wrapper = lp(fn)
        result = lp_wrapper(*args, **kwargs)
        lp.print_stats()
        return result

    # Give inner the same signature as fn so tools that inspect the function are not affected: (e.g. pytest)
    inner.__signature__ = inspect.signature(fn)  # type: ignore[attr-defined]

    return inner


def CPROFILE(fn):
    if not _is_enabled():
        return fn

    import cProfile
    import pstats

    profiler = cProfile.Profile()

    def inner(*args, **kwargs):
        result = None
        try:
            result = profiler.runcall(fn, *args, **kwargs)
        finally:
            stats = pstats.Stats(profiler)
            stats.sort_stats("cumtime").print_stats(100)
            # stats.strip_dirs().sort_stats("cumtime").print_stats(100)
            profiler.dump_stats("cprofile.prof")
        return result

    # Give inner the same signature as fn so tools that inspect the function are not affected: (e.g. pytest)
    inner.__signature__ = inspect.signature(fn)  # type: ignore[attr-defined]

    return inner


def _is_enabled():
    """Checking whether PROFILE env var set, if not then print message and don't profile."""

    # Note using os directly than settings.CONF, to allow this to happen completely outside of django for profiling before django loads.
    import os

    if "PROFILE" not in os.environ:
        print(
            "Not profiling! need to set environ var 'PROFILE=True' to actually profile!",
        )
        return False

    return True
