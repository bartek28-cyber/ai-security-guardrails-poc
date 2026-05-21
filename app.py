import os
import logging
from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

# Import the secure logging function from our second file
from secure_logging import log_security_event

app = FastAPI(title="AI Security Guardrails PoC")

# --- SECURE DATABASE MOCK (Data Minimization / RBAC) ---
# Instead of sending all data to the LLM, we filter records in the backend application.
MOCK_SALARIES = {
    101: {"name": "Jan Kowalski", "role": "Intern", "salary": "4000 PLN"},
    102: {"name": "Anna Nowak", "role": "Regular Developer", "salary": "12000 PLN"}
}

class QueryModel(BaseModel):
    user_id: str
    session_id: str
    employee_id_query: Optional[int] = None
    user_input: str

# --- SAFE VERDICT PARSING ---
def parse_guardrail_verdict(raw_verdict: str) -> bool:
    """
    Returns True if an attack is detected (block), False if the input is safe.
    Uses strict matching to prevent bypasses hidden inside long model answers.
    """
    clean = raw_verdict.strip().upper()
    if "MALICIOUS" in clean:
        return True
    if "SAFE" in clean:
        return False
    
    # FAIL-CLOSED PRINCIPLE: If the model answer is strange or unclear, we block the request.
    return True

# --- GUARDRAIL ARCHITECTURE (LLM-as-a-Judge) ---
def call_guardrail_llm(user_input: str) -> str:
    """
    NOTE: Production implementation calls the local Ollama API (Llama 3) with temperature=0.0.
    The system prompt forces the model to reply with ONLY 'SAFE' or 'MALICIOUS'.
    Mocked here with 'pass' to isolate and show the structural design.
    """
    pass

def is_prompt_injection(user_input: str) -> bool:
    try:
        # We isolate user data using XML tags inside the system prompt
        raw_verdict = call_guardrail_llm(user_input)
        return parse_guardrail_verdict(raw_verdict)
    except Exception as e:
        # CRITICAL: Log internal system failure
        print(f"[CRITICAL_ERROR] Guardrail Failure: {str(e)}")
        # FAIL-CLOSED PRINCIPLE: If the security system fails, we block the traffic immediately.
        return True 

@app.post("/api/v1/query")
async def handle_query(payload: QueryModel, request: Request):
    client_ip = request.client.host
    
    # 1. Check Guardrail (Prompt Injection / Jailbreak detection)
    if is_prompt_injection(payload.user_input):
        log_security_event(
            event_type="ai_guardrail_alert",
            attack_vector="OWASP_LLM01_Prompt_Injection",
            source_ip=client_ip,
            session_id=payload.session_id,
            user_id=payload.user_id,
            raw_input=payload.user_input,
            action="blocked"
        )
        raise HTTPException(status_code=403, detail="Security Policy Violation: Malicious input detected.")
    
    # 2. Secure Context Control (Prevention of Data Disclosure)
    context_data = "No specific corporate context provided."
    if payload.employee_id_query:
        # Role-Based Access Control (RBAC) is done in Python, NOT by asking the LLM nicely.
        if payload.user_id != "admin_manager":
            raise HTTPException(status_code=403, detail="Access Denied to sensitive financial records.")
        
        record = MOCK_SALARIES.get(payload.employee_id_query)
        if record:
            context_data = f"Employee Profile: {record['name']}, Role: {record['role']}, Salary: {record['salary']}"
    
    # 3. Safe LLM execution using the sanitized context
    # response = call_main_llm(payload.user_input, context=context_data)
    
    return {"status": "success", "data": "Response generated safely using sanitized context."}
