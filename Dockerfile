FROM python:3.6-alpine

WORKDIR /opt/estateminer 
COPY src /opt/estateminer
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "estateminer.py"]
