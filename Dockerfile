FROM python:latest

WORKDIR /opt/estateminer 
COPY src /opt/estateminer
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "data_parser.py"]
