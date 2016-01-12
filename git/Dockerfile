FROM rebase/api
RUN apt-get update && \
    apt-get install -y \
        git \
        openssh-server
COPY sshd_config /etc/ssh/sshd_config
COPY supervisor.conf /etc/git/supervisor.conf
COPY filter /usr/bin/filter
VOLUME /git
RUN mkdir -p /var/run/sshd \
    /root/.ssh && \
    adduser --quiet --disabled-password --gecos "Rebase Git" git && \
    echo "git:foo" | chpasswd && \
    virtualenv -p python2.7 /venv/super && \
    /venv/super/bin/pip install supervisor

USER git
WORKDIR /home/git
RUN mkdir .ssh && \
    chmod 700 .ssh && \
    touch .ssh/authorized_keys && \
    chmod 600 .ssh/authorized_keys
USER root
WORKDIR /
EXPOSE 22
ENTRYPOINT ["/venv/super/bin/supervisord", "--nodaemon", "--configuration", "/etc/git/supervisor.conf"]
