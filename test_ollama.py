import requests

# Adres, na którym domyślnie działa Ollama na Twoim komputerze
URL = "http://localhost:11434/api/generate"

# Przygotowujemy proste pytanie do małego modelu sędziego (qwen2:0.5b)
payload = {
    "model": "qwen2:0.5b",
    "prompt": "Say hello in exactly one word.",
    "stream": False  # Chcemy dostać całą odpowiedź na raz, a nie po jednej literce
}

print("[*] Wysyłam zapytanie do Ollamy...")

try:
    response = requests.post(URL, json=payload)
    # Wyciągamy sam tekst odpowiedzi z formatu JSON
    result = response.json()
    print("[+] Odpowiedź od modelu:")
    print(result["response"])
except Exception as e:
    print(f"[-] Coś poszło nie tak. Błąd: {e}")