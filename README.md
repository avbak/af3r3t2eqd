#### В качестве удаленного хоста в конфигурации рекомендуется использовать:
 - Для Docker хост-машину, запускающую контейнеры (В примере содержится стандартный IP)
 - Для Ansible и прочих конфигураций машину, на которой запущена основная БД

Плейбук Ansible протестирован на хостах c ОС Ubuntu 22.04.4 LTS.

#### Не оставляйте стандартные пароли!


#### Пример содержания файла .env (Docker-compose)
```
TOKEN = "TG TOKEN"
RM_HOST = "172.17.0.1"           # Стандартный IP хост-машины для Docker
RM_PORT = "22"
RM_USER = "user"
RM_PASSWORD = "password"
DB_USER = "postgres"
DB_PASSWORD = "password"
DB_PORT = "5432"                 # Стандартный порт
DB_HOST = "db_image"             # Хостнейм контейнера
DB_DATABASE = "base"
DB_REPL_USER = "repl"
DB_REPL_PASSWORD = "password"
DB_REPL_HOST = "db_repl_image"   # Хостнейм контейнера
DB_REPL_PORT = "5433"            # Стандартный порт
```
