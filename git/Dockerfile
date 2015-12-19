FROM debian
RUN apt-get update && \
    apt-get install -y \
        daemontools \
        git \
        openssh-server
COPY ./sshd_config /etc/ssh/sshd_config
RUN mkdir -p /git /git/sshd /var/run/sshd && \
    echo "#!/bin/bash\nexec /usr/sbin/sshd" > /git/sshd/run && \
    chmod +x /git/sshd/run
EXPOSE 22
COPY .ssh/id_rsa.pub /root/.ssh/authorized_keys
ENTRYPOINT ["/usr/sbin/sshd", "-D"]
COPY ./filter /usr/bin/filter
