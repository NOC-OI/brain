FROM docker-repo.bodc.me/oceaninfo/l4t-base:j62-r36.4-2
RUN pip install --no-cache pika==1.3.2 requests==2.32.4
COPY src /app
WORKDIR /app
RUN mkdir -p temp
ENTRYPOINT ["python3", "init.py"]
STOPSIGNAL SIGQUIT

