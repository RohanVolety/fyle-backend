FROM python:3.8

WORKDIR /core


COPY . /core


RUN pip install -r requirements.txt


EXPOSE 7755  


CMD ["gunicorn", "--bind", "0.0.0.0:7755", "-c", "gunicorn_config.py", "core.server:app"]


