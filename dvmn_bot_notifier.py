import requests
import os
import telegram
import time
from dotenv import load_dotenv
import logging


def send_crash_notification(admin_chat_id, message, bot, logger):
    bot.send_message(chat_id=admin_chat_id, text=message)
    logger.info(f"Уведомление о сбое отправлено: {message}")


def get_attempt_result(dvmn_token):
    timestamp = None
    headers = {
        "Authorization": f"Token {dvmn_token}"
    }
    while True:
        try:
            payload = {}
            if timestamp:
                payload["timestamp"] = timestamp
            response = requests.get(
                "https://dvmn.org/api/long_polling/",
                headers=headers,
                params=payload
            )
            response.raise_for_status()
            response_json = response.json()
            if response_json["status"] == "timeout":
                timestamp = response_json["timestamp_to_request"]
            elif response_json["status"] == "found":
                timestamp = response_json["last_attempt_timestamp"]
                for attempt in response_json["new_attempts"]:
                    lesson_title = attempt["lesson_title"]
                    is_negative = attempt["is_negative"]
                    lesson_url = attempt["lesson_url"]
                    yield lesson_title, is_negative, lesson_url
        except requests.exceptions.ReadTimeout:
            continue
        except ConnectionError:
            time.sleep(30)
            continue


def send_message_from_bot(dvmn_token, chat_id, bot):
    for lesson_title, is_negative, lesson_url in get_attempt_result(dvmn_token):
        if is_negative:
            is_correct = 'Преподавателю всё понравилось, можно приступать к следующему уроку ✅'
        else:
            is_correct = 'К сожалению, в работе нашлись ошибки❌'

        msg = (f'{lesson_title},\n'
               f'{is_correct},\n'
               f'{lesson_url}')
        bot.send_message(chat_id=chat_id, text=msg)


def main():
    load_dotenv()
    DVMN_TOKEN = os.environ['DVMN_TOKEN']
    NOTIFICATION_BOT_TOKEN = os.environ['NOTIFICATION_BOT_TOKEN']
    ALLERT_BOT_TOKEN = os.environ['ALLERT_BOT_TOKEN']
    CHAT_ID = os.environ['CHAT_ID']
    ADMIN_CHAT_ID = os.environ['ADMIN_CHAT_ID']
    notification_bot = telegram.Bot(token=NOTIFICATION_BOT_TOKEN)
    alert_bot = telegram.Bot(token=ALLERT_BOT_TOKEN)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)

    while True:
        try:
            logger.info("Бот запустился...")
            send_message_from_bot(dvmn_token=DVMN_TOKEN, chat_id=CHAT_ID, bot=notification_bot)
        except Exception as e:
            error_message = f"Бот упал в {time.strftime('%Y-%m-%d %H:%M:%S')}: {str(e)}"
            logger.error(error_message)
            try:
                send_crash_notification(ADMIN_CHAT_ID, error_message, alert_bot, logger)
            except Exception as notify_error:
                logger.error(f"Не удалось отправить уведомление о сбое: {str(notify_error)}")
            time.sleep(60)
            continue


if __name__ == "__main__":
    main()
