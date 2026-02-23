from multiprocessing import Process
import os

def sing():
    print('Sing Process id:', os.getpid())
    print('Sing Parent Process id', os.getppid())
    print('Sing...')

def dance():
    print('Dance Process id:', os.getpid())
    print('Dance Parent Process id', os.getppid())
    print('Dance...')

if __name__ == '__main__':
    print('Main thread ID:', os.getpid())
    print('Main thread parent thread ID:', os.getppid())
    p1 = Process(target=sing, name='sub-process1')
    p2 = Process(target=dance, name='sub-process2')
    p1.start()
    p2.start()
    print('p1:', p1.name, p1.pid)
    print('p2:', p2.name, p2.pid)

