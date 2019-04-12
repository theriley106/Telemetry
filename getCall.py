import requests
from flask import Flask, Response, request, render_template, jsonify
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import threading
import re
from string import punctuation
import time
import random
import json
import os
from flask_sockets import Sockets
import webbrowser
import datetime
try:
	from keys import *
except:
	account_sid = raw_input("Account SID: ")
	auth_token = raw_input("Auth Token: ")

app = Flask(__name__)
responses = []
ALLOWED_RESPONSES = ["I see you're trying to change your pin?  This is not a currently supported feature with the Citi Services API, but you can login to your account in the citi mobile application.  I've just sent you a text with a link to download the app.", "I see you're trying to close your account.  Unfortunately, that's not something I can help with, but I can forward you to someone who can.  Please stay on the line.", "I see you're trying to pay your bill.  Unfortunately, that's not something I can do over the phone, but I would recommend accessing the Citi Bank website.", "I see you're trying to change your pin?  What card do you want to use?", "I see you're trying to dispute a fraudelent transaction.  Unfortunately, that's not something I can help with, but I can forward you to someone who can.  Please stay on the line.", "I see you're trying to check your balance.  You currently have $47.82 in your account ending in 3313"]
MAX_SEQUENCE = []
DEFAULT_SEQUENCE = {'callTime': '--', 'FromZip': '--', 'From': '--', 'FromCity': '--', 'ApiVersion': '--', 'To': '--', 'ToCity': '--', 'CalledState': '--', 'FromState': '--', 'Direction': '--', 'SequenceNumber': '--', 'CallStatus': '--', 'ToZip': '--', 'UnstableSpeechResult': '--', 'CallerCity': '--', 'FromCountry': '--', 'Language': '--', 'CalledCity': '--', 'CalledCountry': '--', 'Caller': '--', 'CallSid': '--', 'AccountSid': '--', 'Called': '--', 'CallerCountry': '--', 'CalledZip': '--', 'CallerZip': '--', 'StableSpeechResult': '--', 'Stability': '--', 'CallerState': '--', 'ToCountry': '--', 'ToState': '--'}
ALL_INFO = [DEFAULT_SEQUENCE]
SPEECHES = []
sockets = Sockets(app)
CALL_INFO = {}
CALL_LOGS = {}

URL = "https://maps.googleapis.com/maps/api/geocode/json?address={0}&key=AIzaSyDBZre20-q9hSY0BFXTqmiZr5-orJSuwr0"
def get_address(addressString):
	a = requests.get(URL.format(addressString.replace(" ", "+"))).json()
	x = a["results"][0]["geometry"]["location"]
	return (x['lat'], x['lng'])

print("STARTING WITH WEB SOCKETS")

def dict_to_array(dictValue):
	a = []
	found = False
	for key, value in dictValue.iteritems():
		if key == 'callTime':
			found = True
		a.append([key, value])
	if found == False:
		a.append(['callTime', CALL_INFO[tmp['CallSid']]])
	return a

def addNewInfo(value=None):
	if value == None:
		#return "AYYO"
		try:
			g = dict_to_array(ALL_INFO[-1].to_dict())
			#print g
			return json.dumps(g)
		except:
			g = dict_to_array(DEFAULT_SEQUENCE)
			#print g
			return json.dumps(g)
	else:
		#print(value)
		for val in ALL_INFO:
			ALL_INFO.remove(val)
		ALL_INFO.append(value)

@sockets.route('/echo')
def echo_socket(ws):
	while True:
		#message = ws.receive()
		ws.send(str(addNewInfo()))
		print("WEBSOCKET: {}".format(str(addNewInfo())))
		time.sleep(.1)

@app.route('/echo_test', methods=['GET'])
def echo_test():
	return render_template('example.html')


def countDown():
	time.sleep(5)
	for i in range(5):
		#print("Waiting {} more seconds for additional user input".format(5-i))
		time.sleep(1)

@app.route('/', methods=['GET'])
def indexPage():
	return render_template("index.html")

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
	SPEECHES.append("Is there anything else I can help you with today?")
	#CALL_LOGS[ALL_INFO[-1]['CallSid']].append("Is there anything else I can help you with today?")
	resp = VoiceResponse()
	resp.redirect('/ncrVoice', method="POST")
	return str(resp)

@app.route('/anyThingElseUber', methods=["GET","POST"])
def getAnotherUber():
	resp = VoiceResponse()
	gather = Gather(input='speech', action='/completedUber', partial_result_callback='/partialUber', timeout=3)
	threading.Thread(target=countDown).start()
	#speechVal = SPEECHES[-1]
	if len(SPEECHES) == 0:
		# This means it's the start
		speechVal = ""
	gather.say(speechVal)
	resp.append(gather)
	#CALL_LOGS[ALL_INFO[-1]['CallSid']].append(speechVal)
	resp.redirect('/completedUber', method='POST')
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
	addNewInfo(request.form)
	print("UNSTABLE: {}".format(request.form['UnstableSpeechResult']))
	print("STABLE: {}".format(request.form['StableSpeechResult']))
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
					all_sentences = ["ask NCR " + x for x in all_sentences]
					print(all_sentences)
			except Exception as exp:
				print exp
	return returnVal

@app.route('/partialUber', methods=["GET", "POST"])
def partialUber():
	print request.form['UnstableSpeechResult']

@app.route('/partialBackup', methods=["GET","POST"])
def partialBackup():
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
							call = client.calls(request.form['CallSid']).update(method='POST', url='http://telemetry.ngrok.io/completed')
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
	print request.form
	print("POSTED TO GET RESPONSE")
	print("User Said: " + request.form['SpeechResult'])
	try:
		if CALL_LOGS[ALL_INFO[-1]['CallSid']] != request.form['SpeechResult']:
			CALL_LOGS[ALL_INFO[-1]['CallSid']].append(request.form['SpeechResult'])
	except:
		pass
	resp = VoiceResponse()
	print("DONE WITH RESP")
	question = ""
	if 'global' not in request.form['SpeechResult'].lower():
		print('Saying: "Alexa, Ask NCR store {}" to the Alexa Emulator'.format(request.form['SpeechResult']))
		question += "ask ncr store "
	else:
		print('Saying: "Alexa, {}" to the Alexa Emulator'.format(request.form['SpeechResult']))
	question += request.form['SpeechResult'].replace("Global", "").replace("global", "")
	a = requests.post("http://127.0.0.1:8001/interact", data={"question": question})
	print("DONE WITH A: {}".format(a))
	interaction = a.json()['response']
	resp.say(interaction[0]['answer'])
	CALL_LOGS[ALL_INFO[-1]['CallSid']].append(interaction[0]['answer'])
	print(resp)
	if 'absolutely' in str(interaction).lower():
		resp.dial('864-567-4106')
	if 'absolutely' not in str(interaction).lower():
		print("REDIRECTING TO ANYTHIGN ELSE")
		resp.redirect('/anyThingElse', method='POST')
	return str(resp)

@app.route('/completedUber', methods=['GET', 'POST'])
def getResponseUber():
	print request.form
	#print("POSTED TO GET RESPONSE")
	print("User Said: " + request.form['SpeechResult'])
	try:
		if CALL_LOGS[ALL_INFO[-1]['CallSid']] != request.form['SpeechResult']:
			CALL_LOGS[ALL_INFO[-1]['CallSid']].append(request.form['SpeechResult'])
	except:
		pass
	resp = VoiceResponse()
	#print("DONE WITH RESP")
	question = ""
	print('Saying: "Alexa, book an uber {}" to the Alexa Emulator'.format(request.form['SpeechResult']))
	question += "ask book an uber " + request.form['SpeechResult'].replace("Global", "").replace("global", "")
	question = ' '.join(re.findall("\w+", str(question)))
	a = requests.post("http://127.0.0.1:8001/interact", data={"question": question})
	print("D8ONE WITH A: {}".format(a))
	interaction = a.json()['response']
	print(interaction)
	print("ask book an uber " + question + "!!!!!!!!!")
	resp.say(interaction[0]['answer'])
	CALL_LOGS[ALL_INFO[-1]['CallSid']].append(interaction[0]['answer'])
	print CALL_LOGS[ALL_INFO[-1]['CallSid']]
	if 'Your driver' in interaction[0]['answer']:
		ite = str(CALL_LOGS[ALL_INFO[-1]['CallSid']][-3]).partition("from ")[2].partition(", is that")[0].replace("bring you to ", "").replace(", USA", "")
		fromVal, toVal = ite.split(" to ")
		lat1, lng1 = get_address(fromVal)
		lat2, lng2 = get_address(toVal)
		print("http://127.0.0.1:8011/options?lat1={}&lng1={}&lat2={}&lng2={}".format(lat1, lng1, lat2, lng2))
		res = requests.get("http://127.0.0.1:8011/options?lat1={}&lng1={}&lat2={}&lng2={}".format(lat1, lng1, lat2, lng2))
		g = res.json()['prices'][0]
		price = g['low_estimate'] + round(random.uniform(1.1, 1.9),2)
		newTimeVal = datetime.datetime.now() + datetime.timedelta(minutes = random.randint(1,10)+(g['duration']/60))
		newTimeVal = newTimeVal.strftime('%I:%M %p')
		send_message(request.form.get("From"), """Thank you for using RideCaring!  Your {} mile trip from {} will cost ${}.  Your {} driver will arrive by {}.""".format(g['distance'], ite, price, g['display_name'], newTimeVal))
		send_message(request.form.get("From"), "To cancel this trip respond with the word: 'cancel' or call us at (888) 250-4319")
	print(resp)
	if 'absolutely' in str(interaction).lower():
		resp.dial('864-567-4106')
	if 'absolutely' not in str(interaction).lower():
		#print("HOPEFULLY THIS IS STILL WORKING")
		resp.redirect('/anyThingElseUber', method='POST')
	return str(resp)

@app.route("/ncrVoice", methods=["GET", "POST"])
def getNCRResponse():
	print("New call initiated...")
	print('Saying: "Thanks for calling the Stanford University Innovation Store!  Powered by Telemetry.  How can I help you today?"')
	if ALL_INFO[-1] == DEFAULT_SEQUENCE:
		tmp = ALL_INFO[-1]
		x = request.form.to_dict()
		for key, val in tmp.iteritems():
			if key in x:
				tmp[key] = x[key]
			else:
				tmp[key] = ""
		try:
			if tmp['CallSid'] not in CALL_LOGS:
				CALL_LOGS[tmp['CallSid']] = []
			if tmp['CallSid'] not in CALL_INFO:
				CALL_INFO[tmp['CallSid']] = int(time.time())
			tmp['callTime'] = CALL_INFO[tmp['CallSid']]
		except Exception as exp:
			tmp['callTime'] = str(exp)
		addNewInfo(tmp)
	resp = VoiceResponse()
	gather = Gather(input='speech', action='/completedUber', partial_result_callback='/partial', timeout=5)
	threading.Thread(target=countDown).start()
	#speechVal = SPEECHES[-1]
	if len(SPEECHES) == 0:
		# This means it's the start
		speechVal = "Thanks for calling the Stanford University Innovation Store!  Powered by Telemetry.  How can I help you today?"
	else:
		speechVal = SPEECHES.pop(-1)
	CALL_LOGS[ALL_INFO[-1]['CallSid']].append(speechVal)
	gather.say(speechVal)
	resp.append(gather)
	#CALL_LOGS[ALL_INFO[-1]['CallSid']].append(speechVal)
	resp.redirect('/completedNCR', method='POST')
	print(resp)
	print(CALL_LOGS[ALL_INFO[-1]['CallSid']])
	return str(resp)

@app.route("/uberVoice", methods=["GET", "POST"])
def getUberResponse():
	print("New call initiated...")
	print('Saying: "Thank you for calling RideCaring!  The first ride sharing platform that does not rely on internet connectivity.  Where is your pickup location?"')
	requests.post("http://127.0.0.1:8001/interact", data={"question": "open book an uber"})
	print("Opening session in the 'Ride Caring' Alexa Skill")
	if ALL_INFO[-1] == DEFAULT_SEQUENCE:
		tmp = ALL_INFO[-1]
		x = request.form.to_dict()
		for key, val in tmp.iteritems():
			if key in x:
				tmp[key] = x[key]
			else:
				tmp[key] = ""
		try:
			if tmp['CallSid'] not in CALL_LOGS:
				CALL_LOGS[tmp['CallSid']] = []
			if tmp['CallSid'] not in CALL_INFO:
				CALL_INFO[tmp['CallSid']] = int(time.time())
			tmp['callTime'] = CALL_INFO[tmp['CallSid']]
		except Exception as exp:
			tmp['callTime'] = str(exp)
		addNewInfo(tmp)
	resp = VoiceResponse()
	gather = Gather(input='speech', action='/completedUber', partial_result_callback='/partialUber', timeout=3)
	#print("SECOND PART")
	threading.Thread(target=countDown).start()
	#speechVal = SPEECHES[-1]
	if len(SPEECHES) == 0:
		# This means it's the start
		speechVal = "Thank you for calling RideCaring!  The first ride sharing platform that does not rely on internet connectivity.  Where is your pickup location?"
	else:
		speechVal = SPEECHES.pop(-1)
	CALL_LOGS[ALL_INFO[-1]['CallSid']].append(speechVal)
	gather.say(speechVal)
	resp.append(gather)
	#CALL_LOGS[ALL_INFO[-1]['CallSid']].append(speechVal)
	resp.redirect('/completedUber', method='POST')
	return str(resp)

def send_message(toNum, message="TEST"):
	client = Client(account_sid, auth_token)

	message = client.messages.create(
		from_='+18882504319',
		body=message,
		to=str(toNum)
	)

	print(message.sid)



if __name__ == "__main__":
	message = """Thank you for using RideCaring!  Your trip from {} {} to {} {} will cost {}.  Your driver, {} will arrive by {}"""
	send_message("+18645674106")
	app.run(debug=True)
