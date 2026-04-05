# AI Voice Agent (Twilio + FastAPI + Groq + ElevenLabs)

This project is a simple AI voice marketing agent. It:
1. Answers live phone calls via Twilio.
2. Uses Groq (LLM) to generate a short reply.
3. Speaks the reply back to the caller using Twilio's Polly voice.
4. Includes a small Streamlit dashboard to trigger outbound calls.

---

## Project Structure
- `ai_agent.py` - LLM prompt + response generation, and optional text-to-speech helper.
- `main.py` - FastAPI app that handles Twilio webhooks and makes outbound calls.
- `dashboard.py` - Streamlit UI to trigger a call.
- `call.py` - Simple script that makes a single outbound call.
- `.env` - API keys and secrets (not committed).

---

## Prerequisites
- Python 3.10+ recommended
- Twilio account (voice-enabled number)
- Groq API key
- (Optional) ElevenLabs API key if you plan to use `text_to_audio`
- Ngrok (or any public tunnel) to expose your local server to Twilio

---

## Setup

1. Create a virtual environment (recommended)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies
```powershell
pip install fastapi uvicorn twilio python-dotenv groq elevenlabs streamlit requests
```

3. Create `.env` in `voice-agent/` with:
```env
GROQ_API_KEY=your_groq_key
ELEVENLABS_API_KEY=your_elevenlabs_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=+1234567890
NGROK_URL=https://your-public-url.ngrok-free.app
```

Notes:
- `ELEVENLABS_API_KEY` is only required if you use `text_to_audio()` in `ai_agent.py`.
- `NGROK_URL` must be the public URL that routes to your local FastAPI server.

---

## Running the Server

Start the FastAPI server:
```powershell
uvicorn main:app --host 0.0.0.0 --port 8000
```

Expose your server publicly (example with ngrok):
```powershell
ngrok http 8000
```

Copy the public URL and set it in `NGROK_URL` in `.env`.

---

## Twilio Voice Flow

Twilio will hit:
- `POST /voice` when a call is connected.
- The app responds with TwiML that:
  - listens for speech
  - generates an AI response
  - speaks it back to the caller

You can also trigger outbound calls using:
- `POST /call` (used by the Streamlit dashboard)

---

## Run the Dashboard

```powershell
streamlit run dashboard.py
```

Then open the dashboard and enter a phone number including country code.

---

## Manual Call Test (Script)

You can trigger a call directly:
```powershell
python call.py
```

Be sure `call.py` has the correct phone number and `url` points to your public `/voice` endpoint.

---

## Customize the AI Behavior

The prompt is defined in `ai_agent.py`:
```python
You are an AI voice marketing agent.
Introduce AI automation services.
Ask what business they run.
Keep message short and natural.
```

Edit these lines to change the voice agent's behavior.

---

## Troubleshooting

- If Twilio can’t reach your server:
  - Verify `NGROK_URL` is correct.
  - Make sure ngrok is running and forwarding to `localhost:8000`.

- If responses are empty:
  - Confirm `GROQ_API_KEY` is set.
  - Check Groq model name in `ai_agent.py`.

- If the call ends quickly:
  - Increase `timeout` in the `Gather` block in `main.py`.

---

## Next Ideas
- Store conversation history per caller
- Add call recordings
- Switch to ElevenLabs TTS instead of Twilio voice
- Add lead scoring or CRM export

