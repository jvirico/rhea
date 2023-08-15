# (c) Copyright 2023 Rico Corp. All rights reserved.

import logging

logger = logging.getLogger(__name__)


def example(name: str) -> int:
    """
    Counts and returns the number of characters of the given name
    """
    count = len(name)

    # Avoid print and instead leverage the Python logging framework!
    logger.debug(f"{name} has {count} characters")

    return count


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    example(name="Rico Corp")
