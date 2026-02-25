import random
from testlibpy import write_test_case

random.seed(9823718273)


def write_random():
    write_test_case(f"{random.randint(1, 100000)} 15", rpt_name="rand-")


for _ in range(10):
    write_random()
