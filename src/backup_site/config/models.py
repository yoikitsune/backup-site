"""Modèles Pydantic pour la validation des configurations."""

from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
    ConfigDict,
    FilePath,
    DirectoryPath,
    HttpUrl,
    SecretStr,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class SSHConfig(BaseModel):
    """Configuration SSH pour la connexion au serveur distant."""
    
    host: str = Field(..., description="Adresse du serveur SSH")
    user: str = Field(..., description="Nom d'utilisateur SSH")
    port: int = Field(22, description="Port SSH (défaut: 22)")
    private_key_path: Path = Field(..., description="Chemin vers la clé privée SSH")
    public_key_path: Optional[Path] = Field(None, description="Chemin vers la clé publique SSH")
    
    @field_validator('private_key_path', 'public_key_path')
    @classmethod
    def resolve_path(cls, value: Optional[Path]) -> Optional[Path]:
        """Résout le chemin du fichier et vérifie qu'il existe."""
        if value is None:
            return None
            
        # Développe le ~ en chemin absolu
        expanded_path = value.expanduser()
        
        # Vérifie que le fichier existe
        if not expanded_path.exists():
            raise ValueError(f"Le fichier {expanded_path} n'existe pas")
            
        return expanded_path


class FilesConfig(BaseModel):
    """Configuration pour la sauvegarde des fichiers."""
    
    remote_path: Path = Field(..., description="Chemin distant des fichiers à sauvegarder")
    include_patterns: List[str] = Field(
        default_factory=list,
        description="Liste des motifs glob pour inclure des fichiers"
    )
    exclude_patterns: List[str] = Field(
        default_factory=list,
        description="Liste des motifs glob pour exclure des fichiers (prioritaire sur include_patterns)"
    )
    
    @field_validator('remote_path')
    @classmethod
    def validate_remote_path(cls, v: Path) -> Path:
        """Valide que le chemin distant est absolu."""
        if not v.is_absolute():
            raise ValueError("Le chemin distant doit être un chemin absolu")
        return v


class DatabaseConfig(BaseModel):
    """Configuration pour la connexion à la base de données."""
    
    host: str = Field(..., description="Hôte de la base de données")
    port: int = Field(3306, description="Port de la base de données (défaut: 3306)")
    name: str = Field(..., description="Nom de la base de données")
    user: str = Field(..., description="Utilisateur de la base de données")
    password: SecretStr = Field(..., description="Mot de passe de la base de données")
    
    @property
    def connection_string(self) -> str:
        """Retourne la chaîne de connexion à la base de données."""
        return (
            f"mysql://{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class BackupConfig(BaseModel):
    """Configuration pour les paramètres de sauvegarde."""
    
    destination: Path = Field(
        "backups",
        description="Dossier de destination des sauvegardes (relatif au répertoire du projet)"
    )
    compression: str = Field(
        "gzip",
        description="Type de compression (gzip, bzip2, xz, none)",
        pattern=r"^(gzip|bzip2|xz|none)$"
    )
    retention_days: int = Field(
        30,
        description="Nombre de jours de rétention des sauvegardes",
        ge=1,
        le=3650  # 10 ans
    )
    prefix: str = Field(
        "backup",
        description="Préfixe pour les noms de fichiers de sauvegarde",
        min_length=1,
        max_length=50
    )
    
    @field_validator('destination')
    @classmethod
    def resolve_destination_path(cls, v: Path) -> Path:
        """Résout le chemin de destination et crée le dossier si nécessaire."""
        expanded = v.expanduser().resolve()
        expanded.mkdir(parents=True, exist_ok=True)
        return expanded


class SiteConfig(BaseSettings):
    """Configuration complète d'un site à sauvegarder."""
    
    model_config = SettingsConfigDict(
        env_prefix='BACKUP_SITE_',
        env_nested_delimiter='__',
        extra='ignore',
        env_file='.env',
        env_file_encoding='utf-8',
    )
    
    # Section site
    site: Dict[str, str] = Field(
        ...,
        description="Informations générales sur le site"
    )
    
    # Configuration SSH
    ssh: SSHConfig = Field(
        ...,
        description="Configuration pour la connexion SSH"
    )
    
    # Configuration des fichiers
    files: FilesConfig = Field(
        ...,
        description="Configuration pour la sauvegarde des fichiers"
    )
    
    # Configuration de la base de données
    database: DatabaseConfig = Field(
        ...,
        description="Configuration pour la sauvegarde de la base de données"
    )
    
    # Paramètres de sauvegarde
    backup: BackupConfig = Field(
        default_factory=BackupConfig,
        description="Paramètres de sauvegarde"
    )
    
    # Options avancées (optionnel)
    options: Optional[Dict[str, Any]] = Field(
        None,
        description="Options avancées spécifiques au site"
    )
    
    @model_validator(mode='after')
    def validate_site_section(self) -> 'SiteConfig':
        """Valide que la section site contient les champs obligatoires."""
        required_fields = ['name', 'provider', 'app_type']
        missing = [field for field in required_fields if field not in self.site]
        
        if missing:
            raise ValueError(
                f"La section 'site' doit contenir les champs: {', '.join(missing)}"
            )
            
        return self
    
    @classmethod
    def from_yaml(cls, yaml_path: Path) -> 'SiteConfig':
        """Charge une configuration depuis un fichier YAML."""
        import yaml
        from pydantic import ValidationError
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            return cls.model_validate(config_data)
            
        except yaml.YAMLError as e:
            raise ValueError(f"Erreur de syntaxe YAML dans le fichier {yaml_path}: {e}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Le fichier de configuration {yaml_path} n'existe pas")
        except ValidationError as e:
            raise ValueError(f"Erreur de validation de la configuration: {e}")
