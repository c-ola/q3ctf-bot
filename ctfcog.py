import discord.ext
from discord.ext import commands


class CTF(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(name="view", description="Lets you view things", invoke_without_command=True)
    async def view(self, ctx):
        pass

    @view.command(name="challenge", description="View Challenge Properties")
    async def chalview(
            self,
            ctx: discord.Interaction,
            chal_id: str = commands.parameter(description="id of the challenge you want to view")
            ):
        if (not (await self.client.verifyChal(ctx, chal_id))):
            return
        chal = self.client.challenges[chal_id]
        response = "# " + chal.chal_id + "\n"
        if chal.description is not None:
            response += "### Message: \n" + chal.description + "\n"
        response += "### Points:\n {}\n".format(chal.points)
        response += "### Available Files:\n"
        for filename in chal.files:
            response += " - {}\n".format(filename)
        if chal.role_id is not None:
            response += "### Role Gained for Completing:\n " + chal.role_id + "\n"
        await ctx.message.channel.send(response)

    @commands.command(name="list", description="Lists specified challenges based on arguments?")
    async def _list(self, ctx: discord.Interaction):
        response = "### Available Challenges:\n"
        response += "```\n"
        for chal in self.client.challenges.values():
            response += chal.chal_id + "\n"
        response += "\n```"
        await ctx.message.channel.send(response)

    @commands.command(name="get",
                      description="Sends the files for the challenge")
    async def get(self, ctx: discord.Interaction, chal_id: str):
        if chal_id not in self.client.challenges:
            await ctx.message.channel.send("Challenge not found", ephemeral=True)
            return

        chal = self.client.challenges[chal_id]
        files = []
        for filename in chal.files:
            filename.replace('./', '')
            filename.replace('../', '')
            files.append(discord.File("./challenges/" + chal_id + "/" + filename))
        await ctx.message.channel.send(files=files)
