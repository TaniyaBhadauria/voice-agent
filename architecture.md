# Architecture Documentation

## System Overview
The Voice Bot is designed as a webhook-based application using **FastAPI** to handle Twilio voice events and **OpenAI's GPT-4** to generate intelligent responses. It acts as an automated "patient" calling a target AI receptionist.

## Key Design Choices

### 1. Webhook-Based Architecture (Twilio <Gather>)
We chose a traditional request-response model using Twilio's `<Gather>` verb instead of a WebSocket stream.
- **Reasoning**: While WebSockets offer lower latency, the `<Gather>` approach is significantly simpler to implement, easier to debug, and sufficient for a testing bot where sub-second latency is not the primary metric (unlike a real-time assistant). It also provides built-in speech-to-text (STT) via Twilio, reducing the need for a separate STT service.

### 2. OpenAI for Conversational Intelligence
We use `gpt-4-turbo` for generating responses.
- **Reasoning**: GPT-4 provides high-quality, context-aware responses that can simulate complex patient scenarios (e.g., specific insurance questions, detailed symptoms) better than smaller models. The prompt engineering is modularized in `personas.py`, allowing easy switching between different patient personalities.

### 3. Stateless Server with State Management
The FastAPI server is stateless, but we maintain conversation state in memory using a simple dictionary keyed by `CallSid`.
- **Reasoning**: This allows the server to handle multiple concurrent calls without a complex database backend. For a testing tool, in-memory state is acceptable. Transcripts are saved to disk(in transcript directory) immediately after each turn to ensure data persistence.

### 4. Persona-Driven Voice and Behavior
- Each call uses a persona to define behavior, tone, and intent. 
- Personas include edge-case scenarios such as:
  - Multi-intent calls (scheduling + refills + insurance questions)
  - Identity verification challenges 
  - Safety-critical or ambiguous symptom reporting 
- Reasoning: Ensures that the AI agent is tested under realistic, diverse, and challenging situations.

### 5. Automated Analysis
We use a secondary LLM process (`analyze_transcripts.py`) to review call logs.
- **Reasoning**: Post-call analysis allows for a more thorough review of the target agent's performance without impacting the real-time call flow. It can detect subtle issues like hallucinations or loop detection that might be missed during the call.

## Workflow
1.  **Initiation**: `call_manager.py`
>Reads configuration from environment variables: Twilio credentials, phone numbers, server URL.
Selects a persona for the call. Initiates an outbound call via Twilio API with:url pointing to /voice webhook
and status_callback pointing to /status endpoint.Recording is enabled for auditing and analysis.
2.  **Connection**: When the call connects, Twilio hits the `/voice` endpoint.
> Triggered when Twilio connects the call. Initializes a VoiceBot instance and assigns the persona’s voice.
> Sends initial <Gather> to capture the AI agent’s first response. Ensures continuous listening loop for multi-turn conversation.
3.  **Interaction Loop**:
>  - The server sends TwiML `<Gather input="speech">`.
>  - User speaks -> Twilio transcribes -> hits `/gather` with `SpeechResult`.
> - Server sends text to OpenAI -> gets response -> sends `<Say>` and `<Gather>` back to Twilio. 
> - Saves transcript after each turn. Loops until call ends or a stopping condition is met.
4.  **Completion**: On hangup, Twilio hits `/status`, Receives call lifecycle events (completed, failed, busy, canceled). and the server cleans up the in-memory state.
5. Once calls are complete, analyze_transcripts.py reads all transcript files, sends them to GPT-4 for evaluation, and generates a Markdown bug report (bug_report.md) summarizing issues


