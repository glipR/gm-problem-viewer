import random
from pathlib import Path

rand_count = 0

random.seed(19283718273)

def write_random():
    global rand_count
    rand_count += 1

    with open(Path(__file__).parent / f"rand-{rand_count}.in", "w") as f:
        f.write(f"{random.randint(1, 100000)} 51")

for _ in range(10):
    write_random()