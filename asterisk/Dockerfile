FROM omnileads/asterisk_base_img:241115.01 as run

COPY conf/* /etc/asterisk/
COPY build/docker-entrypoint.sh /docker-entrypoint.sh

RUN chmod 750 -R /var/spool/asterisk
RUN useradd -M omnileads
RUN chown -R omnileads:omnileads /var/lib/asterisk /etc/asterisk /usr/lib/asterisk /docker-entrypoint.sh /var/spool/asterisk /var/log/asterisk

ENTRYPOINT ["/docker-entrypoint.sh"]
