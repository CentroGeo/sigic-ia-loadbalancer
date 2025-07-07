from flask import Flask, request, jsonify, Response
from rq import Queue, Worker, Retry
from rq.job import Job
from redis import Redis
from task import background_task
from multiprocessing import Process
import os
import socket
import requests
import time
import json
import uuid

host_redis = os.getenv("REDIS_HOST", "localhost")
port_redis = os.getenv("REDIS_PORT", "6379")
host_load_balance = os.getenv("BALANCER_HOST", "nginx")
port_load_balance = os.getenv("BALANCER_PORT", "8080")

r = Redis(host=host_redis, port=port_redis)
q = Queue(connection=r)

app = Flask(__name__)
    
@app.route("/start", methods=["POST"])
def start():
    try:
        job_uuid = str(uuid.uuid4())
        send_data_chat           = json.loads(request.data)
        
        if(send_data_chat["type"] == "Preguntar"):
            send_data_chat["job_id"] = job_uuid
            
            url = f"http://{host_load_balance}:{port_load_balance}/project/chat/register/v3"
            
            respuesta = requests.post(
                url,
                headers={"Content-type": "application/json"},
                data=json.dumps(send_data_chat),
            )

            if respuesta.status_code == 200:
                print("Solicitud exitosa")
                send_data_chat["chat_id"] = respuesta.json()["chat_id"]
                job = q.enqueue(background_task, json.dumps(send_data_chat), job_id=job_uuid, retry=Retry(max=10, interval=20))
                
                return jsonify({"job_id": job.id})
            else:
                return jsonify({"error": str(respuesta.status_code)})
                
        else:
            job = q.enqueue(background_task, request.data, job_id=job_uuid, retry=Retry(max=10, interval=20))
            return jsonify({"job_id": job.id})
        
        
    except Exception as e:
        return jsonify({"error": str(e)})
            


@app.route("/process/<job_id>", methods=["GET"])
def health(job_id):
    def event_stream():
        while True:
            try:
                job = Job.fetch(job_id, connection=r)
                
                status = job.get_status()
                result = job.result
                
                yield f"data: {status}\n\n result: {result}\n\n"
                
                if status in ["finished", "failed"]:
                    break

                time.sleep(10)
            except Exception as e:
                yield f"data: {e}\n\n"
                break

            
    return Response(event_stream(), mimetype="text/event-stream")


@app.route("/process/v1/<job_id>", methods=["GET"])
def healthV1(job_id):
    job = Job.fetch(job_id, connection=r)
    
    return jsonify ({
        "hostname": socket.gethostname(),
        "job_id": job.id,   
        "status": job.get_status(),
        "result": job.result
    })
    
def start_worker():
    worker = Worker([q], connection=r)
    worker.work(with_scheduler=True)
    
@app.route("/status", methods=["GET"])
def status():
    register = q.job_ids
    return jsonify({"hostname": socket.gethostname(), "job_ids": register})

if __name__ == "__main__":
    Process(target=start_worker).start()
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

#docker build -t flask-app .
#docker run -d --name flask-app -p 8000:8000 flask-app
#docker run -p 8000:8000 flask-app