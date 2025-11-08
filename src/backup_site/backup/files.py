"""Module de sauvegarde des fichiers via SSH avec compression côté serveur.

Stratégie de compression :
- Utilise `find` pour filtrer les fichiers selon les patterns d'inclusion/exclusion
- Pipe vers `tar -czf - -T -` pour archiver et compresser
- Compatible avec GNU tar et BusyBox tar (contrairement à --include/--exclude)

Avantages :
1. Compression côté serveur : réduit la bande passante réseau
2. Compatible avec tous les systèmes (GNU tar, BusyBox tar, etc.)
3. Patterns flexibles via find (! -path, -path, etc.)
4. Pas de script serveur requis, utilise les outils natifs

Flux :
  find . -type f [patterns] | tar -czf - -T - > archive.tar.gz
  
Exemple :
  find . -type f ! -path '*cache*' ! -path '*.log' -path '*wp-content*' | tar -czf - -T -
"""

import io
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import paramiko
from paramiko.ssh_exception import SSHException

logger = logging.getLogger(__name__)


class FileBackup:
    """Gère la sauvegarde des fichiers via SSH avec compression côté serveur."""
    
    def __init__(
        self,
        ssh_client: paramiko.SSHClient,
        remote_path: str,
        include_patterns: list[str],
        exclude_patterns: list[str],
    ):
        """Initialise le gestionnaire de sauvegarde des fichiers.
        
        Args:
            ssh_client: Client SSH Paramiko connecté
            remote_path: Chemin distant des fichiers à sauvegarder
            include_patterns: Liste des motifs glob pour inclure des fichiers
            exclude_patterns: Liste des motifs glob pour exclure des fichiers
        """
        self.ssh_client = ssh_client
        self.remote_path = remote_path
        self.include_patterns = include_patterns
        self.exclude_patterns = exclude_patterns
    
    def _build_tar_command(self) -> str:
        """Construit la commande tar avec les patterns d'inclusion/exclusion.
        
        Compatible avec GNU tar et BusyBox tar.
        Utilise find pour filtrer les fichiers, puis tar pour les archiver.
        
        Returns:
            Commande tar complète avec pipe gzip
        """
        # Commande de base : find pour lister les fichiers
        find_cmd = f"cd {self.remote_path} && find . -type f"
        
        # Ajoute les patterns d'exclusion
        for pattern in self.exclude_patterns:
            find_cmd += f" ! -path '*{pattern}*'"
        
        # Ajoute les patterns d'inclusion (si spécifiés)
        if self.include_patterns:
            include_conditions = " -o ".join(
                f"-path '*{pattern}*'" for pattern in self.include_patterns
            )
            find_cmd += f" \\( {include_conditions} \\)"
        
        # Pipe find vers tar
        # find génère la liste des fichiers, tar les archive et gzip les compresse
        cmd = f"{find_cmd} | tar -czf - -T -"
        
        return cmd
    
    def backup_to_file(
        self,
        output_path: Path,
        buffer_size: int = 65536
    ) -> Tuple[bool, str, int]:
        """Sauvegarde les fichiers dans une archive compressée.
        
        Args:
            output_path: Chemin local où sauvegarder l'archive
            buffer_size: Taille du buffer pour la lecture du flux (défaut: 64KB)
            
        Returns:
            Tuple (succès, message, taille_en_bytes)
            
        Raises:
            SSHException: Si la commande SSH échoue
            IOError: Si l'écriture du fichier échoue
        """
        try:
            # Construit la commande tar
            tar_command = self._build_tar_command()
            logger.debug(f"Exécution de la commande: {tar_command}")
            
            # Exécute la commande SSH
            stdin, stdout, stderr = self.ssh_client.exec_command(tar_command)
            
            # Crée le répertoire de destination s'il n'existe pas
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Écrit le flux compressé dans le fichier local
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
                logger.warning(f"Avertissements SSH: {stderr_output}")
            
            # Vérifie le code de sortie
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                raise SSHException(
                    f"La commande tar a échoué avec le code {exit_status}. "
                    f"Erreur: {stderr_output}"
                )
            
            # Vérifie que le fichier a bien été créé
            if not output_path.exists():
                raise IOError(f"Le fichier {output_path} n'a pas été créé")
            
            message = (
                f"✓ Sauvegarde des fichiers réussie\n"
                f"  Archive: {output_path.name}\n"
                f"  Taille: {bytes_written / 1024 / 1024:.2f} MB"
            )
            logger.info(message)
            
            return True, message, bytes_written
            
        except SSHException as e:
            error_msg = f"Erreur SSH lors de la sauvegarde: {str(e)}"
            logger.error(error_msg)
            raise
        except IOError as e:
            error_msg = f"Erreur d'écriture du fichier: {str(e)}"
            logger.error(error_msg)
            raise
    
    def backup_to_stream(self) -> io.BytesIO:
        """Sauvegarde les fichiers dans un flux BytesIO.
        
        Utile pour les tests ou pour traiter les données en mémoire.
        
        Returns:
            BytesIO contenant l'archive compressée
            
        Raises:
            SSHException: Si la commande SSH échoue
        """
        try:
            # Construit la commande tar
            tar_command = self._build_tar_command()
            logger.debug(f"Exécution de la commande: {tar_command}")
            
            # Exécute la commande SSH
            stdin, stdout, stderr = self.ssh_client.exec_command(tar_command)
            
            # Lit le flux compressé dans un BytesIO
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
                logger.warning(f"Avertissements SSH: {stderr_output}")
            
            # Vérifie le code de sortie
            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0:
                raise SSHException(
                    f"La commande tar a échoué avec le code {exit_status}. "
                    f"Erreur: {stderr_output}"
                )
            
            # Réinitialise la position du stream
            stream.seek(0)
            logger.info(f"Sauvegarde en mémoire réussie ({stream.getbuffer().nbytes} bytes)")
            
            return stream
            
        except SSHException as e:
            error_msg = f"Erreur SSH lors de la sauvegarde en mémoire: {str(e)}"
            logger.error(error_msg)
            raise
