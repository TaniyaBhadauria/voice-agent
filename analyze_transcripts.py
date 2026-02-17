import os
import glob
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_transcript(filename):
    with open(filename, "r") as f:
        content = f.read()
    
    prompt = f"""
    Analyze the following conversation between a patient (Voice Assistant) and an AI receptionist (Agent).
    The AI receptionist is being tested.
    Identify any issues, bugs, or quality problems in the AI receptionist's responses.
    Look for:
    - Hallucinations or incorrect information.
    - Repetitive loops.
    - Failure to understand the patient.
    - Awkward phrasing or latency issues (implied).
    - Failure to handle the scenario correctly.
    
    Conversation:
    {content}
    
    Output a brief summary of the call and a list of issues found (if any).
    Format as Markdown.
    """
    
    try:
        completion = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error analyzing {filename}: {e}"

def generate_bug_report():
    transcript_files = glob.glob("transcripts/*.txt")
    if not transcript_files:
        print("No transcripts found.")
        return

    report_content = "# Bug Report & Quality Analysis\n\n"
    
    for filename in transcript_files:
        print(f"Analyzing {filename}...")
        analysis = analyze_transcript(filename)
        report_content += f"## Call: {os.path.basename(filename)}\n\n"
        report_content += analysis + "\n\n"
        report_content += "---\n\n"
    
    with open("bug_report.md", "w") as f:
        f.write(report_content)
    
    print("Analysis complete. Saved to bug_report.md")

if __name__ == "__main__":
    generate_bug_report()
