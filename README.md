# SmartCustomerService
Implementing Amazon's Alexa into a customer service platform

## How to use

python resetCookie.py
python startVoice.py
gunicorn -k flask_sockets.worker -b 0.0.0.0:5000 getCall:app
./ngrok http 5000
Go to Twilio and change endpoint


<p align="center">
<img src ="static/workflow.png">
</p>


### Stanford Skill Flow

- When are undergraduate admission decisions released

- When do you close today

- What is the phone number for the {office name}
