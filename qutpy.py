import os
from dotenv import load_dotenv
import yaml

import discord
import discord.ext
from discord.ext import commands
from discord import app_commands

from chal import Chal, load_challenges, load_chal

from typing import Optional

challenges = load_challenges()

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TEST_GUILD_ID = os.getenv('TEST_GUILD_ID')
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.emojis = True
intents.messages = True
intents.members = True

client = commands.Bot(command_prefix='!', intents=intents, help_command=None)


@client.event
async def on_ready():
    # await client.load_extension("maincog"V
    # print(client.guilds)
    await client.tree.sync(guild=discord.Object(id=TEST_GUILD_ID))
    for guild in client.guilds:
        await client.tree.sync(guild=guild)
        print(
            f'{client.user} is connected to the following guild:\n'
            f'{guild.name}(id: {guild.id})'
        )
    await client.tree.sync()


@client.tree.command(name="submit",
                     description="Submits a flag for the specified challenge",
                     guild=discord.Object(id=TEST_GUILD_ID),
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
                     guild=discord.Object(id=TEST_GUILD_ID)
                     )
async def chal(ctx: discord.Interaction, chal_id: str):
    chal = None
    if chal_id not in challenges:
        await ctx.response.send_message("Invalid Challenge " + chal_id, ephemeral=True)
        return

    chal = challenges[chal_id]
    response = "# " + chal.chal_id + "\n"
    if chal.description is not None:
        response += "**Message:** " + chal.description + "\n"
    if chal.role_id is not None:
        response += "**Role Gained for Completing:** " + chal.role_id + "\n"
    await ctx.response.send_message(response)


@client.tree.command(name="get",
                     description="Sends the files for the challenge",
                     guild=discord.Object(id=TEST_GUILD_ID)
                     )
async def get(ctx: discord.Interaction, chal_id: str):
    if chal_id not in challenges:
        await ctx.response.send_message("Challenge not found", ephemeral=True)
        return

    chal = challenges[chal_id]
    files = []
    for filename in chal.files:
        filename.replace('./', '')
        filename.replace('../', '')
        files.append(discord.File("./challenges/" + chal_id + "/" + filename))
    await ctx.response.send_message(files=files)


@client.tree.command(name="create",
                     description="Creates a new challenge",
                     guild=discord.Object(id=TEST_GUILD_ID)
                     )
async def createchal(ctx: discord.Interaction, chal_id: str, flag: str,
                     message: Optional[str], role_id: Optional[str],
                     points: Optional[str]):
    role = discord.utils.get(ctx.guild.roles, name="CTF-EXEC")
    if role not in ctx.user.roles:
        await ctx.response.send_message("User cannot use this command: incorrect permissions")
        return

    if chal_id in challenges:
        await ctx.response.send_message("Challenge with same Id already exists", ephemeral=True)
        return

    chal_id.replace('./', '')
    chal_id.replace('../', '')
    chal_data = {}
    chal_data["name"] = chal_id
    chal_data["flag"] = flag
    chal_data["message"] = message
    chal_data["role"] = role_id
    chal_data["points"] = points

    chal = Chal(chal_id, flag)
    chal.role_id = role_id
    chal.description = message
    chal.files = []
    challenges[chal_id] = chal
    print("created challenges data")

    chaldir = "./challenges/"
    print(chal_data)
    f = open(chaldir + chal_id + ".yaml", 'w')
    yaml.dump(chal_data, f, default_flow_style=False)
    f.close()
    await ctx.response.send_message("Successfully Created Challenge: {}".format(chal_id), ephemeral=True)


@client.tree.command(name="addfile",
                     description="Add a file to a challenges list of files",
                     guild=discord.Object(id=TEST_GUILD_ID)
                     )
async def addfile(ctx: discord.Interaction, chal_id: str, file: str):
    if chal_id not in challenges:
        await ctx.response.send_message("Invalid challenge Id: does not exist", ephemeral=True)
        return

    # f = open("./challenges/" + chal_id + ".yaml")
    # chal_data = yaml.safe_load(f)
    # f.close()
    chal = challenges[chal_id]
    chal.files.append(file)
    # if "files" not in chal_data:
    #    chal_data["files"] = [file]
    # else:
    #    chal_data["files"].append(file)
    challenges[chal_id] = chal
    # challenges[chal_id] = load_chal(chal_id + ".yaml")

    await ctx.response.send_message("Successfully Added file to chal: {}".format(chal_id), ephemeral=True)


@client.command(name="help", description="Returns all commands available")
async def help(ctx):
    helptext = "```"
    for command in client.commands:
        helptext += f"{command}\n"
    commands = client.tree.walk_commands()
    print(commands)
    for command in client.tree.walk_commands(guild=discord.Object(id=TEST_GUILD_ID)):
        helptext += f"{command.name}\n"
    helptext += "```"
    await ctx.send(helptext)

client.run(TOKEN)
