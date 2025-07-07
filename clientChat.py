import os
import openai
import csv 
import time
import json
import requests

def chatear(context):
    """Permite interactuar con el chatbot utilizando un texto como contexto."""
    
    # Crear el prompt
    prompt = context
    print(prompt)
    
    try:
        ############### usando nuestro gpt
        # Construir el cuerpo de la solicitud
        body = {
            "messages": [
                # {"role": "system", "content": "Eres un asistente que puede responder preguntas basadas en noticias."},
                {"role": "user", "content": prompt}
            ],
            'user_id': 'ec5c0c31-4ee1-4407-bcfc-c5a73b7db878',
            'chat_id': 65,
            'type': "Preguntar",
            'workspace_id': 6,
            'project_id': [11]
            # ~ "stream": False,
            # ~ "include_sources": False
        }

        # Eliminar claves con valor None del cuerpo
        body = {k: v for k, v in body.items() if v is not None}

        # URL del endpoint
        url = "http://localhost:8000/start" #ip de mi local

        # Realizar la solicitud
        init_date = time.time()  #para tomar el tiempo
        respuesta = requests.post(
            url,
            headers={"Content-type": "application/json"},
            data=json.dumps(body),
            #stream=True
        )
        
        if respuesta.status_code == 200:
            print("Solicitud exitosa")
            try:
                # Si la respuesta es JSON
                end_date = time.time()
                data = respuesta.json()
                #print("\n\n**** Respuesta JSON:\n", data)
                print("\n\n**** Respuesta JSON:\n", json.dumps(data, indent=2))
                delta_date = end_date - init_date
                print("tiempo (segundos):", delta_date)
                #print(data['choices'][0])
                respuesta_chatbot = data["job_id"]
                #print("\n\n**** Respuesta modelo: \n",respuesta_chatbot)
                return respuesta_chatbot                
            except json.JSONDecodeError:
                # Si la respuesta no es JSON, manejar como texto
                print("\n\n*** Respuesta en texto:\n", respuesta.text)
        else:
            print(f"Error en la solicitud: {respuesta.status_code}")
            print(respuesta.text)
        
    except Exception as e:
        return str(e)


def health(uuid):
    try:
        url = "http://localhost:8000/process/"+uuid #ip de mi local

        respuesta = requests.get(
            url,
            headers={"Content-type": "application/json"},
            data=json.dumps({}),
            stream=True
        )
        
        for chunk in respuesta.iter_content(chunk_size=8192):
            if chunk:
                print("DATA!!!", chunk, url)
                        
    except Exception as e:
        return str(e)

if __name__ == '__main__':   
    answer_json = {}
    try:
        
        
        context = """ La gobernadora Mara Lezama Espinosa fue galardonada con el prestigioso Reconocimiento al Liderazgo Femenino en Turismo 2025 por la organización internacional Women Leading Tourism (WLT) en el marco de la Feria Internacional de Turismo (FITUR) 2025, que se celebra en Madrid, España.
            Women Leading Tourism, una plataforma global dedicada a promover un turismo inclusivo, competitivo y sostenible, destacó la trayectoria de Mara Lezama como una líder transformadora. La organización subrayó su enfoque en la inclusión de las mujeres en la toma de decisiones, su trabajo incansable por la equidad de género y su defensa activa del medio ambiente, principios alineados con los valores de WLT.
            “El liderazgo de mujeres como Mara Lezama es fundamental para transformar el sector turístico y hacerlo más inclusivo y representativo. Este reconocimiento celebra su incansable trabajo para lograr un sector más justo y equitativo para todos, alineado con los Objetivos de Desarrollo Sostenible de la Agenda 2030”, afirmó la organización.
            Mara Lezama, al recibir este reconocimiento de manos de Maribel Rodríguez, presidenta de Women Leading Tourism, expresó que este reconocimiento no solo es por logros alcanzados, sino para honrar la lucha, determinación y el corazón de tantas mujeres que, con su liderazgo, han transformado la historia y continúan cambiando el rumbo de las naciones.
            “En esta ocasión tan significativa, me llena de emoción saber que estamos escribiendo una nueva página de esa historia. Una página que va muy de la mano con la filosofía de lo que es mi forma de gobernar: la prosperidad compartida, la igualdad de oportunidades, la sostenibilidad y un liderazgo femenino que no solo inspira, sino que transforma”, dijo Mara Lezama.
            Asimismo, puntualizó que este reconocimiento es un reflejo del trabajo realizado en Quintana Roo para construir un sector turístico que valore la equidad de género, promueva la sostenibilidad y ofrezca oportunidades para todos. “Agradezco profundamente a Women Leading Tourism por visibilizar el esfuerzo de las mujeres en la industria, y reafirmo mi compromiso de seguir impulsando políticas que favorezcan la inclusión y el bienestar de todas las personas en nuestra sociedad”, mencionó Mara Lezama.
            Con este galardón, Mara Lezama se suma a un selecto grupo de líderes femeninas que están dejando una huella significativa en el sector turístico global, reafirmando su papel como una de las figuras más influyentes del turismo y la sostenibilidad en América Latina.
            Durante la ceremonia, se destacó que Women Leading Tourism tiene como uno de sus principales objetivos impulsar la participación femenina en los niveles más altos de la estructura turística, promoviendo su presencia en los órganos de decisión y liderazgo, acorde con la cantidad y la calidad del trabajo que desempeñan las mujeres en este sector. A pesar de que el 54% de los puestos de trabajo en el turismo son ocupados por mujeres, menos del 5% se encuentran en roles de dirección general, según datos del Banco Mundial.
            JVR
        """ 
            
        prompt_preguntas = f"""
        1.- Personaje principal: Quien es el personaje principal de la noticia, si se mencionan varios personajes solo quiero el nombre del principal, si no hay responde 'ninguno'
        3.- Polaridad noticia: Cual es la polaridad de la noticia, solo quiero saber si es positivo o negativo
        6.- Tema: Cuál es tema de la noticia según sea Protección civil, Política, Seguridad Ciudadana, Salud, Seguridad Vial, Cultura, Delincuencia organizada, Economía, Medio Ambiente, Educación, Vivienda, Ciencia y tecnología, Turismo
        7.- Resumen: Haz un resumen corto de la noticia.
        """    
        
        prompt = f"Dada la siguiente noticia:\n{context}\n, responde a la siguientes preguntas en formato json, sólo el json, las llaves del json son el nombre de la pregunta: {prompt_preguntas}"

        answer = chatear(prompt)
        print("ID:", answer)
        answer = health(answer)
    except:
        answer_json = {}
        print("error")


