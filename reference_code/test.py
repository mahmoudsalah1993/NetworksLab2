import sched, time

def print_time(a='default'):
	print("From print_time", time.time(), a)

s = sched.scheduler(time.time, time.sleep)
s.enter(10, 1, print_time)
s.enter(5, 2, print_time, argument=('positional',))
s.enter(5, 1, print_time, kwargs={'a': 'keyword'})
ret = s.run(False)

if len(s.queue) > 0:
	print('still some events in here')
	print('returned', ret)
	ret = s.run(False)
	print('returned', ret)
	ret = s.run(False)
	print('returned', ret)
	ret = s.run(False)
	print('returned', ret)

print('end scheduler routine')