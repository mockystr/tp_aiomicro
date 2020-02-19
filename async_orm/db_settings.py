from os import getenv

user_db_constant = getenv('POSTGRES_USER', "emirnavruzov")
password_db_constant = getenv('POSTGRES_PASSWORD', "qwe123")
host_db_constant = getenv('POSTGRES_HOST_DB', '127.0.0.1')
port_db_constant = getenv('POSTGRES_PORT_DB', "5432")
database_db_constant = getenv('POSTGRES_DB_NAME', "tp_aiomicro")
