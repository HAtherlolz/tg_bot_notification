import asyncio

from typing import List

from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, time

from telegram.error import TimedOut

from cfg.celery_conf import celery_app
from utils.logs import log

from services.bot import Bot
from schemas.igonred_users import IgnoredUserSchema
from repositories.mongodb import (
    ChatRepository, MessageRepository,
    UserRepository, IgnoredUserRepository
)


@celery_app.task()
def check_msg():
    is_working_time: bool = is_work_time()
    if not is_working_time:
        log.info("It is not a working time, skipping...")
        return

    time_delta = datetime.now() - timedelta(minutes=14)
    log.info(f"time_delta, {time_delta}")

    last_messages_today = MessageRepository.get_last_message_from_all_group_chats_for_today()
    moderators = UserRepository.get_all_moderators()
    moderators_usernames = [moderator.username for moderator in moderators]

    moderators_group_chat = ChatRepository.get_admins_chat_id()
    ignored_users_list: List[IgnoredUserSchema] = IgnoredUserRepository.get_list_ignored_users()
    ign_usr_list = ignored_users_to_list(ignored_users_list)

    advertisers = []
    messages_to_ignore = [
        "thanks", "thank", "no", "moment", "atm", "noted",
        "pushing", "us", "thank you", "need", "push"
    ]
    for last_message in last_messages_today:
        first_name = last_message.first_name if last_message.first_name else ''
        last_name = last_message.last_name if last_message.last_name else ''

        if (
                # Check if message was created 15 minute ago
                (last_message.created_at < time_delta)
                # Check if username of the message owner is not in moderator list
                and (
                    last_message.username not in moderators_usernames)
                # Check if message is not contains a "stark" in first or last name
                and (
                    ("stark" not in first_name.lower())
                    and
                    (last_name.lower() != "stark")
                )
                # Check if last message is not in ignored list
                and (
                    last_message.message.lower() not in messages_to_ignore
                )
                # Check if username of the message owner is not in ignored list
                and (
                    last_message.username not in ign_usr_list
                )
        ):
            advertisers.append({
                "chat_id": last_message.chat_id,
                "username": last_message.username,
                "name": last_message.name,
            })

    if advertisers:
        notification_message = (
            "These are the advertisers that are waiting for a reply:\n" +
            "\n".join(f"- {adv['name']} - @{adv['username']}" for adv in advertisers)
        )

        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        loop.run_until_complete(send_msg_to_moderators(moderators_group_chat, notification_message))


async def send_msg_to_moderators(
        moderators_group_chat: int,
        notification_message: str
) -> None:
    try:
        await Bot.send_message_to_chat(
            moderators_group_chat, notification_message
        )
    except TimedOut as e:
        log.info(f"Error: {e}")
        log.info(f"Retrying ...: {e}")
        await Bot.send_message_to_chat(
            moderators_group_chat, notification_message
        )
    except BaseException as e:
        log.info(f"Base Exception Error: {e}")


def ignored_users_to_list(
        ignored_users: List[IgnoredUserSchema]
) -> List:
    ignored_list: List = [ign_usr.username for ign_usr in ignored_users]
    return ignored_list


def is_work_time() -> bool:
    utc_date_time = datetime.now()

    gmt_plus_3 = ZoneInfo('Etc/GMT-3')  # 'Etc/GMT-3' corresponds to GMT+3
    local_date_time = utc_date_time.astimezone(gmt_plus_3)
    current_time = local_date_time.time()

    start_time = time(22, 0)  # 22:00 PM
    end_time = time(8, 0)  # 08:00 AM

    # Check if current time is within the range
    if start_time <= current_time or current_time <= end_time:
        return False
    return True
