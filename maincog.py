from discord.ext import commands


class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def dosomething(self, ctx):
        print("Doing cog: " + type(self).__name__)
        await ctx.response.send_message("Doing Something")


async def setup(bot):
    await bot.add_cog(MainCog(bot))
