from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pickle
import bs4
try:
	from urls import *
	from keys import *
except:
	alexa_url = raw_input("URL: ")
	username = raw_input("Username: ")
	password = raw_input("Password: ")

driver = webdriver.Firefox()
driver.get("https://www.amazon.com/ap/signin?clientContext=130-4314282-6632427&openid.return_to=https%3A%2F%2Fdeveloper.amazon.com%2F&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=mas_dev_portal&openid.mode=checkid_setup&marketPlaceId=ATVPDKIKX0DER&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&pageId=amzn_developer_portal&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&siteState=clientContext%3D136-5613104-2452306%2CsourceUrl%3Dhttps%253A%252F%252Fdeveloper.amazon.com%252F%2Csignature%3Dnull&language=en_US")
driver.find_element_by_id("ap_email").clear()
driver.find_element_by_id("ap_email").send_keys(username)
driver.find_element_by_id("ap_password").clear()
driver.find_element_by_id("ap_password").send_keys(password)
driver.find_element_by_id("signInSubmit").click()
raw_input("")
driver.get("https://developer.amazon.com/alexa/console/ask/test/amzn1.ask.skill.a00d7304-d36b-4ae0-8352-dd7e8fbc5d79/development/en_US/")
try:
	driver.find_element_by_id("ap_password").clear()
	driver.find_element_by_id("ap_password").send_keys(password)
	driver.find_element_by_id("ap_password").send_keys(Keys.ENTER)
except:
	pass
raw_input("Press Enter When logged in")
#driver.get("https://www.amazon.com/ap/signin?clientContext=130-4314282-6632427&openid.return_to=https%3A%2F%2Fdeveloper.amazon.com%2F&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=mas_dev_portal&openid.mode=checkid_setup&marketPlaceId=ATVPDKIKX0DER&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&pageId=amzn_developer_portal&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&siteState=clientContext%3D136-5613104-2452306%2CsourceUrl%3Dhttps%253A%252F%252Fdeveloper.amazon.com%252F%2Csignature%3Dnull&language=en_US")
'''driver.get("https://developer.amazon.com/alexa/console/ask/test/amzn1.ask.skill.14b0df53-f2d0-4031-b53d-f2a6bf9e23b1/development/en_US/?captcha_verified=1&")
for cookie in pickle.load(open("MyCookies.pkl", "rb")):
	driver.add_cookie(cookie)
driver.get("https://developer.amazon.com/alexa/console/ask/test/amzn1.ask.skill.14b0df53-f2d0-4031-b53d-f2a6bf9e23b1/development/en_US/?captcha_verified=1&")'''
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

