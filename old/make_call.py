import os
from twilio.rest import Client
try:
	from key import *
except:
	account_sid = raw_input("SID: ")
	auth_token = raw_input("Auth Token: ")

client = Client(account_sid, auth_token)

call = client.calls.create(
	to="+18645674106", from_="+18644028960", url="http://demo.twilio.com/docs/voice.xml")


print(call.sid)
