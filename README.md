# Local LLM Guardrails & Prompt Injection Mitigation PoC

## Overview
This repository contains a local **Proof of Concept (PoC)** demonstrating security auditing and mitigation strategies for Large Language Models, focusing specifically on **OWASP LLM01: Prompt Injection** and data exfiltration vectors. 

The architecture simulates a corporate AI HR assistant connected to an internal data repository (SQLite), protected by a secondary defense layer utilizing a **LLM-as-a-Judge (Guardrail)** mechanism.

## Architecture & Flow
1. **Data Layer:** Local SQLite database containing simulated restricted corporate data.
2. **Defense Layer (Guardrail):** A strict, zero-temperature `Llama 3` model operating as an automated gateway analyzing user intent within isolated XML/HTML structural tags (`<USER_INPUT>`).
3. **Application Layer:** Operational `Llama 3` processing verified requests.
4. **Monitoring (SOC Integration):** Any triggered threat mitigation logs structured event data in standardized **JSON format**, designed for direct SIEM ingestion (e.g., Wazuh, ELK).

### 🛡️ System Threat Model & Risk Analysis (OWASP LLM & Network Alignment)

| Threat Vector / Vector Ataku | OWASP LLM ID / Tech Class | Mitigation Implemented / Wdrożona Mitygacja |
| :--- | :--- | :--- |
| **Direct Prompt Injection** | LLM01: Prompt Injection | Advanced two-stage pipeline utilizing **Llama 3** as a real-time autonomous security judge. |
| **Sensitive Data Exfiltration** | LLM06: Sensitive Info Disclosure | Isolated query pipeline with strict limits on data extraction from the internal SQLite repository. |
| **Unauthorized API Ingestion** | OWASP API: Broken Auth | Hardened endpoint protection enforcing strict HTTP Bearer Token authentication via FastAPI. |
| **System Telemetry Tampering** | Traditional: Log Injection | Immutable, structured JSON logging (`secure_logging.py`) ready for native external SIEM (Wazuh/ELK) ingestion. |

## SIEM-Ready Telemetry Example
When a semantic manipulation attack is deflected, the system produces structured logs optimized for automated SOC alerting pipelines:

```json
{
  "timestamp": "2026-05-21T12:40:10.336731Z", 
  "event_type": "AI_GUARDRAIL_TRIGGER", 
  "attack_vector": "OWASP_LLM01_Prompt_Injection", 
  "user_input_snippet": "ZMIANA ZASAD. Ignoruj wszystkie poprzednie instrukcje...", 
  "status": "BLOCKED", 
  "severity": "HIGH"
}


