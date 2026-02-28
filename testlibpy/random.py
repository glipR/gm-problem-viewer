import random


def select_k_distinct(collection: list, k: int):
    ind = [
        x + i
        for i, x in enumerate(
            sorted([random.randint(0, len(collection) - k - 1) for _ in range(k)])
        )
    ]
    vals = [collection[i] for i in ind]
    random.shuffle(vals)
    return vals
