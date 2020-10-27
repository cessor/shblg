FROM alpine:latest
RUN apk add --update python3 python3-dev py-pip build-base gettext\
    && rm -rf /var/cache/apk/*\
    && python3 -m pip install --no-cache-dir --upgrade pip
COPY src/ /var/shit/
WORKDIR /var/shit/
RUN python3 -m pip install -r requirements.txt --no-cache-dir
EXPOSE 8000
CMD ["/bin/sh", "./run.sh"]
