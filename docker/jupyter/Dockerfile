FROM debian

MAINTAINER Rebase Inc. <raphael@joinrebase.com>


ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        locales \
        python3-dev \
        python3-pip && \
    apt-get clean && \
    dpkg-reconfigure locales && \
    locale-gen en_US.UTF-8 && \
    echo "America/Los_Angeles" > /etc/timezone && \
    dpkg-reconfigure --frontend noninteractive tzdata && \
    apt-get autoremove && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

COPY ./requirements.txt /requirements.txt

RUN easy_install3 -U pip && \
    pip3 install -r /requirements.txt && \
    rm -rf /root/.cache/pip/*

WORKDIR /crawler

COPY ./cmd.bash /cmd.bash

ENV PYTHONPATH=/api

CMD ["/cmd.bash"]
