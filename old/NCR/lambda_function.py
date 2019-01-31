import responses

def returnSpeech(speech, endSession=True):
	return {
		"version": "1.0",
		"sessionAttributes": {},
		"response": {
		"outputSpeech": {
		"type": "PlainText",
		"text": speech
			},
			"shouldEndSession": endSession
		  }
	}

def on_intent(intent_request, session):
	speech = ""
	item = ""
	print intent_request["intent"]["slots"]
	try:
		item = intent_request["intent"]["slots"]['food']['value']
	except:
		item = intent_request["intent"]["slots"]['drink']['value']
	print item
	# This means the person asked the skill to do an action
	intent_name = intent_request["intent"]["name"]
	# This is the name of the intent (Defined in the Alexa Skill Kit)
	if intent_name == 'checkInventory':
		speech = responses.full_response(item)
	return returnSpeech(speech)



def lambda_handler(event, context):
	if event["request"]["type"] == "LaunchRequest":
		speech = "ayyo"
	elif event["request"]["type"] == "IntentRequest":
		return on_intent(event["request"], event["session"])
	return returnSpeech(speech)

if __name__ == '__main__':
	pass
