"""
Confirms the test suite is wired correctly.
"""


def test_pytest_runs():
    """
    Confirm pytest collects and executes tests without errors.
    """

    assert True


def test_one_plus_one():
    """
    Sanity check — arithmetic works.
    """

    assert 1 + 1 == 2
