 # threading test to alter one global list 

import numpy as np
from collections import deque
import threading 
import time 

def populate(queue):

	global counter 
	while counter < 100: 
		queue.append(counter)
		counter += 1
		time.sleep(.002)

	print('finished populating')

def remove_oldest(queue):
	
	removed = []
	viewed = []
	global counter 

	# make sure it doesn't start before counter starts going
	while counter > 0:
		
		if len(queue) > 0: 
			# make sure removing is slower 
			time.sleep(0.01)
			viewed.append(queue[0])
			popped = queue.popleft()
			removed.append(popped)

		if len(queue) == 0 and counter == 100:
			break

	print('removed from left: ',removed)
	print('viewed from left: ',viewed)

def print_latest_slowly(queue):

	global counter 

	while counter < 100:
		# look at the latest member of the queue
		# just a view, no popping 
		if len(queue) > 1:
			print('latest: ',queue[-1])
		time.sleep(.02)



def main():

	global counter 

	queue = deque([])

	# zeros_thread =threading.Thread(target=add_a_zero, args=(queue,))
	# zeros_thread.start()

	# ones_thread =threading.Thread(target=add_a_one, args=(queue,))
	# ones_thread.start()	

	counter_thread = threading.Thread(target=populate, args=(queue,))
	counter_thread.start()

	removing_thread = threading.Thread(target=remove_oldest, args=(queue,))
	removing_thread.start()

	print_thread = threading.Thread(target=print_latest_slowly, args=(queue,))
	print_thread.start()
	print_thread.join()

	counter_thread.join()
	removing_thread.join()

	print('finished queue: ',queue)
	print('finished length: ',len(queue))

	del queue

if __name__ == '__main__':

	counter = 0

	main()

