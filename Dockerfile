FROM python:3.10

WORKDIR /app

COPY Ex4_Server_Omri_Krelman.py ./

CMD [ "python", "./Ex4_Server_Omri_Krelman" ]
