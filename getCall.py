import requests
from flask import Flask, Response, request
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)


@app.route('/voice', methods=['GET', 'POST'])
def get_capability_token():
	resp = VoiceResponse()
	gather = Gather(input='speech', action='/completed', timeout=3)
	gather.say("Thanks for calling Citi Bank!  How can I help you today?")
	resp.append(gather)
	resp.redirect('/completed', method='POST')
	print(resp)
	return str(resp)

@app.route('/anyThingElse', methods=["GET","POST"])
def getAnother():
	resp = VoiceResponse()
	gather = Gather(input='speech', action='/completed', timeout=3)
	gather.say("Is there anything else I can help you with today?")
	resp.append(gather)
	print(resp)
	return str(resp)

@app.route('/completed', methods=['GET', 'POST'])
def getResponse():
	print("POSTED TO GET RESPONSE")
	print(request.form['SpeechResult'])
	resp = VoiceResponse()
	question = ""
	if 'global' not in request.form['SpeechResult'].lower():
		question += "ask citi bank "
	question += request.form['SpeechResult'].replace("Global", "").replace("global", "")
	a = requests.post("http://127.0.0.1:8000/interact", data={"question": question})
	interaction = a.json()['response']
	resp.say(interaction)
	print(resp)
	if 'unfortunately' in str(interaction).lower():
		resp.dial('864-567-4106')
	if 'unfortunately' not in str(interaction).lower():
		resp.redirect('/anyThingElse', method='POST')
	return str(resp)



if __name__ == "__main__":
    app.run(debug=True)
