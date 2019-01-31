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
	# This means the person asked the skill to do an action
	intent_name = intent_request["intent"]["name"]
	# This is the name of the intent (Defined in the Alexa Skill Kit)
	if intent_name == 'changePin':
		# whatDay intent
		return responses.change_pin()
		# Return the response for what day
	if intent_name == 'disputeTransaction':
		# whatDay intent
		return responses.dispute_transaction()
		# Return the response for what day
	if intent_name == 'checkBalance':
		# whatDay intent
		return responses.check_balance()
		# Return the response for what day
	if intent_name == 'payBill':
		# whatDay intent
		return responses.pay_bill()
		# Return the response for what day
	if intent_name == 'closeAccount':
		return responses.close_account()



def lambda_handler(event, context):
	if event["request"]["type"] == "LaunchRequest":
		speech = responses.start_response()
	elif event["request"]["type"] == "IntentRequest":
		speech = on_intent(event["request"], event["session"])
	return returnSpeech(speech)

if __name__ == '__main__':
	pass
