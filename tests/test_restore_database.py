"""Tests unitaires pour la restauration de la base de données via SSH."""

import io
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backup_site.restore.database import DatabaseRestore


@pytest.fixture
def mock_ssh_client():
    """Crée un mock du client SSH."""
    return MagicMock()


@pytest.fixture
def database_restore(mock_ssh_client):
    """Crée une instance DatabaseRestore avec un mock SSH."""
    return DatabaseRestore(
        ssh_client=mock_ssh_client,
        db_host="localhost",
        db_port=3306,
        db_name="wordpress",
        db_user="wordpress",
        db_password="wordpress"
    )


class TestDatabaseRestore:
    """Tests pour la classe DatabaseRestore."""
    
    def test_init(self, mock_ssh_client):
        """Test l'initialisation de DatabaseRestore."""
        restore = DatabaseRestore(
            ssh_client=mock_ssh_client,
            db_host="localhost",
            db_port=3306,
            db_name="wordpress",
            db_user="wordpress",
            db_password="wordpress"
        )
        
        assert restore.ssh_client == mock_ssh_client
        assert restore.db_host == "localhost"
        assert restore.db_port == 3306
        assert restore.db_name == "wordpress"
        assert restore.db_user == "wordpress"
        assert restore.db_password == "wordpress"
    
    def test_build_restore_command_compressed(self, database_restore):
        """Test la construction de la commande de restauration pour un fichier compressé."""
        cmd = database_restore._build_restore_command("/tmp/database.sql.gz", is_compressed=True)
        
        assert "gunzip < /tmp/database.sql.gz" in cmd
        assert "mysql -h localhost -P 3306" in cmd
        assert "-u wordpress" in cmd
        assert "-pwordpress" in cmd
        assert "wordpress" in cmd
    
    def test_build_restore_command_uncompressed(self, database_restore):
        """Test la construction de la commande de restauration pour un fichier non compressé."""
        cmd = database_restore._build_restore_command("/tmp/database.sql", is_compressed=False)
        
        assert "gunzip" not in cmd
        assert "mysql -h localhost -P 3306" in cmd
        assert "< /tmp/database.sql" in cmd
    
    def test_restore_from_file_success_compressed(self, database_restore, mock_ssh_client, tmp_path):
        """Test la restauration réussie d'un dump compressé."""
        # Crée un dump de test
        dump_path = tmp_path / "database.sql.gz"
        dump_path.write_bytes(b"fake dump data")
        
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
        success, message = database_restore.restore_from_file(dump_path)
        
        # Vérifie les résultats
        assert success is True
        assert "✓ Restauration de la base de données réussie" in message
        assert "database.sql.gz" in message
        assert "wordpress" in message
        
        # Vérifie que SFTP a été utilisé
        mock_ssh_client.open_sftp.assert_called_once()
        mock_sftp.put.assert_called_once()
        
        # Vérifie que les commandes SSH ont été exécutées
        assert mock_ssh_client.exec_command.call_count == 2
        
        # Vérifie les commandes
        calls = mock_ssh_client.exec_command.call_args_list
        assert "gunzip < /tmp/database.sql.gz" in calls[0][0][0]
        assert "mysql -h localhost -P 3306" in calls[0][0][0]
        assert "rm -f /tmp/database.sql.gz" in calls[1][0][0]
    
    def test_restore_from_file_success_uncompressed(self, database_restore, mock_ssh_client, tmp_path):
        """Test la restauration réussie d'un dump non compressé."""
        # Crée un dump de test
        dump_path = tmp_path / "database.sql"
        dump_path.write_bytes(b"fake dump data")
        
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
        success, message = database_restore.restore_from_file(dump_path)
        
        # Vérifie les résultats
        assert success is True
        assert "✓ Restauration de la base de données réussie" in message
        assert "database.sql" in message
        
        # Vérifie les commandes
        calls = mock_ssh_client.exec_command.call_args_list
        assert "gunzip" not in calls[0][0][0]
        assert "< /tmp/database.sql" in calls[0][0][0]
    
    def test_restore_from_file_dump_not_found(self, database_restore, tmp_path):
        """Test la restauration avec un dump inexistant."""
        dump_path = tmp_path / "nonexistent.sql.gz"
        
        with pytest.raises(FileNotFoundError):
            database_restore.restore_from_file(dump_path)
    
    def test_restore_from_file_mysql_command_fails(self, database_restore, mock_ssh_client, tmp_path):
        """Test la restauration avec une erreur de la commande mysql."""
        # Crée un dump de test
        dump_path = tmp_path / "database.sql.gz"
        dump_path.write_bytes(b"fake dump data")
        
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
        mock_stderr.read.return_value = b"mysql: Error"
        
        mock_ssh_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        # Exécute la restauration et vérifie l'erreur
        with pytest.raises(Exception):
            database_restore.restore_from_file(dump_path)
    
    def test_restore_from_file_sftp_fails(self, database_restore, mock_ssh_client, tmp_path):
        """Test la restauration avec une erreur SFTP."""
        # Crée un dump de test
        dump_path = tmp_path / "database.sql.gz"
        dump_path.write_bytes(b"fake dump data")
        
        # Mock SFTP avec erreur
        mock_sftp = MagicMock()
        mock_sftp.put.side_effect = IOError("SFTP error")
        mock_ssh_client.open_sftp.return_value = mock_sftp
        
        # Exécute la restauration et vérifie l'erreur
        with pytest.raises(IOError):
            database_restore.restore_from_file(dump_path)
    
    def test_restore_from_stream_success_compressed(self, database_restore, mock_ssh_client):
        """Test la restauration réussie depuis un flux compressé."""
        dump_data = b"fake dump data"
        
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
        success, message = database_restore.restore_from_stream(dump_data, is_compressed=True)
        
        # Vérifie les résultats
        assert success is True
        assert "✓ Restauration depuis un flux réussie" in message
        assert "wordpress" in message
        
        # Vérifie que SFTP a été utilisé
        mock_ssh_client.open_sftp.assert_called_once()
        mock_sftp.file.assert_called_once()
        
        # Vérifie que les commandes SSH ont été exécutées
        assert mock_ssh_client.exec_command.call_count == 2
    
    def test_restore_from_stream_success_uncompressed(self, database_restore, mock_ssh_client):
        """Test la restauration réussie depuis un flux non compressé."""
        dump_data = b"fake dump data"
        
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
        success, message = database_restore.restore_from_stream(dump_data, is_compressed=False)
        
        # Vérifie les résultats
        assert success is True
        assert "✓ Restauration depuis un flux réussie" in message
    
    def test_restore_from_stream_mysql_command_fails(self, database_restore, mock_ssh_client):
        """Test la restauration depuis un flux avec une erreur mysql."""
        dump_data = b"fake dump data"
        
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
        mock_stderr.read.return_value = b"mysql: Error"
        
        mock_ssh_client.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)
        
        # Exécute la restauration et vérifie l'erreur
        with pytest.raises(Exception):
            database_restore.restore_from_stream(dump_data, is_compressed=True)
