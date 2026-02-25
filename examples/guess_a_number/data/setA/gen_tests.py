import random
from testlibpy import write_test_case

random.seed(19283718273)


def write_random():
    write_test_case(f"{random.randint(1, 100000)} 51", rpt_name="rand-")


for _ in range(10):
    write_random()
