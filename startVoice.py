# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pickle
import bs4
import copy
import json
import threading
import random
from selenium.webdriver.chrome.options import Options
SIM_URL = "https://developer.amazon.com/alexa/console/ask/test/amzn1.ask.skill.a00d7304-d36b-4ae0-8352-dd7e8fbc5d79/development/en_US/"
COOKIES = "myCookies.json"
COOKIES = json.load(open(COOKIES))
ACTIVE_SIMS = []
ALL_SIMS = []
lock = threading.Lock()
THREADS = 3
ANSWERS = {}
class simulator(object):
	"""docstring for simulator"""
	def login(self):
		self.tempLock.acquire()
		self.driver.get(SIM_URL)
		for cookie in COOKIES:
			if cookie['domain'] == '.amazon.com':
				self.driver.add_cookie(cookie)
		self.driver.get(SIM_URL)
		self.tempLock.release()

	def test_driver(self):
		self.tempLock.acquire()
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
			self.driver.save_screenshot("{}.png".format(random.randint(1, 50)))
		self.tempLock.release()
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
		self.tempLock.acquire()
		self.driver.find_element_by_css_selector("input.askt-utterance__input").clear()
		self.driver.find_element_by_css_selector("input.askt-utterance__input").send_keys(question)
		self.driver.find_element_by_css_selector("input.askt-utterance__input").send_keys(Keys.ENTER)
		page_source = self.driver.page_source
		a = 0
		while "askt-dialog__message askt-dialog__message--spinner" in str(page_source):
			print("Waiting on question: {} | Working: {} Active: {}".format(question.replace("ask ncr store", ""), len(ALL_SIMS)-len(ACTIVE_SIMS), len(ACTIVE_SIMS)))
			time.sleep(.1)
			page_source = self.driver.page_source
			a += 1
			if a > 100:
				break
		for i in range(30):
			x = self.get_response()
			if x != None:
				ANSWERS[question] = x
				self.tempLock.release()
				return
			time.sleep(.1)
		ANSWERS[question] = "I'm not really sure about that."
		self.tempLock.release()
		return

	def refresh_token(self):
		while True:
			time.sleep(random.randint(1, 10)*30)
			lock.acquire()
			self.tempLock.acquire()
			ACTIVE_SIMS.append(self.id)
			lock.release()
			print("Refreshing token")
			self.driver.get(SIM_URL)
			if self.test_driver() == False:
				self.driver.quit()
				ALL_SIMS.append(simulator())
			else:
				ACTIVE_SIMS.remove(self.id)
			self.tempLock.release()

	def __init__(self):
		self.tempLock = threading.Lock()
		options = Options()
		options.add_argument('--headless')
		options.add_argument('--disable-gpu')
		options.add_argument("--mute-audio")
		self.id = ''.join([str(random.randint(1,9)) for i in range(10)])
		self.driver = webdriver.Chrome(chrome_options=options)
		self.driver.set_window_size(1920, 1080)
		self.login()
		if self.test_driver() == False:
			raise Exception("Error on driver...")
		else:
			pass
			#threading.Thread(target=self.refresh_token).start()



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
	mySim.ask_question(question)
	ACTIVE_SIMS.remove(sim.id)

def ask_questions(listOfQuestions):
	threads = [threading.Thread(target=ask_question, args=(arg,)) for arg in listOfQuestions]
	for thread in threads:
		thread.start()
	for thread in threads:
		thread.join()
	return [{"question": question, "answer": ANSWERS[question]} for question in listOfQuestions]

from flask import Flask, Response, request, jsonify
app = Flask(__name__)

@app.route('/interact', methods=['POST'])
def main():
	start = time.time()
	questions = request.form.getlist('question')
	response = ask_questions(questions)
	end = time.time()
	return jsonify({"response": response, "time": end - start})

if __name__ == "__main__":
    setup(THREADS)
    app.run(port=8001, threaded=True)

