from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from authenticator import AuthenticatorModule
from database import DatabaseManager

ALLOWED_IDS = [6744940078, 6583143367, 7042153047]  # chaser, rupert, liza
TEAMLEAD_IDS = [102768495]

class TelegramBot:
    def __init__(self, token, db_manager):
        self.updater = Updater(token, use_context=True)
        self.dp = self.updater.dispatcher
        self.db_manager = db_manager
        self.setup_handlers()

    def setup_handlers(self):
        """
        Set up the command and message handlers for the bot.
        """
        self.dp.add_handler(CommandHandler("start", self.start))
        self.dp.add_handler(CommandHandler("add", self.add))
        self.dp.add_handler(CommandHandler("del", self.delete))
        self.dp.add_handler(CallbackQueryHandler(self.button))
        self.dp.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))

    def start(self, update: Update, context: CallbackContext):
        """
        Handle the /start command.

        :param update: Telegram update object.
        :param context: Callback context object.
        """
        if not self.check_if_user_has_rights(update):
            return

        pages = self.db_manager.get_entities()
        buttons = []

        for page in pages:
            buttons.append([InlineKeyboardButton(f"{page['name']}", callback_data=page['id'])])

        reply_markup = InlineKeyboardMarkup(buttons)
        update.message.reply_text('Please choose:', reply_markup=reply_markup)

    def button(self, update: Update, context: CallbackContext) -> None:
        query = update.callback_query

        # CallbackQueries need to be answered, even if no notification to the user is needed
        query.answer()

        # Here, you can handle what happens when a button is pressed
        query.edit_message_text(text=f"Selected option: {query.data}")

    def add(self, update: Update, context: CallbackContext):
        """
        Handle the /add command.

        :param update: Telegram update object.
        :param context: Callback context object.
        """
        if not self.check_if_user_has_rights(update):
            return

        text = update.message.text
        commands = text.split()

        id = commands[1]
        name = commands[2]
        code = commands[3]
        self.db_manager.execute_query("INSERT INTO pages VALUES (?, ?, ?)", (id, name, code))
        update.message.reply_text(f"Added {id} {name} {code}")

    def delete(self, update: Update, context: CallbackContext):
        """
        Handle the /add command.

        :param update: Telegram update object.
        :param context: Callback context object.
        """
        if not self.check_if_user_has_rights(update):
            return

        text = update.message.text
        commands = text.split()

        id = commands[1]
        self.db_manager.execute_query("DELETE FROM pages WHERE id = ?", id)
        update.message.reply_text(f"Deleted model with {id}")


    def handle_message(self, update: Update, context: CallbackContext):
        """
        Handle incoming messages.

        :param update: Telegram update object.
        :param context: Callback context object.
        """

        # if update.effective_user.id in TEAMLEAD_IDS:
        #     site_service =

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
