"""Module de restauration de la base de données MySQL via SSH.

Stratégie :
- Télécharge le dump SQL (compressé ou non) depuis le serveur local vers le client
- Restaure le dump via SSH tunnel (localhost:3306)
- Compatible avec MySQL et MariaDB

Flux :
  SSH → gunzip < database.sql.gz | mysql -h localhost -u user -p db
  ou
  SSH → mysql -h localhost -u user -p db < database.sql
"""

import logging
from pathlib import Path
from typing import Tuple

import paramiko
from paramiko.ssh_exception import SSHException

logger = logging.getLogger(__name__)


class DatabaseRestore:
    """Gère la restauration de la base de données MySQL via SSH."""
    
    def __init__(
        self,
        ssh_client: paramiko.SSHClient,
        db_host: str,
        db_port: int,
        db_name: str,
        db_user: str,
        db_password: str,
    ):
        """Initialise le gestionnaire de restauration de BDD.
        
        Args:
            ssh_client: Client SSH Paramiko connecté
            db_host: Hôte de la base de données (localhost pour SSH tunnel)
            db_port: Port de la base de données (défaut: 3306)
            db_name: Nom de la base de données
            db_user: Utilisateur de la base de données
            db_password: Mot de passe de la base de données
        """
        self.ssh_client = ssh_client
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
    
    def _build_restore_command(self, dump_file: str, is_compressed: bool) -> str:
        """Construit la commande de restauration MySQL.
        
        Args:
            dump_file: Chemin du fichier dump sur le serveur
            is_compressed: Si le fichier est compressé (gzip)
            
        Returns:
            Commande de restauration complète
        """
        # Commande mysql de base
        mysql_cmd = (
            f"mysql -h {self.db_host} -P {self.db_port} "
            f"-u {self.db_user} -p{self.db_password} "
            f"{self.db_name}"
        )
        
        # Si le fichier est compressé, ajoute gunzip
        if is_compressed:
            cmd = f"gunzip < {dump_file} | {mysql_cmd}"
        else:
            cmd = f"{mysql_cmd} < {dump_file}"
        
        return cmd
    
    def restore_from_file(
        self,
        dump_path: Path,
        buffer_size: int = 65536
    ) -> Tuple[bool, str]:
        """Restaure la base de données depuis un fichier dump.
        
        Stratégie :
        1. Crée un répertoire temporaire sur le serveur
        2. Télécharge le dump via SFTP
        3. Restaure le dump via SSH
        4. Nettoie les fichiers temporaires
        
        Args:
            dump_path: Chemin local du fichier dump (SQL ou SQL.GZ)
            buffer_size: Taille du buffer pour le transfert SFTP (défaut: 64KB)
            
        Returns:
            Tuple (succès, message)
            
        Raises:
            FileNotFoundError: Si le dump n'existe pas
            SSHException: Si la commande SSH échoue
            IOError: Si le transfert SFTP échoue
        """
        try:
            # Vérifie que le dump existe
            if not dump_path.exists():
                raise FileNotFoundError(f"Le dump {dump_path} n'existe pas")
            
            # Détecte si le fichier est compressé
            is_compressed = dump_path.suffix == '.gz'
            
            # Génère un nom de fichier temporaire sur le serveur
            dump_name = dump_path.name
            temp_dump = f"/tmp/{dump_name}"
            
            logger.info(f"Restauration de {dump_name} vers la base {self.db_name}")
            
            # Étape 1 : Télécharge le dump via SFTP
            logger.debug(f"Téléchargement de {dump_path} vers {temp_dump}")
            sftp_client = self.ssh_client.open_sftp()
            try:
                sftp_client.put(str(dump_path), temp_dump, callback=None)
            finally:
                sftp_client.close()
            
            # Étape 2 : Restaure le dump via SSH
            logger.debug(f"Restauration du dump {temp_dump}")
            restore_cmd = self._build_restore_command(temp_dump, is_compressed)
            stdin, stdout, stderr = self.ssh_client.exec_command(restore_cmd)
            
            # Vérifie s'il y a eu des erreurs
            stderr_output = stderr.read().decode('utf-8', errors='ignore').strip()
            if stderr_output:
                logger.warning(f"Avertissements MySQL: {stderr_output}")
            
            # Vérifie le code de sortie
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                raise SSHException(
                    f"La commande de restauration a échoué avec le code {exit_status}. "
                    f"Erreur: {stderr_output}"
                )
            
            # Étape 3 : Nettoie le fichier temporaire
            logger.debug(f"Suppression du fichier temporaire {temp_dump}")
            rm_cmd = f"rm -f {temp_dump}"
            stdin, stdout, stderr = self.ssh_client.exec_command(rm_cmd)
            stdout.channel.recv_exit_status()
            
            message = (
                f"✓ Restauration de la base de données réussie\n"
                f"  Dump: {dump_name}\n"
                f"  Base: {self.db_name}\n"
                f"  Taille: {dump_path.stat().st_size / 1024:.2f} KB"
            )
            logger.info(message)
            
            return True, message
            
        except FileNotFoundError as e:
            error_msg = f"Erreur: {str(e)}"
            logger.error(error_msg)
            raise
        except SSHException as e:
            error_msg = f"Erreur SSH lors de la restauration BDD: {str(e)}"
            logger.error(error_msg)
            raise
        except IOError as e:
            error_msg = f"Erreur de transfert SFTP: {str(e)}"
            logger.error(error_msg)
            raise
    
    def restore_from_stream(
        self,
        dump_data: bytes,
        is_compressed: bool = True,
        buffer_size: int = 65536
    ) -> Tuple[bool, str]:
        """Restaure la base de données depuis un flux de données (dump en mémoire).
        
        Utile pour les tests ou pour traiter les données en mémoire.
        
        Args:
            dump_data: Données binaires du dump SQL (compressé ou non)
            is_compressed: Si les données sont compressées (gzip)
            buffer_size: Taille du buffer pour le transfert SFTP (défaut: 64KB)
            
        Returns:
            Tuple (succès, message)
            
        Raises:
            SSHException: Si la commande SSH échoue
            IOError: Si le transfert SFTP échoue
        """
        try:
            # Génère un nom de fichier temporaire
            temp_dump = "/tmp/restore_stream.sql.gz" if is_compressed else "/tmp/restore_stream.sql"
            
            logger.info(f"Restauration depuis un flux vers la base {self.db_name}")
            
            # Étape 1 : Télécharge le flux via SFTP
            logger.debug(f"Téléchargement du flux vers {temp_dump}")
            sftp_client = self.ssh_client.open_sftp()
            try:
                with sftp_client.file(temp_dump, 'wb') as f:
                    f.write(dump_data)
            finally:
                sftp_client.close()
            
            # Étape 2 : Restaure le dump via SSH
            logger.debug(f"Restauration du dump {temp_dump}")
            restore_cmd = self._build_restore_command(temp_dump, is_compressed)
            stdin, stdout, stderr = self.ssh_client.exec_command(restore_cmd)
            
            # Vérifie s'il y a eu des erreurs
            stderr_output = stderr.read().decode('utf-8', errors='ignore').strip()
            if stderr_output:
                logger.warning(f"Avertissements MySQL: {stderr_output}")
            
            # Vérifie le code de sortie
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                raise SSHException(
                    f"La commande de restauration a échoué avec le code {exit_status}. "
                    f"Erreur: {stderr_output}"
                )
            
            # Étape 3 : Nettoie le fichier temporaire
            logger.debug(f"Suppression du fichier temporaire {temp_dump}")
            rm_cmd = f"rm -f {temp_dump}"
            stdin, stdout, stderr = self.ssh_client.exec_command(rm_cmd)
            stdout.channel.recv_exit_status()
            
            message = (
                f"✓ Restauration depuis un flux réussie\n"
                f"  Base: {self.db_name}\n"
                f"  Taille: {len(dump_data) / 1024:.2f} KB"
            )
            logger.info(message)
            
            return True, message
            
        except SSHException as e:
            error_msg = f"Erreur SSH lors de la restauration BDD: {str(e)}"
            logger.error(error_msg)
            raise
        except IOError as e:
            error_msg = f"Erreur de transfert SFTP: {str(e)}"
            logger.error(error_msg)
            raise
