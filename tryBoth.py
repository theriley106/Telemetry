import threading
import requests
import time

def try1():
	a = requests.post("http://127.0.0.1:8000/interact", data={"question": "what is the weather in akron ohio"})
	interaction = a.json()['response']
	print interaction

def try2():
	a = requests.post("http://127.0.0.1:8001/interact", data={"question": "what is the weather in simpsonville sc"})
	interaction = a.json()['response']
	print interaction


if __name__ == '__main__':
	thread = threading.Thread(target=try1)
	thread2 = threading.Thread(target=try2)
	raw_input("Press enter to start: ")
	thread.start()
	thread2.start()
