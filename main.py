#!/usr/bin/env python
# file: main.py

from fastapi import FastAPI, Request
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client

import os
import csv
import datetime

from dotenv import load_dotenv
from ai_agent import generate_reply

load_dotenv()

app = FastAPI()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")


def save_log(user, ai):

    with open("call_logs.txt", "a") as f:

        f.write(f"""
{datetime.datetime.now()}

User: {user}

AI: {ai}

----------------
""")


def save_lead(phone, interest):

    file_exists = os.path.isfile("leads.csv")

    with open("leads.csv", "a", newline="") as f:

        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["phone", "interested", "date"])

        writer.writerow([
            phone,
            interest,
            datetime.datetime.now()
        ])


@app.get("/")
def home():
    return {"status": "AI voice agent running"}


@app.post("/voice")
async def voice(request: Request):

    form = await request.form()

    user_input = form.get("SpeechResult")

    phone = form.get("From")

    print("USER:", user_input)

    if not user_input:

        ai_text = """
Hello, this is an AI assistant helping businesses automate customer support,
WhatsApp replies and appointment booking.

What type of business do you run?
"""

        interested = False

    else:

        ai_text, interested = generate_reply(user_input)

    print("AI:", ai_text)

    save_log(user_input, ai_text)

    if interested:
        save_lead(phone, "YES")

    response = VoiceResponse()

    gather = Gather(

        input="speech",

        action="/voice",

        method="POST",

        speechTimeout="auto",

        timeout=5
    )

    gather.say(

        ai_text,

        voice="Polly.Joanna-Neural"
    )

    response.append(gather)

    return Response(

        content=str(response),

        media_type="application/xml"
    )


@app.post("/call")
def make_call(data: dict):

    client = Client(

        TWILIO_ACCOUNT_SID,

        TWILIO_AUTH_TOKEN
    )

    call = client.calls.create(

        to=data["phone"],

        from_=TWILIO_PHONE_NUMBER,

        url=data["ngrok_url"] + "/voice"
    )

    print("CALL SID:", call.sid)

    return {"status": "calling"}