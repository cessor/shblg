FROM python:latest
ENV PYTHONUNBUFFERED=1
COPY src/ /var/shit/
WORKDIR /var/shit/
RUN python3 -m pip install -r requirements.txt --no-cache-dir
EXPOSE 8000
CMD ["/bin/sh", "./run.sh"]
