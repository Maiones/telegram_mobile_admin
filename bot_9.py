#!/usr/bin/python3

import telebot
import paramiko
import chardet
import subprocess
import datetime
import requests

# Устанавливаем тайм-аут чтения для requests на 60 секунд
requests.adapters.DEFAULT_RETRIES = 5
requests.adapters.SOCKET_TIMEOUT = 60
requests.adapters.HTTP_ADAPTER_POOL_SIZE = 50

# установка параметров подключения к Telegram API
bot = telebot.TeleBot("5995192509:AAGfFPqLl2uV-q3IRuoyJU2kUbj-EosPrL4")

# установка параметров подключения к удаленному серверу
username = "root"
key_file = "/home/user/medkey"

scripts = {
    "Переставить бутылку": "/home/user/kva-kva/scripts/wine_pain_2.sh",
    "Переустановить wine": "/home/user/kva-kva/scripts/wine_pain_3.sh",
    "script3": "/home/user/kva-kva/scripts/wine_pain_4.sh"
}

# обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Работа с компуктером: /terminal\nРабота со скриптами: /scripts")

@bot.message_handler(commands=['scripts'])
def show_scripts(message):
    script_list = "\n".join([f"{i+1}. {key}" for i, key in enumerate(scripts.keys())])
    bot.reply_to(message, f"Доступные скрипты:\n{script_list}\nУказать /script и номер")


# обработчик команды /script
@bot.message_handler(commands=['script'])
def select_script(message):
    try:
        script_number = int(message.text.split()[1]) - 1 # получаем номер скрипта из сообщения и вычитаем 1, чтобы индексировать с 0
        script_names = list(scripts.keys())
        if script_number < len(script_names):
            script_name = script_names[script_number]
            bot.reply_to(message, f"Скрипт '{script_name}' выбран. IP?  /ip 10.XXX.XXX.XXX")
            bot.register_next_step_handler(message, get_ip_address, script_name) # регистрируем обработчик следующего шага
        else:
            bot.reply_to(message, f"Скрипт с номером {script_number + 1} не найден.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Номер скрипта не указан или указан некорректно. Например, /script 1")

# обработчик команды /ip
def get_ip_address(message, script_name):
    try:
        ip_address = message.text.split()[1] # получаем IP-адрес из сообщения
        execute_script(message, script_name, ip_address) # выполняем скрипт
    except IndexError:
        bot.reply_to(message, "IP-адрес не указан. Например, /ip 10.XXX.XXX.XXX")

# функция для выполнения скрипта на удаленном сервере
def execute_script(message, script_name, ip_address):
    try:
        # создание объекта SSH-клиента
        ssh = paramiko.SSHClient()

        # автоматическое добавление ключей хостов
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # подключение к серверу по SSH-протоколу
        ssh.connect(ip_address, username=username, key_filename=key_file)

        # чтение скрипта с сервера
        script_file = scripts[script_name]
        with open(script_file, "r") as f:
            script = f.read()

        # выполнение скрипта на сервере
        stdin, stdout, stderr = ssh.exec_command(script)

        # вывод результатов выполнения скрипта
        output = f"stdout:\n{stdout.read().decode()}\nstderr:\n{stderr.read().decode()}"

        # проверка длины сообщения перед отправкой
        if len(output) > 4096:
            output_parts = [output[i:i+4096] for i in range(0, len(output), 4096)]
            for part in output_parts:
                bot.send_message(message.chat.id, part)
        else:
            bot.send_message(message.chat.id, output)

    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при выполнении скрипта на сервере: {e}")

    finally:
        # закрытие соединения с сервером
        ssh.close()
        
        # Создаем функцию, которая будет исполнять команды в терминале и возвращать результаты
@bot.message_handler(commands=['terminal'])
def execute_command(message):
    
    # Получаем команду из сообщения пользователя
    command = message.text.split(' ', 1)
    if len(command) < 2:
        bot.reply_to(message, "Где аргументы?")
        return
    
    command = command[1]
    
    # Исполняем команду в терминале
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    output, error = process.communicate()
    detection = chardet.detect(output)
    encoding = detection['encoding'] if detection['encoding'] is not None else 'utf-8'
    output = output.decode(encoding)
    error = error.decode(encoding)
    
    # Отправляем результат пользователю
    if output:
        bot.reply_to(message, output)
    if error:
        bot.reply_to(message, error)

# запуск бота
bot.polling(none_stop=True)
       


