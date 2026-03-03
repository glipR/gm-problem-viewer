### Automated block - translate to fit DMOJ interactive grader:
import os
import sys

DEBUG = os.environ("DEBUG", False)

{test_res_function}

if not (len(sys.argv) > 1 and not DEBUG):
    from dmoj.graders import InteractiveGrader
    from dmoj.result import CheckerResult

    class Grader(InteractiveGrader):
        def interact(self, case, interactor):
            input_data = case.input_data().decode().strip()
            write_fn = interactor.writeln
            read_fn = lambda: interactor.readln().decode()
            return test_res(input_data, write_fn, read_fn, case.points)

else:
    CheckerResult = lambda a, b, c: (a, b, c)
    res = test_res(sys.argv[2], print, input, 1)

### End automated block
