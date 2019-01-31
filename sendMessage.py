# Download the helper library from https://www.twilio.com/docs/python/install
from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
account_sid = 'AC59aa83ab44ffade052dd2c4693a344df'
auth_token = 'ce8dd48f14ce8651a1dfc3595d052ae7'
client = Client(account_sid, auth_token)

message = client.messages.create(
                              from_='+18886590585',
                              body='Check out the Citi mobile app here: https://online.citi.com/US/JRS/portal/template.do?ID=MobileAppDownload',
                              to='+18645674106'
                          )

print(message.sid)
