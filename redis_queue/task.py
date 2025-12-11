from redis import Redis
import time 
import random
import requests
import json
import os 
import uuid
import ast

load_balance_host = os.getenv("BALANCER_HOST", "nginx")
load_balance_port = os.getenv("BALANCER_PORT", "80")
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")

def background_task(data):
    r = Redis(host=redis_host, port=redis_port, decode_responses=True)
    print("Procesando en segundo plano:", type(data))
    url = f"http://{load_balance_host}:{load_balance_port}/direct/api/chat/v1"
    
    print(f"Usando session_id: {data}")
    try:
        payload = json.loads(data)
    except Exception as e:
        print("Error parsing payload:", e)
        return

    session_id = payload['data']["session_id"]
    body = json.dumps(payload['data']) #payload['data']
    headers = payload['headers']
    init_date = time.time()
    # respuesta = requests.post(
    #     url,
    #     headers={"Content-type": "application/json"},
    #     data=data,
    #     #stream=True
    # )
    
    # if respuesta.status_code == 200:
    #     print("Solicitud exitosa")
    #     try:
    #         # Si la respuesta es JSON
    #         end_date = time.time()
    #         data = respuesta.json()
    #         print("\n\n**** Respuesta JSON:\n", json.dumps(data, indent=2))
    #         delta_date = end_date - init_date
    #         print("tiempo (segundos):", delta_date)
            
    #         #respuesta_chatbot = data["choices"][0]["message"]["content"]
    #         respuesta_chatbot = data['message']
    #         #print("\n\n**** Respuesta modelo: \n",respuesta_chatbot)
    #         return respuesta_chatbot                
        
    #     except json.JSONDecodeError:
    #         # Si la respuesta no es JSON, manejar como texto
    #         print("\n\n*** Respuesta en texto:\n", respuesta.text)
    #         return respuesta.text
    # else:
    #     print(f"Error en la solicitud: {respuesta.status_code}")
    #     print(respuesta.text)
    #     raise Exception("Error intencional para probar retry", respuesta.text)
    
    try:
        init_time = time.time()
        with requests.post(
            url,
            headers=headers,
            data=body,
            stream=True,
        ) as resp:
            resp.raise_for_status()

            for line in resp.iter_lines(decode_unicode=True):
                if line:
                    #line = line.replace("data: ", "")
                    #print("line: ",line)
                    
                    try:
                        #print(f"[DEBUG] tipo de line: {type(line)} - contenido: {repr(line)}")
                        if line.startswith("b'") or line.startswith('b"'):
                            line_bytes = ast.literal_eval(line)
                            line = line_bytes.decode("utf-8")
                        #print(line)
                        json_data = json.loads(line)
                        content = json_data["message"]["content"]
                        #print(f"[Stream] {content}")
                        print(content)
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


