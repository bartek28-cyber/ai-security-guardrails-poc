import json
import logging
from datetime import datetime

# Configure logger to output clean text/JSON for SIEM integration
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("SIEM_Defender")

def log_security_event(event_type: str, attack_vector: str, source_ip: str, session_id: str, user_id: str, raw_input: str, action: str):
    """
    Generates a unified security log in JSON format.
    This structure is ready for direct parsing and event correlation 
    in SIEM / SOAR systems like Wazuh, Splunk, or Elastic Stack.
    """
    log_payload = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "security_metadata": {
            "attack_vector": attack_vector,
            "mitigation_action": action,
            "framework_target": "OWASP_Top_10_LLM"
        },
        "network_context": {
            "source_ip": source_ip,
            "session_id": session_id,
            "authenticated_user": user_id
        },
        "payload_analysis": {
            "truncated_raw_input": raw_input[:500],  # Protects against Log Flooding while keeping IoC evidence
            "input_length_bytes": len(raw_input.encode('utf-8'))
        }
    }
    
    # Print the log in a single line (optimal for log collectors like Logstash or Wazuh Agent)
    logger.info(json.dumps(log_payload))
