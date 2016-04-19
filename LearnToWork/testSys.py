import sys
import os
import signal
__author__ = 'Edward'


def main():
    try:
        os.kill(os.getpid(),signal.SIGINT)
    except KeyboardInterrupt:
        sys.exit(0)

main()