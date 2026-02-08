#!/usr/bin/env python3
"""
Telegram Auto-Accept Bot
Automatically accepts join requests and provides inline buttons for adding to groups/channels
"""

import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ChatJoinRequestHandler,
    ContextTypes,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
BOT_USERNAME = os.environ.get("BOT_USERNAME")

# Validate configuration
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required!")
if not BOT_USERNAME:
    raise ValueError("BOT_USERNAME environment variable is required!")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command"""
    user = update.effective_user
    first_name = user.first_name or "User"
    
    # Create the message text
    message_text = (
        f"Hello🎈 {first_name}!\n\n"
        "I Accept Join Requests Automatically\n"
        "Just ✨ Add Me To Your Channel ➕\n"
        "Click /start To Know More ⭐⭐"
    )
    
    # Create inline keyboard buttons
    keyboard = [
        [
            InlineKeyboardButton(
                "Add me to your group",
                url=f"https://t.me/{BOT_USERNAME}?startgroup=s&admin=invite_users"
            )
        ],
        [
            InlineKeyboardButton(
                "Add me to your channel",
                url=f"https://t.me/{BOT_USERNAME}?startchannel=s&admin=invite_users"
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the message
    await update.message.reply_text(
        message_text,
        reply_markup=reply_markup
    )


async def handle_chat_join_request(
    update: Update, 
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Automatically approve join requests"""
    try:
        chat_join_request = update.chat_join_request
        chat = chat_join_request.chat
        user = chat_join_request.from_user
        
        # Approve the join request
        await chat_join_request.approve()
        
        logger.info(
            f"Approved join request from {user.first_name} ({user.id}) "
            f"to {chat.title} ({chat.id})"
        )
        
        # Send welcome message to the user (private message)
        try:
            first_name = user.first_name or "User"
            
            welcome_message = (
                f"Hello🎈 !\n\n"
                "I Accept Join Requests Automatically\n"
                "Just ✨ Add Me To Your Channel ➕\n"
                "Click /start To Know More ⭐⭐\n\n"
                "🔴Click Here To Start🔴"
            )
            
            # Create button to start the bot
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🔴Click Here To Start🔴",
                        url=f"https://t.me/{BOT_USERNAME}?start=start"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Add me to your group",
                        url=f"https://t.me/{BOT_USERNAME}?startgroup=s&admin=invite_users"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Add me to your channel",
                        url=f"https://t.me/{BOT_USERNAME}?startchannel=s&admin=invite_users"
                    )
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=user.id,
                text=welcome_message,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.warning(f"Could not send private message to user {user.id}: {e}")
            
    except Exception as e:
        logger.error(f"Error approving join request: {e}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command"""
    help_text = (
        "🤖 *Auto-Accept Bot Help*\n\n"
        "This bot automatically accepts join requests for your private groups and channels.\n\n"
        "*How to use:*\n"
        "1. Add me to your private group or channel as admin\n"
        "2. Give me 'Invite Users' permission\n"
        "3. I will automatically accept all join requests!\n\n"
        "*Commands:*\n"
        "/start - Start the bot and get add links\n"
        "/help - Show this help message\n\n"
        "That's it! Simple and automatic! ✨"
    )
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


def main() -> None:
    """Start the bot"""
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(ChatJoinRequestHandler(handle_chat_join_request))
    
    # Start the bot
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
