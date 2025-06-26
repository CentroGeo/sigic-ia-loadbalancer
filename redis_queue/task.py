
import time 
import random

def background_task(data):
    random_boolean = random.choice([True, False, False, False])
    print("Procesando en segundo plano:", type(data), random_boolean)
    time.sleep(20)
    
    
    if(random_boolean):
        return data.decode('utf-8')
    else:
        raise Exception("Error intencional para probar retry")