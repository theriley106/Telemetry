from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pickle
import bs4
import copy
import json
try:
	from urls import *
	from keys import *
except:
	alexa_url = raw_input("URL: ")
	username = raw_input("Username: ")
	password = raw_input("Password: ")

driver = webdriver.Firefox()
driver.get("https://developer.amazon.com/alexa/console/ask/test/amzn1.ask.skill.a00d7304-d36b-4ae0-8352-dd7e8fbc5d79/development/en_US/")
a = json.load(open("myCookies.json"))
for cookie in a:
	if cookie['domain'] == '.amazon.com':
		driver.add_cookie(cookie)
driver.get("https://developer.amazon.com/alexa/console/ask/test/amzn1.ask.skill.a00d7304-d36b-4ae0-8352-dd7e8fbc5d79/development/en_US/")
count = 0
while True:
	try:
		driver.find_element_by_css_selector("input.askt-utterance__input").clear()
		driver.find_element_by_css_selector("input.askt-utterance__input").send_keys("alexa what is the weather")
		driver.find_element_by_css_selector("input.askt-utterance__input").send_keys(Keys.ENTER)
		break
	except:
		pass
	if count > 8:
		break
	count += 1
	time.sleep(3)
#a = copy.copy(driver)
#a.get("https://developer.amazon.com/alexa/console/ask/test/amzn1.ask.skill.a00d7304-d36b-4ae0-8352-dd7e8fbc5d79/development/en_US/")
#pickle.dump(driver.get_cookies() , open("MyCookies.pkl","wb"))

def get_response(page_source):
	page = bs4.BeautifulSoup(page_source, 'lxml')
	return page.select(".askt-dialog__message--active-response")[0].getText()

def ask_question(string, drive):
	drive.find_element_by_css_selector("input.askt-utterance__input").clear()
	drive.find_element_by_css_selector("input.askt-utterance__input").send_keys(string)
	drive.find_element_by_css_selector("input.askt-utterance__input").send_keys(Keys.ENTER)

def interact(q):
	try:
		ask_question(q, driver)
		time.sleep(.3)
		for i in range(30):
			try:
				x = get_response(driver.page_source)
				return x
			except:
				time.sleep(.1)
		return "I'm not really sure about that"
	except:
		return "I'm not really sure about that"


from flask import Flask, Response, request, jsonify
app = Flask(__name__)

@app.route('/interact', methods=['POST'])
def main():
	question = request.form['question']
	response = interact(question)
	return jsonify({"response": response})

if __name__ == "__main__":
    app.run(port=8001)

