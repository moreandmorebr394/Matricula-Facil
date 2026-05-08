"""
Configurações de conexão com o banco de dados MySQL.

Edite os valores abaixo para coincidir com sua instalação local
do WampServer / MySQL Workbench.
"""

# Configurações padrão do WampServer
HOST_BANCO = "localhost"
PORTA_BANCO = 3306
USUARIO_BANCO = "root"
SENHA_BANCO = ""           # WampServer padrão: senha vazia
NOME_BANCO = "sistema_facil_sf"

# Tempo (em segundos) para timeout de conexão
TIMEOUT_CONEXAO = 5

# Charset
CHARSET_BANCO = "utf8mb4"
