#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  pylint: disable=W0612
"""
    pathic.py - Build keys, a hat size and borders.

    by: nullpass, 2012

    Example:

$ ./pathic.py xxx
pathic - xxx

4 @ [1, 2]
h57GfUVnEe3pRoVq
8yw9Wqb4FsvchPz4
8tkLCmLm8Ze52djQ

"""
___version___ = "3.0.0"
import random
import time
import datetime
from sys import argv

TEMPLATE = """
pathic - {base}

{hat_size}@{border}
{key1}
{key2}
{key3}

"""

def planter():
    """
    Create an integer for random.seed to use without using any random methods.
    %f 	Microsecond as a decimal number [0,999999], zero-padded on the left
    """

    seed = int(time.time()) * (int(datetime.datetime.now().strftime("%f")) + 29)
    seed = seed - int(datetime.datetime.now().strftime("%f")) + 113
    seed = seed + 229
    seed = ((seed * (int(str(seed)[-1]) + 349)) * seed) - (seed + seed)
    return int(seed)

def grow():
    """
    Build a key, return as string.
    """
    #
    # Define root list of friendly strings
    root = list("abcdefghijkmopqrstuvwxyzQWERTYUPLKJHGFDAZXCVN92345678")
    #
    # Create a random number of times to shuffle the list
    for i in range(random.randint(29, 1129)):
        #
        # Shuffle the list in place.
        random.shuffle(root)
    #
    # Build a list until it's 16 chr long.
    key_list = []
    while len(key_list) < 16:
        #
        # You have a 33% chance of choosing a random char to append
        # at this point in this loop.
        if random.randint(1, 3) == 3:
            #
            # If lucky, append random character to list.
            key_list.append(random.choice(root))
    #
    # Create a random number of times to shuffle the list
    for i in range(random.randint(1151, 3329)):
        #
        # Shuffle the list in place.
        random.shuffle(key_list)
    #
    # Convert list to string by character
    retval = ''.join(key_list)
    return retval

def border():
    """
    Return a random border from a list of valid borders as str
    """
    return random.choice([[1, 2], [1, 3], [2, 3]])

def hat():
    """
    Return a randomly chosen hat size as str, must be even number.
    """
    return random.randrange(2, 14, 2)

def main():
    """
    main
    """
    base = ""
    if argv[1:]:
        base = argv[1]
    random.seed(planter())
    print(TEMPLATE.format(
        base=base,
        hat_size=hat(),
        border=border(),
        key1=grow(),
        key2=grow(),
        key3=grow(),
        ))
    return

if __name__ == '__main__':
    main()
