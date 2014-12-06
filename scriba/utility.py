"""
"""

import collections

class Stack(collections.deque):
    """Stack from deque.

    Cosmetic only. If I've to use a stack, it must have ``push`` and ``pop``
    methods. That's all my problem.
    """
    push = collections.deque.append
