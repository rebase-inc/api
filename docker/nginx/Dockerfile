FROM nginx

RUN apt-get update && \
    apt-get install -y wget && \
    wget https://dl.eff.org/certbot-auto && \
    chmod a+x certbot-auto

COPY nginx.conf /etc/nginx/nginx.conf

COPY default-443.conf /etc/nginx/default-443.conf

COPY default-80.conf /etc/nginx/default-80.conf

COPY nginx-ssl.conf /etc/nginx/nginx-ssl.conf

COPY api_proxy.conf /etc/nginx/api_proxy.conf

COPY listen.bash /usr/bin/listen

RUN mkdir -p /etc/letsencrypt/webrootauth && \
    ln -sf /etc/nginx/default-443.conf /etc/nginx/conf.d/default.conf

