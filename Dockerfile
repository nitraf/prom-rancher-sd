FROM frolvlad/alpine-python3

LABEL Maintainer "dzmitry@akunevich.com"
LABEL Name "Dzmitry Akunevich"
LABEL Version "1.0.2"

RUN apk add --update -t deps wget ca-certificates curl jq \
    && apk del --purge deps \
    && rm /var/cache/apk/*

RUN pip install urllib3

COPY prom-rancher-sd.py /
RUN chmod +x /prom-rancher-sd.py

VOLUME /prom-rancher-sd-data

CMD ["/prom-rancher-sd.py"]
