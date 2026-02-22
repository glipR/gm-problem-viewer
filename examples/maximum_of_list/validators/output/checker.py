def make_result(code: str, points: float, comment: str):
    pass

def check(input_data: str, process_data: str, judge_data: str, points: float):
    n = int(input_data.split("\n")[0])
    a = list(map(int, input_data.split("\n")[1]))
    m = max(a)

    a1, a2 = list(map(int,  process_data.split("\n")[0].split()))
    if a1 != m:
        return make_result("WA", 0, "Not correct maximum")
    elif a2 == a1:
        return make_result("WA", 0, "Second value returned is the same as the maximum")
    elif a2 not in a:
        return make_result("WA", 0, "Second value is not in the input list")
    return make_result("AC", points, "Correctly provided")

