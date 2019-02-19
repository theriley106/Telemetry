import threading
import requests
import time
import random

TOTAL_AMOUNT = 20

def genQuestion():
	return "what is {} times {}".format(random.randint(1,1000), random.randint(1, 1000))

def try1():
	a = requests.post("http://127.0.0.1:8001/interact", data={"question": [genQuestion() for i in range(TOTAL_AMOUNT)]})
	interaction = a.json()['response']
	print interaction

def try2():
	a = requests.post("http://127.0.0.1:8001/interact", data={"question": [genQuestion() for i in range(TOTAL_AMOUNT)]})
	interaction = a.json()
	print interaction


if __name__ == '__main__':
	thread = threading.Thread(target=try2)
	thread2 = threading.Thread(target=try2)
	raw_input("Press enter to start: ")
	thread.start()
	thread2.start()
