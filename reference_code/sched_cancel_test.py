import sched, time
s = sched.scheduler(time.time, time.sleep)
def print_time(a='default'):
	print("From print_time", time.time(), a)

def print_some_times():
	print(time.time())
	s.enter(10, 1, print_time)
	event = s.enter(5, 2, print_time, argument=('positional',))
	s.enter(5, 1, print_time, kwargs={'a': 'keyword'})

	print('event', event)
	print('event[kwargs]', event[-1])
	s.cancel(event)
	s.run()
	print(time.time())

print_some_times()
