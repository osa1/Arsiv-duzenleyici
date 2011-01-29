import threading
import time

def hello():
    print "hello, world"

t = threading.Timer(2.0, hello)
t.start()

while True:
    print "test"
    t.cancel()
    t = threading.Timer(2.0, hello)
    time.sleep(1)
