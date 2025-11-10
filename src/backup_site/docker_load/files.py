"""Module de chargement des fichiers dans Docker local.

Stratégie :
- Utilise `docker cp` pour copier l'archive dans le container
- Utilise `docker exec` pour extraire l'archive
- Pas de SSH, accès direct au container Docker

Flux :
  docker cp archive.tar.gz container:/tmp/
  docker exec container tar -xzf /tmp/archive.tar.gz -C destination
"""

import logging
import subprocess
from pathlib import Path
from typing import Tuple

logger = logging.getLogger(__name__)


class DockerFileLoad:
    """Gère le chargement des fichiers dans Docker local."""
    
    def __init__(
        self,
        container_name: str,
        remote_path: str,
    ):
        """Initialise le gestionnaire de chargement des fichiers.
        
        Args:
            container_name: Nom du container Docker
            remote_path: Chemin dans le container où charger les fichiers
        """
        self.container_name = container_name
        self.remote_path = remote_path
    
    def load_from_file(
        self,
        archive_path: Path,
    ) -> Tuple[bool, str]:
        """Charge les fichiers depuis une archive tar.gz dans Docker.
        
        Stratégie :
        1. Copie l'archive dans le container via docker cp
        2. Extrait l'archive dans le container via docker exec
        3. Nettoie les fichiers temporaires
        
        Args:
            archive_path: Chemin local de l'archive tar.gz
            
        Returns:
            Tuple (succès, message)
            
        Raises:
            FileNotFoundError: Si l'archive n'existe pas
            subprocess.CalledProcessError: Si une commande Docker échoue
        """
        try:
            # Vérifie que l'archive existe
            if not archive_path.exists():
                raise FileNotFoundError(f"L'archive {archive_path} n'existe pas")
            
            archive_name = archive_path.name
            temp_archive = f"/tmp/{archive_name}"
            
            logger.info(f"Chargement de {archive_path.name} vers {self.container_name}:{self.remote_path}")
            
            # Étape 1 : Copie l'archive dans le container via docker cp
            logger.debug(f"Copie de {archive_path} vers {self.container_name}:{temp_archive}")
            try:
                subprocess.run(
                    ["docker", "cp", str(archive_path), f"{self.container_name}:{temp_archive}"],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Erreur lors de la copie Docker: {e.stderr}")
            
            # Étape 2 : Extrait l'archive dans le container
            logger.debug(f"Extraction de {temp_archive} vers {self.remote_path}")
            extract_cmd = f"tar -xzf {temp_archive} -C {self.remote_path}"
            try:
                subprocess.run(
                    ["docker", "exec", self.container_name, "bash", "-c", extract_cmd],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                raise RuntimeError(f"Erreur lors de l'extraction: {e.stderr}")
            
            # Étape 3 : Nettoie le fichier temporaire
            logger.debug(f"Suppression du fichier temporaire {temp_archive}")
            try:
                subprocess.run(
                    ["docker", "exec", self.container_name, "rm", "-f", temp_archive],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError:
                logger.warning(f"Impossible de supprimer {temp_archive}")
            
            message = (
                f"✓ Chargement des fichiers réussi\n"
                f"  Archive: {archive_name}\n"
                f"  Container: {self.container_name}\n"
                f"  Destination: {self.remote_path}\n"
                f"  Taille: {archive_path.stat().st_size / 1024 / 1024:.2f} MB"
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
        archive_data: bytes,
    ) -> Tuple[bool, str]:
        """Charge les fichiers depuis un flux de données (archive en mémoire).
        
        Utile pour les tests ou pour traiter les données en mémoire.
        
        Args:
            archive_data: Données binaires de l'archive tar.gz
            
        Returns:
            Tuple (succès, message)
            
        Raises:
            RuntimeError: Si une commande Docker échoue
        """
        try:
            # Crée un fichier temporaire local
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
                tmp.write(archive_data)
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
