Телеграм-бот для мониторинга различных показателей сервера, поиска и записи в базу данных телефонов и электронных почт из текста, проверки надежности пароля.


###  !!! ВАЖНО !!!
Конфигурации в каждой ветке **различаются**. Ниже представлен .env файл для самого бота. Файлы конфигураций для развертывания через docker-compose и ansible находятся в соответствующих ветках репозитория. 

```
TOKEN= "Токен_бота"
RM_HOST= "IP-хоста_для_мониторинга_или_его_доменное_имя"
RM_PORT= "Порт_SSH_хоста"
RM_USER= "Пользователь_хоста"
RM_PASSWORD= "Пароль_хоста"
DB_USER= "Имя_пользователя_бд"					
DB_PASSWORD= "Пароль_БД"
DB_PORT= "Порт_БД"
DB_HOST= "IP-адрес_или_доменное_имя_ДБ"
DB_DATABASE= "Имя_бд"
```
