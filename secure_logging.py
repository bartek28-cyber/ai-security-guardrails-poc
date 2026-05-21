import json
from datetime import datetime

def log_security_event(event_type: str, user_prompt: str, status: str):
    """
    Generates and appends a structured JSON security log for SIEM processing.
    """
    log_payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "attack_vector": "OWASP_LLM01_Prompt_Injection",
        "user_input_snippet": user_prompt[:100],
        "status": status,
        "severity": "HIGH" if status == "BLOCKED" else "INFO"
    }
    
    with open("ai_security_events.log", "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_payload, ensure_ascii=False) + "\n")