FROM python:3.4

ENV VERSION 0.1.0

RUN pip3 install echo==VERSION

EXPOSE 9876
