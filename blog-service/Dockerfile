FROM ubuntu:22.04

RUN apt-get update && apt install -y gunicorn3 python3-pip 

WORKDIR /blog-service

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /blog-service

EXPOSE 7777

CMD ["gunicorn3", "--bind", "0.0.0.0:7777", "app:app"]