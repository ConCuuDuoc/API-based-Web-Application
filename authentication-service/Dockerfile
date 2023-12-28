FROM ubuntu:22.04

RUN apt-get update && apt install -y gunicorn3 python3-pip 

WORKDIR /authentication-service

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /authentication-service

EXPOSE 5012

CMD ["gunicorn3", "--bind", "0.0.0.0:5012", "app:app"]
