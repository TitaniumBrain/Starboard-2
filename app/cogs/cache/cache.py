from typing import Any, Dict, List, Optional, Tuple

import discord
from aiocache import Cache as MemCache
from aiocache import SimpleMemoryCache

from app import utils
from app.classes.bot import Bot
from app.constants import MISSING


def cached(  # for future use
    namespace: str,
    ttl: int,
    *,
    cache_args: Tuple[int] = None,
    cache_kwargs: Tuple[str] = None,
):
    cache: SimpleMemoryCache = MemCache(namespace=namespace, ttl=ttl)

    def get_cache_sig(args: List[Any], kwargs: Dict[Any, Any]) -> List[Any]:
        return [
            *[args[i] for i in cache_args],
            *[kwargs.get(k, None) for k in cache_kwargs],
        ]

    def wrapper(coro):
        async def predicate(*args, **kwargs):
            sig = get_cache_sig(args, kwargs)
            if await cache.exists(sig):
                return await cache.get(sig)

            result = await coro(*args, **kwargs)
            await cache.set(sig, result)
            return result

        return predicate

    return wrapper


class Cache:
    def __init__(self, bot) -> None:
        self.messages: SimpleMemoryCache = MemCache(
            namespace="messages", ttl=10
        )
        self.bot = bot
        self.users: SimpleMemoryCache = MemCache(namespace="users", ttl=10)

    async def fetch_user(self, user_id: int) -> discord.User:
        cached = await self.users.get(user_id)
        if cached:
            return cached
        user = await self.bot.fetch_user(user_id)
        await self.users.set(user_id, user)
        return user

    async def get_members(
        self, uids: List[int], guild: discord.Guild
    ) -> Dict[int, Optional[discord.Member]]:
        await self.bot.wait_until_ready()
        not_found: List[int] = []
        result: Dict[int, Optional[discord.Member]] = {}

        for uid in uids:
            cached = guild.get_member(uid)
            if cached:
                result[uid] = cached
            else:
                not_found.append(uid)

        # only query 50 members at a time
        for group in utils.chunk_list(not_found, 50):
            query = await guild.query_members(limit=None, user_ids=group)
            for r in query:
                result[r.id] = r

        return result

    async def fetch_message(
        self, guild_id: int, channel_id: int, message_id: int
    ) -> Optional[discord.Message]:
        cached = await self.messages.get(message_id)
        if not cached:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return None
            channel = guild.get_channel(channel_id)
            if not channel:
                return None
            try:
                message = await channel.fetch_message(message_id)
            except discord.errors.NotFound:
                message = None
            await self.messages.set(message_id, message or MISSING)
            return message
        return cached if cached is not MISSING else None


def setup(bot: Bot) -> None:
    bot.cache = Cache(bot)
