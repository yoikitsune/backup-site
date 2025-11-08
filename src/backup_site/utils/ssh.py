"""Utilitaires pour la gestion sécurisée des clés SSH."""

import os
from pathlib import Path
from typing import Optional, Tuple

import paramiko
from paramiko.ssh_exception import SSHException, AuthenticationException
from rich.console import Console

console = Console()


class SSHKeyValidator:
    """Valide et gère les clés SSH pour FOURNISSEUR_HEBERGEMENT."""
    
    @staticmethod
    def validate_key_file(key_path: Path, key_type: str = "private") -> bool:
        """Valide qu'un fichier de clé SSH existe et a les bonnes permissions.
        
        Args:
            key_path: Chemin vers le fichier de clé
            key_type: Type de clé ("private" ou "public")
            
        Returns:
            True si la clé est valide, False sinon
            
        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            PermissionError: Si les permissions sont incorrectes
        """
        # Développe le chemin
        expanded_path = key_path.expanduser().resolve()
        
        if not expanded_path.exists():
            raise FileNotFoundError(f"Le fichier de clé {expanded_path} n'existe pas")
        
        # Vérifie les permissions pour la clé privée
        if key_type == "private":
            mode = expanded_path.stat().st_mode
            # La clé privée doit avoir les permissions 600 (rw-------)
            if mode & 0o077:  # Vérifie que les autres bits ne sont pas définis
                console.print(
                    f"[yellow]Attention:[/] Les permissions de {expanded_path} "
                    f"ne sont pas sécurisées (actuellement {oct(mode)}).\n"
                    f"Correction automatique en 600..."
                )
                expanded_path.chmod(0o600)
        
        return True
    
    @staticmethod
    def load_private_key(
        key_path: Path,
        passphrase: Optional[str] = None
    ) -> paramiko.RSAKey:
        """Charge une clé privée SSH.
        
        Args:
            key_path: Chemin vers la clé privée
            passphrase: Passphrase de la clé (si elle en a une)
            
        Returns:
            Objet RSAKey de Paramiko
            
        Raises:
            FileNotFoundError: Si le fichier n'existe pas
            SSHException: Si la clé ne peut pas être chargée
        """
        expanded_path = key_path.expanduser().resolve()
        
        try:
            # Essaie de charger la clé
            key = paramiko.RSAKey.from_private_key_file(
                str(expanded_path),
                password=passphrase.encode() if passphrase else None
            )
            return key
            
        except paramiko.PasswordRequiredException:
            raise SSHException(
                f"La clé {expanded_path} est protégée par une passphrase. "
                "Veuillez la fournir."
            )
        except paramiko.SSHException as e:
            raise SSHException(
                f"Impossible de charger la clé {expanded_path}: {e}"
            )
    
    @staticmethod
    def test_ssh_connection(
        host: str,
        username: str,
        key_path: Path,
        port: int = 22,
        passphrase: Optional[str] = None,
        timeout: int = 10
    ) -> Tuple[bool, str]:
        """Teste la connexion SSH avec les clés fournies.
        
        Args:
            host: Adresse du serveur SSH
            username: Nom d'utilisateur
            key_path: Chemin vers la clé privée
            port: Port SSH (défaut: 22)
            passphrase: Passphrase de la clé (si elle en a une)
            timeout: Délai d'attente en secondes
            
        Returns:
            Tuple (succès: bool, message: str)
        """
        try:
            # Charge la clé privée
            key = SSHKeyValidator.load_private_key(key_path, passphrase)
            
            # Crée un client SSH
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Essaie de se connecter
            client.connect(
                hostname=host,
                port=port,
                username=username,
                pkey=key,
                timeout=timeout,
                look_for_keys=False,
                allow_agent=False
            )
            
            # Teste une commande simple
            stdin, stdout, stderr = client.exec_command("echo 'SSH connection successful'")
            output = stdout.read().decode().strip()
            
            client.close()
            
            return True, f"Connexion SSH réussie: {output}"
            
        except AuthenticationException as e:
            return False, f"Erreur d'authentification: {e}"
        except SSHException as e:
            return False, f"Erreur SSH: {e}"
        except Exception as e:
            return False, f"Erreur de connexion: {e}"


def print_ssh_setup_guide() -> None:
    """Affiche un guide pour configurer les clés SSH avec FOURNISSEUR_HEBERGEMENT."""
    from rich.panel import Panel
    from rich.syntax import Syntax
    
    guide = """
[bold]Configuration des clés SSH pour FOURNISSEUR_HEBERGEMENT[/]

[bold cyan]Étape 1 : Générer une paire de clés locales[/]
Si vous n'avez pas encore de clés SSH, générez-les :

[yellow]ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa[/]

Appuyez sur Entrée pour les questions (pas de passphrase recommandée pour l'automatisation).

[bold cyan]Étape 2 : Ajouter la clé publique dans FOURNISSEUR_HEBERGEMENT[/]

Option A - Générer une nouvelle clé dans FOURNISSEUR_HEBERGEMENT :
  1. Allez dans l'interface FOURNISSEUR_HEBERGEMENT > Accès SSH
  2. Cliquez sur "+ Générer une nouvelle clé"
  3. Téléchargez la clé privée
  4. Sauvegardez-la dans ~/.ssh/id_rsa

Option B - Importer votre clé publique existante :
  1. Allez dans l'interface FOURNISSEUR_HEBERGEMENT > Accès SSH
  2. Cliquez sur "⬇ Importer une clé"
  3. Copiez le contenu de ~/.ssh/id_rsa.pub
  4. Collez-le dans le formulaire d'import

[bold cyan]Étape 3 : Configurer backup-site[/]

Créez un fichier config/mon-site.yaml :

[yellow]backup-site config init config/mon-site.yaml[/]

Modifiez les paramètres SSH :
  - host: ssh.FOURNISSEUR_HEBERGEMENT.net
  - user: votre_identifiant_FOURNISSEUR_HEBERGEMENT
  - private_key_path: ~/.ssh/id_rsa
  - public_key_path: ~/.ssh/id_rsa.pub

[bold cyan]Étape 4 : Tester la connexion[/]

[yellow]backup-site ssh test config/mon-site.yaml[/]

Si la connexion réussit, vous êtes prêt à sauvegarder !
"""
    
    console.print(Panel(guide, title="Guide de configuration SSH", border_style="blue"))
