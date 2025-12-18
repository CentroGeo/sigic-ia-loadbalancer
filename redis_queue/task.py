from redis import Redis
import time 
import random
import requests
import json
import os 
import uuid
import ast

ia_engine_base_url = os.getenv("IA_ENGINE_BASE_URL", "http://ia-engine:8000")
ia_engine_path_url = os.getenv("IA_ENGINE_PATH_URL", "/api/chat/v1")
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")


def background_task(data):
    r = Redis(host=redis_host, port=redis_port, decode_responses=True)
    print("Procesando en segundo plano:", type(data))
    url = f"{ia_engine_base_url}{ia_engine_path_url}"

    print(f"Usando session_id: {data}")
    try:
        payload = json.loads(data)
    except Exception as e:
        print("Error parsing payload:", e)
        return

    session_id = payload['data']["session_id"]
    body = json.dumps(payload['data'])  #payload['data']
    headers = payload['headers']
    init_date = time.time()
    
    try:
        init_time = time.time()
        with requests.post(
                url,
                headers=headers,
                data=body,
                stream=True,
                timeout=int(os.environ.get("OLLAMA_TIMEOUT", 600)),
        ) as resp:
            resp.raise_for_status()

            for line in resp.iter_lines(decode_unicode=True):
                if line:
                    try:
                        if line.startswith("b'") or line.startswith('b"'):
                            line_bytes = ast.literal_eval(line)
                            line = line_bytes.decode("utf-8")
                        json_data = json.loads(line)
                        content = json_data["message"]["content"]
                        r.rpush(f"stream:{session_id}", content)
                    except json.JSONDecodeError as e:
                        print(f"[ERROR] JSON inválido: {e} {line}")
                    time.sleep(0.07)

            r.set(f"stream_done:{session_id}", "1", ex=3600)
            total_time = round(time.time() - init_time, 2)
            print(f"Stream finalizado en {total_time}s")

    except Exception as e:
        print(f"[Error] {str(e)}")
        r.rpush(f"stream:{session_id}", f"[ERROR] {str(e)}")
