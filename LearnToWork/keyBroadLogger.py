#!/usr/bin/python
# coding=utf-8
import threading
import time

from tkinter import *

char = u'\u0000'
mutex = threading.Lock()

__author__ = 'Edward'


def print_key(event):
    global char
    global mutex
    print "你按下了 %r" % event.char
    if mutex.acquire(1):
        char = event.char
        mutex.release()

def printChar():
    global char
    global mutex
    print "%s starts" % threading.current_thread().name
    key_dict = {u'\uf700': "上", u'\uf701': "下", u'\uf702': '左', u'\uf703': '右', u'\u0000': '空'}
    while True:
        try:
            if char:
                if mutex.acquire(1):
                    print key_dict[char]
                    char = u'\u0000'
                    mutex.release()
            time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)


def main():
    global mutex
    print "Main Thread start!"

    print_thread = threading.Thread(name="print_thread", target=printChar)

    print_thread.setDaemon(True)

    print_thread.start()

    tk = Tk()

    entry = Entry(tk)

    entry.bind('<Key>', print_key)

    entry.pack()

    try:
        tk.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)

main()
