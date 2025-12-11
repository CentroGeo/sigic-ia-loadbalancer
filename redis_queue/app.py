from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from rq import Queue, Worker, Retry
from rq.job import Job
from redis import Redis
from task import background_task
from multiprocessing import Process
from flasgger import Swagger
import os
import socket
import requests
import time
import json
import uuid

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")
load_balance_host = os.getenv("BALANCER_HOST", "nginx")
load_balance_port = os.getenv("BALANCER_PORT", "80")

r = Redis(host=redis_host, port=redis_port)
redis_dis = Redis(host=redis_host, port=redis_port, decode_responses=True)
q = Queue(connection=r)

app = Flask(__name__)
swagger = Swagger(app)
#CORS(app)
#CORS(app, resources={r"/*": {"origins": "*", "allow_headers": "*", "expose_headers": "*"}})

@app.route("/start", methods=["POST"])
def start():
    """
    Start a new job
    ---
    parameters:
      - name: data
        in: body
        type: string
        required: true
    responses:
      200:
        description: Start a new job
        schema:
          type: object
          properties:
            job_id:
              type: string
            session_id:
              type: string
              example: 0c4a4c2e-1d5e-4d7d-9d6a-8a8a8a8a8a8a
            chat_id:
              type: integer
              example: 0     
    """
    session_id = str(uuid.uuid4())
    data = json.loads(request.data)
    print("####START!!!!!")
    
    data["session_id"] = session_id
    #if(data["type"] == "Preguntar" or data["type"] == "RAG"):
    headers = dict(request.headers)
    headers["Content-Type"] = "application/json"
    
    payload = {
        "data": data,
        "headers": headers
    }
    
    if(data["chat_id"] == 0):
        url = f"http://{load_balance_host}:{load_balance_port}/llmb/api/chat/history/generate"
            
        respuesta = requests.post(
            url,
            headers=headers,
            data=json.dumps(data),
        )

        if respuesta.status_code == 200:
            data["chat_id"] = respuesta.json()["chat_id"]
            print("Solicitud exitosa!!!", data["chat_id"])
            
            job = q.enqueue(background_task, json.dumps(payload), job_id=session_id, retry=Retry(max=10, interval=20))
            
            return jsonify({"job_id": job.id, 'session_id': session_id, "chat_id":data["chat_id"]})
        else:
            return jsonify({"error": str(respuesta.status_code)})            

    else:
        job = q.enqueue(background_task, json.dumps(payload), job_id=session_id, retry=Retry(max=10, interval=20))
        print(f"Job ID: {job.id}")
        return jsonify({"job_id": job.id, 'session_id': session_id})    

@app.route("/process/<job_id>", methods=["GET"])
def health(job_id):
    def event_stream():
        while True:
            try:
                job = Job.fetch(job_id, connection=r)
                
                status = job.get_status()
                result = job.result
                
                yield f"data: {json.dumps({'status': status, 'result': result})}\n\n"
                
                if status in ["finished", "failed"]:
                    break

                time.sleep(0.2)
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

@app.route("/stream/<session_id>", methods=["GET"])
def stream_from_redis(session_id):
    """
    Stream data from Redis
    ---
    parameters:
      - name: session_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Stream data from Redis
        schema:
          type: string
          example: "data: [STREAM_COMPLETED]\n\n"
          default: "data: [STREAM_COMPLETED]\n\n"
    """
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400

    stream_key = f"stream:{session_id}"
    done_key = f"stream_done:{session_id}"

    def generate():
        last_index = 0
        job = Job.fetch(session_id, connection=r)
            
        while True:
            status = job.get_status()
            result = job.result
            
            yield f"status: {json.dumps({'status': status, 'result': result})}\n\n"
                
            messages = redis_dis.lrange(stream_key, last_index, -1)
            for msg in messages:
                info = {
                    "status": status,
                    "message": msg
                }
                yield f"data: {json.dumps(info)}\n\n"
            last_index += len(messages)
                
            # Terminar si hay señal de finalización
            if redis_dis.get(done_key):
                yield "event: done\ndata: [STREAM_COMPLETED]\n\n"
                break

            #time.sleep(0.5)

    return Response(generate(), mimetype="text/event-stream")


if __name__ == "__main__":
    for _ in range(2):
        Process(target=start_worker).start()
        
    port = int(os.environ.get("PORT", 8000))
    app.run(host='0.0.0.0', port=port)

#docker build -t flask-app .
#docker run -d --name flask-app -p 8000:8000 flask-app
#docker run -p 8000:8000 flask-app
