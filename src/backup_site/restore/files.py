"""Module de restauration des fichiers depuis une archive tar.gz via SSH.

Stratégie :
- Télécharge l'archive tar.gz depuis le serveur local vers le client
- Extrait l'archive localement ou via SSH sur le serveur distant
- Compatible avec GNU tar et BusyBox tar

Flux :
  SSH → tar -xzf archive.tar.gz -C destination
"""

import logging
from pathlib import Path
from typing import Tuple

import paramiko
from paramiko.ssh_exception import SSHException

logger = logging.getLogger(__name__)


class FileRestore:
    """Gère la restauration des fichiers depuis une archive tar.gz via SSH."""
    
    def __init__(
        self,
        ssh_client: paramiko.SSHClient,
        remote_path: str,
    ):
        """Initialise le gestionnaire de restauration des fichiers.
        
        Args:
            ssh_client: Client SSH Paramiko connecté
            remote_path: Chemin distant où restaurer les fichiers
        """
        self.ssh_client = ssh_client
        self.remote_path = remote_path
    
    def restore_from_file(
        self,
        archive_path: Path,
        buffer_size: int = 65536
    ) -> Tuple[bool, str]:
        """Restaure les fichiers depuis une archive tar.gz.
        
        Stratégie :
        1. Crée un répertoire temporaire sur le serveur
        2. Télécharge l'archive via SFTP
        3. Extrait l'archive sur le serveur
        4. Nettoie les fichiers temporaires
        
        Args:
            archive_path: Chemin local de l'archive tar.gz
            buffer_size: Taille du buffer pour le transfert SFTP (défaut: 64KB)
            
        Returns:
            Tuple (succès, message)
            
        Raises:
            FileNotFoundError: Si l'archive n'existe pas
            SSHException: Si la commande SSH échoue
            IOError: Si le transfert SFTP échoue
        """
        try:
            # Vérifie que l'archive existe
            if not archive_path.exists():
                raise FileNotFoundError(f"L'archive {archive_path} n'existe pas")
            
            # Génère un nom de fichier temporaire sur le serveur
            archive_name = archive_path.name
            temp_archive = f"/tmp/{archive_name}"
            
            logger.info(f"Restauration de {archive_path.name} vers {self.remote_path}")
            
            # Étape 1 : Télécharge l'archive via SFTP
            logger.debug(f"Téléchargement de {archive_path} vers {temp_archive}")
            sftp_client = self.ssh_client.open_sftp()
            try:
                sftp_client.put(str(archive_path), temp_archive, callback=None)
            finally:
                sftp_client.close()
            
            # Étape 2 : Extrait l'archive sur le serveur
            logger.debug(f"Extraction de {temp_archive} vers {self.remote_path}")
            extract_cmd = f"tar -xzf {temp_archive} -C {self.remote_path}"
            stdin, stdout, stderr = self.ssh_client.exec_command(extract_cmd)
            
            # Vérifie s'il y a eu des erreurs
            stderr_output = stderr.read().decode('utf-8', errors='ignore').strip()
            if stderr_output:
                logger.warning(f"Avertissements tar: {stderr_output}")
            
            # Vérifie le code de sortie
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                raise SSHException(
                    f"La commande tar a échoué avec le code {exit_status}. "
                    f"Erreur: {stderr_output}"
                )
            
            # Étape 3 : Nettoie le fichier temporaire
            logger.debug(f"Suppression du fichier temporaire {temp_archive}")
            rm_cmd = f"rm -f {temp_archive}"
            stdin, stdout, stderr = self.ssh_client.exec_command(rm_cmd)
            stdout.channel.recv_exit_status()  # Attend la fin de la commande
            
            message = (
                f"✓ Restauration des fichiers réussie\n"
                f"  Archive: {archive_name}\n"
                f"  Destination: {self.remote_path}\n"
                f"  Taille: {archive_path.stat().st_size / 1024 / 1024:.2f} MB"
            )
            logger.info(message)
            
            return True, message
            
        except FileNotFoundError as e:
            error_msg = f"Erreur: {str(e)}"
            logger.error(error_msg)
            raise
        except SSHException as e:
            error_msg = f"Erreur SSH lors de la restauration: {str(e)}"
            logger.error(error_msg)
            raise
        except IOError as e:
            error_msg = f"Erreur de transfert SFTP: {str(e)}"
            logger.error(error_msg)
            raise
    
    def restore_from_stream(
        self,
        archive_data: bytes,
        buffer_size: int = 65536
    ) -> Tuple[bool, str]:
        """Restaure les fichiers depuis un flux de données (archive en mémoire).
        
        Utile pour les tests ou pour traiter les données en mémoire.
        
        Args:
            archive_data: Données binaires de l'archive tar.gz
            buffer_size: Taille du buffer pour le transfert SFTP (défaut: 64KB)
            
        Returns:
            Tuple (succès, message)
            
        Raises:
            SSHException: Si la commande SSH échoue
            IOError: Si le transfert SFTP échoue
        """
        try:
            # Génère un nom de fichier temporaire
            temp_archive = "/tmp/restore_stream.tar.gz"
            
            logger.info(f"Restauration depuis un flux vers {self.remote_path}")
            
            # Étape 1 : Télécharge le flux via SFTP
            logger.debug(f"Téléchargement du flux vers {temp_archive}")
            sftp_client = self.ssh_client.open_sftp()
            try:
                with sftp_client.file(temp_archive, 'wb') as f:
                    f.write(archive_data)
            finally:
                sftp_client.close()
            
            # Étape 2 : Extrait l'archive sur le serveur
            logger.debug(f"Extraction de {temp_archive} vers {self.remote_path}")
            extract_cmd = f"tar -xzf {temp_archive} -C {self.remote_path}"
            stdin, stdout, stderr = self.ssh_client.exec_command(extract_cmd)
            
            # Vérifie s'il y a eu des erreurs
            stderr_output = stderr.read().decode('utf-8', errors='ignore').strip()
            if stderr_output:
                logger.warning(f"Avertissements tar: {stderr_output}")
            
            # Vérifie le code de sortie
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                raise SSHException(
                    f"La commande tar a échoué avec le code {exit_status}. "
                    f"Erreur: {stderr_output}"
                )
            
            # Étape 3 : Nettoie le fichier temporaire
            logger.debug(f"Suppression du fichier temporaire {temp_archive}")
            rm_cmd = f"rm -f {temp_archive}"
            stdin, stdout, stderr = self.ssh_client.exec_command(rm_cmd)
            stdout.channel.recv_exit_status()
            
            message = (
                f"✓ Restauration depuis un flux réussie\n"
                f"  Taille: {len(archive_data) / 1024 / 1024:.2f} MB\n"
                f"  Destination: {self.remote_path}"
            )
            logger.info(message)
            
            return True, message
            
        except SSHException as e:
            error_msg = f"Erreur SSH lors de la restauration: {str(e)}"
            logger.error(error_msg)
            raise
        except IOError as e:
            error_msg = f"Erreur de transfert SFTP: {str(e)}"
            logger.error(error_msg)
            raise
