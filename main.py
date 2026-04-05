#!/usr/bin/env python
# main.py

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response, HTMLResponse
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client

import os
import csv
import datetime

from dotenv import load_dotenv
from ai_agent import generate_reply

load_dotenv()

app = FastAPI()

def _clean_base_url(value: str | None) -> str | None:
    if not value:
        return None
    return value.rstrip("/")


BASE_URL = _clean_base_url(
    os.getenv("BASE_URL")
    or os.getenv("NGROK_URL")
    or os.getenv("RENDER_EXTERNAL_URL")
    or os.getenv("PUBLIC_URL")
)

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


# -------- UI PAGE --------

@app.get("/ui")
def ui():

    return HTMLResponse("""

    <html>

    <head>

        <title>AI Call Agent</title>

        <style>

            body{
                font-family: Arial;
                background:#f5f5f5;
                padding:40px;
                text-align:center;
            }

            input{
                padding:10px;
                width:250px;
                margin:10px;
            }

            button{
                padding:10px 20px;
                background:#4CAF50;
                color:white;
                border:none;
                cursor:pointer;
            }

            button:hover{
                background:#45a049;
            }

            .box{
                background:white;
                padding:30px;
                border-radius:10px;
                display:inline-block;
                box-shadow:0 0 10px rgba(0,0,0,0.1);
            }

        </style>

    </head>

    <body>

        <div class="box">

            <h2>AI Voice Call Agent</h2>

            <input id="phone" placeholder="+91xxxxxxxxxx"/>

            <br>

            <button onclick="makeCall()">Call Customer</button>

            <p id="msg"></p>

        </div>

        <script>

        async function makeCall(){

            let phone = document.getElementById("phone").value;

            let res = await fetch("/call",{

                method:"POST",

                headers:{

                    "Content-Type":"application/json"

                },

                body:JSON.stringify({

                    phone:phone

                })

            });

            document.getElementById("msg").innerText="Calling...";

        }

        </script>

    </body>

    </html>

    """)


# -------- TWILIO VOICE --------

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


# -------- CALL API --------

@app.post("/call")
def make_call(data: dict):
    if not BASE_URL:
        raise HTTPException(
            status_code=500,
            detail="BASE_URL is not set. Set BASE_URL (or NGROK_URL / RENDER_EXTERNAL_URL) to your public server URL.",
        )

    client = Client(

        TWILIO_ACCOUNT_SID,

        TWILIO_AUTH_TOKEN
    )

    call = client.calls.create(

        to=data["phone"],

        from_=TWILIO_PHONE_NUMBER,

        url=f"{BASE_URL}/voice"

    )

    return {

        "status": "calling"

    }
