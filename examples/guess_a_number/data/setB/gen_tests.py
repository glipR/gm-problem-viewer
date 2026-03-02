import random
from testlibpy import test_case

random.seed(9823718273)


for _ in range(10):
    with test_case(rpt_name="rand-") as w:
        w.write_line(f"{random.randint(1, 100000)} 17")
