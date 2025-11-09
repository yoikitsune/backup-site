#!/bin/sh

# Script d'initialisation de MySQL pour le conteneur de test

echo "Initialisation de MySQL..."
mysql_install_db --user=mysql --datadir=/var/lib/mysql 2>&1 | grep -v "Using default"

echo "Démarrage de MySQL..."
/usr/bin/mysqld --user=mysql --datadir=/var/lib/mysql --skip-grant-tables --bind-address=0.0.0.0 &

# Attendre que MySQL soit prêt
echo "Attente du démarrage de MySQL..."
for i in {1..30}; do
  if mysql -u root -e "SELECT 1" > /dev/null 2>&1; then
    echo "MySQL est prêt"
    break
  fi
  echo "Tentative $i/30..."
  sleep 1
done

# Création de la base de données de test
echo "Création de la base de données de test..."
mysql -u root << 'EOFMYSQL'
CREATE DATABASE IF NOT EXISTS test_wp;
CREATE USER 'testuser'@'%' IDENTIFIED BY 'testpass';
GRANT ALL PRIVILEGES ON test_wp.* TO 'testuser'@'%';
FLUSH PRIVILEGES;

USE test_wp;

CREATE TABLE wp_posts (
  ID bigint(20) NOT NULL AUTO_INCREMENT,
  post_author bigint(20) NOT NULL DEFAULT 0,
  post_date datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  post_date_gmt datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  post_content longtext NOT NULL,
  post_title text NOT NULL,
  post_excerpt text NOT NULL,
  post_status varchar(20) NOT NULL DEFAULT 'publish',
  comment_status varchar(20) NOT NULL DEFAULT 'open',
  ping_status varchar(20) NOT NULL DEFAULT 'open',
  post_password varchar(255) NOT NULL DEFAULT '',
  post_name varchar(200) NOT NULL DEFAULT '',
  to_ping text NOT NULL,
  pinged text NOT NULL,
  post_modified datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  post_modified_gmt datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  post_content_filtered longtext NOT NULL,
  post_parent bigint(20) NOT NULL DEFAULT 0,
  guid varchar(255) NOT NULL DEFAULT '',
  menu_order int(11) NOT NULL DEFAULT 0,
  post_type varchar(20) NOT NULL DEFAULT 'post',
  post_mime_type varchar(100) NOT NULL DEFAULT '',
  comment_count bigint(20) NOT NULL DEFAULT 0,
  PRIMARY KEY (ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO wp_posts (post_author, post_date, post_date_gmt, post_content, post_title, post_status, post_name, post_type)
VALUES 
  (1, NOW(), NOW(), 'Contenu du premier article', 'Premier article', 'publish', 'premier-article', 'post'),
  (1, NOW(), NOW(), 'Contenu du deuxième article', 'Deuxième article', 'publish', 'deuxieme-article', 'post');
EOFMYSQL

echo "Base de données de test créée avec succès"
