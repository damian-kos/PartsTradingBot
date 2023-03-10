import discord
from discord.ext import commands
from discord import Embed, File, Color
from embed.embed_message import embed_simple_message
from error_handler.errors import handle_command_error, handle_error
from instance.pymongo_test_insert import MongoDb


class Join(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = MongoDb()
        self.title = "Trading Bot has joined the server"
        self.description = "‣ You can configure me using: `/settings`"

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await guild.system_channel.send("I'm ready to go!")
        print(guild.name)
        print(guild.id)
        print(guild.system_channel.id)
        embed = embed_simple_message(self.title, self.description)
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(embed=embed)
            break
        self.db.insert_guild(
            guild_id=guild.id,
            guild_name=guild.name,
            guild_system_channel=guild.system_channel.id,
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.db.delete_guild(guild_id=guild.id)


async def setup(bot):
    await bot.add_cog(Join(bot))
