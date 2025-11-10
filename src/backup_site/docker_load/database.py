"""Module de chargement de la base de données dans Docker local.

Stratégie :
- Utilise `docker cp` pour copier le dump dans le container MySQL
- Utilise `docker exec` pour charger le dump
- Extrait les infos du wp-config.php via wp-cli (robuste)
- Crée automatiquement la base et l'utilisateur
- Pas de SSH, accès direct au container Docker

Flux :
  1. Extraire DB_NAME, DB_USER, DB_PASSWORD depuis wp-config.php via wp-cli
  2. Créer la base de données et l'utilisateur dans MySQL
  3. docker cp dump.sql.gz mysql_container:/tmp/
  4. docker exec mysql_container bash -c "gunzip < /tmp/dump.sql.gz | mysql ..."
"""

import logging
import subprocess
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger(__name__)


class DockerDatabaseLoad:
    """Gère le chargement de la base de données dans Docker local."""
    
    def __init__(
        self,
        container_name: str,
        wordpress_container: Optional[str] = None,
        db_name: Optional[str] = None,
        db_user: Optional[str] = None,
        db_password: Optional[str] = None,
    ):
        """Initialise le gestionnaire de chargement de BDD.
        
        Args:
            container_name: Nom du container MySQL/MariaDB Docker
            wordpress_container: Nom du container WordPress (pour extraire les infos via wp-cli)
            db_name: Nom de la base de données (optionnel si wordpress_container fourni)
            db_user: Utilisateur de la base de données (optionnel si wordpress_container fourni)
            db_password: Mot de passe de la base de données (optionnel si wordpress_container fourni)
        """
        self.container_name = container_name
        self.wordpress_container = wordpress_container
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
    
    def _extract_db_config_from_wordpress(self) -> Tuple[str, str, str]:
        """Extrait les infos de la BDD depuis wp-config.php via wp-cli.
        
        Returns:
            Tuple (db_name, db_user, db_password)
            
        Raises:
            RuntimeError: Si wp-cli n'est pas disponible ou si l'extraction échoue
        """
        if not self.wordpress_container:
            raise RuntimeError("wordpress_container n'est pas configuré")
        
        logger.info(f"Extraction des infos BDD depuis {self.wordpress_container} via wp-cli")
        
        try:
            # Extrait DB_NAME
            result = subprocess.run(
                ["docker", "exec", self.wordpress_container, "wp", "--allow-root", "config", "get", "DB_NAME"],
                check=True,
                capture_output=True,
                text=True
            )
            db_name = result.stdout.strip()
            
            # Extrait DB_USER
            result = subprocess.run(
                ["docker", "exec", self.wordpress_container, "wp", "--allow-root", "config", "get", "DB_USER"],
                check=True,
                capture_output=True,
                text=True
            )
            db_user = result.stdout.strip()
            
            # Extrait DB_PASSWORD
            result = subprocess.run(
                ["docker", "exec", self.wordpress_container, "wp", "--allow-root", "config", "get", "DB_PASSWORD"],
                check=True,
                capture_output=True,
                text=True
            )
            db_password = result.stdout.strip()
            
            logger.info(f"✓ Infos BDD extraites: {db_name} / {db_user}")
            return db_name, db_user, db_password
            
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de l'extraction via wp-cli: {e.stderr}")
    
    def _create_database_and_user(self, db_name: str, db_user: str, db_password: str) -> None:
        """Crée la base de données et l'utilisateur dans MySQL.
        
        Args:
            db_name: Nom de la base de données
            db_user: Utilisateur de la base de données
            db_password: Mot de passe de la base de données
            
        Raises:
            RuntimeError: Si la création échoue
        """
        logger.info(f"Création de la base {db_name} et utilisateur {db_user}")
        
        # Commande SQL pour créer la base et l'utilisateur
        sql_cmd = (
            f"CREATE DATABASE IF NOT EXISTS {db_name}; "
            f"GRANT ALL PRIVILEGES ON {db_name}.* TO '{db_user}'@'%' IDENTIFIED BY '{db_password}'; "
            f"FLUSH PRIVILEGES;"
        )
        
        try:
            subprocess.run(
                ["docker", "exec", self.container_name, "mariadb", "-u", "root", "-proot", "-e", sql_cmd],
                check=True,
                capture_output=True,
                text=True
            )
            logger.info(f"✓ Base {db_name} et utilisateur {db_user} créés")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Erreur lors de la création de la base: {e.stderr}")
    
    def _build_load_command(self, dump_file: str, is_compressed: bool) -> str:
        """Construit la commande de chargement MySQL/MariaDB.
        
        Args:
            dump_file: Chemin du fichier dump dans le container
            is_compressed: Si le fichier est compressé (gzip)
            
        Returns:
            Commande de chargement complète
        """
        # Commande mariadb de base (compatible avec MySQL aussi)
        db_cmd = (
            f"mariadb -u {self.db_user} -p{self.db_password} {self.db_name}"
        )
        
        # Si le fichier est compressé, ajoute gunzip
        if is_compressed:
            cmd = f"gunzip < {dump_file} | {db_cmd}"
        else:
            cmd = f"{db_cmd} < {dump_file}"
        
        return cmd
    
    def load_from_file(
        self,
        dump_path: Path,
    ) -> Tuple[bool, str]:
        """Charge la base de données depuis un fichier dump dans Docker.
        
        Stratégie :
        1. Extrait les infos BDD depuis wp-config.php via wp-cli (si wordpress_container fourni)
        2. Crée la base de données et l'utilisateur dans MySQL
        3. Copie le dump dans le container via docker cp
        4. Charge le dump via docker exec
        5. Nettoie les fichiers temporaires
        
        Args:
            dump_path: Chemin local du fichier dump (SQL ou SQL.GZ)
            
        Returns:
            Tuple (succès, message)
            
        Raises:
            FileNotFoundError: Si le dump n'existe pas
            RuntimeError: Si une commande Docker échoue
        """
        try:
            # Vérifie que le dump existe
            if not dump_path.exists():
                raise FileNotFoundError(f"Le dump {dump_path} n'existe pas")
            
            # Étape 0 : Extrait les infos BDD si wordpress_container est fourni
            if self.wordpress_container:
                db_name, db_user, db_password = self._extract_db_config_from_wordpress()
                self.db_name = db_name
                self.db_user = db_user
                self.db_password = db_password
            elif not (self.db_name and self.db_user and self.db_password):
                raise RuntimeError("Infos BDD manquantes (wordpress_container ou db_name/db_user/db_password requis)")
            
            # Étape 1 : Crée la base de données et l'utilisateur
            self._create_database_and_user(self.db_name, self.db_user, self.db_password)
            
            # Détecte si le fichier est compressé
            is_compressed = dump_path.suffix == '.gz'
            
            dump_name = dump_path.name
            temp_dump = f"/tmp/{dump_name}"
            
            logger.info(f"Chargement de {dump_name} vers {self.container_name}:{self.db_name}")
            
            # Étape 2 : Copie le dump dans le container via docker cp
            logger.debug(f"Copie de {dump_path} vers {self.container_name}:{temp_dump}")
            try:
                subprocess.run(
                    ["docker", "cp", str(dump_path), f"{self.container_name}:{temp_dump}"],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Erreur lors de la copie Docker: {e.stderr}")
            
            # Étape 3 : Charge le dump via docker exec
            logger.debug(f"Chargement du dump {temp_dump}")
            load_cmd = self._build_load_command(temp_dump, is_compressed)
            try:
                subprocess.run(
                    ["docker", "exec", self.container_name, "bash", "-c", load_cmd],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Erreur lors du chargement: {e.stderr}")
            
            # Étape 4 : Nettoie le fichier temporaire
            logger.debug(f"Suppression du fichier temporaire {temp_dump}")
            try:
                subprocess.run(
                    ["docker", "exec", self.container_name, "rm", "-f", temp_dump],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError:
                logger.warning(f"Impossible de supprimer {temp_dump}")
            
            message = (
                f"✓ Chargement de la base de données réussi\n"
                f"  Dump: {dump_name}\n"
                f"  Container: {self.container_name}\n"
                f"  Base: {self.db_name}\n"
                f"  Utilisateur: {self.db_user}\n"
                f"  Taille: {dump_path.stat().st_size / 1024:.2f} KB"
            )
            logger.info(message)
            
            return True, message
            
        except FileNotFoundError as e:
            error_msg = f"Erreur: {str(e)}"
            logger.error(error_msg)
            raise
        except RuntimeError as e:
            error_msg = f"Erreur lors du chargement: {str(e)}"
            logger.error(error_msg)
            raise
        except Exception as e:
            error_msg = f"Erreur inattendue: {str(e)}"
            logger.error(error_msg)
            raise
    
    def load_from_stream(
        self,
        dump_data: bytes,
        is_compressed: bool = True,
    ) -> Tuple[bool, str]:
        """Charge la base de données depuis un flux de données (dump en mémoire).
        
        Utile pour les tests ou pour traiter les données en mémoire.
        
        Args:
            dump_data: Données binaires du dump SQL (compressé ou non)
            is_compressed: Si les données sont compressées (gzip)
            
        Returns:
            Tuple (succès, message)
            
        Raises:
            RuntimeError: Si une commande Docker échoue
        """
        try:
            # Crée un fichier temporaire local
            import tempfile
            suffix = ".sql.gz" if is_compressed else ".sql"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
                tmp.write(dump_data)
                tmp_path = Path(tmp.name)
            
            try:
                # Utilise load_from_file pour faire le travail
                return self.load_from_file(tmp_path)
            finally:
                # Nettoie le fichier temporaire
                tmp_path.unlink(missing_ok=True)
            
        except Exception as e:
            error_msg = f"Erreur lors du chargement depuis un flux: {str(e)}"
            logger.error(error_msg)
            raise
