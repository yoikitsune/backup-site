"""Tests pour le module de sauvegarde de la base de données."""

import io
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest

from backup_site.backup.database import DatabaseBackup


class TestDatabaseBackup:
    """Tests pour la classe DatabaseBackup."""
    
    @pytest.fixture
    def mock_ssh_client(self):
        """Crée un mock de client SSH."""
        return Mock()
    
    @pytest.fixture
    def db_backup(self, mock_ssh_client):
        """Crée une instance de DatabaseBackup avec un mock SSH."""
        return DatabaseBackup(
            ssh_client=mock_ssh_client,
            db_host="test-mysql",
            db_port=3306,
            db_name="test_wp",
            db_user="testuser",
            db_password="testpass",
            compress=True,
            ssl_enabled=False,
        )
    
    def test_build_mysqldump_command_with_compression(self, db_backup):
        """Teste la construction de la commande mysqldump avec compression."""
        cmd = db_backup._build_mysqldump_command()
        
        # Vérifie que la commande contient les éléments clés
        assert "mysqldump" in cmd
        assert "-h test-mysql" in cmd
        assert "-P 3306" in cmd
        assert "-u testuser" in cmd
        assert "-ptestpass" in cmd
        assert "--ssl=0" in cmd
        assert "test_wp" in cmd
        assert "| gzip" in cmd
    
    def test_build_mysqldump_command_without_compression(self, mock_ssh_client):
        """Teste la construction de la commande mysqldump sans compression."""
        db_backup = DatabaseBackup(
            ssh_client=mock_ssh_client,
            db_host="localhost",
            db_port=3306,
            db_name="test_db",
            db_user="user",
            db_password="pass",
            compress=False,
            ssl_enabled=False,
        )
        
        cmd = db_backup._build_mysqldump_command()
        
        # Sans compression, pas de pipe gzip
        assert "| gzip" not in cmd
        assert "mysqldump" in cmd
        assert "test_db" in cmd
    
    def test_build_mysqldump_command_with_ssl(self, mock_ssh_client):
        """Teste la construction de la commande mysqldump avec SSL."""
        db_backup = DatabaseBackup(
            ssh_client=mock_ssh_client,
            db_host="localhost",
            db_port=3306,
            db_name="test_db",
            db_user="user",
            db_password="pass",
            compress=False,
            ssl_enabled=True,
        )
        
        cmd = db_backup._build_mysqldump_command()
        
        # Avec SSL, pas de --ssl=0
        assert "--ssl=0" not in cmd
        assert "mysqldump" in cmd
    
    def test_backup_to_file_success(self, db_backup, mock_ssh_client):
        """Teste la sauvegarde réussie dans un fichier."""
        # Mock la réponse SSH
        mock_stdout = MagicMock()
        mock_stdout.read.side_effect = [b"SQL dump chunk 1", b"SQL dump chunk 2", b""]
        mock_stdout.channel.recv_exit_status.return_value = 0
        
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""
        
        mock_ssh_client.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        # Lance la sauvegarde dans un fichier temporaire
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "database.sql.gz"
            
            success, message, bytes_written = db_backup.backup_to_file(output_path)
            
            # Vérifie les résultats
            assert success is True
            assert bytes_written == 32  # "SQL dump chunk 1" + "SQL dump chunk 2"
            assert output_path.exists()
            assert "✓ Sauvegarde de la base de données réussie" in message
            
            # Vérifie le contenu du fichier
            with open(output_path, 'rb') as f:
                content = f.read()
            assert content == b"SQL dump chunk 1SQL dump chunk 2"
    
    def test_backup_to_file_ssh_error(self, db_backup, mock_ssh_client):
        """Teste la gestion d'erreur SSH."""
        # Mock une erreur SSH
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 1
        
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b"mysqldump: error"
        
        mock_ssh_client.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        # Lance la sauvegarde
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "database.sql.gz"
            
            with pytest.raises(Exception) as exc_info:
                db_backup.backup_to_file(output_path)
            
            assert "mysqldump a échoué" in str(exc_info.value)
    
    def test_backup_to_stream_success(self, db_backup, mock_ssh_client):
        """Teste la sauvegarde réussie dans un stream."""
        # Mock la réponse SSH
        mock_stdout = MagicMock()
        mock_stdout.read.side_effect = [b"stream chunk 1", b"stream chunk 2", b""]
        mock_stdout.channel.recv_exit_status.return_value = 0
        
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""
        
        mock_ssh_client.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        # Lance la sauvegarde dans un stream
        stream = db_backup.backup_to_stream()
        
        # Vérifie les résultats
        assert isinstance(stream, io.BytesIO)
        assert stream.tell() == 0  # Position au début
        assert stream.read() == b"stream chunk 1stream chunk 2"
    
    def test_backup_to_stream_ssh_error(self, db_backup, mock_ssh_client):
        """Teste la gestion d'erreur SSH pour le stream."""
        # Mock une erreur SSH
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 1
        
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b"mysqldump: error"
        
        mock_ssh_client.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        # Lance la sauvegarde
        with pytest.raises(Exception) as exc_info:
            db_backup.backup_to_stream()
        
        assert "mysqldump a échoué" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
