FROM python:3.10-slim

WORKDIR /app
#COPY apicontroller.py .
COPY app.py .
COPY task.py .

RUN pip install flask
RUN pip install redis
RUN pip install requests
RUN pip install rq
RUN pip install flask-cors
RUN pip install flasgger

#CMD ["python", "apicontroller.py"]
CMD ["python", "app.py"]

#docker run --name redis -p 6379:6379 -d redis
#docker build -t flask-app .
#docker run -p 8001:8001 flask-app