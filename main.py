"""Goofy ass docstring to make pylint shut up"""

import os
import shutil
from random import randint

from domail import Cope

if __name__ == "__main__":
    if os.path.exists("program.log"):
        shutil.move("program.log", "program.log." + str(randint(1, 10000)))

    e = Cope()
    e.process()
