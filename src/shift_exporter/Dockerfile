FROM python:3.10-slim

WORKDIR /home

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY .env .
COPY ProcOncall.py .
COPY main.py .

EXPOSE 8002

CMD ["python", "main.py"]
