"""Backup Site - Solution CLI de sauvegarde de site web."""

__version__ = "0.1.0"
__author__ = "Julien"
__description__ = "Solution CLI de sauvegarde de site web avec support Docker"

# Configuration du logging
import logging
from logging import NullHandler

# Désactive les logs par défaut
logging.getLogger(__name__).addHandler(NullHandler())
