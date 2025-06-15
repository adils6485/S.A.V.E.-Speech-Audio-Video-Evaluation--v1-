import requests
import json
import os


def text_based_scan(text):
    endpoint = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }
    system_prompt = (
            """
        You are a clinically-aware mental health assistant trained to detect any possible suicide risk from user messages.

        Your job is to carefully analyze the user's message for any direct or indirect signs of suicidal ideation. These signs may include, but are not limited to:
        - Expressions of hopelessness, worthlessness, or despair
        - Statements indicating emotional exhaustion, guilt, or shame
        - Mention of being a burden, or that life has no purpose or meaning
        - References to wanting to disappear or believing others would be better off without them
        - Reactions to triggering life events such as relationship breakups, abuse, failure, or job loss

        You must consider both explicit phrases (e.g., "I want to end my life") and implicit cues (e.g., "the world doesn’t need me anymore").

        Your response should be a JSON object ONLY in the following format:
        {
        "risk_level": "suicide" or "non-suicide",
        "confidence": float between 0.0 and 1.0
        }

        The confidence score should reflect how strongly the message suggests suicide risk, even if the language is indirect.
        """
    )
    payload = {
        "model": "meta-llama/llama-4-scout-17b-16e-instruct", 
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "response_format": {"type": "json_object"} 
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        output = response.json()['choices'][0]['message']['content']
        
        # Parse JSON properly
        data = json.loads(output)
        return data
    except requests.exceptions.RequestException as e:
        print(f"Groq API request error: {e}")
        return {"risk_level": "error", "confidence": 0.0}
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw output: {output}")
        return {"risk_level": "error", "confidence": 0.0}
    except Exception as e:
        print(f"General error: {e}")
        return {"risk_level": "error", "confidence": 0.0}

def send_alert_email(user_text, confidence):
    """
    Sends an alert email using Resend API when high suicide risk is detected
    """
    # Store your API key as an environment variable rather than hardcoding
    # os.environ["RESEND_API_KEY"] = "your_key_here" # Set this outside the code
    api_key = os.environ.get("RESEND_API_KEY", "re_e7dTnyDn_5repyrCCU3VBQnWgbRbkNnAf")
    
    html_content = f"""
    <h2>🚨 Suicide Risk Alert</h2>
    <p><strong>Confidence:</strong> {confidence:.2%}</p>
    <p><strong>User Message:</strong><br>{user_text}</p>
    <hr>
    <p>This message triggered a high-risk score (>85%) during suicide risk analysis in the testing phase of the project.</p>
    <p>Please review it manually or notify a qualified person if required.</p>
    <p><i>This email was sent for testing/demo purposes from a prototype suicide risk detection application.</i></p>
    """
    
    try:
        url = "https://api.resend.com/emails"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "from": "Suicide Risk Alert <onboarding@resend.dev>",
            "to": ["prathamesh.jakkula.01042005@gmail.com"],
            "subject": "⚠️ High Suicide Risk Detected in Analysis",
            "html": html_content
        }
        
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        print("Alert email sent successfully using direct API method.")
        return True
    except Exception as api_error:
        print(f"Email sending via direct API also failed: {api_error}")
        return False
