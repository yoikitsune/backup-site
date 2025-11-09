"""Module de sauvegarde de la base de données MySQL via SSH.

Stratégie :
- Utilise mysqldump pour exporter la base de données
- Exécution via SSH tunnel (localhost:3306)
- Compression gzip optionnelle
- Compatible avec MySQL et MariaDB

Flux :
  SSH → mysqldump -h localhost -u user -p db | gzip > database.sql.gz
"""

import io
import logging
from pathlib import Path
from typing import Optional, Tuple

import paramiko
from paramiko.ssh_exception import SSHException

logger = logging.getLogger(__name__)


class DatabaseBackup:
    """Gère la sauvegarde de la base de données MySQL via SSH."""
    
    def __init__(
        self,
        ssh_client: paramiko.SSHClient,
        db_host: str,
        db_port: int,
        db_name: str,
        db_user: str,
        db_password: str,
        compress: bool = True,
        ssl_enabled: bool = False,
    ):
        """Initialise le gestionnaire de sauvegarde de BDD.
        
        Args:
            ssh_client: Client SSH Paramiko connecté
            db_host: Hôte de la base de données (localhost pour SSH tunnel)
            db_port: Port de la base de données (défaut: 3306)
            db_name: Nom de la base de données
            db_user: Utilisateur de la base de données
            db_password: Mot de passe de la base de données
            compress: Compresser le dump avec gzip (défaut: True)
            ssl_enabled: Utiliser SSL pour la connexion MySQL (défaut: False)
        """
        self.ssh_client = ssh_client
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.compress = compress
        self.ssl_enabled = ssl_enabled
    
    def _build_mysqldump_command(self) -> str:
        """Construit la commande mysqldump.
        
        Returns:
            Commande mysqldump complète avec pipe gzip optionnel
        """
        # Commande mysqldump de base
        cmd = (
            f"mysqldump -h {self.db_host} -P {self.db_port} "
            f"-u {self.db_user} -p{self.db_password} "
        )
        
        # Ajoute les options SSL
        if not self.ssl_enabled:
            cmd += "--ssl=0 "
        
        # Ajoute les options de dump
        cmd += (
            "--routines --triggers --events "
            "--complete-insert --extended-insert "
            "--disable-keys --quick "
        )
        
        # Ajoute le nom de la base
        cmd += self.db_name
        
        # Pipe vers gzip si compression activée
        if self.compress:
            cmd += " | gzip"
        
        return cmd
    
    def backup_to_file(
        self,
        output_path: Path,
        buffer_size: int = 65536
    ) -> Tuple[bool, str, int]:
        """Sauvegarde la base de données dans un fichier.
        
        Args:
            output_path: Chemin local où sauvegarder le dump
            buffer_size: Taille du buffer pour la lecture du flux (défaut: 64KB)
            
        Returns:
            Tuple (succès, message, taille_en_bytes)
            
        Raises:
            SSHException: Si la commande SSH échoue
            IOError: Si l'écriture du fichier échoue
        """
        try:
            # Construit la commande mysqldump
            mysqldump_command = self._build_mysqldump_command()
            logger.debug(f"Exécution de la commande: {mysqldump_command}")
            
            # Exécute la commande SSH
            stdin, stdout, stderr = self.ssh_client.exec_command(mysqldump_command)
            
            # Crée le répertoire de destination s'il n'existe pas
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Écrit le flux dans le fichier local
            bytes_written = 0
            with open(output_path, 'wb') as f:
                while True:
                    chunk = stdout.read(buffer_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    bytes_written += len(chunk)
            
            # Vérifie s'il y a eu des erreurs
            stderr_output = stderr.read().decode('utf-8', errors='ignore').strip()
            if stderr_output:
                # Filtre les avertissements non critiques
                if "Deprecated program name" not in stderr_output:
                    logger.warning(f"Avertissements mysqldump: {stderr_output}")
            
            # Vérifie le code de sortie
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                raise SSHException(
                    f"La commande mysqldump a échoué avec le code {exit_status}. "
                    f"Erreur: {stderr_output}"
                )
            
            # Vérifie que le fichier a bien été créé
            if not output_path.exists():
                raise IOError(f"Le fichier {output_path} n'a pas été créé")
            
            message = (
                f"✓ Sauvegarde de la base de données réussie\n"
                f"  Fichier: {output_path.name}\n"
                f"  Taille: {bytes_written / 1024:.2f} KB"
            )
            logger.info(message)
            
            return True, message, bytes_written
            
        except SSHException as e:
            error_msg = f"Erreur SSH lors de la sauvegarde BDD: {str(e)}"
            logger.error(error_msg)
            raise
        except IOError as e:
            error_msg = f"Erreur d'écriture du fichier: {str(e)}"
            logger.error(error_msg)
            raise
    
    def backup_to_stream(self) -> io.BytesIO:
        """Sauvegarde la base de données dans un flux BytesIO.
        
        Utile pour les tests ou pour traiter les données en mémoire.
        
        Returns:
            BytesIO contenant le dump SQL (compressé si activé)
            
        Raises:
            SSHException: Si la commande SSH échoue
        """
        try:
            # Construit la commande mysqldump
            mysqldump_command = self._build_mysqldump_command()
            logger.debug(f"Exécution de la commande: {mysqldump_command}")
            
            # Exécute la commande SSH
            stdin, stdout, stderr = self.ssh_client.exec_command(mysqldump_command)
            
            # Lit le flux dans un BytesIO
            stream = io.BytesIO()
            buffer_size = 65536
            while True:
                chunk = stdout.read(buffer_size)
                if not chunk:
                    break
                stream.write(chunk)
            
            # Vérifie s'il y a eu des erreurs
            stderr_output = stderr.read().decode('utf-8', errors='ignore').strip()
            if stderr_output:
                if "Deprecated program name" not in stderr_output:
                    logger.warning(f"Avertissements mysqldump: {stderr_output}")
            
            # Vérifie le code de sortie
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                raise SSHException(
                    f"La commande mysqldump a échoué avec le code {exit_status}. "
                    f"Erreur: {stderr_output}"
                )
            
            # Réinitialise la position du stream
            stream.seek(0)
            logger.info(f"Sauvegarde BDD en mémoire réussie ({stream.getbuffer().nbytes} bytes)")
            
            return stream
            
        except SSHException as e:
            error_msg = f"Erreur SSH lors de la sauvegarde BDD en mémoire: {str(e)}"
            logger.error(error_msg)
            raise
