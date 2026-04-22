import threading
import time

t = threading.current_thread()
print(t.name)
print(threading.active_count())

# Only one main thread
t = threading.main_thread()
print(t.name)

print('=====Method 1:Execute function as sub thread=====')
# Thread body function
def thread_body():
    t = threading.current_thread()
    for n in range(5):
        print('The {0} time to execute thread {1}'.format(n, t.name))
        # Thread sleep 2 seconds to yield CPU
        time.sleep(2)
    print('Thread {0} execute completed!'.format(t.name))

# Invocation part
t1 = threading.Thread(target=thread_body)
t2 = threading.Thread(target=thread_body, name = 'my_thread')
t1.start()
t2.start()

# (Recommend) Method2: Inherit threading.Thread parent class
print('=====Method 2:Inherit threading class=====')
class MySmallThread(threading.Thread):
    def __init__(self, name=None):
        super().__init__(name=name)

    def run(self):
        t = threading.current_thread()
        for n in range(5):
            print('The {0} time to execute thread {1}'.format(n, t.name))
            time.sleep(2)
        print('Thread {0} execute completed!'.format(t.name))

# Invocation part
t1 = MySmallThread()
t2 = MySmallThread(name='my_thread')
t1.start()
t2.start()

# Thread join and wait
print('=====Thread join and wait demo=====')
# Shared variable
value = []
def thread_body():
    print('t1 sub thread started...')
    for n in range(2):
        print('t1 sub thread executing...')
        value.append(n)
        time.sleep(1)
    print('t1 sub thread completed.')

print('Main thread started...')
t1 = threading.Thread(target=thread_body)
t1.start()
t1.join()
print('Value: {0}'.format(value))
print('Main thread continue executing...')

# Thread scheduling and stop under control
print('=====Thread scheduling and stop demo=====')
# Thread terminate flag variable
is_running = True

def work_thread_body():
    while is_running:
        print('Work thread executing...')
        time.sleep(5)
    print('Work thread stopped.')

def control_thread_body():
    global is_running
    while is_running:
        cmd = input('Please input command:')
        if cmd == 'exit':
            is_running = False
            print('Control to stop work thread...')

# Main thread
work_thread = threading.Thread(target=work_thread_body)
work_thread.start()

control_thread = threading.Thread(target=control_thread_body())
control_thread.start()