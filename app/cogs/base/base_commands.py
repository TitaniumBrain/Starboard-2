import time

import discord
from discord.ext import commands

import config
from app import converters
from app.classes.context import MyContext
from app.i18n import t_
from app.utils import clean_prefix, ms

from ...classes.bot import Bot


class Base(commands.Cog):
    "Basic information and commands"

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.about_starboard = t_(
            "A Starboard is a bot that allows users of a server"
            ' to "vote" to "pin" a message. The main idea is this:\n'
            " - You set a channel as the starboard, typically called "
            "`#starboard`\n"
            " - You set an emoji for voting to pin messages, usually :star:\n"
            " - You set a limit (called requiredStars on this bot) that "
            "tells Starboard how many reactions (of the emoji you set) a "
            "message needs before it is sent to the starboard.\n\n"
            "Once a message reaches the requiredStars limit in  reactions, "
            "Starboard will essentially copy the message and repost it in "
            "your starboard.",
            True,
        )

    @commands.command(name="credits", help=t_("Show credits", True))
    @commands.bot_has_permissions(embed_links=True)
    @commands.guild_only()
    async def show_credits(self, ctx: "MyContext"):
        embed = (
            discord.Embed(
                title=t_("Starboard Credits"),
                color=self.bot.theme_color,
            )
            .add_field(
                name=t_("Owner(s)"),
                value=", ".join(
                    [
                        str(await self.bot.cache.fetch_user(uid))
                        for uid in config.OWNER_IDS
                    ]
                ),
            )
            .add_field(
                name=t_("Developer(s)"),
                value=", ".join(
                    [
                        str(await self.bot.cache.fetch_user(uid))
                        for uid in config.DEVELOPERS
                    ]
                ),
            )
            .add_field(
                name=t_("Translator(s)"),
                value=", ".join(
                    [
                        str(await self.bot.cache.fetch_user(uid))
                        for uid in config.TRANSLATORS
                    ]
                ),
            )
        )

        await ctx.send(embed=embed)

    @commands.command(name="help", help=t_("Get help with Starboard", True))
    @commands.bot_has_permissions(embed_links=True)
    async def starboard_help(self, ctx: "MyContext", *, command=None) -> None:
        if command:
            await converters.CommandOrCog().convert(ctx, command)
            return await ctx.send_help(command)

        p = clean_prefix(ctx)

        embed = discord.Embed(
            title="Staboard Help",
            description=t_(
                "**[Starboard Documentation]({0.DOCS})**\n\n"
                "To see a complete command list, run `{1}commands`.\n"
                "To see a list of disabled commands, run `{1}disabled`.\n"
                "To list all prefixes, run `{1}prefixes`.\n"
                "For a list of useful links, run `{1}links`\n\n"
                "If you need any help, you can join [the support server]"
                "({0.SUPPORT_INVITE})"
            ).format(config, p),
            color=self.bot.theme_color,
        ).add_field(
            name=t_("What is a Starboard?"), value=str(self.about_starboard)
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="commands", help=t_("See a list of commands.", True)
    )
    @commands.bot_has_permissions(
        embed_links=True, add_reactions=True, read_message_history=True
    )
    async def invoke_pretty_help(
        self, ctx: "MyContext", *, command: str = None
    ) -> None:
        if command:
            await converters.CommandOrCog().convert(ctx, command)
            await ctx.send_help(command)
        else:
            await ctx.send_help()

    @commands.command(
        name="botstats", aliases=["botinfo"], help=t_("Shows bot statistics")
    )
    @commands.bot_has_permissions(embed_links=True)
    async def botinfo(self, ctx: "MyContext") -> None:
        clusters = [c for _, c in self.bot.stats.items()]
        total_guilds = sum([c["guilds"] for c in clusters])
        total_members = sum([c["members"] for c in clusters])

        embed = discord.Embed(
            title=t_("Bot Stats"),
            description=t_(
                "Guilds: **{0}**\n"
                "Users: **{1}**\n"
                "Clusters: **{2}**\n"
                "Shards: **{3}**"
            ).format(
                total_guilds,
                total_members,
                len(clusters),
                self.bot.shard_count,
            ),
            color=self.bot.theme_color,
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="ping",
        aliases=["latency"],
        help=t_("Shows current clusters and shards latency", True),
    )
    @commands.cooldown(1, 3, commands.BucketType.member)
    @commands.bot_has_permissions(embed_links=True)
    async def ping(self, ctx: "MyContext") -> None:
        cluster = self.bot.cluster_name
        shard = self.bot.get_shard(ctx.guild.shard_id if ctx.guild else 0)

        t1 = time.time()
        m = await ctx.send(t_("Pinging..."))
        t2 = time.time()
        await m.edit(content=t_("Editing..."))
        t3 = time.time()
        await m.delete()
        t4 = time.time()

        send = t2 - t1
        edit = t3 - t2
        delete = t4 - t3

        embed = discord.Embed(
            title=t_("Pong!"),
            color=self.bot.theme_color,
            description=t_(
                "Send: {0}ms\n" "Edit: {1}ms\n" "Delete: {2}ms"
            ).format(ms(send), ms(edit), ms(delete)),
        )
        embed.add_field(
            name=t_("Cluster **{0}**").format(cluster),
            value=t_("{0} ms").format(ms(self.bot.latency)),
            inline=False,
        )
        embed.add_field(
            name=t_("Shard **{0}**").format(shard.id),
            value=t_("{0} ms").format(ms(shard.latency)),
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="links",
        aliases=["invite", "support"],
        help=t_("Lists important/useful links", True),
    )
    @commands.bot_has_permissions(embed_links=True)
    async def links(self, ctx: "MyContext") -> None:
        embed = (
            discord.Embed(
                title=t_("Important Links"),
                color=self.bot.theme_color,
                description=t_(
                    "**[Documentation]({0.DOCS})**\n"
                    "**[Support Server]({0.SUPPORT_INVITE})**\n"
                    "**[Invite Starboard]({0.BOT_INVITE})**\n"
                ).format(config),
            )
            .add_field(
                name=t_("Support Starboard"),
                value=str(
                    "**"
                    + "\n".join(config.DONATE_LINKS)
                    + t_("\n[Become a Patron]({0.PATREON_LINK})**").format(
                        config
                    )
                ),
            )
            .add_field(
                name=t_("Vote Links"),
                value=str("**" + "\n".join(config.VOTE_LINKS) + "**"),
                inline=False,
            )
            .add_field(
                name=t_("Review Links"),
                value=str("**" + "\n".join(config.REVIEW_LINKS) + "**"),
                inline=False,
            )
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="vote",
        aliases=["votes"],
        help=t_("View vote links and number of times you've voted", True),
    )
    @commands.bot_has_permissions(embed_links=True)
    async def vote(self, ctx: "MyContext", user: discord.User = None) -> None:
        user = user or ctx.message.author
        if user.bot:
            await ctx.send(
                t_(
                    "{0} is a bot. How many times do you "
                    "think they've voted?"
                ).format(user)
            )
            return
        sql_user = await self.bot.db.users.get(user.id)
        if sql_user:
            count = sql_user["votes"]
        else:
            count = 0
        embed = (
            discord.Embed(
                title=t_("Vote for Starboard"),
                color=self.bot.theme_color,
                description=t_("You have voted **{0}** time(s).").format(count)
                if user.id == ctx.message.author.id
                else t_("**{0}** has voted **{1}** time(s).").format(
                    user, count
                ),
                inline=False,
            )
            .add_field(
                name=t_("Vote Links"),
                value="**" + "\n".join(config.VOTE_LINKS) + "**",
                inline=False,
            )
            .add_field(
                name=t_("Review Links"),
                value="**" + "\n".join(config.REVIEW_LINKS) + "**",
                inline=False,
            )
        )
        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    bot.add_cog(Base(bot))
