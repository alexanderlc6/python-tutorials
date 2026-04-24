import threading


class Singleton:
    instance = None
    lock = threading.RLock()

    def __init__(self, name):
        self.name = name

    def __new__(cls, *args, **kwargs):
        if cls.instance:
            return cls.instance

        with cls.lock:
            if cls.instance:
                return cls.instance
            cls.instance = object.__new__(cls)
            return cls.instance

def task():
    obj = Singleton('x')
    print(obj)

for i in range(10):
    t = threading.Thread(target=task)
    t.start()