# Singleton
class Singleton:
    obj = None
    def __new__(cls, *args, **kwargs):
        print('new...')
        if cls.obj == None:
            cls.obj = super().__new__(cls)
        return cls.obj

    def __init__(self):
        print('Initializing...')

s1 = Singleton()
print('s1 obj:', s1)
s2 = Singleton()
print('s2 obj:', s2)
