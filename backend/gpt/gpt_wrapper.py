import redis
import hashlib
import openai
import os

redis_client = redis.Redis(host="localhost", port=6379, db=0)

openai.api_key = os.getenv("OPENAI_API_KEY")

def cache_key(prompt: str, model: str = "gpt-4") -> str:
    return f"gpt_cache:{model}:" + hashlib.sha256(prompt.encode()).hexdigest()

def get_gpt_response(prompt: str, model: str = "gpt-4"):
    key = cache_key(prompt, model)

    cached = redis_client.get(key)
    if (cached):
        return cached.decode()
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )

    result = response.choices[0].message.content
    redis_client.setex(key, 3600, result)
    return result


