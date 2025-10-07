#!/usr/bin/env python3
"""
Claude 3.5 Sonnet Terminal Interface (Gratuito)
Uso: python claude_terminal.py "sua pergunta aqui"
"""

import sys
import anthropic
import os

# Configuração da API Key (você precisa conseguir uma gratuita)
API_KEY = os.getenv('ANTHROPIC_API_KEY') or 'sua-api-key-aqui'

def chat_with_claude(message):
    try:
        client = anthropic.Anthropic(api_key=API_KEY)
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": message}
            ]
        )
        
        return response.content[0].text
    
    except Exception as e:
        return f"Erro: {str(e)}"

def main():
    if len(sys.argv) < 2:
        print("Uso: python claude_terminal.py 'sua pergunta'")
        print("Exemplo: python claude_terminal.py 'Como criar uma função em Python?'")
        return
    
    # Junta todos os argumentos como uma pergunta
    question = ' '.join(sys.argv[1:])
    
    print("🤖 Perguntando para Claude 3.5 Sonnet...")
    print("─" * 50)
    
    response = chat_with_claude(question)
    
    print(response)
    print("─" * 50)

if __name__ == "__main__":
    main()
