#### В качестве удаленного хоста в конфигурации рекомендуется использовать:
 - Для Docker хост-машину, запускающую контейнеры
 - Для Ansible и прочих конфигураций машину, на которой запущена основная БД
Иначе потребуется ручная настройка вывода логов репликации.


#### Пример заполнения env.yaml (Ansible)
```
TOKEN: "telegram token"
RM_HOST: "ip"
RM_PORT: "port"
RM_USER: "user"
RM_PASSWORD: "password"
DB_USER: "user"
DB_PASSWORD: "password"
DB_PORT: "port"
DB_HOST: "ip"
DB_DATABASE: "db_name"
DB_REPL_USER: "user"
DB_REPL_PASSWORD: "password"
DB_REPL_PORT: "port"
```

#### Пример заполнения .env (Docker-compose и остальные варианты запуска)
```
TOKEN = "telegram token"
RM_HOST = "ip"
RM_PORT = "port"
RM_USER = "user"
RM_PASSWORD = "password"
DB_USER = "user"
DB_PASSWORD = "password"
DB_PORT = "port"
DB_HOST = "ip"
DB_DATABASE = "db_name"
DB_REPL_USER = "user"
DB_REPL_PASSWORD = "password"
DB_REPL_PORT = "port"
```