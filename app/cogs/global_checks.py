from discord.ext import commands

from app import errors
from app.classes.bot import Bot
from app.classes.context import MyContext
from app.cogs.permroles import pr_functions


async def not_disabled(ctx: "MyContext") -> bool:
    if ctx.guild is None:
        return True
    if ctx.channel.permissions_for(ctx.message.author).manage_guild:
        return True
    guild = await ctx.bot.db.guilds.get(ctx.guild.id)
    if not guild["allow_commands"]:
        raise errors.AllCommandsDisabled()
    name = ctx.command.qualified_name
    if name in guild["disabled_commands"]:
        raise errors.CommandDisabled(name)
    return True


async def can_use_commands(ctx: "MyContext") -> bool:
    if ctx.guild is None:
        return True
    if ctx.channel.permissions_for(ctx.message.author).administrator:
        return True
    perms = await pr_functions.get_perms(
        ctx.bot,
        [r.id for r in ctx.message.author.roles],
        ctx.guild.id,
        ctx.channel.id,
        None,
    )
    if not perms["allow_commands"]:
        raise errors.CannotUseCommands()
    return True


async def can_send_messages(ctx: "MyContext") -> bool:
    user = ctx.me
    if not ctx.channel.permissions_for(user).send_messages:
        raise commands.BotMissingPermissions(("Send Messages",))
    return True


GLOBAL_CHECKS = [not_disabled, can_send_messages, can_use_commands]


def setup(bot: Bot) -> None:
    for check in GLOBAL_CHECKS:
        bot.add_check(check)
