FROM alpine:latest

# Installation des paquets nécessaires
RUN apk add --no-cache openssh-server mysql-client

# Création de l'utilisateur de test
RUN adduser -D -s /bin/sh testuser

# Configuration SSH
RUN mkdir -p /run/sshd && \
    echo "PermitRootLogin yes" >> /etc/ssh/sshd_config && \
    echo "PasswordAuthentication yes" >> /etc/ssh/sshd_config && \
    echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config

# Création des répertoires de test
RUN mkdir -p /home/testuser/www && \
    mkdir -p /home/testuser/.ssh && \
    chown -R testuser:testuser /home/testuser

# Création d'un faux site WordPress de test
RUN mkdir -p /home/testuser/www/wp-content/{themes,plugins,uploads} && \
    echo "<?php define('DB_NAME', 'test_wp'); ?>" > /home/testuser/www/wp-config.php && \
    echo "# BEGIN WordPress" > /home/testuser/www/.htaccess && \
    echo "RewriteEngine On" >> /home/testuser/www/.htaccess && \
    echo "# END WordPress" >> /home/testuser/www/.htaccess

# Script de démarrage
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22

CMD ["/entrypoint.sh"]
