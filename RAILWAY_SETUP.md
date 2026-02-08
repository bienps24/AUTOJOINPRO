# Railway Deployment Guide 🚂

Complete guide para sa pag-deploy ng Telegram Auto-Accept Bot sa Railway.

## Pre-requisites

1. **GitHub Account** - Para sa repository
2. **Railway Account** - Mag-sign up sa [railway.app](https://railway.app)
3. **Telegram Bot Token** - Galing sa @BotFather

## Step-by-Step Deployment

### Part 1: I-setup ang GitHub Repository

1. **I-create ang new repository sa GitHub**
   - Pumunta sa [github.com](https://github.com)
   - Click **"New repository"**
   - Name: `telegram-auto-accept-bot` (o kahit ano)
   - Public o Private (pareho okay)
   - **Huwag** mag-add ng README, .gitignore, o license (meron na tayo)

2. **I-upload ang files**
   
   Option A - Using Git (Terminal/Command Line):
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/telegram-auto-accept-bot.git
   git push -u origin main
   ```

   Option B - Using GitHub Web Interface:
   - I-drag and drop lahat ng files sa repository page
   - Files na dapat i-upload:
     - `telegram_auto_accept_bot.py`
     - `requirements.txt`
     - `runtime.txt`
     - `Procfile`
     - `railway.json`
     - `.gitignore`
     - `.env.example`
     - `README.md`

### Part 2: I-setup ang Railway

1. **Pumunta sa Railway**
   - Go to [railway.app](https://railway.app)
   - I-click ang **"Login"** o **"Start a New Project"**
   - Sign in gamit ang GitHub account mo

2. **I-create ang New Project**
   - I-click ang **"New Project"**
   - Piliin **"Deploy from GitHub repo"**
   - I-authorize ang Railway sa GitHub kung first time
   - I-select ang repository: `telegram-auto-accept-bot`

3. **I-configure ang Environment Variables**
   
   Pagkatapos mag-deploy, may error pa kasi walang variables:
   
   a. Sa Railway dashboard, i-click ang project mo
   
   b. I-click ang **"Variables"** tab
   
   c. I-add ang dalawang variables:
   
   **Variable 1:**
   ```
   Name: BOT_TOKEN
   Value: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
   (Ilagay ang actual bot token mo from @BotFather)
   
   **Variable 2:**
   ```
   Name: BOT_USERNAME
   Value: YourBotUsername
   ```
   (Ilagay ang username ng bot mo, WALANG @ symbol)
   
   d. I-click **"Add"** para sa bawat variable

4. **I-redeploy ang Bot**
   - Automatic mag-redeploy pagkatapos mag-add ng variables
   - Kung hindi, i-click ang **"Deploy"** button
   - Wait 1-2 minutes para mag-build at mag-start

5. **I-check kung Running**
   - Pumunta sa **"Logs"** tab
   - Dapat makita mo: `"Bot is starting..."`
   - Kung may error, i-check ang variables kung tama

### Part 3: I-test ang Bot

1. **Pumunta sa Telegram**
   - I-search ang bot username mo
   - I-send ng `/start`
   - Dapat may response with buttons

2. **I-test sa Group/Channel**
   - I-add ang bot sa private group o channel
   - I-promote as admin with "Invite Users" permission
   - I-try mag-request ng join
   - Dapat automatic approval!

## Railway Features

### Free Tier
- **$5 free credits per month**
- Enough para sa small bots (24/7 running)
- 500MB RAM, shared CPU
- Auto-sleep after 5 mins of inactivity (pero telegram bots hindi naman nag-iidle)

### Automatic Features
- ✅ Auto-deploy sa every push sa GitHub
- ✅ Auto-restart kung mag-crash
- ✅ Build logs at runtime logs
- ✅ Environment variable management
- ✅ HTTPS endpoints (kung kailangan mo ng webhooks)

## Troubleshooting

### Bot hindi nag-start sa Railway

**Check 1: Logs**
```
Pumunta sa Railway > Logs tab
Hanapin ang error messages
```

**Check 2: Variables**
```
Variables tab > Siguraduhing may dalawa:
- BOT_TOKEN (mahabang string with numbers at letters)
- BOT_USERNAME (short name, walang @)
```

**Check 3: Deployment**
```
Pumunta sa Deployments tab
I-check kung "Success" o "Failed"
Kung failed, i-click para sa details
```

### Bot nag-crash or nag-restart

**Common causes:**
- Invalid bot token (i-check sa @BotFather)
- Wrong bot username (i-check walang @ symbol)
- Network issues (i-restart ang deployment)

**Solution:**
```
Settings > Redeploy
O kaya
I-push ulit sa GitHub para mag-trigger ng new deploy
```

### Hindi gumagana ang auto-accept

**Hindi issue ng Railway, i-check:**
- Bot ay admin ba sa group/channel?
- May "Invite Users" permission?
- Private ba ang group/channel? (dapat private para may join requests)

## Updating the Bot

Kapag may changes sa code:

1. **I-edit ang files sa local**
2. **I-push sa GitHub:**
   ```bash
   git add .
   git commit -m "Updated bot"
   git push
   ```
3. **Automatic mag-deploy** sa Railway!

## Monitoring

### Check Uptime
- Railway dashboard > Metrics
- Makikita mo ang CPU, RAM usage
- Uptime percentage

### Check Logs
- Railway dashboard > Logs
- Real-time logs ng bot
- Makikita mo ang join requests being processed

## Cost Estimate

**Typical usage para sa auto-accept bot:**
- RAM: ~50-100MB
- CPU: Very light (only when processing requests)
- **Estimated monthly cost: $0-1** (within free tier usually)

## Security Best Practices

1. **Never commit .env file**
   - Already in .gitignore
   - Variables stay sa Railway only

2. **Use Railway variables**
   - Hindi hardcoded sa code
   - Secure at encrypted

3. **Private repository** (optional but recommended)
   - I-set ang GitHub repo as private
   - Lalo na kung may sensitive data

## Support

Kung may issues:
1. I-check ang Railway logs first
2. I-verify ang environment variables
3. I-test locally muna using .env file
4. Check Railway documentation: [docs.railway.app](https://docs.railway.app)

---

**That's it!** Ang bot mo ay running 24/7 na sa Railway! 🎉
