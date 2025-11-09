"""Tests pour le module de sauvegarde des fichiers."""

import io
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest

from backup_site.backup.files import FileBackup


class TestFileBackup:
    """Tests pour la classe FileBackup."""
    
    @pytest.fixture
    def mock_ssh_client(self):
        """Crée un mock de client SSH."""
        return Mock()
    
    @pytest.fixture
    def file_backup(self, mock_ssh_client):
        """Crée une instance de FileBackup avec un mock SSH."""
        return FileBackup(
            ssh_client=mock_ssh_client,
            remote_path="/home/testuser/www",
            include_patterns=["wp-content/**", "wp-config.php"],
            exclude_patterns=["wp-content/cache/**", "*.log"],
        )
    
    def test_build_tar_command_with_patterns(self, file_backup):
        """Teste la construction de la commande tar avec patterns."""
        cmd = file_backup._build_tar_command()
        
        # Vérifie que la commande contient les éléments clés
        assert "cd /home/testuser/www" in cmd
        assert "find . -type f" in cmd
        assert "! -path '*wp-content/cache/***'" in cmd  # Les * sont ajoutés par le code
        assert "! -path '**.log*'" in cmd  # Les * sont ajoutés par le code
        assert "-path '*wp-content/***'" in cmd  # Les * sont ajoutés par le code
        assert "-path '*wp-config.php*'" in cmd  # Les * sont ajoutés par le code
        assert "tar -czf - -T -" in cmd  # tar lit depuis stdin (find)
    
    def test_build_tar_command_without_include_patterns(self, mock_ssh_client):
        """Teste la construction de la commande tar sans patterns d'inclusion."""
        file_backup = FileBackup(
            ssh_client=mock_ssh_client,
            remote_path="/home/testuser/www",
            include_patterns=[],
            exclude_patterns=["*.log"],
        )
        
        cmd = file_backup._build_tar_command()
        
        # Sans patterns d'inclusion, la commande ne doit pas inclure -path avec conditions
        assert "find . -type f" in cmd
        assert "! -path '**.log*'" in cmd  # Les * sont ajoutés par le code
        assert "tar -czf - -T -" in cmd
    
    def test_backup_to_file_success(self, file_backup, mock_ssh_client):
        """Teste la sauvegarde réussie dans un fichier."""
        # Mock la réponse SSH
        mock_stdout = MagicMock()
        mock_stdout.read.side_effect = [b"test data chunk 1", b"test data chunk 2", b""]
        mock_stdout.channel.recv_exit_status.return_value = 0
        
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""
        
        mock_ssh_client.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        # Lance la sauvegarde dans un fichier temporaire
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "backup.tar.gz"
            
            success, message, bytes_written = file_backup.backup_to_file(output_path)
            
            # Vérifie les résultats
            assert success is True
            assert bytes_written == 34  # "test data chunk 1" + "test data chunk 2"
            assert output_path.exists()
            assert "✓ Sauvegarde des fichiers réussie" in message
            
            # Vérifie le contenu du fichier
            with open(output_path, 'rb') as f:
                content = f.read()
            assert content == b"test data chunk 1test data chunk 2"
    
    def test_backup_to_file_ssh_error(self, file_backup, mock_ssh_client):
        """Teste la gestion d'erreur SSH."""
        # Mock une erreur SSH
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 1
        
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b"tar: error"
        
        mock_ssh_client.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        # Lance la sauvegarde
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "backup.tar.gz"
            
            with pytest.raises(Exception) as exc_info:
                file_backup.backup_to_file(output_path)
            
            assert "tar a échoué" in str(exc_info.value)
    
    def test_backup_to_stream_success(self, file_backup, mock_ssh_client):
        """Teste la sauvegarde réussie dans un stream."""
        # Mock la réponse SSH
        mock_stdout = MagicMock()
        mock_stdout.read.side_effect = [b"stream chunk 1", b"stream chunk 2", b""]
        mock_stdout.channel.recv_exit_status.return_value = 0
        
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b""
        
        mock_ssh_client.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        # Lance la sauvegarde dans un stream
        stream = file_backup.backup_to_stream()
        
        # Vérifie les résultats
        assert isinstance(stream, io.BytesIO)
        assert stream.tell() == 0  # Position au début
        assert stream.read() == b"stream chunk 1stream chunk 2"
    
    def test_backup_to_stream_ssh_error(self, file_backup, mock_ssh_client):
        """Teste la gestion d'erreur SSH pour le stream."""
        # Mock une erreur SSH
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b""
        mock_stdout.channel.recv_exit_status.return_value = 1
        
        mock_stderr = MagicMock()
        mock_stderr.read.return_value = b"tar: error"
        
        mock_ssh_client.exec_command.return_value = (None, mock_stdout, mock_stderr)
        
        # Lance la sauvegarde
        with pytest.raises(Exception) as exc_info:
            file_backup.backup_to_stream()
        
        assert "tar a échoué" in str(exc_info.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
