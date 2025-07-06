import requests
from dotenv import load_dotenv
import os
import telegram


def request_to_dvmn_api(dvmn_token):
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
            continue


def send_message_from_bot(dvmn_token, chat_id, bot):
    for lesson_title, is_negative, lesson_url in request_to_dvmn_api(dvmn_token):
        if is_negative:
            is_correct = 'Преподавателю всё понравилось, можно приступать к следующему уроку ✅'
        else:
            is_correct = 'К сожалению, в работе нашлись ошибки❌'

        msg = (f'{lesson_title},\n'
               f'{is_correct},\n'
               f'{lesson_url}')
        bot.send_message(chat_id=chat_id, text=msg)


def main ():
    load_dotenv()
    DVMN_TOKEN = os.getenv('DVMN_TOKEN')
    BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
    CHAT_ID = os.getenv('CHAT_ID')
    bot = telegram.Bot(token=BOT_TOKEN)
    send_message_from_bot(dvmn_token=DVMN_TOKEN, chat_id=CHAT_ID, bot=bot)


if __name__ == "__main__":
    main()