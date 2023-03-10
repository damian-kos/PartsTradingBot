from discord.ext import commands
from embed.embed_pagination import Pagination
from embed.embed_message import embed_message
from .search_in_inventory import SearchInInventory
from pathlib import Path
import discord
from error_handler.errors import handle_command_error, handle_error
from instance.pymongo_test_insert import MongoDb


class Search(commands.Cog):
    def __init__(self, bot):
        """
        A class representing the search functionality of the bot.

        Methods
        -------
        search(ctx)
            Searches for items in the bot's inventory based on user input.
        on_command_error(ctx, error)
            An error handler for the search command.
        """
        self.search = SearchInInventory()
        self.bot = bot
        self.db = MongoDb()
        self.path_to_inv_images = (
            Path("trading_bot") / "inventory" / "inventory_images"
        )

    @commands.command(name="search")
    async def search(self, ctx):
        """
        Searches for items in the bot's inventory based on user input.

        Parameters
        ----------
        ctx : Context
            The context of the message.
        """
        self.db.guild_in_database(guild_id=ctx.guild.id)
        if self.db.guild is not None:
            self.search_channel = self.db.guild["search_channel"]
            self.search.convert_message(ctx.message.content)
            to_search = self.search.search()
            search_results = self.db.search_item(
                guild_id=ctx.guild.id, search_dict=to_search
            )

        try:
            if isinstance(search_results, str):
                message = self.search.no_items_message(search_results)
                await ctx.send(
                    message[0],
                    embed=message[1],
                    file=message[2],
                )
            else:
                items_dicts = search_results
                first_dict = items_dicts[0]
                embed = embed_message(
                    item_id=(f"{ctx.guild.id}_{first_dict['id']}.png"),
                    image_path=f"{self.path_to_inv_images}",
                    item_dict=first_dict,
                )

                view = Pagination(
                    guild_id=ctx.guild.id, found_items=items_dicts
                )
                view.response = await ctx.send(
                    "I've found these items for you.",
                    embed=embed[0],
                    files=embed[1],
                    view=view,
                )
        except Exception as e:
            await handle_command_error(ctx, e)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """
        An error handler for the search command.

        Parameters
        ----------
        ctx : Context
            The context of the message.
        error : Exception
            The error that occurred.
        """
        await handle_error(ctx, error)


async def setup(bot):
    await bot.add_cog(Search(bot))
