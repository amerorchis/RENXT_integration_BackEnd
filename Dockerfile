# syntax=docker/dockerfile:1

FROM python:3.10

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
