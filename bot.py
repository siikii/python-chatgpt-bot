import logging
import openai
from telegram import Update
from telegram.ext import (
    filters,
    MessageHandler,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)
from dotenv import dotenv_values


# Set logger
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

# Read .env
config = dotenv_values(".env")

# Define OpenAI API key
openai.api_key = config["OPENAI_API_KEY"]
telegram_bot_token = config["TELEGRAM_BOT_TOKEN"]


# Initialize messages
messages = [
    {
        "role": "system",
        "content": "You are a coding tutor bot to help user write and optimize python code.",
    },
]

# Handle /start command


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm your personal openai bot."
    )
    return generate_response_handler


# Generate response
async def generate_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # # Get user message
    message = update.message.text

    #
    messages.append({"role": "user", "content": message})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )

    response_text = response["choices"][0]["message"]["content"].replace(
        "\n\n", "\n"
    )

    messages.append({"role": "assistant", "content": response_text})

    total_tokens = response["usage"]["total_tokens"]

    if total_tokens > 3000:
        response_text = (
            "I'm sorry, Token limit reached. The conversation has been reset."
        )
        messages.clear()
        messages.append(
            {
                "role": "system",
                "content": "You are a coding tutor bot to help user write and optimize python code.",
            }
        )

    # Send message back
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=response_text
    )

    print(total_tokens)


# Handle unknow command


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Sorry, I don't understand your command.",
    )


if __name__ == '__main__':
    application = ApplicationBuilder().token(telegram_bot_token).build()

    # /start
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)

    # Message handler
    generate_response_handler = MessageHandler(
        filters.TEXT & (~filters.COMMAND), generate_response
    )
    application.add_handler(generate_response_handler)

    # Unknown command handler
    unknown_handler = MessageHandler(filters.COMMAND, unknown)
    application.add_handler(unknown_handler)

    # Start bot
    application.run_polling()
