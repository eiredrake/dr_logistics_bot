# base image of the host os
FROM python:3.9.5
LABEL maintainer="eiredrake@gmail.com"

RUN mkdir /dr_logistics_bot

WORKDIR /dr_logistics_bot

COPY /docker/requirements.txt .

RUN pip install -r requirements.txt

COPY LogisticsBot.py .

RUN mkdir /dr_logistics_bot/src

COPY /src /dr_logistics_bot/src