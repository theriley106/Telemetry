import requests
from flask import Flask, Response, request
from twilio.twiml.voice_response import VoiceResponse, Gather

app = Flask(__name__)


@app.route('/voice', methods=['GET', 'POST'])
def get_capability_token():
	resp = VoiceResponse()
	gather = Gather(input='speech', action='/completed')
	gather.say("Thanks for calling Citi Bank!  How can I help you today?")
	resp.append(gather)
	print(resp)
	return str(resp)

@app.route('/anyThingElse', methods=["GET","POST"])
def getAnother():
	resp = VoiceResponse()
	gather = Gather(input='speech', action='/completed')
	gather.say("Is there anything else I can help you with today?")
	resp.append(gather)
	print(resp)
	return str(resp)

@app.route('/completed', methods=['GET', 'POST'])
def getResponse():
	print("POSTED TO GET RESPONSE")
	resp = VoiceResponse()
	question = request.form['SpeechResult']
	a = requests.post("http://127.0.0.1:8000/interact", data={"question": request.form['SpeechResult']})
	interaction = a.json()['response']
	resp.say(interaction)
	print(resp)
	resp.redirect('/anyThingElse', method='POST')
	return str(resp)



if __name__ == "__main__":
    app.run(debug=True)
