touch /etc/systemd/system/openai-telegram-bot.service
chmod 664 /etc/systemd/system/openai-telegram-bot.service

/

[Unit]
Description=OpenAi Telegram bot
After=network.target
[Service]
ExecStart=/usr/bin/python3 /root/openai_telegram_bot/main.py
[Install]
WantedBy=multi-user.target

systemctl daemon-reload
systemctl start openai-telegram-bot.service
systemctl enable openai-telegram-bot.service

systemctl status openai-telegram-bot.service

https://t.me/yurchest_chatgpt_bot
Телеграм бот предназнчен для легкого взаимодействия с OpenAI API (ChatGPT).
Открыв бота и нажав Start, прользователь увидит контент, представленный на рисунке "приветствие.png". У пользователя есть 50 бесплатных пробных запросов для знакомства с сервисом. Чтобы получить неограниченное число запросов, необходимо оплатить подписку (на данный момент 100 руб.). Также присутствует кнопка меню "/reset_conversation", сбрасывающая историю сообщений (необходимо, если пользователь хочет поменять тему диалога).  Пример работы бота представлен на рисунке "работа.jpg".
Данные пользователя хранятся в базе даных на выделенном сервере.