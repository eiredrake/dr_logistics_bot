# base image of the host os
FROM python:3.9.5

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

LABEL maintainer="eiredrake@gmail.com"

RUN mkdir /dr_logistics

WORKDIR /dr_logistics

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /dr_logistics/

ENV PYTHONPATH "${PYTHONPATH}:/dr_logistics/"
