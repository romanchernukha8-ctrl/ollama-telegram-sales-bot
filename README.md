# 🤖 Ollama Telegram Sales Bot

## Overview

This project is an AI-powered Telegram sales assistant for smartphone stores.

The bot uses a local Ollama LLM to communicate with users, recommend smartphones, collect customer contacts and display product images.

It includes:

* Telegram bot interface
* Ollama LLM integration
* Smartphone image search via SerpAPI
* SQLite database for order storage
* Interactive button-based navigation

The main goal of the project is to showcase:

* AI chatbot integration with Ollama
* Telegram bot development in Python
* External API integration
* User interaction automation
* Local LLM usage in real applications

---

## Tech Stack

* Python
* Ollama
* Telegram Bot API
* SQLite
* SerpAPI
* Requests

---

## Project Structure

```text
.
├── bot.py
├── requirements.txt
├── .gitignore
├── README.md
├── .env
│
├── database/
│   └── orders.db
│
└── models/
    └── Modelfile

Features
AI-powered smartphone recommendations
Telegram interactive menus
Product image loading
Contact validation
SQLite order storage
Conversation history support
Local LLM via Ollama
Automatic order flow

How It Works
User interacts with Telegram bot
Ollama processes user requests and generates responses
Bot detects smartphone model names
SerpAPI searches product images
Customer contacts are validated and stored in SQLite database

How to Run
1. Install dependencies
pip install -r requirements.txt

2. Create .env
BOT_TOKEN=your_telegram_bot_token
SERPAPI_KEY=your_serpapi_key

3. Create Ollama model
ollama create mobile_sales_bot -f models/Modelfile

4. Run the bot
python bot.py

Example Features
Smartphone search
AI-generated recommendations
Interactive Telegram buttons
Automatic order collection
Product image preview

Future Improvements
Docker support
Admin panel
Multi-language support
PostgreSQL integration
Conversation memory improvements
RAG integration
Voice message support
Deployment on VPS

