# Телеграм-бот для отправки уведомлений о проверке работ
Бот использует API при помощи long polling, получая информацию о правильном или неправильном выполнении задания.

## Запуск
1. Установите необходимые зависимости командой:
```
pip install -r requirements.txt
```
2. Создайте своего бота через `Bot-Father`
3. В файлы окружения введите `TG_BOT_TOKEN`, `DVMN_TOKEN`, `CHAT_ID`
4. Запускаем бота, из директории проекта, командой
```
python request_to_API.py
```

### Вид отправленного уведомления о проверке
<img alt="Пример" src="./Снимок.PNG"/>