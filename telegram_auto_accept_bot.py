#!/usr/bin/env python3
"""
Telegram Auto-Accept Bot with Admin Panel
Automatically accepts join requests with customizable ads and statistics
"""

import logging
import os
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ChatJoinRequestHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
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
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))  # Your Telegram user ID

# Validate configuration
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable is required!")
if not BOT_USERNAME:
    raise ValueError("BOT_USERNAME environment variable is required!")
if not ADMIN_ID:
    raise ValueError("ADMIN_ID environment variable is required!")

# Conversation states
WAITING_FOR_PHOTO, WAITING_FOR_TEXT, WAITING_FOR_BUTTON, WAITING_FOR_MORE_BUTTONS = range(4)

# Database setup
def init_db():
    """Initialize the database"""
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    
    # Table for ad configuration
    c.execute('''
        CREATE TABLE IF NOT EXISTS ad_config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            photo_file_id TEXT,
            message_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table for ad buttons (support multiple buttons)
    c.execute('''
        CREATE TABLE IF NOT EXISTS ad_buttons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            button_text TEXT NOT NULL,
            button_url TEXT NOT NULL,
            button_order INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table for join statistics
    c.execute('''
        CREATE TABLE IF NOT EXISTS join_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            chat_id INTEGER,
            chat_title TEXT,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table for click tracking
    c.execute('''
        CREATE TABLE IF NOT EXISTS ad_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Database helper functions
def get_ad_config():
    """Get current ad configuration"""
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('SELECT photo_file_id, message_text FROM ad_config WHERE id = 1')
    result = c.fetchone()
    conn.close()
    return result

def get_ad_buttons():
    """Get all ad buttons"""
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('SELECT button_text, button_url FROM ad_buttons ORDER BY button_order, id')
    results = c.fetchall()
    conn.close()
    return results

def set_ad_config(photo_file_id=None, message_text=None):
    """Set ad configuration"""
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    
    # Check if config exists
    c.execute('SELECT id FROM ad_config WHERE id = 1')
    exists = c.fetchone()
    
    if exists:
        # Update existing
        updates = []
        params = []
        if photo_file_id is not None:
            updates.append('photo_file_id = ?')
            params.append(photo_file_id)
        if message_text is not None:
            updates.append('message_text = ?')
            params.append(message_text)
        
        if updates:
            updates.append('updated_at = CURRENT_TIMESTAMP')
            query = f"UPDATE ad_config SET {', '.join(updates)} WHERE id = 1"
            c.execute(query, params)
    else:
        # Insert new
        c.execute('''
            INSERT INTO ad_config (id, photo_file_id, message_text)
            VALUES (1, ?, ?)
        ''', (photo_file_id, message_text))
    
    conn.commit()
    conn.close()

def add_ad_button(button_text, button_url, button_order=0):
    """Add an ad button"""
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO ad_buttons (button_text, button_url, button_order)
        VALUES (?, ?, ?)
    ''', (button_text, button_url, button_order))
    conn.commit()
    conn.close()

def clear_ad_buttons():
    """Clear all ad buttons"""
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('DELETE FROM ad_buttons')
    conn.commit()
    conn.close()

def clear_ad_config():
    """Clear ad configuration and buttons"""
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('DELETE FROM ad_config WHERE id = 1')
    c.execute('DELETE FROM ad_buttons')
    conn.commit()
    conn.close()

def log_join(user_id, username, first_name, chat_id, chat_title):
    """Log a user join"""
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO join_stats (user_id, username, first_name, chat_id, chat_title)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, chat_id, chat_title))
    conn.commit()
    conn.close()

def log_click(user_id, username):
    """Log an ad click"""
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO ad_clicks (user_id, username)
        VALUES (?, ?)
    ''', (user_id, username))
    conn.commit()
    conn.close()

def get_stats(days=7):
    """Get statistics for the last N days"""
    conn = sqlite3.connect('bot_data.db')
    c = conn.cursor()
    
    # Calculate date threshold
    date_threshold = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    
    # Total joins
    c.execute('SELECT COUNT(*) FROM join_stats')
    total_joins = c.fetchone()[0]
    
    # Recent joins
    c.execute('SELECT COUNT(*) FROM join_stats WHERE joined_at >= ?', (date_threshold,))
    recent_joins = c.fetchone()[0]
    
    # Total clicks
    c.execute('SELECT COUNT(*) FROM ad_clicks')
    total_clicks = c.fetchone()[0]
    
    # Recent clicks
    c.execute('SELECT COUNT(*) FROM ad_clicks WHERE clicked_at >= ?', (date_threshold,))
    recent_clicks = c.fetchone()[0]
    
    # Unique groups
    c.execute('SELECT COUNT(DISTINCT chat_id) FROM join_stats')
    unique_groups = c.fetchone()[0]
    
    conn.close()
    
    return {
        'total_joins': total_joins,
        'recent_joins': recent_joins,
        'total_clicks': total_clicks,
        'recent_clicks': recent_clicks,
        'unique_groups': unique_groups,
        'days': days
    }

# Check if user is admin
def is_admin(user_id: int) -> bool:
    """Check if user is the bot admin"""
    return user_id == ADMIN_ID

# Command handlers
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
    
    # Add admin button if user is admin
    if is_admin(user.id):
        keyboard.append([
            InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")
        ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the message
    await update.message.reply_text(
        message_text,
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command"""
    user = update.effective_user
    
    # Different help text for admin vs regular users
    if is_admin(user.id):
        # Admin sees full help with admin commands
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
            "*Admin Commands:*\n"
            "/setad - Set up advertisement\n"
            "/viewad - View current ad\n"
            "/clearad - Remove advertisement\n"
            "/stats - View statistics\n\n"
            "That's it! Simple and automatic! ✨"
        )
    else:
        # Regular users see basic help only
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

# Admin command handlers
async def setad_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the ad setup process"""
    if not is_admin(update.effective_user.id):
        # Don't reveal this is an admin command - just ignore or send generic message
        await update.message.reply_text("❓ Unknown command. Use /help to see available commands.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "📸 *Setup Advertisement*\n\n"
        "Step 1/3: Send me a photo for the ad\n"
        "Or send /skip to use text only",
        parse_mode='Markdown'
    )
    return WAITING_FOR_PHOTO

async def receive_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive photo for ad"""
    if update.message.photo:
        # Get the largest photo
        photo = update.message.photo[-1]
        context.user_data['ad_photo'] = photo.file_id
        
        await update.message.reply_text(
            "✅ Photo received!\n\n"
            "Step 2/3: Send me the message text for the ad"
        )
        return WAITING_FOR_TEXT
    else:
        await update.message.reply_text("Please send a photo or /skip")
        return WAITING_FOR_PHOTO

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skip photo step"""
    context.user_data['ad_photo'] = None
    await update.message.reply_text(
        "⏭️ Photo skipped\n\n"
        "Step 2/3: Send me the message text for the ad"
    )
    return WAITING_FOR_TEXT

async def receive_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive message text for ad"""
    context.user_data['ad_text'] = update.message.text
    
    await update.message.reply_text(
        "✅ Message text received!\n\n"
        "Step 3/3: Send me the button details in this format:\n"
        "`Button Text | https://example.com`\n\n"
        "Example:\n"
        "`🎁 Visit Our Sponsor | https://t.me/yourchannel`\n\n"
        "Or send /skip to have no button",
        parse_mode='Markdown'
    )
    return WAITING_FOR_BUTTON

async def receive_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive button details for ad"""
    text = update.message.text
    
    if '|' not in text:
        await update.message.reply_text(
            "❌ Invalid format. Please use:\n"
            "`Button Text | https://example.com`",
            parse_mode='Markdown'
        )
        return WAITING_FOR_BUTTON
    
    parts = text.split('|', 1)
    button_text = parts[0].strip()
    button_url = parts[1].strip()
    
    # Validate URL
    if not button_url.startswith(('http://', 'https://', 't.me/')):
        await update.message.reply_text(
            "❌ Invalid URL. Must start with http://, https://, or t.me/"
        )
        return WAITING_FOR_BUTTON
    
    # Initialize button list if not exists
    if 'ad_buttons' not in context.user_data:
        context.user_data['ad_buttons'] = []
    
    # Add button to list
    context.user_data['ad_buttons'].append({
        'text': button_text,
        'url': button_url
    })
    
    # Ask if they want to add more buttons
    button_count = len(context.user_data['ad_buttons'])
    await update.message.reply_text(
        f"✅ Button #{button_count} added!\n\n"
        "Want to add another button?\n"
        "• Send another button: `Button Text | URL`\n"
        "• Or send /done to finish",
        parse_mode='Markdown'
    )
    
    return WAITING_FOR_MORE_BUTTONS

async def receive_more_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive additional buttons"""
    text = update.message.text
    
    if '|' not in text:
        await update.message.reply_text(
            "❌ Invalid format. Please use:\n"
            "`Button Text | https://example.com`\n"
            "Or send /done to finish",
            parse_mode='Markdown'
        )
        return WAITING_FOR_MORE_BUTTONS
    
    parts = text.split('|', 1)
    button_text = parts[0].strip()
    button_url = parts[1].strip()
    
    # Validate URL
    if not button_url.startswith(('http://', 'https://', 't.me/')):
        await update.message.reply_text(
            "❌ Invalid URL. Must start with http://, https://, or t.me/"
        )
        return WAITING_FOR_MORE_BUTTONS
    
    # Add button to list
    context.user_data['ad_buttons'].append({
        'text': button_text,
        'url': button_url
    })
    
    button_count = len(context.user_data['ad_buttons'])
    await update.message.reply_text(
        f"✅ Button #{button_count} added!\n\n"
        "Want to add another button?\n"
        "• Send another button: `Button Text | URL`\n"
        "• Or send /done to finish",
        parse_mode='Markdown'
    )
    
    return WAITING_FOR_MORE_BUTTONS

async def finish_ad_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Finish ad setup and save to database"""
    # Save ad config to database
    photo_id = context.user_data.get('ad_photo')
    ad_text = context.user_data.get('ad_text')
    ad_buttons = context.user_data.get('ad_buttons', [])
    
    # Clear existing buttons first
    clear_ad_buttons()
    
    # Save ad config
    set_ad_config(
        photo_file_id=photo_id,
        message_text=ad_text
    )
    
    # Save buttons
    for idx, button in enumerate(ad_buttons):
        add_ad_button(
            button_text=button['text'],
            button_url=button['url'],
            button_order=idx
        )
    
    button_count = len(ad_buttons)
    await update.message.reply_text(
        f"✅ *Advertisement Setup Complete!*\n\n"
        f"📸 Photo: {'Yes' if photo_id else 'No'}\n"
        f"📝 Message: Yes\n"
        f"🔘 Buttons: {button_count}\n\n"
        "Your ad will now be shown to all users who join groups/channels.\n\n"
        "Use /viewad to preview or /clearad to remove it.",
        parse_mode='Markdown'
    )
    
    # Clear user data
    context.user_data.clear()
    return ConversationHandler.END

async def skip_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Skip button step"""
    # Initialize empty button list
    context.user_data['ad_buttons'] = []
    
    # Finish setup
    return await finish_ad_setup(update, context)

async def cancel_setup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel ad setup"""
    context.user_data.clear()
    await update.message.reply_text("❌ Ad setup cancelled.")
    return ConversationHandler.END

async def viewad_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """View current ad configuration"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❓ Unknown command. Use /help to see available commands.")
        return
    
    ad_config = get_ad_config()
    
    if not ad_config or not ad_config[1]:  # Check if message_text exists
        await update.message.reply_text(
            "📭 No advertisement configured.\n\n"
            "Use /setad to create one."
        )
        return
    
    photo_id, message_text = ad_config
    ad_buttons = get_ad_buttons()
    
    # Prepare preview message
    preview_text = "📺 *Current Advertisement Preview:*\n\n"
    
    # Create keyboard if buttons exist
    reply_markup = None
    if ad_buttons:
        keyboard = []
        for button_text, button_url in ad_buttons:
            keyboard.append([InlineKeyboardButton(button_text, url=button_url)])
        reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send preview
    if photo_id:
        await update.message.reply_photo(
            photo=photo_id,
            caption=message_text,
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            message_text,
            reply_markup=reply_markup
        )

async def clearad_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear ad configuration"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❓ Unknown command. Use /help to see available commands.")
        return
    
    clear_ad_config()
    await update.message.reply_text(
        "✅ Advertisement cleared!\n\n"
        "Users will receive the default welcome message."
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show bot statistics"""
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❓ Unknown command. Use /help to see available commands.")
        return
    
    # Get stats for different periods
    stats_7d = get_stats(7)
    stats_30d = get_stats(30)
    stats_all = get_stats(36500)  # ~100 years for "all time"
    
    # Calculate click rate
    click_rate_7d = (stats_7d['recent_clicks'] / stats_7d['recent_joins'] * 100) if stats_7d['recent_joins'] > 0 else 0
    click_rate_all = (stats_all['total_clicks'] / stats_all['total_joins'] * 100) if stats_all['total_joins'] > 0 else 0
    
    stats_text = (
        "📊 *Bot Statistics*\n\n"
        "*Last 7 Days:*\n"
        f"👥 New Joins: {stats_7d['recent_joins']}\n"
        f"🖱️ Ad Clicks: {stats_7d['recent_clicks']}\n"
        f"📈 Click Rate: {click_rate_7d:.1f}%\n\n"
        "*Last 30 Days:*\n"
        f"👥 New Joins: {stats_30d['recent_joins']}\n"
        f"🖱️ Ad Clicks: {stats_30d['recent_clicks']}\n\n"
        "*All Time:*\n"
        f"👥 Total Joins: {stats_all['total_joins']}\n"
        f"🖱️ Total Clicks: {stats_all['total_clicks']}\n"
        f"📈 Click Rate: {click_rate_all:.1f}%\n"
        f"🏢 Active Groups: {stats_all['unique_groups']}"
    )
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')

# Callback query handler for inline buttons
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "admin_panel":
        if not is_admin(query.from_user.id):
            await query.edit_message_text("⛔ Unauthorized access.")
            return
        
        # Show admin panel
        keyboard = [
            [InlineKeyboardButton("📝 Setup Ad", callback_data="setup_ad")],
            [InlineKeyboardButton("👁️ View Ad", callback_data="view_ad")],
            [InlineKeyboardButton("🗑️ Clear Ad", callback_data="clear_ad")],
            [InlineKeyboardButton("📊 Statistics", callback_data="show_stats")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "⚙️ *Admin Panel*\n\n"
            "Choose an option:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == "setup_ad":
        await query.edit_message_text(
            "To setup an ad, use the command:\n"
            "/setad"
        )
    
    elif query.data == "view_ad":
        ad_config = get_ad_config()
        
        if not ad_config or not ad_config[1]:
            await query.edit_message_text(
                "📭 No advertisement configured.\n\n"
                "Use /setad to create one."
            )
            return
        
        photo_id, message_text = ad_config
        ad_buttons = get_ad_buttons()
        
        # Create keyboard if buttons exist
        reply_markup = None
        if ad_buttons:
            keyboard = []
            for button_text, button_url in ad_buttons:
                keyboard.append([InlineKeyboardButton(button_text, url=button_url)])
            reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send preview
        if photo_id:
            await context.bot.send_photo(
                chat_id=query.message.chat_id,
                photo=photo_id,
                caption=message_text,
                reply_markup=reply_markup
            )
            await query.edit_message_text("📺 Advertisement preview sent above.")
        else:
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=message_text,
                reply_markup=reply_markup
            )
            await query.edit_message_text("📺 Advertisement preview sent above.")
    
    elif query.data == "clear_ad":
        clear_ad_config()
        await query.edit_message_text("✅ Advertisement cleared!")
    
    elif query.data == "show_stats":
        stats_7d = get_stats(7)
        stats_all = get_stats(36500)
        
        click_rate_7d = (stats_7d['recent_clicks'] / stats_7d['recent_joins'] * 100) if stats_7d['recent_joins'] > 0 else 0
        click_rate_all = (stats_all['total_clicks'] / stats_all['total_joins'] * 100) if stats_all['total_joins'] > 0 else 0
        
        stats_text = (
            "📊 *Bot Statistics*\n\n"
            "*Last 7 Days:*\n"
            f"👥 Joins: {stats_7d['recent_joins']}\n"
            f"🖱️ Clicks: {stats_7d['recent_clicks']}\n"
            f"📈 Rate: {click_rate_7d:.1f}%\n\n"
            "*All Time:*\n"
            f"👥 Joins: {stats_all['total_joins']}\n"
            f"🖱️ Clicks: {stats_all['total_clicks']}\n"
            f"📈 Rate: {click_rate_all:.1f}%\n"
            f"🏢 Groups: {stats_all['unique_groups']}"
        )
        
        await query.edit_message_text(stats_text, parse_mode='Markdown')
    
    elif query.data == "back_to_start":
        first_name = query.from_user.first_name or "User"
        message_text = (
            f"Hello🎈 {first_name}!\n\n"
            "I Accept Join Requests Automatically\n"
            "Just ✨ Add Me To Your Channel ➕\n"
            "Click /start To Know More ⭐⭐"
        )
        
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
        
        if is_admin(query.from_user.id):
            keyboard.append([
                InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")
            ])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message_text, reply_markup=reply_markup)
    
    elif query.data.startswith("track_click_"):
        # Track ad click
        user_id = query.from_user.id
        username = query.from_user.username or ""
        log_click(user_id, username)
        
        # Just answer the callback, URL will open automatically
        await query.answer("Opening link...")

# Join request handler
async def handle_chat_join_request(
    update: Update, 
    context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Automatically approve join requests and send custom welcome"""
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
        
        # Log the join
        log_join(
            user_id=user.id,
            username=user.username or "",
            first_name=user.first_name or "",
            chat_id=chat.id,
            chat_title=chat.title or ""
        )
        
        # Get ad configuration
        ad_config = get_ad_config()
        
        # Send messages to the user (private message)
        try:
            first_name = user.first_name or "User"
            
            # FIRST MESSAGE: Send ad if configured (SEPARATE MESSAGE)
            if ad_config and ad_config[1]:
                photo_id, message_text = ad_config
                ad_buttons = get_ad_buttons()
                
                # Create keyboard for ad buttons only
                reply_markup = None
                if ad_buttons:
                    keyboard = []
                    for button_text, button_url in ad_buttons:
                        keyboard.append([InlineKeyboardButton(button_text, url=button_url)])
                    reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Send ad message (with photo or text)
                if photo_id:
                    await context.bot.send_photo(
                        chat_id=user.id,
                        photo=photo_id,
                        caption=message_text,
                        reply_markup=reply_markup
                    )
                else:
                    await context.bot.send_message(
                        chat_id=user.id,
                        text=message_text,
                        reply_markup=reply_markup
                    )
            
            # SECOND MESSAGE: Always send default welcome message (SEPARATE MESSAGE)
            welcome_message = (
                f"Hello🎈 {first_name}!\n\n"
                "I Accept Join Requests Automatically\n"
                "Just ✨ Add Me To Your Channel ➕\n"
                "Click /start To Know More ⭐⭐"
            )
            
            keyboard = [
                [
                    InlineKeyboardButton(
                        "🔴 Click Here To Start 🔴",
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


def main() -> None:
    """Start the bot"""
    # Initialize database
    init_db()
    
    # Create the Application
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler for ad setup
    ad_setup_conv = ConversationHandler(
        entry_points=[CommandHandler('setad', setad_command)],
        states={
            WAITING_FOR_PHOTO: [
                MessageHandler(filters.PHOTO, receive_photo),
                CommandHandler('skip', skip_photo),
            ],
            WAITING_FOR_TEXT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_text),
            ],
            WAITING_FOR_BUTTON: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_button),
                CommandHandler('skip', skip_button),
            ],
            WAITING_FOR_MORE_BUTTONS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_more_buttons),
                CommandHandler('done', finish_ad_setup),
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel_setup)],
    )
    
    # Register handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("viewad", viewad_command))
    application.add_handler(CommandHandler("clearad", clearad_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(ad_setup_conv)
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(ChatJoinRequestHandler(handle_chat_join_request))
    
    # Start the bot
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
