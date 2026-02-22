import random
from pathlib import Path

rand_count = 0

random.seed(764819273812)

MAX_N = 10**6
MAX_A = 10**8


def write_random():
    global rand_count
    rand_count += 1

    with open(Path(__file__).parent / f"rand-{rand_count}.in", "w") as f:
        n = random.randint(MAX_N // 2, MAX_N)
        a = set()
        while len(a) < n:
            a.add(random.randint(1, MAX_A))
        a = list(a)
        random.shuffle(a)
        a_str = " ".join(map(str, a))
        f.write(f"{n}\n{a_str}")


for _ in range(10):
    write_random()
