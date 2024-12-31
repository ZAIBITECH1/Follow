import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# Initialize logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "7432378274:AAGlE28b8ayYHucjOTB17Ic5oOG-BVtZGrs"

# Global dictionaries to manage user states and connections
user_states = {}  # Tracks whether users are connected, searching, or idle
connections = {}  # Maps user_id -> partner_id

# Function to create persistent keyboard
def get_persistent_keyboard():
    keyboard = [
        [KeyboardButton("Find"), KeyboardButton("Next")],
        [KeyboardButton("Stop"), KeyboardButton("Help")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /start command."""
    keyboard = get_persistent_keyboard()
    await update.message.reply_text(
        "Welcome to the bot! Use the buttons below to start chatting.Click on Find button,share your username, send screenshots to show that you have followed successfully, Click on Next button to find another partner.Please follow me also..my username is 👉 zaibi077 ",
        reply_markup=keyboard,
    )

async def find_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Connects a user to a random partner."""
    user_id = update.message.from_user.id
    if user_id in connections:
        await update.message.reply_text(
            "You are already connected to someone. Use 'Next' to find another partner."
        )
        return

    user_states[user_id] = "searching"
    for partner_id, state in user_states.items():
        if state == "searching" and partner_id != user_id:
            # Connect the users
            connections[user_id] = partner_id
            connections[partner_id] = user_id
            user_states[user_id] = "connected"
            user_states[partner_id] = "connected"

            await update.message.reply_text("You are now connected to a partner. Start chatting!")
            await context.bot.send_message(
                chat_id=partner_id, text="You are now connected to a partner. Start chatting!"
            )
            return

    await update.message.reply_text("Searching for a partner... Please wait.")

async def next_partner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Disconnects from the current partner and searches for a new one."""
    user_id = update.message.from_user.id
    if user_id not in connections:
        await update.message.reply_text("You are not connected. Use 'Find' to search for a partner.")
        return

    partner_id = connections[user_id]
    await context.bot.send_message(
        chat_id=partner_id, text="Your partner has left the chat. Click 'Next' to find another partner."
    )
    await update.message.reply_text("You have left the chat. Click 'Next' to find another partner.")

    # Disconnect the users
    del connections[user_id]
    del connections[partner_id]
    user_states[user_id] = "searching"
    user_states[partner_id] = "idle"

    await find_partner(update, context)

async def stop_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stops the current chat session."""
    user_id = update.message.from_user.id
    if user_id in connections:
        partner_id = connections[user_id]
        await context.bot.send_message(
            chat_id=partner_id, text="Your partner has ended the chat. Click 'Find' to start chatting with someone new."
        )
        del connections[user_id]
        del connections[partner_id]
        user_states[partner_id] = "idle"

    user_states[user_id] = "idle"
    await update.message.reply_text("Chat ended. Click 'Find' to start chatting with someone new.")

async def show_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays help options."""
    keyboard = [
        [InlineKeyboardButton("Contact Us", url="https://t.me/Zaibi077")],
        [InlineKeyboardButton("Join Us", url="https://t.me/ZAIBITECH")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Need help? Use the buttons below to get in touch or join our group.",
        reply_markup=reply_markup,
    )

async def relay_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Relays messages between connected users."""
    user_id = update.message.from_user.id
    if user_id in connections:
        partner_id = connections[user_id]
        if update.message.text:
            await context.bot.send_message(chat_id=partner_id, text=update.message.text)
        elif update.message.photo:
            photo = update.message.photo[-1]
            await context.bot.send_photo(chat_id=partner_id, photo=photo.file_id)

# Initialize the bot application
application = Application.builder().token(TOKEN).build()

# Add handlers to the bot
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.Text("Find"), find_partner))
application.add_handler(MessageHandler(filters.Text("Next"), next_partner))
application.add_handler(MessageHandler(filters.Text("Stop"), stop_chat))
application.add_handler(MessageHandler(filters.Text("Help"), show_help))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, relay_message))

# Run the bot locally with polling
print("Bot is running locally. Press Ctrl+C to stop.")
application.run_polling()
