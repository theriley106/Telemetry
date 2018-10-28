import requests
from flask import Flask, Response, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import threading
import re
from string import punctuation
import time
import os
try:
	from keys import *
except:
	account_sid = raw_input("Account SID: ")
	auth_token = raw_input("Auth Token: ")

app = Flask(__name__)
responses = []
ALLOWED_RESPONSES = ["I see you're trying to change your pin?  This is not a currently supported feature with the Citi Services API, but you can login to your account in the citi mobile application.  I've just sent you a text with a link to download the app.", "I see you're trying to close your account.  Unfortunately, that's not something I can help with, but I can forward you to someone who can.  Please stay on the line.", "I see you're trying to pay your bill.  Unfortunately, that's not something I can do over the phone, but I would recommend accessing the Citi Bank website.", "I see you're trying to change your pin?  What card do you want to use?", "I see you're trying to dispute a fraudelent transaction.  Unfortunately, that's not something I can help with, but I can forward you to someone who can.  Please stay on the line.", "I see you're trying to check your balance.  You currently have $47.82 in your account ending in 3313"]
MAX_SEQUENCE = []
def countDown():
	time.sleep(5)
	for i in range(5):
		print("Waiting {} more seconds for additional user input".format(5-i))
		time.sleep(1)

@app.route('/voice', methods=['GET', 'POST'])
def get_capability_token():
	print("New call initiated...")
	print('Saying: "Thanks for calling Citi Bank!  How can I help you today?"')
	resp = VoiceResponse()
	gather = Gather(input='speech', partial_result_callback='/partial')
	gather.say("Thanks for calling Citi Bank!  How can I help you today?")
	threading.Thread(target=countDown).start()
	resp.append(gather)
	resp.redirect('/completed', method='POST')
	print(resp)
	return str(resp)

@app.route('/anyThingElse', methods=["GET","POST"])
def getAnother():
	resp = VoiceResponse()
	threading.Thread(target=countDown).start()
	gather = Gather(input='speech', partial_result_callback='/partial')
	gather.say("Is there anything else I can help you with today?")
	resp.append(gather)
	print(resp)
	return str(resp)

@app.route('/anyThingElseNCR', methods=["GET","POST"])
def getAnotherNCR():
	resp = VoiceResponse()
	threading.Thread(target=countDown).start()
	gather = Gather(input='speech', action='/completedNCR', timeout=5)
	gather.say("Is there anything else I can help you with today?")
	resp.append(gather)
	print(resp)
	return str(resp)

def save_request(string):
	os.system("echo '{}' > temp.txt".format(string))

@app.route('/partUpdate', methods=['GET'])
def getUpdate():
	f = sorted(MAX_SEQUENCE, key=lambda k: k['num'])
	try:
		stringVal = f[-1]['speech']
	except:
		stringVal = "Error"
	return stringVal


@app.route('/partial', methods=["GET","POST"])
def partial():
	returnVal = ""
	temp_info = {"speech": request.form['UnstableSpeechResult'], "num": int(request.form['SequenceNumber'])}
	MAX_SEQUENCE.append(temp_info)
	if len(responses) == 0:
		print request.form['StableSpeechResult']
		if any(p in request.form['StableSpeechResult'] for p in punctuation):
			try:
				all_sentences = re.split('(?<=[.!?]) +',request.form['StableSpeechResult'])
				for val in all_sentences:
					if any(p in str(val) for p in punctuation) == False:
						all_sentences.remove(val)
				if len(all_sentences) > 0:
					print("FOUND EARLY FIRST PART")
					all_sentences = ["ask citi bank " + x for x in all_sentences]
					a = requests.post("http://127.0.0.1:8001/interact", data={"question": all_sentences})
					print a.json()
					for val in a.json()['response']:
						if val in ALLOWED_RESPONSES:
							responses.append(val)
							print("AYYYYOOOO FOUND EARLY")
							#resp = VoiceResponse()
							#resp.append(val)
							client = Client(account_sid, auth_token)
							call = client.calls(request.form['CallSid']).update(method='POST', url='http://92aa1051.ngrok.io/completed')
							return ""
						else:
							print("{} not in {}".format(val, ALLOWED_RESPONSES))
				else:
					print("Nah")
			except Exception as exp:
				print exp

	return returnVal


@app.route('/completed', methods=['GET', 'POST'])
def getResponse():
	while len(MAX_SEQUENCE) > 0:
		MAX_SEQUENCE.pop()
	print("ON RESPONSES: {}".format(responses))
	resp = VoiceResponse()
	if len(responses) == 0:
		print("POSTED TO GET RESPONSE")
		print("User Said: " + request.form['SpeechResult'])
		question = ""
		if 'global' not in request.form['SpeechResult'].lower():
			print('Saying: "Alexa, Ask {}" to the Alexa Emulator'.format(request.form['SpeechResult']))
			question += "ask citi bank "
		else:
			print('Saying: "Alexa, {}" to the Alexa Emulator'.format(request.form['SpeechResult']))
		if 'manager' in request.form['SpeechResult'].lower():
			question = question.replace("citi bank", "NCR store")
		question += request.form['SpeechResult'].replace("Global", "").replace("global", "")
		a = requests.post("http://127.0.0.1:8001/interact", data={"question": question})
		interaction = a.json()['response']
	else:
		interaction = responses.pop(-1)
		while len(responses) > 0:
			responses.pop(-1)
	resp.say(interaction)
	if 'unfortunately' in str(interaction).lower():
		resp.dial('864-567-4106')
	if 'unfortunately' not in str(interaction).lower():
		if ' pin' in str(interaction).lower():
			phoneNum = request.form['From']
			send_message(phoneNum)
		resp.redirect('/anyThingElse', method='POST')
	return str(resp)

@app.route('/completedNCR', methods=['GET', 'POST'])
def getResponseNCR():
	print("POSTED TO GET RESPONSE")
	print("User Said: " + request.form['SpeechResult'])
	resp = VoiceResponse()
	question = ""
	if 'global' not in request.form['SpeechResult'].lower():
		print('Saying: "Alexa, Ask NCR store {}" to the Alexa Emulator'.format(request.form['SpeechResult']))
		question += "ask ncr store "
	else:
		print('Saying: "Alexa, {}" to the Alexa Emulator'.format(request.form['SpeechResult']))
	question += request.form['SpeechResult'].replace("Global", "").replace("global", "")
	a = requests.post("http://127.0.0.1:8000/interact", data={"question": question})
	interaction = a.json()['response']
	resp.say(interaction)
	print(resp)
	if 'absolutely' in str(interaction).lower():
		resp.dial('864-567-4106')
	if 'absolutely' not in str(interaction).lower():
		resp.redirect('/anyThingElse', method='POST')
	return str(resp)

@app.route("/ncrVoice", methods=["GET", "POST"])
def getNCRResponse():
	print("New call initiated...")
	print('Saying: "Thanks for calling the HackGT Grocery Store!  Powered by NCR.  How can I help you today?"')
	resp = VoiceResponse()
	gather = Gather(input='speech', action='/completedNCR', timeout=5)
	threading.Thread(target=countDown).start()
	gather.say("Thanks for calling the HackGT Grocery Store!  Powered by NCR.  How can I help you today?")

	resp.append(gather)
	resp.redirect('/completedNCR', method='POST')
	print(resp)
	return str(resp)

def send_message(toNum):
	client = Client(account_sid, auth_token)

	message = client.messages.create(
		from_='+18886590585',
		body='Check out the Citi mobile app here: https://online.citi.com/US/JRS/portal/template.do?ID=MobileAppDownload',
		to=str(toNum)
	)

	print(message.sid)



if __name__ == "__main__":
	app.run(debug=True)
