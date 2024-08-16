import yaml
from telegram_bot import TelegramBot
from database import DatabaseManager

if __name__ == "__main__":
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)

    TOKEN = config.get('TOKEN')
    DB_PATH = config.get('DB_PATH')
    db_manager = DatabaseManager(DB_PATH)
    bot = TelegramBot(TOKEN, db_manager)
    bot.run()
