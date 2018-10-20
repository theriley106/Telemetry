import random

def start_response():
	# This is the speech that is said when the skill starts for the first time
	return "Hello World!"

def change_pin():
	# This is the speech that is said when the person asks what day the event starts
	return "I see you're trying to change your pin?  What card do you want to use?"

def dispute_transaction():
	return "I see you're trying to dispute a fraudelent transaction.  Unfortunately, that's not something I can help with, but I can forward you to someone who can.  Please stay on the line."

def check_balance():
	return "I see you're trying to check your balance.  You currently have $47.82 in your account ending in 3313"

def pay_bill():
	return "I see you're trying to pay your bill.  Unfortunately, that's not something I can do over the phone, but I would recommend accessing the Citi Bank website."

def close_account():
	return "I see you're trying to close your account.  Unfortunately, that's not something I can help with, but I can forward you to someone who can.  Please stay on the line."
