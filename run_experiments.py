import os
import requests
import json

def query_free_model(question):
    # OpenRouter handles free API routing seamlessly
    response = requests.post(
        url="https://openrouter.ai",
        headers={
            "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        },
        data=json.dumps({
            # You can swap this to any free model or meta-research model available
            "model": "openrouter/free", 
            "messages": [{"role": "user", "content": question}]
        })
    )
    return response.json()['choices'][0]['message']['content']
