import logging
import asyncio
from telegram import Update, ChatPermissions, ChatMember
from telegram.ext import ApplicationBuilder, ChatMemberHandler, ContextTypes

# 7441538182:AAHSxxZtWGhY6oFtbqqpDC5ZLgTksDpcMUA
BOT_TOKEN = '7441538182:AAHSxxZtWGhY6oFtbqqpDC5ZLgTksDpcMUA'

# تخزين الأعضاء المكتومين {chat_id: set(user_ids)}
muted_members = {}

# إعداد اللوقز
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def mute_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.chat_member is None:
        return

    member = update.chat_member.new_chat_member
    user = member.user
    chat_id = update.chat_member.chat.id

    # لو العضو دخل بدون Username
    if update.chat_member.old_chat_member.status == ChatMember.LEFT and \
       member.status == ChatMember.MEMBER and \
       (user.username is None or user.username == ''):

        try:
            permissions = ChatPermissions(can_send_messages=False)
            await context.bot.restrict_chat_member(
                chat_id=chat_id,
                user_id=user.id,
                permissions=permissions
            )

            # حفظ العضو في قائمة المكتومين
            if chat_id not in muted_members:
                muted_members[chat_id] = set()
            muted_members[chat_id].add(user.id)

            logging.info(f"Muted user without username: {user.first_name}")
        except Exception as e:
            logging.error(f"Failed to mute user: {e}")

async def unmute_checked_members(context: ContextTypes.DEFAULT_TYPE):
    while True:
        await asyncio.sleep(43200)  # 12 ساعة = 43200 ثانية

        for chat_id, user_ids in list(muted_members.items()):
            for user_id in list(user_ids):
                try:
                    member = await context.bot.get_chat_member(chat_id=chat_id, user_id=user_id)
                    user = member.user

                    if user.username is not None and user.username != '':
                        permissions = ChatPermissions(
                            can_send_messages=True,
                            can_send_media_messages=True,
                            can_send_polls=True,
                            can_send_other_messages=True,
                            can_add_web_page_previews=True,
                            can_change_info=False,
                            can_invite_users=True,
                            can_pin_messages=False
                        )
                        await context.bot.restrict_chat_member(
                            chat_id=chat_id,
                            user_id=user.id,
                            permissions=permissions
                        )

                        muted_members[chat_id].remove(user_id)
                        logging.info(f"Unmuted user after username update: {user.first_name}")
                except Exception as e:
                    logging.error(f"Error checking user: {e}")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(ChatMemberHandler(mute_member, ChatMemberHandler.CHAT_MEMBER))

    # تشغيل الفاحص كل ١٢ ساعة
    app.create_task(unmute_checked_members(app))

    print("البوت شغال...")
    await app.run_polling()

if __name__ == '__main__':
    import asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

