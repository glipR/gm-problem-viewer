"""---
name: Judge
description: Plays the higher/lower game.
---
"""
def read_line():
    pass

def write_line(s: str):
    pass

def make_result(code: str, points: float, comment: str):
    pass

def grade(input_file: str, points: float):
    x, q = list(map(int, input_file.split("\n")[0].split()))

    for i in range(q):
        d = int(read_line())
        if d == x:
            write_line("YES")
            return make_result("AC", points, "Correctly guessed the number!")
        elif i == q - 1:
            write_line("DONE")
        elif d < x:
            write_line("HIGHER")
        elif d > x:
            write_line("LOWER")
            return make_result("WA", 0, f"Failed to guess the number after {q} querues.")
