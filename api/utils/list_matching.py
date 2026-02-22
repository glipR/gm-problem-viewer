"""
This utility supports many of the frontmatter filters that exist for things like solutions and validators,
that can optionally specify a list of test sets they apply to / have expected results for.
"""


def filter_list_matches_test_set(filter_list: list[str] | None, test_set: str):
    if filter_list is None:
        return True
    return test_set in filter_list
