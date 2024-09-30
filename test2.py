import mysql.connector
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

def parse_and_save():
    # Конфигурация подключения к базе данных MySQL
    config = {
        'user': 'root',
        'password': 'Uz94deco!',
        'host': '127.0.0.1',
        'database': 'parser'
    }

    # Подключение к базе данных
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # Очистка таблицы перед добавлением новых данных
    try:
        cursor.execute("TRUNCATE TABLE posts")
        conn.commit()  # Сохранение изменений в базе данных
        print("Таблица posts очищена и автоинкремент сброшен.")
    except Exception as ex:
        print(f"Ошибка при очистке таблицы: {ex}")
        conn.rollback()

    # Укажите путь к chromedriver.exe
    chrome = ""  # Замените на путь к вашему chromedriver

    service = Service(chrome)
    driver = webdriver.Chrome(service=service)

    # Ссылки для парсинга и названия каналов
    a = [     
        "https://t.me/s/ruarbitr?q=%D0%90%D1%80%D0%B1%D0%B8%D1%82%D1%80%D0%B0%D0%B6%D0%BD%D1%8B%D0%B9+%D1%81%D1%83%D0%B4", 
        "https://t.me/s/SPbGS",
        "https://t.me/s/povorotnapravo"
    ]
    nazvanie = ["Арбитраж", "Пресс-служба СПБ", "Поворот на право"]

    # Ключевые слова для поиска
    poisk = [
        "возбуждено дело", "возбуждено уголовное дело", "введена процедура конкурсного производства", 
        "заведено уголовное дело", "заключен под стражу", "административный иск", "начался процесс", 
        "разбирательство"
    ]

    try:
        driver.maximize_window()

        for i, url in enumerate(a):
            driver.get(url=url)

            for query in poisk:
                search_input = driver.find_element(By.CSS_SELECTOR, '.tgme_header_search_form_input')
                search_input.clear()

                # Вводим запрос в поле поиска
                search_input.send_keys(query)
                search_input.send_keys(Keys.RETURN)

                # Ждём загрузки результатов
                time.sleep(5)

                # Получаем HTML страницы
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                # Ищем текст всех постов
                posts = soup.find_all('div', class_='tgme_widget_message_text')

                for post in posts:
                    text = post.get_text(strip=True)

                    # Запись в базу данных
                    cursor.execute("""
                        INSERT INTO posts (channel_name, channel_link, post_text)
                        VALUES (%s, %s, %s)
                    """, (nazvanie[i], url, text))
                    conn.commit()

                    print(f"Текст поста из канала {nazvanie[i]} добавлен в базу данных.")

    except Exception as ex:
        print(ex)

    finally:
        driver.close()
        driver.quit()
        cursor.close()
        conn.close()

    # Извлечение данных из базы и запись в Excel
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM posts")
        results = cursor.fetchall()

        # Преобразуем результаты в DataFrame
        df = pd.DataFrame(results)

        # Сохраняем в Excel
        file_path = 'parsed_posts.xlsx'
        df.to_excel(file_path, index=False)
        print(f"Данные успешно сохранены в {file_path}")
        
        return file_path

    except Exception as ex:
        print(ex)

    finally:
        cursor.close()
        conn.close()
