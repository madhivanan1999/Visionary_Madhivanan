from sqlalchemy import text
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

from database import engine, Base
from services import (
    register_user_full,
    get_user_by_telegram_id,
    assign_task,
    get_pending_task,
    complete_task,
    delete_user_by_telegram_id,
)
from ai_tutor import generate_ai_response, clear_chat_history
from config import TELEGRAM_BOT_TOKEN

# Telegram Bot Token
TOKEN = TELEGRAM_BOT_TOKEN

# Ensure schema exists
with engine.connect() as conn:
    conn.execute(text("CREATE SCHEMA IF NOT EXISTS vs"))
    conn.commit()

# Create tables if not present
Base.metadata.create_all(bind=engine)

# Conversation States
(
    NAME,
    UNIVERSITY,
    COLLEGE,
    STREAM,
    YEAR,
    DEPARTMENT,
    SEM,
    MOBILE,
    EMAIL,
) = range(9)


# -------------------------------
# Utility: Send Long Messages
# -------------------------------
async def send_long_message(update: Update, text: str, chunk_size: int = 3900):
    """
    Splits long messages into chunks to comply with Telegram's
    4096-character limit.
    """
    if not text:
        await update.message.reply_text("⚠️ Empty response from AI.")
        return

    for i in range(0, len(text), chunk_size):
        await update.message.reply_text(text[i:i + chunk_size])


# -------------------------------
# Start Command
# -------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    user = get_user_by_telegram_id(telegram_id)

    if user:
        await update.message.reply_text(
            f"Welcome back, {user.student_name}! 🎓\n"
            "Use /task to view your assigned task."
        )
        return ConversationHandler.END

    context.user_data["registration_in_progress"] = True
    await update.message.reply_text(
        "🎓 Welcome to Smart Learning Bot!\n\n"
        "Please enter your Full Name:"
    )
    return NAME


# -------------------------------
# Registration Flow
# -------------------------------
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["student_name"] = update.message.text
    await update.message.reply_text("Enter your University:")
    return UNIVERSITY


async def get_university(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["university"] = update.message.text.lower()
    await update.message.reply_text("Enter your College Name:")
    return COLLEGE


async def get_college(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["college_name"] = update.message.text
    await update.message.reply_text("Enter your Stream (e.g., b.tech):")
    return STREAM


async def get_stream(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["stream"] = update.message.text.lower()
    await update.message.reply_text("Enter your Year (e.g., 1):")
    return YEAR


async def get_year(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["std_year"] = int(update.message.text)
        await update.message.reply_text("Enter your Department:")
        return DEPARTMENT
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid numeric year.")
        return YEAR


async def get_department(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["department"] = update.message.text.lower()
    await update.message.reply_text("Enter your Semester:")
    return SEM


async def get_sem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data["sem"] = int(update.message.text)
        await update.message.reply_text("Enter your Mobile Number:")
        return MOBILE
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid semester.")
        return SEM


async def get_mobile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mobile = update.message.text.strip()
    if not mobile.isdigit() or len(mobile) not in (10, 12, 13):
        await update.message.reply_text(
            "❌ Please enter a valid mobile number."
        )
        return MOBILE

    context.user_data["mobile_no"] = mobile
    await update.message.reply_text("Enter your Email ID:")
    return EMAIL


async def get_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()

    # ✅ Validation
    if "@" not in email or "." not in email:
        await update.message.reply_text(
            "❌ Please enter a valid email address."
        )
        return EMAIL

    telegram_id = str(update.effective_user.id)
    context.user_data["email_id"] = email
    context.user_data["telegram_id"] = telegram_id

    try:
        user = register_user_full(context.user_data)

        if not user:
            await update.message.reply_text(
                "❌ Registration failed. Try again."
            )
            return EMAIL

        # 🔥 Assign task (FIXED CALL)
        from database import SessionLocal
        db = SessionLocal()
        task = assign_task(db, user)
        db.close()

        message = f"✅ Registration Successful, {user.student_name}!\n"

        if task:
            message += (
                f"\n📚 Your First Task:\n"
                f"Subject: {task.subjects}\n"
                f"Topic: {task.topics}"
            )
        else:
            message += "\nNo tasks found for your syllabus."

        context.user_data.pop("registration_in_progress", None)
        await update.message.reply_text(message)
        return ConversationHandler.END

    except Exception as e:
        print("EMAIL ERROR:", e)

        await update.message.reply_text(
            "❌ Email already exists or invalid.\n"
            "Please enter a different email:"
        )
        return EMAIL

    telegram_id = str(update.effective_user.id)
    context.user_data["email_id"] = email
    context.user_data["telegram_id"] = telegram_id

    user = register_user_full(context.user_data)
    task = assign_task(user)

    message = f"✅ Registration Successful, {user.student_name}!\n"

    if task:
        message += (
            f"\n📚 Your First Task:\n"
            f"Subject: {task.subjects}\n"
            f"Topic: {task.topics}"
        )
    else:
        message += "\nNo tasks found for your syllabus."

    context.user_data.pop("registration_in_progress", None)
    await update.message.reply_text(message)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop("registration_in_progress", None)
    await update.message.reply_text("❌ Registration cancelled.")
    return ConversationHandler.END


# -------------------------------
# Task Commands
# -------------------------------
async def task_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    task = get_pending_task(telegram_id)

    if not task:
        await update.message.reply_text("📭 No pending tasks found.")
        return

    message = (
        "📚 Your Current Task:\n\n"
        f"Subject: {task.subjects}\n"
        f"Topic: {task.topics}\n"
        f"Module: {task.module_no}\n"
        f"Description: {task.model_description}"
    )
    await update.message.reply_text(message)


async def complete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    task = complete_task(telegram_id)

    if not task:
        await update.message.reply_text("⚠️ No active task to complete.")
        return

    await update.message.reply_text(
        f"✅ Task Completed!\n\n"
        f"Subject: {task.subjects}\n"
        f"Topic: {task.topics}"
    )


# -------------------------------
# AI Tutor (MCP + Groq)
# -------------------------------
async def ai_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ignore commands
    if update.message.text.startswith("/"):
        return

    # Prevent AI from interfering with registration
    if context.user_data.get("registration_in_progress"):
        return

    telegram_id = str(update.effective_user.id)
    user_message = update.message.text

    try:
        response = generate_ai_response(user_message, telegram_id)
    except Exception as e:
        response = (
            "⚠️ AI service is temporarily unavailable.\n"
            f"Error: {str(e)}"
        )

    await send_long_message(update, response)


# -------------------------------
# Reset Chat Memory
# -------------------------------
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    clear_chat_history(telegram_id)
    await update.message.reply_text("🧹 Chat history has been cleared.")


# -------------------------------
# Global Error Handler
# -------------------------------
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    print(f"⚠️ Exception occurred: {context.error}")


async def reset_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_user.id)
    success = delete_user_by_telegram_id(telegram_id)

    if success:
        await update.message.reply_text(
            "🔄 Your registration has been reset. Please use /start to register again."
        )
    else:
        await update.message.reply_text(
            "No registration data found."
        )



# -------------------------------
# Main Function
# -------------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            UNIVERSITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_university)],
            COLLEGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_college)],
            STREAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_stream)],
            YEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_year)],
            DEPARTMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_department)],
            SEM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_sem)],
            MOBILE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_mobile)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_email)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Register Handlers
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("task", task_command))
    app.add_handler(CommandHandler("complete", complete_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_chat))
    app.add_error_handler(error_handler)
    app.add_handler(CommandHandler("reset_registration", reset_registration))
    
    print("🚀 Smart Learning Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()