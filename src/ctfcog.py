import discord.ext
from discord.ext import commands
import os
from typing import Optional
import heapq

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

        if chal.files is not None:
            response += "### Available Files:\n"
            for filename in chal.files:
                path = "./challenges/" + name + "/" + filename
                response += " - {}".format(filename)
                if not os.path.exists(path):
                    response += " *(file does not exist on server)*"
                response += "\n"

        if chal.role_id is not None:
            response += "### Role Gained for Completing:\n " + chal.role_id + "\n"

        if chal.attributes is not None:
            response += "### Attributes\n"
        for attribute in chal.attributes:
            response += "**" + attribute + "**: " + chal.attributes[attribute] + "\n"
        await ctx.message.channel.send(response)


    # Need to find a list of keywords that are processed differently in the filter list
    # this could be things like "points=5", where it will filter by challenges that have more than 5 points
    # current ideas:
    # points
    # gives_role

    # also make the list weighted property > category > fuzzy find
    @commands.command(name="list", description="Lists chals using filter strings (seperated by comma)")
    async def _list(self, ctx: discord.Interaction, filter_string: Optional[str]):
        filters = []
        filtered_list = [] # should be a heap queue
        heap_map = {}
        if filter_string is not None:
            filters = filter_string.split(",")
            print(filters)
            for chal in self.client.challenges.values():
                chal_string = str(chal.get_data_as_dict())
                for filter in filters:
                    weight = -1
                    add_chal = False
                    if chal.has_property(filter):
                        print(filter)
                        weight = 0
                        add_chal = True
                    elif chal.has_category(filter):
                        weight = 5
                        add_chal = True
                    elif filter in chal_string:
                        weight = 100
                        add_chal = True
                    if add_chal:
                        filtered_list.append((weight, chal))
                        break
        else:
            for chal in self.client.challenges.values():
                filtered_list.append((0, chal))

        filtered_list.sort(key=lambda a: a[0])

        print(filtered_list)
        response = ""
        if not filtered_list:
            response += "No challenges found\n"
        else:
            response += "### Available Challenges:\n"
            response += "```\n"
            for weight, chal in filtered_list:
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
