### Automated block - translate to fit DMOJ checker:
import os

TESTING = os.getenv("TESTING", False)

if TESTING:

    class CheckerResult:
        def __init__(self, *args, **kwargs) -> None:
            self.args = args
            self.kwargs = kwargs

else:
    from dmoj.result import CheckerResult


def check(process_output: bytes, judge_output: bytes, **kwargs):
    points = kwargs.get("points", 0)
    process_data = process_output.decode("utf-8").strip()
    judge_data = judge_output.decode("utf-8").strip()
    case_input = kwargs.get("judge_input", "").decode("utf-8").strip()
    verdict, points, comment = judge(case_input, process_data, judge_data, points)
    return CheckerResult(verdict == "AC", points, comment)


### End automated block
