#!/usr/bin/env python
# file: ai_agent.py

from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

conversation_memory = []

INTEREST_WORDS = [
    "yes",
    "interested",
    "price",
    "demo",
    "tell me more",
    "details",
    "cost",
    "how much"
]


def check_interest(text):

    if not text:
        return False

    text = text.lower()

    for word in INTEREST_WORDS:
        if word in text:
            return True

    return False


def generate_reply(user_input):

    conversation_memory.append({
        "role": "user",
        "content": user_input
    })

    messages = [

        {
            "role": "system",
            "content": """
You are a friendly AI voice agent calling business owners.

Goal:
Understand business and suggest AI automation.

Conversation style:
- speak naturally
- short sentences
- ask 1 question at a time
- sound human
- avoid technical words
- respond in SAME language as user (Hindi or English)

Services:
• automate customer replies
• WhatsApp automation
• appointment booking
• lead followup automation

Try to understand:
1. business type
2. how customers contact them
3. if they want more leads
4. if interested in demo
"""
        }

    ] + conversation_memory

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages
    )

    reply = response.choices[0].message.content.strip()

    conversation_memory.append({
        "role": "assistant",
        "content": reply
    })

    return reply, check_interest(user_input)