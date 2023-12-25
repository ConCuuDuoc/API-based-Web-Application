FROM ubuntu:22.04

RUN apt-get update && apt install -y gunicorn3 python3-pip 

WORKDIR /authorization-service

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /authorization-service

EXPOSE 5013

CMD ["gunicorn3", "--bind", "0.0.0.0:5013", "app:app"]
