
import time 
import random
import requests
import json
import os 

host_load_balance = os.getenv("BALANCER_HOST", "nginx")
port_load_balance = os.getenv("BALANCER_PORT", "8080")


def background_task(data):
    print("Procesando en segundo plano:", type(data))
    url = f"http://{host_load_balance}:{port_load_balance}/v1/chat/completions"
    
    init_date = time.time()
    respuesta = requests.post(
        url,
        headers={"Content-type": "application/json"},
        data=data,
        #stream=True
    )
    
    if respuesta.status_code == 200:
        print("Solicitud exitosa")
        try:
            # Si la respuesta es JSON
            end_date = time.time()
            data = respuesta.json()
            print("\n\n**** Respuesta JSON:\n", json.dumps(data, indent=2))
            delta_date = end_date - init_date
            print("tiempo (segundos):", delta_date)
            
            respuesta_chatbot = data["choices"][0]["message"]["content"]
            #print("\n\n**** Respuesta modelo: \n",respuesta_chatbot)
            return respuesta_chatbot                
        
        except json.JSONDecodeError:
            # Si la respuesta no es JSON, manejar como texto
            print("\n\n*** Respuesta en texto:\n", respuesta.text)
            return respuesta.text
    else:
        print(f"Error en la solicitud: {respuesta.status_code}")
        print(respuesta.text)
        raise Exception("Error intencional para probar retry")
        