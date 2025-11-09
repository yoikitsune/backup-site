FROM alpine:latest

# Installer OpenSSH
RUN apk add --no-cache openssh openssh-keygen bash

# Créer le répertoire SSH
RUN mkdir -p /etc/ssh

# Générer les clés SSH du serveur
RUN ssh-keygen -A

# Créer l'utilisateur SSH avec mot de passe
RUN addgroup -S sshuser && adduser -S -G sshuser -h /home/sshuser -s /bin/bash sshuser

# Créer les répertoires
RUN mkdir -p /home/sshuser/www /home/sshuser/backups && \
    chown -R sshuser:sshuser /home/sshuser

# Configurer SSH pour accepter les connexions par mot de passe
RUN sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    sed -i 's/PasswordAuthentication no/PasswordAuthentication yes/' /etc/ssh/sshd_config

# Copier le script d'entrée
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22

ENTRYPOINT ["/entrypoint.sh"]
