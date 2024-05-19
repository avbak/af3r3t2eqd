
Телеграм-бот для мониторинга различных показателей сервера, поиска и записи в базу данных телефонов и электронных почт из текста, проверки надежности пароля.


###  !!! ВАЖНО !!!
Конфигурации в каждой ветке **различаются**. Ниже представлен **inventory** файл для развертывания через **ansible**.

Рекомендуется сохранить стандартные порты (уже указаны ниже) для БД и БД-репликации! .
При создании нового пользователя **не называйте его postgres** и не начинайте его имя с цифры, во избежание ошибок. Новый пользователь будет иметь доступ только к БД, содержащей таблицы с телефонами почтами.

Плейбук разделен на 3 подзадачи (развертывание БД, развертывание БД-репликации, развертвывание бота). По умолчанию плейбук развертывает БД и бота на хосте 02 и БД-репликацию на хосте 01. При желании в inventory можно добавить еще один хост и назначить его в плейбуке для развертывания проекта на 3-х машинах. 

Плейбук протестирован на Ubuntu Server 22.04 LST (**предпочтительно**) и Debian Server 12 Bookworm. Для успешного развертывания необходимо установить shhpass на машину, с которой будет развертываться проект, а так же настроить SSH на всех участвующих машинах. Пользователь-ansible должен иметь возможность выполнять все команды на своем хосте без ввода пароля.
 
```
all:
  vars:
    TOKEN: "Токен_бота"
    RM_HOST: "IP-хоста_для_мониторинга_или_его_доменное_имя"
    RM_PORT: "Порт_SSH_хоста"
    RM_USER: "Пользователь_хоста"
    RM_PASSWORD: "Пароль_хоста"
    DB_USER: "Имя_пользователя_бд"
    DB_PASSWORD: "Пароль_БД"
    DB_PORT: "5432"
    DB_HOST: "IP-адрес_БД_или_ее_доменное_имя"
    DB_DATABASE: "Имя_БД"
    DB_REPL_USER: "Пользователь_репликации"
    DB_REPL_PASSWORD: "Пароль_репликации"
    DB_REPL_PORT: "5432"
  hosts:
    host01:
      ansible_host: IP_адрес_хоста_01
      ansible_user: ansible
      ansible_password: Пароль_Ansible
    host02:
      ansible_host: IP_адрес_хоста_02
      ansible_user: ansible
      ansible_password: Пароль_Ansible
```
