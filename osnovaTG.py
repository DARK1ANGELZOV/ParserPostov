import telebot
from test2 import parse_and_save  
import time
import threading

TOKEN = "7432948931:AAEffvDxnoxlRJ_j-DJwIAV238v8Nc20KBo"  # Замените на ваш реальный токен
bot = telebot.TeleBot(TOKEN)

CHANNEL_ID = "-1002157028324"  # Замените на ваш реальный ID канала

def send_parsed_data():
    while True:
        try:
            # Запуск парсинга и получение пути к Excel файлу
            file_path = parse_and_save()
            
            # Отправляем Excel файл в канал
            with open(file_path, 'rb') as file:
                bot.send_document(CHANNEL_ID, file)
            print("Файл успешно отправлен в канал.")
        
        except Exception as e:
            print(f"Произошла ошибка: {e}")
        
        # Ожидание перед следующим выполнением (10 минут)
        time.sleep(600)

# Запуск парсинга в отдельном потоке
thread = threading.Thread(target=send_parsed_data)
thread.start()

# Команда start для запуска бота
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id, "Бот запущен. Файлы будут отправляться каждые 10 минут.")

# Запуск бота
bot.polling(none_stop=True, interval=0)
