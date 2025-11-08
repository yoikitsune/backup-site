#!/bin/bash

# Script pour configurer rapidement l'environnement de test

echo "🚀 Configuration de l'environnement de test pour backup-site"

# Vérifie si Docker est installé
if ! command -v docker &> /dev/null; then
    echo "❌ Docker n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérifie si docker compose est installé
if ! docker compose version &> /dev/null; then
    echo "❌ docker compose n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Génère les clés SSH de test
echo "🔑 Génération des clés SSH de test..."
ssh-keygen -t rsa -b 4096 -f ~/.ssh/test_id_rsa -N "" -q

# Démarre les serveurs Docker
echo "🐳 Démarrage des serveurs Docker..."
docker compose -f compose.yml up -d

# Attend que le serveur SSH soit prêt
echo "⏳ Attente du démarrage du serveur SSH..."
sleep 10

# Copie la clé publique sur le serveur
echo "📤 Copie de la clé publique sur le serveur de test..."
ssh-copy-id -i ~/.ssh/test_id_rsa.pub -p 2222 -o StrictHostKeyChecking=no testuser@localhost

# Test la connexion
echo "🔍 Test de la connexion SSH..."
if ssh -i ~/.ssh/test_id_rsa -p 2222 -o StrictHostKeyChecking=no testuser@localhost "echo 'Connexion réussie!'" > /dev/null 2>&1; then
    echo "✅ Connexion SSH réussie!"
else
    echo "❌ Échec de la connexion SSH"
    exit 1
fi

# Crée la configuration de test
echo "📄 Création de la configuration de test..."
cd ../../
backup-site config init config/test-docker.yaml

# Met à jour la configuration avec les bonnes valeurs
cat > config/test-docker.yaml << EOF
site:
  name: "test-site-docker"
  provider: "FOURNISSEUR_HEBERGEMENT"
  app_type: "wordpress"
  
ssh:
  host: "localhost"
  user: "testuser"
  port: 2222
  private_key_path: "~/.ssh/test_id_rsa"
  public_key_path: "~/.ssh/test_id_rsa.pub"

files:
  remote_path: "/home/testuser/www"
  include_patterns:
    - "wp-content/**"
    - "wp-config.php"
    - ".htaccess"
  exclude_patterns:
    - "wp-content/cache/**"
    - "*.log"

database:
  host: "localhost"
  port: 3306
  name: "test_wp"
  user: "testuser"
  password: "testpass"

backup:
  destination: "./backups/test-docker"
  compression: "gzip"
  retention_days: 7
EOF

echo "✅ Configuration terminée!"
echo ""
echo "🎯 Prochaines étapes :"
echo "1. Testez la connexion SSH :"
echo "   backup-site ssh test config/test-docker.yaml"
echo ""
echo "2. Validez la configuration :"
echo "   backup-site config validate config/test-docker.yaml"
echo ""
echo "3. Pour arrêter les serveurs :"
echo "   cd docker/test-ssh-server && docker compose -f compose.yml down"
