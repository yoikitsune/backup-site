#!/bin/bash

# Script d'entrée pour le serveur SSH

# Récupérer les variables d'environnement
SSH_USER=${SSH_USER:-testuser}
SSH_PASSWORD=${SSH_PASSWORD:-testpass}

# Créer l'utilisateur s'il n'existe pas
if ! id "$SSH_USER" &>/dev/null; then
    addgroup -S "$SSH_USER"
    adduser -S -G "$SSH_USER" -h "/home/$SSH_USER" -s /bin/bash "$SSH_USER"
    mkdir -p "/home/$SSH_USER/www" "/home/$SSH_USER/backups"
    chown -R "$SSH_USER:$SSH_USER" "/home/$SSH_USER"
fi

# Définir le mot de passe
echo "$SSH_USER:$SSH_PASSWORD" | chpasswd

# Démarrer le serveur SSH
/usr/sbin/sshd -D
