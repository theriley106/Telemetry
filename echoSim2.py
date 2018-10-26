from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pickle
import bs4
import copy
import json
import threading
import random
SIM_URL = "https://developer.amazon.com/alexa/console/ask/test/amzn1.ask.skill.a00d7304-d36b-4ae0-8352-dd7e8fbc5d79/development/en_US/"
COOKIES = "myCookies.json"
COOKIES = json.load(open(COOKIES))
ACTIVE_SIMS = []
ALL_SIMS = []
lock = threading.Lock()
class simulator(object):
	"""docstring for simulator"""
	def login(self):
		self.driver.get(SIM_URL)
		for cookie in COOKIES:
			if cookie['domain'] == '.amazon.com':
				self.driver.add_cookie(cookie)
		self.driver.get(SIM_URL)

	def test_driver(self):
		count = 0
		while True:
			try:
				self.driver.find_element_by_css_selector("input.askt-utterance__input").clear()
				self.driver.find_element_by_css_selector("input.askt-utterance__input").send_keys("alexa what is the weather")
				self.driver.find_element_by_css_selector("input.askt-utterance__input").send_keys(Keys.ENTER)
				break
			except:
				pass
			if count > 8:
				break
			count += 1
			time.sleep(3)
		if count > 8:
			return False
		return True

	def get_response(self):
		try:
			page = bs4.BeautifulSoup(self.driver.page_source, 'lxml')
			return page.select(".askt-dialog__message--active-response")[0].getText()
		except:
			return None

	def ask_question(self, question):
		self.driver.find_element_by_css_selector("input.askt-utterance__input").clear()
		self.driver.find_element_by_css_selector("input.askt-utterance__input").send_keys(question)
		self.driver.find_element_by_css_selector("input.askt-utterance__input").send_keys(Keys.ENTER)
		time.sleep(.3)
		for i in range(30):
			x = self.get_response()
			if x != None:
				return x
			time.sleep(.1)
		return "I'm not really sure about that."

	def __init__(self):
		self.id = ''.join([str(random.randint(1,9)) for i in range(10)])
		self.driver = webdriver.Firefox()
		self.login()
		if self.test_driver() == False:
			raise Exception("Error on driver...")

'''
from flask import Flask, Response, request, jsonify
app = Flask(__name__)

@app.route('/interact', methods=['POST'])
def main():
	question = request.form['question']
	response = interact(question)
	return jsonify({"response": response})
'''
def create_driver():
	a = simulator()
	ALL_SIMS.append(a)

def setup(threadCount=10):
	thread = [threading.Thread(target=create_driver) for i in range(threadCount)]
	for t in thread:
		t.start()
	for t in thread:
		t.join()

def ask_question(question):
	mySim = None
	while mySim == None:
		lock.acquire()
		for sim in ALL_SIMS:
			if sim.id not in ACTIVE_SIMS:
				ACTIVE_SIMS.append(sim.id)
				mySim = sim
				break
		lock.release()
		time.sleep(1)
	print mySim.ask_question(question)
	ACTIVE_SIMS.remove(sim.id)

def ask_questions(listOfQuestions):
	threads = [threading.Thread(target=ask_question, args=(arg,)) for arg in listOfQuestions]
	for thread in threads:
		thread.start()
	for thread in threads:
		thread.join()

if __name__ == "__main__":
    #app.run(port=8001)
    setup(5)
    questions = []
    for i in range(10):
    	questions.append('what is {} times {}'.format(random.randint(1,100), random.randint(1,100)))
    ask_questions(questions)
    for sim in ALL_SIMS:
    	sim.driver.close()

