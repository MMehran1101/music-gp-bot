"""
This is main
"""
# -----------------------LIBRARIES-----------------------
from telethon import TelegramClient, events, types, functions
from telethon.tl.custom import Button
from telethon.tl.types import BotCommand

from configparser import ConfigParser
from DataBase import DataBase

# -----------------------SETTINGS-----------------------
config = ConfigParser()
config.read("config.ini")

BOT_TOKEN = config['Bot']['Token']
API_ID = config['ApiIdHash']['ApiId']
API_HASH = config['ApiIdHash']['ApiHash']
admins = [5721277663, 1952338586]

bot = TelegramClient("bot", api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN)

db = DataBase("music_gp.db")
db.init_db()

# -----------------------EVENTS------------------------

@bot.on(events.NewMessage(pattern="/start"))
async def new_message(event):
    user = await event.get_sender()
    if event.is_group and is_admin(user.id):
        await event.reply("Bot is Activate ✅")
        return
    if not is_admin(user.id):
        await event.respond("Hey there👋\n\n⚠️ Sorry, your account has not defined to chat with this bot."
                            "\n\n📞 Please contact with owner : @lzruenal")
        return
    await event.respond(f"Welcome {user.first_name} 👋\n\nHave good day🌞", buttons=home_menu())


@bot.on(events.CallbackQuery(pattern=b"btn_.*"))
async def callback_handler(event: events.CallbackQuery.Event):
    data = event.data.decode().split("_")[1]

    if data == "createlist":
        pass
    elif data == "showlist":
        pass
    elif data == "aboutus":
        await event.answer("My name is Mehran Fallah and creator of this bot")
    elif data == "help":
        await event.answer("There is nothing to help")


# -----------------------FUNCTIONS---------------------

def is_admin(user_id: int) -> bool:
    if user_id in admins:
        return True
    return False


def home_menu():
    keyboard = [
        [
            Button.inline("🎶 تهیه لیست موسیقی هفته 🎶", data="btn_createlist")
        ],
        [
            Button.inline("🔆 نمایش لیست موسیقی هفته 🔆", data="btn_showlist")
        ],
        [
            Button.inline("📢 راهنما", data="btn_help"),
            Button.inline("👥 درباره ما 👥", data="btn_aboutus")
        ]
    ]
    return keyboard


def show_list_menu():
    # this methode connect with db
    keyboard = [
        [Button.inline("بازگشت", data="btn_home")]
    ]


async def setup_commands():
    """
    Setup command button on bot.
    """
    commands = [
        BotCommand("start", "شروع بات"),
        BotCommand("help", "راهنما")
    ]

    await bot(functions.bots.SetBotCommandsRequest(
        scope=types.BotCommandScopeDefault(),
        lang_code="",
        commands=commands
    ))


# -----------------------RUN---------------------
print("BOT STARTED")
with bot:
    bot.loop.run_until_complete(setup_commands())
    bot.run_until_disconnected()
