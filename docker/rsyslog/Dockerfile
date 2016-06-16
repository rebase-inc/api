FROM alpine

RUN apk add --update \
    rsyslog \
    && rm -rf /var/cache/apk/*

COPY rsyslog.conf /etc/rsyslog.conf
COPY rotate_log /usr/bin/rotate_log

EXPOSE 514/udp

CMD ["rsyslogd", "-n"]
