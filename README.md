# 📊 CVR Result Scraper Bot 🤖

A smart Telegram bot that automates the retrieval of student results from the **CVR College portal**, using **Python**, **SeleniumBase**, and **BeautifulSoup**.  
Bypasses Cloudflare protection to deliver results based on **branch**, **year**, **semester**, and **exam type** — all through a simple Telegram chat.

---

## 🚀 Features

- ✅ Telegram Bot interface for real-time result fetching
- 🔐 Cloudflare bypass using SeleniumBase
- 🎯 Filter by Branch, Year, Semester, and Exam Type
- 📄 Parses and displays individual student marks with accuracy
- 🔧 Built for scalability and future integration with a Flask web app
- 🛠️ Clean and modular codebase

---

## 🛠️ Tech Stack

- **Python 3.x**
- **SeleniumBase**
- **BeautifulSoup4**
- **python-telegram-bot**
- **dotenv**
- *(Optional)* Flask – for future web integration

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/codes/cvr-result-scraper-bot.git](https://github.com/code-srikar/Results_Telegram_Bot
cd Results_Telegram_Bot
```

### 2. Install Dependencies
Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```
Install required packages:

```bash
pip install -r requirements.txt
```

### 3. Add Bot Token
Create a .env file in the root directory:

```env
BOT_TOKEN=your_telegram_bot_token_here
```

### 4. Running the Bot
```bash
python telegram_bot.py
```
Now open Telegram, search for your bot, and start chatting 🎉

---

### ✨ How It Works
User interacts with the bot and selects their branch, year, semester, and exam type.

The bot launches a headless browser using SeleniumBase to navigate the CVR results portal.

It bypasses Cloudflare protection, loads the required page, and scrapes the result using BeautifulSoup.

Extracted results are parsed and formatted into a clean response, then sent back to the user via Telegram.

### 🔒 Disclaimer
This bot is made for educational purposes only.
It does not store, misuse, or share any user data.
Always use responsibly and ethically.

### 🚧 Future Enhancements
🌐 Flask-based Web Interface

📁 Export results as downloadable PDF

💬 WhatsApp Bot Integration

📊 Admin Dashboard for result analytics

### 💡 Inspiration
Manually checking results on the CVR portal is tedious and repetitive. This bot simplifies and speeds up that process — giving students their results in seconds via a Telegram chat.

---

📬 Contact
Created by Srikar
💬 DM me on LinkedIn or open an issue on GitHub.

⭐️ Support
If you found this project useful, consider giving it a ⭐️ on GitHub! It helps me stay motivated to build more.
