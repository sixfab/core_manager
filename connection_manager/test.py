from threading import Thread, Lock
import time

lock = Lock()

def worker1():
    while(True):

        with lock:
            print("worker 1")
        time.sleep(4)

def worker2():
    while(True):
        with lock:
            print("worker 2")
        time.sleep(2)

def main():
    Thread(target=worker1).start()
    Thread(target=worker2).start()

main()
