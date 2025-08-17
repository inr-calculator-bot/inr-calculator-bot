import logging
import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simple in-memory state
state = {
    "exchange_rate": 83.0,
    "fee_rate": 0.0,
    "transactions": []
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🇮🇳 INR Calculator Bot activated.\nUse commands like:\n- Set USD exchange rate to 83\n- +1000\n- +1000u\n- Send 1000\n- Bills")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💡 Commands:\n+1000 → Deposit ₹1000\n+1000u → Deposit 1000 USDT\nSend 500 → Withdraw ₹500\nBills → View transactions")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text.strip()
    user = update.message.from_user.first_name

    if msg.lower().startswith("set usd exchange rate to"):
        try:
            rate = float(msg.split("to")[1].strip())
            state["exchange_rate"] = rate
            await update.message.reply_text(f"✅ USD exchange rate set to ₹{rate}")
        except:
            await update.message.reply_text("❌ Invalid format.")

    elif msg.lower().startswith("set fee rate to"):
        try:
            fee = float(msg.split("to")[1].strip())
            state["fee_rate"] = fee
            await update.message.reply_text(f"✅ Fee rate set to {fee}%")
        except:
            await update.message.reply_text("❌ Invalid fee rate.")

    elif msg.startswith("+"):
        amount = msg[1:]
        is_usdt = amount.endswith("u")
        if is_usdt:
            amount = amount[:-1]
        try:
            value = float(amount)
            if is_usdt:
                inr = value * state["exchange_rate"]
                final = inr * (1 - state["fee_rate"] / 100)
                state["transactions"].append(f"{user}: Deposit {value} USDT ≈ ₹{final:.2f}")
                await update.message.reply_text(f"✅ Deposited {value} USDT ≈ ₹{final:.2f}")
            else:
                state["transactions"].append(f"{user}: Deposit ₹{value}")
                await update.message.reply_text(f"✅ Deposited ₹{value}")
        except:
            await update.message.reply_text("❌ Invalid deposit format.")

    elif msg.lower().startswith("send"):
        parts = msg.split()
        if len(parts) < 2:
            return await update.message.reply_text("❌ Usage: Send 1000 or Send 1000u")
        amount = parts[1]
        is_usdt = amount.endswith("u")
        if is_usdt:
            amount = amount[:-1]
        try:
            value = float(amount)
            if is_usdt:
                inr = value * state["exchange_rate"]
                final = inr * (1 - state["fee_rate"] / 100)
                state["transactions"].append(f"{user}: Withdraw {value} USDT ≈ ₹{final:.2f}")
                await update.message.reply_text(f"✅ Sent {value} USDT ≈ ₹{final:.2f}")
            else:
                state["transactions"].append(f"{user}: Withdraw ₹{value}")
                await update.message.reply_text(f"✅ Sent ₹{value}")
        except:
            await update.message.reply_text("❌ Invalid withdrawal format.")

    elif msg.lower() == "bills":
        if not state["transactions"]:
            await update.message.reply_text("📂 No transactions yet.")
        else:
            await update.message.reply_text("📄 Transactions:\n" + "\n".join(state["transactions"]))

    elif msg.lower() == "delete today's data":
        state["transactions"].clear()
        await update.message.reply_text("🗑️ Cleared today's transactions.")

    else:
        await update.message.reply_text("⚠️ Unknown command. Use /help for instructions.")

# Main app
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
