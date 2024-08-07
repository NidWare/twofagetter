from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from authenticator import AuthenticatorModule
from database import DatabaseManager

ALLOWED_IDS = [6744940078, 6583143367, 7042153047]  # chaser, alex

class TelegramBot:
    def __init__(self, token, db_manager):
        self.updater = UpUpdaterdater(token, use_context=True)
        self.dp = self.updater.dispatcher
        self.db_manager = db_manager
        self.setup_handlers()

    def setup_handlers(self):
        """
        Set up the command and message handlers for the bot.
        """
        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))

    def start(self, update: Update, context: CallbackContext):
        """
        Handle the /start command.

        :param update: Telegram update object.
        :param context: Callback context object.
        """
        if not self.check_if_user_has_rights(update):
            return

        entities = self.db_manager.get_entities()
        response = "\n".join([f"{entity['id']} - {entity['name']}" for entity in entities])
        update.message.reply_text(f"Here are the available entities:\n{response}")

    def handle_message(self, update: Update, context: CallbackContext):
        """
        Handle incoming messages.

        :param update: Telegram update object.
        :param context: Callback context object.
        """
        if not self.check_if_user_has_rights(update):
            return

        user_id = update.message.text.strip()
        if user_id.isdigit():
            secret = self.db_manager.get_secret_by_id(user_id)
            if secret:
                auth_service = AuthenticatorModule()
                code, time_remaining = auth_service.get_fresh_totp(secret)
                update.message.reply_text(f"Code: {code}\nSeconds remain: {int(time_remaining)}")
            else:
                update.message.reply_text("ID not found.")
        else:
            update.message.reply_text("Please enter a valid numeric ID.")

    def check_if_user_has_rights(self, update: Update) -> bool:
        """
        Check if the user has the rights to use the bot.

        :param update: Telegram update object.
        :return: True if the user has rights, False otherwise.
        """
        return update.effective_user.id in ALLOWED_IDS

    def run(self):
        """
        Start the bot.
        """
        self.updater.start_polling()
        self.updater.idle()
