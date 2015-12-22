FROM rebase/api
RUN apt-get update && \
    apt-get install -y \
        git \
        openssh-server
COPY sshd_config /etc/ssh/sshd_config
COPY entry_point /usr/sbin/entry_point
RUN mkdir -p /git \
    /var/run/sshd \
    /root/.ssh && \
    adduser --quiet --disabled-password --gecos "Rebase Git" git && \
    echo "git:foo" | chpasswd
USER git
WORKDIR /home/git
RUN mkdir .ssh && \
    chmod 700 .ssh && \
    touch .ssh/authorized_keys && \
    chmod 600 .ssh/authorized_keys
USER root
WORKDIR /
EXPOSE 22
ENTRYPOINT ["/usr/sbin/entry_point"]
CMD ["bash", "-c", "source /venv/api/bin/activate && pip install -r requirements.txt && python git-worker.py"]
COPY filter /usr/bin/filter
