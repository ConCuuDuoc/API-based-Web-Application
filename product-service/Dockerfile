FROM ubuntu:22.04

RUN apt-get update && apt install -y gunicorn3 python3-pip 

WORKDIR /product-service

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . /product-service

EXPOSE 8888

CMD ["gunicorn3", "--bind", "0.0.0.0:8888", "app:app"]