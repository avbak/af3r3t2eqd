import logging, re, paramiko, os
import psycopg2
from psycopg2 import Error
from functools import partial

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
)


env_type = "other"  # "docker" - для запуска через docker-compose, "other" - для остальных способов запуска

if env_type == "docker":
    import shutil
else:
    from dotenv import load_dotenv

    load_dotenv()


logging.basicConfig(
    filename="tg_bot.log",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.DEBUG,
)

logger = logging.getLogger(__name__)


def start(update: Update, context):
    user = update.effective_user
    update.message.reply_text(
        f"Привет, {user.full_name}! Используй /help для получения списка доступных команд."
    )


def helpCommand(update: Update, context):
    help_text = (
        "СПИСОК ДОСТУПНЫХ КОМАНД \n\n"
        "Команды обработки текста:\n"
        "/find_email - найти почты в тексте\n"
        "/find_phone_number - найти номера телефона в тексте\n"
        "/get_emails - получить почты из БД\n"
        "/get_phone_numbers - получить телефоны из БД\n"
        "/verify_password - проверить пароль\n"
        "\n"
        "Команды работы с системой:\n"
        "/get_release - получить информацию о релизе\n"
        "/get_uname - получить информацию о системе (uname)\n"
        "/get_uptime - получить информацию о времени работы системы\n"
        "/get_df - получить информацию о дисковом пространстве\n"
        "/get_free - получить информацию о свободной памяти\n"
        "/get_mpstat - получить информацию о загрузке процессора\n"
        "/get_w - получить список пользователей, вошедших в систему\n"
        "/get_auths - получить информацию об последних 10 входах\n"
        "/get_critical - получить критические ошибки в системных журналах\n"
        "/get_ps - получить список процессов\n"
        "/get_ss - получить список служб\n"
        "/get_apt_list - получить список установленных пакетов (APT)\n"
        "/get_services - получить список работающих служб\n"
        "/get_repl_logs - получить логи репликации\n"
    )
    update.message.reply_text(help_text)


def connect_to_ssh():
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=os.getenv("RM_HOST"),
            username=os.getenv("RM_USER"),
            password=os.getenv("RM_PASSWORD"),
            port=os.getenv("RM_PORT"),
        )
        logging.debug("Успешно подключились к SSH")
        return client
    except Exception as e:
        logging.error("Ошибка при подключении к SSH: %s", e)
        return None


def executor(update: Update, context, command):
    try:
        client = connect_to_ssh()
        stdin, stdout, stderr = client.exec_command(command)
        data = stdout.read() + stderr.read()
        data = str(data).replace("\\n", "\n").replace("\\t", "\t")[2:-1]
        update.message.reply_text(data)
        logging.debug("Команда на сервере выполнена")
        return ConversationHandler.END
    except Exception as e:
        logging.error("Ошибка при выполнении команды на сервере: %s", e)
        update.message.reply_text(
            "Сервер в данный момент недоступен. Попробуйте позже."
        )
        return ConversationHandler.END


def docker_logs(update: Update, context):
    source_file = "/psqllog/postgresql.log"
    destination_file = "/psqllog/postgresql_copy.log"
    if not os.path.isfile(source_file):
        update.message.reply_text("Файл логов репликации не найден. Попробуйте позже.")
        return ConversationHandler.END
    try:
        shutil.copyfile(source_file, destination_file)
        logging.debug("Создана копия лога")
        keywords = re.compile(r"replication|statement|checkpoint|wal", re.IGNORECASE)
        with open(destination_file, "r") as file:
            lines = file.readlines()
        logging.debug("Открыта копия лога")
        matching_lines = [line for line in lines if keywords.search(line)]
        if not matching_lines:
            update.message.reply_text("Логи репликации отсутствуют. Попробуйте позже.")
            return ConversationHandler.END
        data = ""
        for line in matching_lines[-10:]:
            data += f"{line}\n"
        update.message.reply_text(data)
    except:
        update.message.reply_text("Логи репликации отсутствуют. Попробуйте позже.")
    finally:
        os.remove(destination_file)
        logging.debug("Удалена копия лога")
        return ConversationHandler.END


def basecheck(update: Update, context, operand):
    connection = None

    try:
        connection = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_DATABASE"),
        )
        cursor = connection.cursor()
        cursor.execute(f"{operand};")
        data = cursor.fetchall()
        formatted = "\n".join(
            [f"{index + 1}: {row[1]}" for index, row in enumerate(data)]
        )

        update.message.reply_text(formatted)
        logging.debug("Получение данных из БД успешно")
        if connection is not None:
            cursor.close()
            connection.close()
        return ConversationHandler.END
    except (Exception, Error) as error:
        if connection is not None:
            cursor.close()
            connection.close()
        logging.error("Ошибка при подключении к БД: %s", error)
        update.message.reply_text("Нет подключения к БД. Попробуйте позже.")
        return ConversationHandler.END


def basesend(operand, base_op):
    connection = None
    try:
        connection = psycopg2.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            database=os.getenv("DB_DATABASE"),
        )
        cursor = connection.cursor()
        if base_op == "p":
            eight = operand.replace("+7", "8")
            nums_only = re.sub(r"\D", "", eight)
            command = f"INSERT INTO phones (phone) VALUES ('{nums_only}') ON CONFLICT (phone) DO NOTHING;;"
        if base_op == "e":
            command = f"INSERT INTO emails (email) VALUES ('{operand}') ON CONFLICT (email) DO NOTHING;"

        cursor.execute(command)
        connection.commit()
        logging.debug("Данные успешно отправлены в БД")
        if connection is not None:
            cursor.close()
            connection.close()
        return ConversationHandler.END
    except (Exception, Error) as error:
        logging.error("Ошибка при подключении к БД: %s", error)
        if connection is not None:
            cursor.close()
            connection.close()
        return error


def sanitize_apt(text):
    match = re.search(r"[a-zA-Z0-9][\w\-\.]*", text)
    if match:
        new_text = str(match.group(0))
        return new_text
    else:
        return None


def aptCommand(update: Update, context):
    update.message.reply_text(
        "Чтобы получить информацию о всех пакетах введите <all>, для получения информации по конкретному пакету введите <name>"
    )
    return "findApt"


def findApt(update: Update, context):
    user_input = update.message.text
    if user_input == "all":
        logging.debug("Запрашиваем иформацию обо всех APT-пакетах у сервера")
        executor(update, context, "apt list --installed | head -c 4000")
    else:
        logging.debug("Запрашиваем иформацию конкретном APT-пакете у сервера")
        executor(update, context, f"apt show {sanitize_apt(user_input)}")
    return ConversationHandler.END


def checkPassCommand(update: Update, context):
    text = (
        "Введите пароль для проверки надежности.\nНадежным считается пароль, следующий условиям: \n\n"
        "  - Пароль должен содержать не менее восьми символов.\n"
        "  - Пароль должен включать как минимум одну заглавную букву.\n"
        "  - Пароль должен включать хотя бы одну строчную букву.\n"
        "  - Пароль должен включать хотя бы одну цифру.\n"
        "  - Пароль должен включать хотя бы один символ, такой как !@#$%^&*().\n"
    )
    update.message.reply_text(text)
    return "findPass"


def findPass(update: Update, context):
    user_input = update.message.text
    passRegex = re.compile(
        r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*()]).{8,}$"
    )
    passList = passRegex.findall(user_input)
    if not passList:
        update.message.reply_text("Пароль простой")
        return ConversationHandler.END
    update.message.reply_text("Пароль сложный")
    return ConversationHandler.END


def findEmailsCommand(update: Update, context):
    update.message.reply_text("Введите текст для поиска почт: ")
    return "findEmails"


def findEmails(update: Update, context):
    user_input = update.message.text
    emailRegex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

    emailList = emailRegex.findall(user_input)

    if not emailList:
        update.message.reply_text("Почты не найдены")
        return ConversationHandler.END

    emails = ""
    unique_emails = set()
    for i in range(len(emailList)):
        if emailList[i] not in unique_emails:
            unique_emails.add(emailList[i])
            emails += f"{len(unique_emails)}. {emailList[i]}\n"

    update.message.reply_text(emails)
    context.user_data["emailList"] = emailList
    update.message.reply_text("Хотите добавить найденные почты в базу данных? (+/-)")
    return "confirmEmails"


def confirmEmails(update: Update, context):
    user_response = update.message.text.strip().lower()

    if user_response == "+":
        emailList = context.user_data.get("emailList")
        for i in range(len(emailList)):
            result = basesend(str(emailList[i]), "e")
            if isinstance(result, psycopg2.Error):
                logging.error("Ошибка записи почт в БД")
                update.message.reply_text("Нет подключения к БД. Попробуйте позже.")
                return ConversationHandler.END

        update.message.reply_text("Почты успешно добавлены в базу данных!")
        logging.debug("Почты успешно добавлены в базу данных!")
    elif user_response == "-":
        update.message.reply_text("Почты не были добавлены в базу данных.")
    else:
        update.message.reply_text("Пожалуйста, введите только '+' или '-'.")
        return "confirmEmails"
    return ConversationHandler.END


def findPhoneNumbersCommand(update: Update, context):
    text = (
        "Введите текст для поиска телефонных номеров. Поддерживаемые форматы: \n"
        "   8XXXXXXXXXX \n"
        "   8(XXX)XXXXXXX\n"
        "   8 XXX XXX XX XX\n"
        "   8-XXX-XXX-XX-XX\n"
        "   8 (XXX) XXX XX XX\n"
        "   Допускается использование +7 заместо 8\n"
    )
    update.message.reply_text(text)
    return "findPhoneNumbers"


def findPhoneNumbers(update: Update, context):
    user_input = update.message.text
    phoneNumRegex = re.compile(
        re.compile(r"(?:\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}")
    )

    phoneNumberList = phoneNumRegex.findall(user_input)
    if not phoneNumberList:
        update.message.reply_text("Телефонные номера не найдены")
        return ConversationHandler.END

    phoneNumbers = ""
    unique_phones = set()
    for i in range(len(phoneNumberList)):
        eight = phoneNumberList[i].replace("+7", "8")
        nums_only = re.sub(r"\D", "", eight)
        if nums_only not in unique_phones:
            unique_phones.add(nums_only)
            phoneNumbers += f"{len(unique_phones)}. {nums_only}\n"

    update.message.reply_text(phoneNumbers)
    context.user_data["phoneNumberList"] = phoneNumberList
    update.message.reply_text("Хотите добавить номер в базу данных? (+/-)")
    return "confirmAddPhones"


def confirmAddPhones(update: Update, context):
    user_response = update.message.text.strip().lower()

    if user_response == "+":
        phoneNumberList = context.user_data.get("phoneNumberList")
        for i in range(len(phoneNumberList)):
            result = basesend(str(phoneNumberList[i]), "p")
            if isinstance(result, psycopg2.Error):
                logging.error("Ошибка записи телефонов в БД")
                update.message.reply_text("Нет подключения к БД. Попробуйте позже.")
                return ConversationHandler.END

        update.message.reply_text("Номер успешно добавлен в базу данных!")
        logging.debug("Телефоны успешно добавлены в базу данных!")
    elif user_response == "-":
        update.message.reply_text("Номер не был добавлен в базу данных.")
    else:
        update.message.reply_text("Пожалуйста, введите только '+' или '-'.")
        return "confirmAddPhones"
    return ConversationHandler.END


def main():
    logging.debug("Начинаем работу")
    updater = Updater(os.getenv("TOKEN"), use_context=True)
    dp = updater.dispatcher

    convHandlerFindPhoneNumbers = ConversationHandler(
        entry_points=[CommandHandler("find_phone_number", findPhoneNumbersCommand)],
        states={
            "findPhoneNumbers": [
                MessageHandler(Filters.text & ~Filters.command, findPhoneNumbers)
            ],
            "confirmAddPhones": [
                MessageHandler(Filters.text & ~Filters.command, confirmAddPhones)
            ],
        },
        fallbacks=[],
    )

    convHandlerfindEmails = ConversationHandler(
        entry_points=[CommandHandler("find_email", findEmailsCommand)],
        states={
            "findEmails": [MessageHandler(Filters.text & ~Filters.command, findEmails)],
            "confirmEmails": [
                MessageHandler(Filters.text & ~Filters.command, confirmEmails)
            ],
        },
        fallbacks=[],
    )

    convHandlercheckPass = ConversationHandler(
        entry_points=[CommandHandler("verify_password", checkPassCommand)],
        states={
            "findPass": [MessageHandler(Filters.text & ~Filters.command, findPass)],
        },
        fallbacks=[],
    )

    convHandlerfindApt = ConversationHandler(
        entry_points=[CommandHandler("get_apt_list", aptCommand)],
        states={
            "findApt": [MessageHandler(Filters.text & ~Filters.command, findApt)],
        },
        fallbacks=[],
    )

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", helpCommand))
    dp.add_handler(
        CommandHandler("get_release", partial(executor, command="lsb_release -a"))
    )
    dp.add_handler(CommandHandler("get_uname", partial(executor, command="uname -a")))
    dp.add_handler(CommandHandler("get_uptime", partial(executor, command="uptime")))
    dp.add_handler(CommandHandler("get_df", partial(executor, command="df -h")))
    dp.add_handler(CommandHandler("get_free", partial(executor, command="free -h")))
    dp.add_handler(CommandHandler("get_mpstat", partial(executor, command="mpstat")))
    dp.add_handler(CommandHandler("get_w", partial(executor, command="w")))
    dp.add_handler(CommandHandler("get_auths", partial(executor, command="last -10")))
    dp.add_handler(
        CommandHandler(
            "get_critical", partial(executor, command="journalctl -r -p crit -n 5")
        )
    )
    dp.add_handler(CommandHandler("get_ps", partial(executor, command="ps")))
    dp.add_handler(
        CommandHandler("get_ss", partial(executor, command="ss | head -c 4000"))
    )
    dp.add_handler(
        CommandHandler(
            "get_services",
            partial(executor, command="service --status-all | grep + | head -c 4000"),
        )
    )

    if env_type == "docker":
        dp.add_handler(CommandHandler("get_repl_logs", partial(docker_logs)))
    else:
        dp.add_handler(
            CommandHandler(
                "get_repl_logs",
                partial(
                    executor,
                    command="cat /var/log/postgresql/postgresql-16-main.log | grep -iE 'replication|statement|checkpoint|wal' | tail -n 10",
                ),
            )
        )
    dp.add_handler(
        CommandHandler("get_emails", partial(basecheck, operand="SELECT * FROM emails"))
    )
    dp.add_handler(
        CommandHandler(
            "get_phone_numbers", partial(basecheck, operand="SELECT * FROM phones")
        )
    )
    dp.add_handler(convHandlerfindApt)
    dp.add_handler(convHandlerFindPhoneNumbers)
    dp.add_handler(convHandlerfindEmails)
    dp.add_handler(convHandlercheckPass)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
