import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class VoiceBot:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.history = [{"role": "system", "content": system_prompt}]

    def get_response(self, user_input: str) -> str:
        """
        Get a response from the LLM based on the user's input.
        """
        self.history.append({"role": "user", "content": user_input})

        try:
            completion = client.chat.completions.create(
                model="gpt-4-turbo",  # Or gpt-3.5-turbo if latency is an issue
                messages=self.history,
                temperature=0.7,
                max_tokens=150,
            )
            response_text = completion.choices[0].message.content
            self.history.append({"role": "assistant", "content": response_text})
            return response_text
        except Exception as e:
            print(f"Error getting response from OpenAI: {e}")
            return "I'm sorry, I didn't catch that. Could you please repeat?"

    
    def save_transcript(self, call_sid: str):
        """
        Save the conversation history to a file.
        """
        transcript_dir = "transcripts"
        os.makedirs(transcript_dir, exist_ok=True)
        filename = os.path.join(transcript_dir, f"{call_sid}.txt")
        
        with open(filename, "w") as f:
            for turn in self.history:
                role = turn["role"]
                content = turn["content"]
                if role == "system":
                    continue # Skip system prompt in readable transcript
                
                # Map roles to requested labels
                label = role.upper()
                if role == "user":
                    label = "AGENT"
                elif role == "assistant":
                    label = "VOICE ASSISTANT"
                
                f.write(f"{label}: {content}\n")
    
# Example usage (for testing)
if __name__ == "__main__":
    bot = VoiceBot("You are a helpful assistant.")
    print(bot.get_response("Hello!"))
    bot.save_transcript("test_call_sid")
