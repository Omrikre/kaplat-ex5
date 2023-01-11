FROM python:3.10

WORKDIR /app

COPY Ex4_Server_Omri_Krelman.py .
COPY requirements.txt .

RUN pip install -r requirements.txt

CMD [ "python", "Ex4_Server_Omri_Krelman.py" ]