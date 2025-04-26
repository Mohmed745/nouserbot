import asyncio
from telegram import Update, ChatPermissions
from telegram.constants import ChatMemberStatus
from telegram.ext import ApplicationBuilder, ChatMemberHandler, ContextTypes

# توكن البوت حط هنا
TOKEN = "7441538182:AAHSxxZtWGhY6oFtbqqpDC5ZLgTksDpcMUA

# القروبات اللي تبي تراقبها (ID القروب يكون بالسالب - مثلا: -1001234567890)
ALLOWED_CHAT_IDS = [-656840694]

# دالة التعامل مع تحديث حالة العضو
async def handle_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.chat_member is None:
        return

    member = update.chat_member
    if member.status == ChatMemberStatus.MEMBER:
        if not member.user.username:  # ما عنده معرف
            # يكتم العضو
            await context.bot.restrict_chat_member(
                chat_id=update.effective_chat.id,
                user_id=member.user.id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            # يرسل تنبيه في القروب
            await update.effective_chat.send_message(
                text=f"📢 تم كتم العضو [{member.user.full_name}](tg://user?id={member.user.id}) لعدم وجود معرف.",
                parse_mode='Markdown'
            )

# دالة فك الكتم للأعضاء اللي حدثوا معرفاتهم
async def unmute_checked_members(app):
    while True:
        for chat_id in ALLOWED_CHAT_IDS:
            chat = await app.bot.get_chat(chat_id)
            admins = await app.bot.get_chat_administrators(chat_id)
            admin_ids = [admin.user.id for admin in admins]

            async for member in app.bot.get_chat_administrators(chat_id):
                pass  # نتخطى عشان مايخرب علينا التكرار

            # نجيب قائمة الأعضاء
            try:
                async for member in app.bot.get_chat_member_iter(chat_id):
                    if not member.user.is_bot and member.status == ChatMemberStatus.RESTRICTED:
                        if member.user.username:
                            # اذا صار عنده معرف نفك الكتم
                            await app.bot.restrict_chat_member(
                                chat_id=chat_id,
                                user_id=member.user.id,
                                permissions=ChatPermissions(can_send_messages=True,
                                                            can_send_media_messages=True,
                                                            can_send_polls=True,
                                                            can_send_other_messages=True,
                                                            can_add_web_page_previews=True,
                                                            can_change_info=False,
                                                            can_invite_users=True,
                                                            can_pin_messages=False)
                            )
                            # نرسل تنبيه انه انفك عنه الكتم
                            await app.bot.send_message(
                                chat_id=chat_id,
                                text=f"✅ تم فك الكتم عن [{member.user.full_name}](tg://user?id={member.user.id}) بعد إضافة معرف.",
                                parse_mode='Markdown'
                            )
            except Exception as e:
                print(f"خطأ أثناء التحقق: {e}")

        await asyncio.sleep(12 * 60 * 60)  # كل ١٢ ساعة

# دالة التشغيل الرئيسية
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(ChatMemberHandler(handle_chat_member, chat_member_types=ChatMemberHandler.CHAT_MEMBER))

    # تشغيل مهمة الفحص المتكرر لفك الكتم
    app.create_task(unmute_checked_members(app))

    print("البوت شغال...")

    await app.run_polling()

# تشغيل التطبيق
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
