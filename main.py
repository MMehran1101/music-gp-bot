"""
This is main
"""

# -----------------------LIBRARIES-----------------------
from configparser import ConfigParser
import asyncio
import re

from telethon import TelegramClient, events, types, functions
from telethon.tl.custom import Button
from telethon.tl.types import BotCommand
from telethon.tl.types import MessageMediaDocument


import jdatetime
from DataBase import DataBase

# -----------------------SETTINGS-----------------------
config = ConfigParser()
config.read(r"config.ini")

BOT_TOKEN = config["Bot"]["Token"]
API_ID = config["ApiIdHash"]["ApiId"]
API_HASH = config["ApiIdHash"]["ApiHash"]
admins = [5721277663, 1952338586]

bot = TelegramClient("bot", api_id=API_ID, api_hash=API_HASH).start(bot_token=BOT_TOKEN)

# -----------------------DATABASE-----------------------
db = DataBase("music_gp.db")
db.init_db()

# -----------------------WEEK DATA-----------------------
WEEK_ID = jdatetime.date.today().isocalendar()[1]
WEEK_START = (
    f"{jdatetime.date.today().year}/{jdatetime.date.today().month}/"
    f"{jdatetime.date.today().day}"
)

# -----------------------TEXTS-----------------------
TEXT_MENU = "Welcome 👋\n\nHave good day😄\n\nWhat you plan to do ?"
TEXT_WEEK = (
    "**Music of The Week • موسیقی هفته**"
    f"\n\n🔹هفته {WEEK_ID} ام سال ۱۴۰۴"
    f"\n🔸تاریخ شروع هفته : {WEEK_START}"
    "\n\n🎧#MusicOfTheWeek"
)

TOPIC_SIGN = {
    "Instrumental": "🎹",
    "Persian": "🦁",
    "Persian Rap": "🎙",
    "Global": "🌐",
    "Phonk": "👿",
}

TOPIC_CODE = {
    "863": "Global",
    "864": "Persian",
    "859": "Persian Rap",
    "1068": "Phonk",
    "1": "Instrumental",
}
# -----------------------EVENTS------------------------


@bot.on(events.NewMessage(pattern="/start"))
async def new_message(event):
    user = await event.get_sender()
    if event.is_group and is_admin(user.id):
        await event.reply("Bot is Activate ✅")
        return
    if not is_admin(user.id):
        await event.respond(
            "Hey there👋\n\n⚠️ Sorry, your account has not defined to chat with this bot."
            "\n\n📞 Please contact with owner : @lzruenal"
        )
        return
    await event.respond(TEXT_MENU, buttons=home_menu())


@bot.on(events.NewMessage(pattern="/active"))
async def add_list_on_group(event: events.CallbackQuery.Event):
    user = await event.get_sender()
    if event.is_group and is_admin(user.id):
        week_list = db.get_list_of_week(WEEK_ID)
        await event.reply(TEXT_WEEK, buttons=build_week_button(week_list))

    await event.delete()


@bot.on(events.CallbackQuery(pattern=b"btn_.*"))
async def callback_handler(event: events.CallbackQuery.Event):
    data = event.data.decode().split("_")[1]

    if data == "addmusic":
        await event.edit(
            "🔗**ثبت لینک** \n\nلطفا لینک خود را بفرستید : ", buttons=back_menu()
        )

    elif data == "showlist":
        pass

    elif data == "aboutus":
        await event.answer("My name is Mehran Fallah and creator of this bot")
    elif data == "help":
        await event.answer("There is nothing to help")
    elif data == "back":
        await event.edit(TEXT_MENU, buttons=home_menu())


@bot.on(events.NewMessage())
async def msg_bot_handler(event):
    if event.via_bot_id:
        text = event.text
        pattern = r"Name:\s*(.*)\nTopic:\s*(.*)\nLink:\s*(.*)\nalt:\s*(.*)"
        match = re.search(pattern, text)

        if match:
            name, topic, link, alt = match.groups()
            add_to_db(name, topic, link, alt)

        await asyncio.sleep(3)
        await event.delete()


@bot.on(events.InlineQuery(pattern=r"https://t.me/Instrumental_Mosic/.*"))
async def inline_query(event: events.InlineQuery.Event):
    link = event.text
    builder = event.builder
    channel_username = event.text.split("/")[3]
    topic_id = event.text.split("/")[4]
    try:
        msg_id = event.text.split("/")[5]
    except (IndexError, ValueError):
        res = [
            builder.article(
                title="❗❗ COPY FROM TOPIC ❗❗",
                description="PLEASE copy music link from their Topic not from All topic!!",
                text="INDEX ERROR",
            )
        ]
        respond = event.answer(res)
        await respond
        return

    message = await bot.get_messages(channel_username, ids=int(msg_id))

    if not message:
        return {"error": "Message not found"}

    # Check if message has media
    if not message.media or not isinstance(message.media, MessageMediaDocument):
        return {"error": "No audio file found in this message"}

    doc = message.media.document

    # Extract audio attributes
    audio_info = {
        "file_name": None,
        "title": None,
        "performer": None,
        "duration": None,
        "file_size": doc.size,
        "mime_type": doc.mime_type,
        "caption": message.text,
    }

    # Parse document attributes
    for attr in doc.attributes:
        attr_type = type(attr).__name__
        if attr_type == "DocumentAttributeFilename":
            audio_info["file_name"] = attr.file_name

        elif attr_type == "DocumentAttributeAudio":
            print("this is vers : ", vars(attr))
            audio_info["title"] = attr.title
            audio_info["performer"] = attr.performer
            audio_info["duration"] = attr.duration

    # Check Topic of music
    if topic_id in list(TOPIC_CODE.keys()):
        topic_name = TOPIC_CODE[topic_id]
        res = [
            builder.article(
                title=f"🎧 {audio_info['title']}",
                description=f"Artist : {audio_info['performer']}\
                        \nTopic : {TOPIC_SIGN[topic_name]} {topic_name}",
                text=f"🎧 MUSIC SELECTED : \
                \nName: {audio_info['title']}\nTopic: {topic_name}\nLink: {link}\nalt: {None}",
            )
        ]
        await event.answer(res)
    else:
        res = [
            builder.article(
                title="Wrong Link ❗❗",
                description="PLEASE copy music link from their Topic.",
                text="WRONG LINK",
            )
        ]
        await event.answer(res)


# -----------------------FUNCTIONS---------------------


def is_admin(user_id: int) -> bool:
    if user_id in admins:
        return True
    return False


def build_week_button(wlist: list):
    btns = []
    wlist.sort(key=lambda item: item[1])
    whitespace = 3
    for l in wlist:
        topic_text = (TOPIC_SIGN[l[1]] + l[1]) + " " * whitespace
        name_text = " " * whitespace + l[2]
        btns.append([Button.url(f"{topic_text}•••{name_text} {l[4]}", l[3])])

    return btns


def home_menu():
    keyboard = [
        [Button.inline("🎶 تهیه لیست موسیقی هفته 🎶", data="btn_addmusic")],
        [Button.inline("🔹 نمایش لیست موسیقی هفته 🔹", data="btn_showlist")],
        [
            Button.inline("📢 راهنما", data="btn_help"),
            Button.inline("👥 درباره ما 👥", data="btn_aboutus"),
        ],
    ]
    return keyboard


def back_menu():
    keyboard = [[Button.inline("بازگشت", data="btn_back")]]
    return keyboard


def show_list_menu():
    # this methode connect with db
    keyboard = [[Button.inline("بازگشت", data="btn_home")]]
    return keyboard


def add_to_db(name, topic, link, alt):
    # get weekid and plus one for next week
    weekid = WEEK_ID + 1
    db.add_music(name, link, topic, alt, weekid)


async def setup_commands():
    """
    Setup command button on bot.
    """
    commands = [BotCommand("start", "شروع بات"), BotCommand("help", "راهنما")]

    await bot(
        functions.bots.SetBotCommandsRequest(
            scope=types.BotCommandScopeDefault(), lang_code="", commands=commands
        )
    )


# -----------------------RUN---------------------
print("BOT STARTED")
with bot:
    bot.loop.run_until_complete(setup_commands())
    bot.run_until_disconnected()
