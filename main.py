import time
import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import pyotp
import yaml

allowed_ids = [6744940078, 7074573395]  # chaser, alex


class AuthenticatorModule:
    def __init__(self):
        pass

    def generate_totp(self, secret):
        """
        Generate the current TOTP (Time-based One-Time Password) using the secret key.

        :param secret: Secret key used to generate the TOTP.
        :return: Current TOTP.
        """
        totp = pyotp.TOTP(secret)
        return totp.now()

    def get_fresh_totp(self, secret):
        """
        Get a fresh TOTP, ensuring it's not close to expiration.

        :param secret: Secret key used to generate the TOTP.
        :return: Fresh TOTP.
        """
        totp = pyotp.TOTP(secret)

        while True:
            current_otp = totp.now()
            time_remaining = totp.interval - (time.time() % totp.interval)

            if time_remaining > totp.interval / 2:
                return current_otp, time_remaining

            time.sleep(time_remaining + 1)


class TelegramBot:
    def __init__(self, token, db_path):
        self.updater = Updater(token, use_context=True)
        self.dp = self.updater.dispatcher
        self.db_path = db_path
        self.setup_handlers()

    def setup_handlers(self):
        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))

    def start(self, update: Update, context: CallbackContext):
        if not self.checkIfUserHasRights(update):
            return

        entities = self.get_entities()
        response = "\n".join([f"{entity['id']} - {entity['name']}" for entity in entities])
        update.message.reply_text(f"Here are the available entities:\n{response}")

    def handle_message(self, update: Update, context: CallbackContext):
        if not self.checkIfUserHasRights(update):
            return

        user_id = update.message.text.strip()
        if user_id.isdigit():
            secret = self.get_secret_by_id(user_id)
            if secret:
                authService = AuthenticatorModule()
                code = authService.get_fresh_totp(secret)
                update.message.reply_text(f"Code: {code[0]}\nSeconds remain: {int(code[1])}")
            else:
                update.message.reply_text("ID not found.")
        else:
            update.message.reply_text("Please enter a valid numeric ID.")

    def get_entities(self):
        query = "SELECT id, name FROM pages"
        return self.execute_query(query)

    def get_secret_by_id(self, entity_id):
        query = "SELECT secret FROM pages WHERE id = ?"
        result = self.execute_query(query, (entity_id,))
        return result[0]['secret'] if result else None

    def execute_query(self, query, params=()):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]
        conn.close()
        return [dict(zip(column_names, row)) for row in rows]

    def checkIfUserHasRights(self, update: Update) -> bool:
        return update.effective_user.id in allowed_ids

    def run(self):
        self.updater.start_polling()
        self.updater.idle()


if __name__ == "__main__":
    with open('config.yml', 'r') as file:
        config = yaml.safe_load(file)
    TOKEN = config.get('TOKEN')
    DB_PATH = "db.db"  # "/app/db.db"  # Path to your SQLite database in the container
    bot = TelegramBot(TOKEN, DB_PATH)
    bot.run()
