FROM alpine

RUN apk add --update \
    rsyslog \
    && rm -rf /var/cache/apk/*

COPY rsyslog.conf /etc/rsyslog.conf
COPY main /usr/bin/main

EXPOSE 514/udp

CMD ["/usr/bin/main"]
