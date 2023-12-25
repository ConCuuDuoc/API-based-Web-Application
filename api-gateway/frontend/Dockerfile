FROM ubuntu:22.04

WORKDIR /frontend

COPY requirements.txt .

RUN apt update

RUN apt install -y gunicorn3 python3-pip libpq-dev

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY . /frontend

EXPOSE 5015

CMD ["gunicorn3", "--bind", "0.0.0.0:5015", "app:app"]