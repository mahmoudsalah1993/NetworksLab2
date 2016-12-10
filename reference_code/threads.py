import threading

def worker(num):
    """thread worker function"""
    for i in range(100):
    	print('Worker: %s' % num)
    return

threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()