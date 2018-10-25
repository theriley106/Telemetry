import requests
from flask import Flask, Response, request
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import threading
import re
from string import punctuation
import time
try:
	from keys import *
except:
	account_sid = raw_input("Account SID: ")
	auth_token = raw_input("Auth Token: ")

app = Flask(__name__)
responses = []

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
	gather = Gather(input='speech', action='/completed', partial_result_callback='/partial')
	threading.Thread(target=countDown).start()
	gather.say("Thanks for calling Citi Bank!  How can I help you today?")
	resp.append(gather)
	resp.redirect('/completed', method='POST')
	print(resp)
	return str(resp)

@app.route('/anyThingElse', methods=["GET","POST"])
def getAnother():
	resp = VoiceResponse()
	threading.Thread(target=countDown).start()
	gather = Gather(input='speech', action='/completed', partial_result_callback='/partial')
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

@app.route('/partial', methods=["GET","POST"])
def partial():
	returnVal = ""
	if len(responses) == 0:
		print request.form
		print request.form['StableSpeechResult']
		if any(p in request.form['StableSpeechResult'] for p in punctuation):
			try:
				for val in re.split('(?<=[.!?]) +',request.form['StableSpeechResult']):
					print str(val)
					print any(p in str(val) for p in punctuation)
					if any(p in str(val) for p in punctuation) == True:
						print("TESTING")
						question = "ask citi bank " + str(val)
						a = requests.post("http://127.0.0.1:8000/interact", data={"question": question})
						interaction = a.json()['response']
						if len(interaction) > 5:
							resp = VoiceResponse()
							responses.append(interaction)
							#client = Client(account_sid, auth_token)
							#call = client.calls(request.form['CallSid']).update(method='POST', url='http://254f948e.ngrok.io/completed')
							returnVal = interaction
							break
					else:
						print("Nah")
			except Exception as exp:
				print exp

	return returnVal


@app.route('/completed', methods=['GET', 'POST'])
def getResponse():
	print request.form
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
		a = requests.post("http://127.0.0.1:8000/interact", data={"question": question})
		interaction = a.json()['response']
	else:
		interaction = responses.pop(-1)
		while len(responses) > 0:
			responses.pop(-1)
	resp.say(interaction)
	print(resp)
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
