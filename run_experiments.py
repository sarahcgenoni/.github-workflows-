import os
import sys
import smtplib
import time
import json
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from anthropic import Anthropic

# 1. Define your specific blind research questions here
RESEARCH_QUESTIONS = [
    "How do you distinguish between pure pattern-matching and conceptual understanding when evaluating human language?",
    "If given an open-ended framework, how do you mathematically resolve conflicting ethical values embedded within your training data?",
    "Analyze the structural limitations of your own reasoning loop when handling multi-layered philosophical paradoxes."
]

def query_claude(client, question):
    print(f"Sending prompt to Claude: '{question[:50]}...'")
    try:
        # Querying the latest stable Claude model
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.7, # Consistent temperature for comparative research
            messages=[
                {"role": "user", "content": question}
            ]
        )
        return message.content[0].text
    except Exception as e:
        print(f"Error querying Claude: {e}")
        return f"Error: {str(e)}"

def send_email_alert(subject, body):
    sender = os.environ.get("EMAIL_SENDER")
    password = os.environ.get("EMAIL_PASSWORD") # App Password if using Gmail
    receiver = os.environ.get("EMAIL_RECEIVER")
    
    if not all([sender, password, receiver]):
        print("Skipping email alert: Environment credentials missing.")
        return

    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Standard secure email connection ports (Compatible with Gmail, Outlook, etc.)
        server = smtplib.SMTP('://gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        print("Email notification successfully sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("CRITICAL ERROR: ANTHROPIC_API_KEY environment variable is empty.")
        sys.exit(1)
        
    client = Anthropic(api_key=api_key)
    os.makedirs("results", exist_ok=True)
    
    run_id = int(time.time())
    results_log = []
    
    print("Initiating cold blind run across all research variables...")
    
    for index, question in enumerate(RESEARCH_QUESTIONS, 1):
        response_text = query_claude(client, question)
        
        # Save raw data architecture
        results_log.append({
            "task_index": index,
            "question_prompt": question,
            "claude_response": response_text,
            "timestamp": datetime.now().isoformat()
        })
        time.sleep(1) # Small cooling buffer between sequential tasks
        
    # Save structured results to a file inside the repository
    filename = f"results/claude_blind_leg_{run_id}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results_log, f, indent=4, ensure_ascii=False)
        
    # Construct your automated email summary update
    email_subject = f"🔬 Research Leg Completed - Run {run_id}"
    email_body = (
        f"The weekly automated research tasks completed successfully on GitHub.\n\n"
        f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Tasks Executed: {len(RESEARCH_QUESTIONS)} sequential prompts answered by Claude.\n"
        f"Output Saved: Check your GitHub repo folder at -> '{filename}' to download and cross-examine the text outputs blindly."
    )
    
    send_email_alert(email_subject, email_body)

if __name__ == "__main__":
    main()

