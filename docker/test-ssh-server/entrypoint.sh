#!/bin/sh

# Définition du mot de passe root
echo "root:testpass" | chpasswd

# Définition du mot de passe pour l'utilisateur de test
echo "testuser:testpass" | chpasswd

# Génération des clés hôtes
ssh-keygen -A

# Démarrage du serveur SSH
echo "Démarrage du serveur SSH..."
exec /usr/sbin/sshd -D -e
