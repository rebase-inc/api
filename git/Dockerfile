FROM debian
RUN apt-get update && \
    apt-get install -y \
        git \
        ssh && \
    service ssh start && \
    mkdir git
COPY ./filter /usr/bin/filter
