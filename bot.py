from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

import sqlite3
import json
import random
from flask import Flask
from threading import Thread

BOT_TOKEN = "8940510632:AAEjHPDWfZFx8KzeQ7nFh0oRpg-WYaYGuo0"

app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is running!"

def run():
    app_web.run(host='0.0.0.0', port=10000)

t = Thread(target=run)
t.start()

games = {}

conn = sqlite3.connect("showdown.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    wins INTEGER,
    losses INTEGER
)
""")

conn.commit()

conn.commit()

with open("players.json", "r") as file:
    players = json.load(file)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    name = update.effective_user.first_name

    username = update.effective_user.username

    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    if user is None:

        cursor.execute(
            "INSERT INTO users VALUES (?, ?, ?)",
            (username, 0, 0)
        )

        conn.commit()

    await update.message.reply_text(
        f"🏏 Welcome {name} To NTR Cric Draft Bot!"
    )


async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):

    name = update.effective_user.first_name

    username = update.effective_user.username

    cursor.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )

    user_data = cursor.fetchone()

    wins = user_data[1]
    losses = user_data[2]

    draws = 0

    matches = wins + losses + draws

    if matches > 0:
        winrate = round((wins / matches) * 100, 1)
    else:
        winrate = 0

    await update.message.reply_text(
        f"╔════════════════╗\n"
        f"👤 {name.upper()}\n"
        f"╠════════════════╣\n\n"
        f"🏆 Rank      : Unranked\n"
        f"⚔ Matches   : {matches}\n"
        f"🟢 Wins      : {wins}\n"
        f"🔴 Losses    : {losses}\n"
        f"⚪ Draws     : {draws}\n"
        f"📊 Win Rate : {winrate}%\n\n"
        f"╚════════════════╝"
    )


async def rankings(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [
            InlineKeyboardButton("🌍 Global", callback_data="global_rank")
        ],
        [
            InlineKeyboardButton("📅 Daily", callback_data="daily_rank")
        ],
        [
            InlineKeyboardButton("📆 Weekly", callback_data="weekly_rank")
        ],
        [
            InlineKeyboardButton("🏆 Overall", callback_data="overall_rank")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🏆 Rankings Menu",
        reply_markup=reply_markup
    )


async def challengeipl(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.first_name

    chat_id = update.effective_chat.id

    games[chat_id] = {

        "player1": user,
        "player2": None,

        "turn": None,

        "teams": {

            user: {

                "Captain": None,
                "WK": None,
                "Top": None,
                "Middle": None,
                "All Rounder": None,
                "Finisher": None,
                "Pacer": None,
                "Spinner": None,
                "Fielder": None
            }
        },

        "ready": []
    }

    keyboard = [
        [
            InlineKeyboardButton(
                "⚔ Join Game",
                callback_data="join_game"
            )
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    caption = (
        f"🏏 IPL Challenge!\n\n"
        f"User: {user}\n"
        f"Mode: IPL\n\n"
        f"Waiting for opponent..."
    )

    with open("ipl.jpg", "rb") as photo:

        await update.message.reply_photo(
            photo=photo,
            caption=caption,
            reply_markup=reply_markup
        )

def build_draft_text(chat_id):

    game = games[chat_id]

    p1 = game["player1"]

    p2 = game["player2"]

    turn = game["turn"]

    text = f"🏏 DRAFTING PHASE\n\n"

    text += f"🔵 {p1}\n\n"

    for role, player in game["teams"][p1].items():

        if player is None:
            player = "..."

        text += f"• {role} : {player}\n"

    text += "\n━━━━━━━━━━━━━━\n\n"

    text += f"🔴 {p2}\n\n"

    for role, player in game["teams"][p2].items():

        if player is None:
            player = "..."

        text += f"• {role} : {player}\n"

    text += f"\n━━━━━━━━━━━━━━\n\n"

    text += f"🎯 TURN : {turn}"

    return text

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query

    await query.answer()

    if query.data == "global_rank":

        cursor.execute(
            "SELECT username, wins FROM users ORDER BY wins DESC LIMIT 10"
        )

        top_users = cursor.fetchall()

        text = "🏆 GLOBAL RANKINGS\n\n"

        rank = 1

        for user in top_users:

            username = user[0]
            wins = user[1]

            text += f"{rank}. {username} — {wins} Wins\n"

            rank += 1

        await query.message.reply_text(text)

    elif query.data == "daily_rank":

        await query.message.reply_text(
            "📅 Daily Rankings Coming Soon!"
        )

    elif query.data == "weekly_rank":

        await query.message.reply_text(
            "📆 Weekly Rankings Coming Soon!"
        )

    elif query.data == "overall_rank":

        await query.message.reply_text(
            "🏆 Overall Rankings Coming Soon!"
        )

    elif query.data == "join_game":

        join_user = query.from_user.first_name

        text = query.message.caption

        creator_name = text.split("User: ")[1].split("\n")[0]

        if join_user == creator_name:

            await query.answer(
                "❌ You cannot join your own challenge!",
                show_alert=True
            )

        else:

            chat_id = query.message.chat.id

            games[chat_id]["player2"] = join_user

            games[chat_id]["teams"][join_user] = {

                "Captain": None,
                "WK": None,
                "Top": None,
                "Middle": None,
                "All Rounder": None,
                "Finisher": None,
                "Pacer": None,
                "Spinner": None,
                "Fielder": None
            }

            games[chat_id]["turn"] = random.choice([

                games[chat_id]["player1"],
                games[chat_id]["player2"]

            ])

            draft_text = build_draft_text(chat_id)

            keyboard = [
                [
                    InlineKeyboardButton(
                        "🎲 Draw Player",
                        callback_data="draw_player"
                    )
                ]
            ]

            reply_markup = InlineKeyboardMarkup(keyboard)   

            await query.message.edit_caption(
                caption=draft_text,
                reply_markup=reply_markup
            )
            
    elif query.data == "draw_player":
        
        
        chat_id = query.message.chat.id

        turn = games[chat_id]["turn"]

        click_user = query.from_user.first_name

        if click_user != turn:

            await query.answer(
                "❌ Not Your Turn",
                show_alert=True
            )

            return

        player_name = random.choice(
            list(players.keys())
        )

        games[chat_id]["current_player"] = player_name

        draft_text = build_draft_text(chat_id)

        text = (
            f"{draft_text}\n\n"
            f"━━━━━━━━━━━━━━\n\n"
            f"🎴 PLAYER PULLED\n\n"
            f"🏏 {player_name}"
        )

        keyboard = [

            [
                InlineKeyboardButton(
                    "👑 Captain",
                    callback_data="role_Captain"
                ),

                InlineKeyboardButton(
                    "🧤 WK",
                    callback_data="role_WK"
                )
            ],

            [
                InlineKeyboardButton(
                    "🔥 Top",
                    callback_data="role_Top"
                ),

                InlineKeyboardButton(
                    "⚡ Middle",
                    callback_data="role_Middle"
                )
            ],

            [
                InlineKeyboardButton(
                    "🎯 All Rounder",
                    callback_data="role_All Rounder"
                )
            ],

            [
                InlineKeyboardButton(
                    "💥 Finisher",
                    callback_data="role_Finisher"
                )
            ],

            [
                InlineKeyboardButton(
                    "🚀 Pacer",
                    callback_data="role_Pacer"
                ),

                InlineKeyboardButton(
                    "🌀 Spinner",
                    callback_data="role_Spinner"
                )
            ],

            [
                InlineKeyboardButton(
                    "🛡 Fielder",
                    callback_data="role_Fielder"
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.message.edit_caption(
            caption=text,
            reply_markup=reply_markup
        )


async def player(update: Update, context: ContextTypes.DEFAULT_TYPE):

    player_name = random.choice(list(players.keys()))

    roles = players[player_name]

    text = f"🏏 {player_name}\n\n"

    for role, rating in roles.items():

        text += f"🔥 {role} : {rating}\n"

    await update.message.reply_text(text)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("rankings", rankings))
app.add_handler(CommandHandler("challengeipl", challengeipl))
app.add_handler(CommandHandler("player", player))

app.add_handler(CallbackQueryHandler(button_click))

app.run_polling()