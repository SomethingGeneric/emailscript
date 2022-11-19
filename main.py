import os, shutil
from random import randint

from domail import cope

if __name__ == "__main__":
    if os.path.exists("program.log"):
        shutil.move("program.log", "program.log." + str(randint(1, 10000)))

    e = cope()
    e.go()