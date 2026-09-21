FROM python:3.12-slim

WORKDIR /backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

#Busca o requirements da raiz e copia para o container

COPY requirements.txt /backend/
RUN pip install --upgrade pip && pip install -r requirements.txt

#Copia o conteúdo da pasta backend local para dentro do container

COPY backend/ /backend/