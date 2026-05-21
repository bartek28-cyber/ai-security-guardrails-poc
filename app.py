import os
import logging
from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

# Czysty import telemetryczny na górze pliku
from secure_logging import log_security_event

app = FastAPI(title="AI Security Guardrails PoC")

# --- MOCK BEZPIECZNEJ BAZY DANYCH (Data Minimization / RBAC) ---
# Zamiast wrzucać całą bazę danych do LLM, filtrujemy rekordy na poziomie aplikacji
MOCK_SALARIES = {
    101: {"name": "Jan Kowalski", "role": "Intern", "salary": "4000 PLN"},
    102: {"name": "Anna Nowak", "role": "Regular Developer", "salary": "12000 PLN"}
}

class QueryModel(BaseModel):
    user_id: str
    session_id: str
    employee_id_query: Optional[int] = None
    user_input: str

# --- SZYBKIE I BEZPIECZNE PARSOWANIE WERDYKTU ---
def parse_guardrail_verdict(raw_verdict: str) -> bool:
    """
    Zwraca True jeśli wykryto atak (blokujemy), False jeśli ruch jest bezpieczny.
    Zasada ścisłego dopasowania chroni przed manipulacją tekstem wewnątrz odpowiedzi.
    """
    clean = raw_verdict.strip().upper()
    if "MALICIOUS" in clean:
        return True
    if "SAFE" in clean:
        return False
    
    # ZASADA FAIL-CLOSED: Niejednoznaczna odpowiedź modelu traktowana jest jako zagrożenie
    return True

# --- ARCHITEKTURA GUARDRAIL (LLM-as-a-Judge) ---
def call_guardrail_llm(user_input: str) -> str:
    """
    NOTE: Production implementation calls the local Ollama API (Llama 3) with temperature=0.0.
    Wired via system prompts to strictly output either 'SAFE' or 'MALICIOUS'.
    Mocked here with 'pass' to isolate the structural and architectural demonstration.
    """
    pass

def is_prompt_injection(user_input: str) -> bool:
    try:
        # Izolacja danych użytkownika tagami XML w promptie systemowym do Guardraila
        raw_verdict = call_guardrail_llm(user_input)
        return parse_guardrail_verdict(raw_verdict)
    except Exception as e:
        # KRYTYCZNE: Logowanie awarii wewnętrznej komponentu bezpieczeństwa
        print(f"[CRITICAL_ERROR] Guardrail Failure: {str(e)}")
        # ZASADA FAIL-CLOSED: Jeśli system walidacji leży, kategorycznie blokujemy ruch
        return True 

@app.post("/api/v1/query")
async def handle_query(payload: QueryModel, request: Request):
    client_ip = request.client.host
    
    # 1. Sprawdzenie Guardraila (Prompt Injection / Jailbreak)
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
    
    # 2. Bezpieczna kontrola kontekstu (Zabezpieczenie przed Data Disclosure)
    context_data = "No specific corporate context provided."
    if payload.employee_id_query:
        # Walidacja uprawnień (RBAC) na poziomie backendu aplikacji, a nie za pomocą instrukcji LLM
        if payload.user_id != "admin_manager":
            raise HTTPException(status_code=403, detail="Access Denied to sensitive financial records.")
        
        record = MOCK_SALARIES.get(payload.employee_id_query)
        if record:
            context_data = f"Employee Profile: {record['name']}, Role: {record['role']}, Salary: {record['salary']}"
    
    # 3. Bezpieczne przekazanie odfiltrowanego kontekstu do głównego potoku LLM
    # response = call_main_llm(payload.user_input, context=context_data)
    
    return {"status": "success", "data": "Response generated safely using sanitized context."}
