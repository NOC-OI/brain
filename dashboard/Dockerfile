FROM python:3.9.20-bookworm
WORKDIR /app
SHELL ["/bin/bash", "-c"]
RUN pip install flask requests pyjwt gunicorn pika
COPY flask/src /app
WORKDIR /app
RUN mkdir -p temp
ENTRYPOINT ["gunicorn -w 4 -b 0.0.0.0 'main:app'"]
STOPSIGNAL SIGQUIT
