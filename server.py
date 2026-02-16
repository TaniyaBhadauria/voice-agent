from fastapi import FastAPI, Request, Form
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
import os
from dotenv import load_dotenv
from bot import VoiceBot

load_dotenv()

app = FastAPI()

from personas import PERSONAS

# Dictionary to store VoiceBot instances per call
active_calls = {}

@app.post("/voice")
async def voice(request: Request):
    """
    Handle incoming call or outbound call answer.
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    
    # Get persona from query params (passed in call creation URL)
    persona_key = request.query_params.get("persona", "scheduling")
    system_prompt = PERSONAS.get(persona_key, PERSONAS["scheduling"])
    
    # Select voice based on persona (simple heuristic for now)
    voice_name = "Polly.Joanna-Neural" # Default female
    if persona_key in ["refill", "general_inquiry"]: # Marcus, David
        voice_name = "Polly.Matthew-Neural" # Male
    
    print(f"Call {call_sid} with persona: {persona_key}, voice: {voice_name}")
    
    # Initialize a new bot for this call ONLY if it doesn't exist
    if call_sid not in active_calls:
        active_calls[call_sid] = {
            "bot": VoiceBot(system_prompt),
            "voice": voice_name
        }
    
    response = VoiceResponse()
    
    # Wait for the other side to say something or say hello ourselves
    # Since we are the patient making an outbound call, we typically wait for "Hello Dr. Smith's office"
    # Or we can proactively say "Hi".
    # Let's start with a Gather to listen first.
    
    # Use the selected voice
    gather = Gather(input='speech', action='/gather', speechTimeout='2.0')
    gather.say("Hello?", voice=voice_name) 
    response.append(gather)

    # If no input, redirect to voice again to keep listening
    response.redirect('/voice')

    return Response(content=str(response), media_type="application/xml")

@app.post("/gather")
async def gather(request: Request):
    """
    Process speech input and return TwiML response.
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    speech_result = form_data.get("SpeechResult")

    response = VoiceResponse()
    
    if call_sid not in active_calls:
        # Should not happen if flow is correct, but handle gracefully
        # Use default persona and voice
        active_calls[call_sid] = {
            "bot": VoiceBot(DEFAULT_SYSTEM_PROMPT),
            "voice": "Polly.Joanna-Neural"
        }

    call_data = active_calls[call_sid]
    bot = call_data["bot"]
    voice_name = call_data["voice"]
    
    if speech_result:
        print(f"[{call_sid}] User: {speech_result}")
        bot_response = bot.get_response(speech_result)
        print(f"[{call_sid}] Bot: {bot_response}")

        # Save transcript after each turn
        bot.save_transcript(call_sid)

        gather = Gather(input='speech', action='/gather', speechTimeout='2.0')
        gather.say(bot_response, voice=voice_name)
        response.append(gather)
        
        # Keep listening if they don't respond (loop back to gather)
        response.redirect('/voice') 
    else:
        # If silence, maybe just listen again
        gather = Gather(input='speech', action='/gather', speechTimeout='2.0')
        response.append(gather)
        response.redirect('/voice')

    return Response(content=str(response), media_type="application/xml")

@app.post("/status")
async def status(request: Request):
    """
    Handle call status updates.
    """
    form_data = await request.form()
    call_sid = form_data.get("CallSid")
    call_status = form_data.get("CallStatus")
    
    print(f"Call {call_sid} status: {call_status}")
    
    if call_status in ["completed", "failed", "busy", "no-answer", "canceled"]:
        if call_sid in active_calls:
            print(f"Cleaning up call {call_sid}")
            del active_calls[call_sid]
            
    return Response(status_code=200)

@app.get("/")
async def root():
    return {"message": "Voice Bot Server is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
