import asyncio
from telegram import Update, ChatPermissions
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationBuilder, ChatMemberHandler, ContextTypes

# بياناتك
BOT_TOKEN = '7441538182:AAHSxxZtWGhY6oFtbqqpDC5ZLgTksDpcMUA'
ADMIN_ID = 656840694

muted_members = set()

async def on_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not update.chat_member:
            return
        
        member = update.chat_member.new_chat_member
        if member.status == ChatMemberStatus.MEMBER:
            user = member.user
            if user and not user.username:
                await context.bot.restrict_chat_member(
                    chat_id=update.chat_member.chat.id,
                    user_id=user.id,
                    permissions=ChatPermissions(can_send_messages=False)
                )
                muted_members.add((update.chat_member.chat.id, user.id))
                
                await context.bot.send_message(
                    chat_id=ADMIN_ID,
                    text=f"👮‍♂️ تم كتم العضو [{user.full_name}](tg://user?id={user.id}) لأنه بدون معرف.",
                    parse_mode="Markdown"
                )
    except Exception as e:
        print(f"خطأ أثناء كتم عضو: {e}")

async def unmute_checked_members(app):
    while True:
        try:
            for chat_id, user_id in list(muted_members):
                user = await app.bot.get_chat_member(chat_id, user_id)
                if user and user.user.username:
                    await app.bot.restrict_chat_member(
                        chat_id=chat_id,
                        user_id=user_id,
                        permissions=ChatPermissions(
                            can_send_messages=True,
                            can_send_media_messages=True,
                            can_send_polls=True,
                            can_send_other_messages=True,
                            can_add_web_page_previews=True,
                            can_change_info=True,
                            can_invite_users=True,
                            can_pin_messages=True
                        )
                    )
                    muted_members.remove((chat_id, user_id))
                    
                    await app.bot.send_message(
                        chat_id=ADMIN_ID,
                        text=f"🔓 تم فك الكتم عن [{user.user.full_name}](tg://user?id={user.user.id}) بعد إضافة معرف.",
                        parse_mode="Markdown"
                    )
        except Exception as e:
            print(f"خطأ أثناء فك الكتم: {e}")

        await asyncio.sleep(43200)  # كل 12 ساعة

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(ChatMemberHandler(on_chat_member, ChatMemberHandler.CHAT_MEMBER))

    app.create_task(unmute_checked_members(app))

    print("✅ البوت اشتغل بنجاح!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
