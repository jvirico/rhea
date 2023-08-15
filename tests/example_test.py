# (c) Copyright 2023 The Chromosome Project. All rights reserved.

"""
Please follow pytest best practices detailed here https://docs.pytest.org/en/6.2.x/goodpractices.html

We follow the following conventions:
- test files are named "*_test.py", where * is the name of the module that is being tested
  example: tests for some file "rc_core_rhea/foo/foo.py"
  are located in file "rc_core_rhea/tests/foo/foo_test.py"
- all test functions start with "test_"
- relevant test data is located in subfolder "data"
"""
from rc_core_rhea.example import example


def test_example() -> None:
    assert example(name="The Chromosome Project") == 22
