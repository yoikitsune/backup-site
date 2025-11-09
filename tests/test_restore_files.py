"""Tests unitaires pour la restauration des fichiers via SSH."""

import io
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

from backup_site.restore.files import FileRestore


@pytest.fixture
def mock_ssh_client():
    """Crée un mock du client SSH."""
    return MagicMock()


@pytest.fixture
def file_restore(mock_ssh_client):
    """Crée une instance FileRestore avec un mock SSH."""
    return FileRestore(
        ssh_client=mock_ssh_client,
        remote_path="/var/www/html"
    )


class TestFileRestore:
    """Tests pour la classe FileRestore."""
    
    def test_init(self, mock_ssh_client):
        """Test l'initialisation de FileRestore."""
        restore = FileRestore(
            ssh_client=mock_ssh_client,
            remote_path="/var/www/html"
        )
        
        assert restore.ssh_client == mock_ssh_client
        assert restore.remote_path == "/var/www/html"
    
    def test_restore_from_file_success(self, file_restore, mock_ssh_client, tmp_path):
        """Test la restauration réussie d'une archive."""
        # Crée une archive de test
        archive_path = tmp_path / "backup.tar.gz"
        archive_path.write_bytes(b"fake archive data")
        
        # Mock SFTP
        mock_sftp = MagicMock()
        mock_ssh_client.open_sftp.return_value = mock_sftp
        
        # Mock les commandes SSH
        mock_stdin = MagicMock()
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_channel = MagicMock()
        
        mock_stdout.channel = mock_channel
        mock_channel.recv_exit_status.side_effect = [0, 0]  # Deux commandes
        mock_stderr.read.return_value = b""
        
        mock_ssh_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        # Exécute la restauration
        success, message = file_restore.restore_from_file(archive_path)
        
        # Vérifie les résultats
        assert success is True
        assert "✓ Restauration des fichiers réussie" in message
        assert "backup.tar.gz" in message
        assert "/var/www/html" in message
        
        # Vérifie que SFTP a été utilisé
        mock_ssh_client.open_sftp.assert_called_once()
        mock_sftp.put.assert_called_once()
        
        # Vérifie que les commandes SSH ont été exécutées
        assert mock_ssh_client.exec_command.call_count == 2
        
        # Vérifie les commandes
        calls = mock_ssh_client.exec_command.call_args_list
        assert "tar -xzf /tmp/backup.tar.gz -C /var/www/html" in calls[0][0][0]
        assert "rm -f /tmp/backup.tar.gz" in calls[1][0][0]
    
    def test_restore_from_file_archive_not_found(self, file_restore, tmp_path):
        """Test la restauration avec une archive inexistante."""
        archive_path = tmp_path / "nonexistent.tar.gz"
        
        with pytest.raises(FileNotFoundError):
            file_restore.restore_from_file(archive_path)
    
    def test_restore_from_file_tar_command_fails(self, file_restore, mock_ssh_client, tmp_path):
        """Test la restauration avec une erreur de la commande tar."""
        # Crée une archive de test
        archive_path = tmp_path / "backup.tar.gz"
        archive_path.write_bytes(b"fake archive data")
        
        # Mock SFTP
        mock_sftp = MagicMock()
        mock_ssh_client.open_sftp.return_value = mock_sftp
        
        # Mock les commandes SSH avec erreur
        mock_stdin = MagicMock()
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_channel = MagicMock()
        
        mock_stdout.channel = mock_channel
        mock_channel.recv_exit_status.return_value = 1  # Erreur
        mock_stderr.read.return_value = b"tar: Error"
        
        mock_ssh_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        # Exécute la restauration et vérifie l'erreur
        with pytest.raises(Exception):
            file_restore.restore_from_file(archive_path)
    
    def test_restore_from_file_sftp_fails(self, file_restore, mock_ssh_client, tmp_path):
        """Test la restauration avec une erreur SFTP."""
        # Crée une archive de test
        archive_path = tmp_path / "backup.tar.gz"
        archive_path.write_bytes(b"fake archive data")
        
        # Mock SFTP avec erreur
        mock_sftp = MagicMock()
        mock_sftp.put.side_effect = IOError("SFTP error")
        mock_ssh_client.open_sftp.return_value = mock_sftp
        
        # Exécute la restauration et vérifie l'erreur
        with pytest.raises(IOError):
            file_restore.restore_from_file(archive_path)
    
    def test_restore_from_stream_success(self, file_restore, mock_ssh_client):
        """Test la restauration réussie depuis un flux."""
        # Crée des données d'archive
        archive_data = b"fake archive data"
        
        # Mock SFTP
        mock_sftp = MagicMock()
        mock_file = MagicMock()
        mock_sftp.file.return_value.__enter__.return_value = mock_file
        mock_ssh_client.open_sftp.return_value = mock_sftp
        
        # Mock les commandes SSH
        mock_stdin = MagicMock()
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_channel = MagicMock()
        
        mock_stdout.channel = mock_channel
        mock_channel.recv_exit_status.side_effect = [0, 0]  # Deux commandes
        mock_stderr.read.return_value = b""
        
        mock_ssh_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        # Exécute la restauration
        success, message = file_restore.restore_from_stream(archive_data)
        
        # Vérifie les résultats
        assert success is True
        assert "✓ Restauration depuis un flux réussie" in message
        assert "/var/www/html" in message
        
        # Vérifie que SFTP a été utilisé
        mock_ssh_client.open_sftp.assert_called_once()
        mock_sftp.file.assert_called_once()
        
        # Vérifie que les commandes SSH ont été exécutées
        assert mock_ssh_client.exec_command.call_count == 2
    
    def test_restore_from_stream_tar_command_fails(self, file_restore, mock_ssh_client):
        """Test la restauration depuis un flux avec une erreur tar."""
        archive_data = b"fake archive data"
        
        # Mock SFTP
        mock_sftp = MagicMock()
        mock_file = MagicMock()
        mock_sftp.file.return_value.__enter__.return_value = mock_file
        mock_ssh_client.open_sftp.return_value = mock_sftp
        
        # Mock les commandes SSH avec erreur
        mock_stdin = MagicMock()
        mock_stdout = MagicMock()
        mock_stderr = MagicMock()
        mock_channel = MagicMock()
        
        mock_stdout.channel = mock_channel
        mock_channel.recv_exit_status.return_value = 1  # Erreur
        mock_stderr.read.return_value = b"tar: Error"
        
        mock_ssh_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        # Exécute la restauration et vérifie l'erreur
        with pytest.raises(Exception):
            file_restore.restore_from_stream(archive_data)
