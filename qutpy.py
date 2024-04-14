import os
from dotenv import load_dotenv

import discord
import discord.ext
from discord.ext import commands
from discord import app_commands

from chal import Chal, load_challenges


challenges = load_challenges()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.emojis = True
intents.messages = True
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    # await client.load_extension("maincog"V
    # print(client.guilds)
    await client.tree.sync(guild=discord.Object(id=864247133996843019))
    for guild in client.guilds:
        await client.tree.sync(guild=guild)
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )
    await client.tree.sync()


@client.tree.command(name="submit",
                     description="Submits a flag for the specified challenge",
                     guild=discord.Object(id=864247133996843019)
                     )
async def submit(ctx: discord.Interaction, chal_id: str, flag_guess: str):
    chal = None
    if chal_id in challenges:
        chal = challenges[chal_id]
    else:
        await ctx.response.send_message("Invalid Challenge " + chal_id, ephemeral=True)
        return

    response = ""
    if chal.verify(flag_guess):
        response = "Congrats! You found the flag!"
        member = ctx.user
        print("User {} found the flag for {}".format(member, chal.chal_id))
        if chal.role_id is not None and member is not None and discord.utils.get(ctx.guild.roles, name=chal.role_id) is not None:
            print("Adding role {} to user {}".format(chal.role_id, member))
            role = discord.utils.get(ctx.guild.roles, name=chal.role_id)
            await member.add_roles(role)
    else:
        response = "Yikes, wrong flag :p. try again?"

    await ctx.response.send_message(response, ephemeral=True)


@client.tree.command(name="chal",
                     description="View the properties of a challenge",
                     guild=discord.Object(id=864247133996843019)
                     )
async def chal(ctx: discord.Interaction, chal_id: str):
    chal = None
    if chal_id in challenges:
        chal = challenges[chal_id]
        response = "# " + chal.chal_id + "\n"
        if chal.description is not None:
            response += "**Message:** " + chal.description + "\n"
        if chal.role_id is not None:
            response += "**Role Gained for Completing:** " + chal.role_id + "\n"
        await ctx.response.send_message(response)
    else:
        await ctx.response.send_message("Invalid Challenge " + chal_id, ephemeral=True)
        return

@client.tree.command(name="add",
                     description="Adds a challenge",
                     guild=discord.Object(id=864247133996843019)
                     )
async def add(ctx: discord.Interaction, chal_id: str):
    await ctx.response.send_message("Not implemented yet", ephemeral=True)
    if chal in challenges:
        return


client.run(TOKEN)
