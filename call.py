#!/usr/bin/env python

from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(

    os.getenv("TWILIO_ACCOUNT_SID"),

    os.getenv("TWILIO_AUTH_TOKEN")
)

call = client.calls.create(

    to="+91XXXXXXXXXX",

    from_=os.getenv("TWILIO_PHONE_NUMBER"),

    url="https://xxxx.ngrok-free.app/voice"
)

print(call.sid)