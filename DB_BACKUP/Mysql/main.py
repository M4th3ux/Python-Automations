import os
import shutil
import logging
from datetime import datetime
from subprocess import Popen, PIPE
import paramiko
from scp import SCPClient
from dotenv import load_dotenv

# Carregar as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurando o logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Função para fazer backup do banco de dados MySQL
def backup_mysql(db_name, db_user, db_password, host, backup_folder):
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        backup_path = os.path.join(backup_folder, f"mysql_backup_{today}")
        
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)
        
        # Comando para realizar o dump do banco de dados
        dump_file = os.path.join(backup_path, f"{db_name}.sql")
        dump_command = f"mysqldump -h {host} -u {db_user} -p{db_password} {db_name} > {dump_file}"
        
        process = Popen(dump_command, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            logging.info(f"Backup do banco de dados '{db_name}' concluído com sucesso.")
            return dump_file
        else:
            logging.error(f"Erro ao fazer o backup do banco de dados: {stderr.decode()}")
            return None
    except Exception as e:
        logging.error(f"Erro ao fazer backup do banco de dados: {e}")
        return None

# Função para enviar o backup via SCP
def upload_via_scp(local_file, remote_host, remote_user, remote_password, remote_path):
    try:
        # Conectar ao servidor remoto via SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(remote_host, username=remote_user, password=remote_password)

        # Usar o SCP para copiar o arquivo para o servidor remoto
        with SCPClient(ssh.get_transport()) as scp:
            scp.put(local_file, remote_path)
            logging.info(f"Arquivo {os.path.basename(local_file)} enviado com sucesso para {remote_host}:{remote_path}")

        # Fechar a conexão SSH
        ssh.close()

    except Exception as e:
        logging.error(f"Erro ao enviar o arquivo via SCP: {e}")

# Carregar variáveis do arquivo .env
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
host = os.getenv('DB_HOST')

backup_dir = os.getenv('BACKUP_DIR')

remote_host = os.getenv('REMOTE_HOST')
remote_user = os.getenv('REMOTE_USER')
remote_password = os.getenv('REMOTE_PASSWORD')
remote_path = os.getenv('REMOTE_PATH')

# Faz o backup do banco de dados
mysql_backup_file = backup_mysql(db_name, db_user, db_password, host, backup_dir)

# Se o backup for bem-sucedido, faz o upload via SCP
if mysql_backup_file:
    upload_via_scp(mysql_backup_file, remote_host, remote_user, remote_password, remote_path)
