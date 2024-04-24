import discord.ext
from discord.ext import commands
import os

class CTF(commands.Cog):
    def __init__(self, client):
        self.client = client

    # This group contains commands for viewing challenges
    # Should add the filters/grouping of categories here
    @commands.group(name="view", description="Lets you view things", invoke_without_command=True)
    async def view(self, ctx):
        pass

    @view.command(name="challenge", description="View Challenge Properties")
    async def chalview(
            self,
            ctx: discord.Interaction,
            name: str = commands.parameter(description="id of the challenge you want to view")
            ):
        if (not (await self.client.verifyChal(ctx, name))):
            return
        chal = self.client.challenges[name]

        response = "# " + chal.name + "\n"

        if chal.description is not None:
            response += "### Message: \n" + chal.description + "\n"
        response += "### Points:\n {}\n".format(chal.points)

        response += "### Available Files:\n"
        for filename in chal.files:
            response += " - {}\n".format(filename)

        if chal.role_id is not None:
            response += "### Role Gained for Completing:\n " + chal.role_id + "\n"

        if chal.attributes is not None:
            response += "### Attributes\n"
        for attribute in chal.attributes:
            response += "**" + attribute + "**: " + chal.attributes[attribute] + "\n"
        await ctx.message.channel.send(response)

    @commands.command(name="list", description="Lists specified challenges based on arguments?")
    async def _list(self, ctx: discord.Interaction):
        response = "### Available Challenges:\n"
        response += "```\n"
        for chal in self.client.challenges.values():
            response += chal.name + "\n"
        response += "\n```"
        await ctx.message.channel.send(response)

    @commands.command(name="get",
                      description="Sends the files for the challenge")
    async def get(self, ctx: discord.Interaction, name: str):
        if name not in self.client.challenges:
            await ctx.message.channel.send("Challenge not found", ephemeral=True)
            return

        chal = self.client.challenges[name]
        files = []
        for filename in chal.files:
            filename.replace('./', '')
            filename.replace('../', '')
            path = "./challenges/" + name + "/" + filename
            if os.path.exists(path):
                files.append(discord.File(path))
            else:
                print("Specified file does not exist: ", filename)
        await ctx.message.channel.send(files=files)

    # add leaderboard command
