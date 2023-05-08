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