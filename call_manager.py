import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TARGET_PHONE_NUMBER = "805-439-8008" # The AI agent we are testing
SERVER_URL = os.getenv("SERVER_URL") # Must be set (e.g., ngrok url)

if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, SERVER_URL]):
    print("Error: Missing environment variables. Please check your .env file.")
    exit(1)

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

import sys
from personas import PERSONAS

def make_call(persona_key="scheduling"):
    """
    Initiate an outbound call to the target number.
    """
    if persona_key not in PERSONAS:
        print(f"Error: Persona '{persona_key}' not found. Available personas: {list(PERSONAS.keys())}")
        return

    print(f"Initiating call with persona: {persona_key}")
    
    try:
        call = client.calls.create(
            to=TARGET_PHONE_NUMBER,
            from_=TWILIO_PHONE_NUMBER,
            url=f"{SERVER_URL}/voice?persona={persona_key}",
            status_callback=f"{SERVER_URL}/status",
            status_callback_event=["initiated", "ringing", "answered", "completed"],
            record=True
        )
        print(f"Call initiated. SID: {call.sid}")
        return call.sid
    except Exception as e:
        print(f"Failed to initiate call: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        persona = sys.argv[1]
        make_call(persona)
    else:
        print("Usage: python call_manager.py <persona_name>")
        print(f"Available personas: {list(PERSONAS.keys())}")
        # Default to scheduling for testing if user just hits enter?
        # valid_persona = input(f"Enter persona ({list(PERSONAS.keys())}): ")
        # if valid_persona: make_call(valid_persona)
