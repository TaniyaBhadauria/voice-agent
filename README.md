# voice-agent
An automated patient voice bot that calls and evaluates a conversational AI agent, records transcripts, and identifies quality issues.


## Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/TaniyaBhadauria/voice-agent.git
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    - Copy `.env.example` to `.env`.
    - Fill in your Twilio credentials (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`).
    - Add your OpenAI API key (`OPENAI_API_KEY`).
    - Set `SERVER_URL` to your public server URL (e.g., using ngrok).

## Usage

1.  **Start the Server**:
    The server handles Twilio webhooks and manages the conversation flow.
    ```bash
    python server.py
    ```
    
Ensure your server is publicly accessible (e.g., `ngrok http 5000`) and update `SERVER_URL` in `.env`.

2.  **Initiate a Call**:
    Run the `call_manager.py` script to start an outbound call. You can specify a persona:
    ```bash
    python call_manager.py scheduling
    ```
    Available personas: `scheduling`, `vague_scheduling`, `reschedule_conflict`, 
`refill`, `insurance`, `identity_challenge`, `safety_liability_test`,, `multi_task_agent`, `boundary_push_complex`, `multi_intent`.

3.  **Analyze Results**:
    After calls are completed, transcripts are saved in `transcripts/`.
    Run the analysis script to generate a bug report:
    ```bash
    python analyze_transcripts.py
    ```
    This will generate `bug_report.md`.

## Project Structure

- `server.py`: FastAPI server handling Twilio webhooks (`/voice`, `/gather`, `/status`).
- `bot.py`: Logic for the AI patient, integrating with OpenAI.
- `call_manager.py`: Script to initiate outbound calls.
- `personas.py`: Definitions of different patient personas.
- `analyze_transcripts.py`: Script to analyze call transcripts using GPT-4.
- `transcripts/`: Directory where call logs are saved.
