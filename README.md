# Telegram Auto-Accept Bot

Simple bot na automatic nag-aaccept ng join requests sa private groups at channels.

## Features

- ✨ Automatic na nag-aaccept ng lahat ng join requests
- 🎈 Personalized welcome message with user's name
- 🔘 Inline buttons para sa group at channel
- 📱 Simple at madaling gamitin
- ☁️ Ready for Railway deployment

## Requirements

- Python 3.11 o mas bago
- Telegram Bot Token (from @BotFather)

## Railway Deployment (Recommended) 🚂

### 1. Kumuha ng Bot Token

1. Pumunta sa Telegram at i-search ang **@BotFather**
2. I-type ang `/newbot` at sundin ang instructions
3. Copy ang bot token na ibibigay sa'yo
4. I-save ang username ng bot mo

### 2. Deploy sa Railway

1. I-push ang repository na ito sa GitHub
2. Pumunta sa [railway.app](https://railway.app)
3. I-click ang **"New Project"**
4. Piliin **"Deploy from GitHub repo"**
5. Select ang repository mo
6. I-add ang environment variables:
   - `BOT_TOKEN` - Ang bot token mo from BotFather
   - `BOT_USERNAME` - Ang username ng bot mo (walang @)
7. I-click ang **"Deploy"**

Tapos na! Ang bot ay tatakbo 24/7 sa Railway! 🎉

### Railway Environment Variables

Sa Railway dashboard:
1. Pumunta sa **Variables** tab
2. I-add ang sumusunod:

```
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_USERNAME=YourBotUsername
```

## Local Development

### 1. I-install ang Python dependencies

```bash
pip install -r requirements.txt
```

### 2. I-setup ang Environment Variables

I-create ang `.env` file (i-copy mula sa `.env.example`):

```bash
cp .env.example .env
```

I-edit ang `.env` at ilagay ang iyong credentials:

```
BOT_TOKEN=your_bot_token_here
BOT_USERNAME=your_bot_username_here
```

### 3. Patakbuhin ang Bot Locally

```bash
python telegram_auto_accept_bot.py
```

## Paano Gamitin

### Para sa Users:

1. I-type ang `/start` sa bot
2. May lalabas na 2 buttons:
   - **Add me to your group** - Para i-add sa group
   - **Add me to your channel** - Para i-add sa channel

### Para I-setup sa Group/Channel:

1. I-add ang bot sa iyong **private** group o channel
2. I-promote as **admin** 
3. Bigyan ng **"Invite Users"** permission lang (ito lang ang kailangan)
4. Tapos na! Automatic na mag-aaccept ng join requests ang bot

### Kapag May Sumali:

Kapag may user na nag-request ng join:
1. Automatic silang mae-accept ng bot
2. Makakareceive sila ng private message na may:
   - Welcome text with their name
   - Red button: "🔴Click Here To Start🔴"
   - Add to group button
   - Add to channel button

## Bot Commands

- `/start` - Magsimula at makakuha ng add links
- `/help` - Makita ang help message

## Troubleshooting

### Hindi gumagana ang auto-accept:
- Siguraduhing **admin** ang bot sa group/channel
- I-check kung may **"Invite Users"** permission ang bot
- Siguraduhing **private** ang group/channel (hindi public)

### Hindi makareceive ng private message ang user:
- Normal lang ito kung hindi pa nag-start ng conversation ang user sa bot
- Pwede nilang i-click ang start button kapag nag-request sila ng join

### Bot offline:
- Siguraduhing tumatakbo pa ang script
- I-check ang internet connection
- I-verify na tama ang bot token

## Notes

- Ang bot ay tumatakbo lang habang tumatakbo ang script. Para 24/7, kailangan mo ng hosting service (Heroku, Railway, VPS, etc.)
- Kailangan ng **private** group/channel para gumana ang join request feature
- I-save ang bot token mo ng maayos at huwag i-share sa iba

## Security

- Huwag i-commit ang bot token sa public repositories
- I-store ang token sa environment variables kung production
- Regular na i-update ang dependencies

## License

Free to use and modify!
