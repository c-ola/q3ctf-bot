import os
import sys
from dotenv import load_dotenv
import yaml

import discord
import discord.ext
from discord.ext import commands
from discord import app_commands

from chal import Chal, load_challenges, load_chal
from ctfcog import CTF
from typing import Optional

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TESTING_MODE = os.getenv('BOT_TEST_MODE')
TEST_TOKEN = os.getenv('TESTBOT_TOKEN')
TEST_GUILD_ID = os.getenv('TEST_GUILD_ID')
GUILDTWO = os.getenv('GUILDTWO')
OWNER_USER_ID = os.getenv('OWNER_USER_ID')


class Qutpy(commands.Bot):
    def __init__(self, *, command_prefix, intents: discord.Intents):
        help_command = commands.DefaultHelpCommand(show_parameter_descriptions=True)

        super().__init__(command_prefix=command_prefix,
                         intents=intents, help_command=help_command)
        self.challenges = load_challenges()

    async def verifyChal(self, ctx, chal_id: str):
        if chal_id not in self.challenges:
            await ctx.message.channel.send("Invalid Challenge " + chal_id)
            return False
        return True

    async def setup_hook(self):
        await self.add_cog(CTF(self))
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=discord.Object(id=TEST_GUILD_ID))
        await self.tree.sync(guild=discord.Object(id=TEST_GUILD_ID))

    @commands.command(name="helpcustom", description="Returns all commands available")
    async def helpcustom(self, ctx):
        helptext = "```"
        for command in client.commands:
            helptext += f"{command}\n"
        commands = client.tree.walk_commands()
        print(commands)
        for command in client.tree.walk_commands(guild=discord.Object(id=TEST_GUILD_ID)):
            helptext += f"{command.name}\n"
        helptext += "```"
        await ctx.send(helptext)


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.emojis = True
intents.messages = True
intents.members = True
client = Qutpy(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')

    for guild in client.guilds:
        print(
                f'{client.user} is connected to the following guild:\n'
                f'{guild.name}(id: {guild.id})'
                )


@client.command(name='sync', description='Owner only')
async def sync(ctx: discord.Interaction):
    print("trying to sync")
    if ctx.message.author.id == int(OWNER_USER_ID):
        await client.tree.sync()
        print('Command tree synced.')
    else:
        await ctx.message.channel.send('You must be the owner to use this command!')


@client.command(name='synch', description='Owner only')
async def synch(ctx: discord.Interaction):
    guild = ctx.message.guild
    print("trying to sync to guild: ", guild)
    if ctx.message.author.id == int(OWNER_USER_ID):
        client.tree.copy_global_to(guild=guild)
        await client.tree.sync(guild=guild)
        print('Command tree synced.')
    else:
        await ctx.message.channel.send('You must be the owner to use this command!')



@client.tree.command(name="submit",
                     description="Submits a flag for the specified challenge",
                     )
async def submit(ctx: discord.Interaction, chal_id: str, flag_guess: str):
    chal = None
    if chal_id in client.challenges:
        chal = client.challenges[chal_id]
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
                     description="View the properties of a challenge"
                     )
async def chal(ctx: discord.Interaction, chal_id: str):
    chal = None
    if chal_id not in client.challenges:
        await ctx.response.send_message("Invalid Challenge " + chal_id, ephemeral=True)
        return

    chal = client.challenges[chal_id]
    response = "# " + chal.chal_id + "\n"
    if chal.description is not None:
        response += "**Message:** " + chal.description + "\n"
    if chal.role_id is not None:
        response += "**Role Gained for Completing:** " + chal.role_id + "\n"
    await ctx.response.send_message(response)


@client.tree.command(name="create",
                     description="Creates a new challenge",
                     # guild=discord.Object(id=TEST_GUILD_ID)
                     )
async def createchal(ctx: discord.Interaction, chal_id: str, flag: str,
                     message: Optional[str], role_id: Optional[str],
                     points: Optional[str]):
    role = discord.utils.get(ctx.guild.roles, name="CTF-EXEC")
    if role not in ctx.user.roles:
        await ctx.response.send_message("User cannot use this command: incorrect permissions")
        return

    if chal_id in client.challenges:
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
    client.challenges[chal_id] = chal
    print("created challenges data")

    chaldir = "./challenges/"
    print(chal_data)
    f = open(chaldir + chal_id + ".yaml", 'w')
    yaml.dump(chal_data, f, default_flow_style=False)
    f.close()
    await ctx.response.send_message("Successfully Created Challenge: {}".format(chal_id), ephemeral=True)


@client.tree.command(name="addfile",
                     description="Add a file to a challenges list of files",
                     )
async def addfile(ctx: discord.Interaction, chal_id: str, file: str):
    if chal_id not in client.challenges:
        await ctx.response.send_message("Invalid challenge Id: does not exist", ephemeral=True)
        return

    # f = open("./challenges/" + chal_id + ".yaml")
    # chal_data = yaml.safe_load(f)
    # f.close()
    chal = client.challenges[chal_id]
    chal.files.append(file)
    # if "files" not in chal_data:
    #    chal_data["files"] = [file]
    # else:
    #    chal_data["files"].append(file)
    client.challenges[chal_id] = chal
    # challenges[chal_id] = load_chal(chal_id + ".yaml")

    await ctx.response.send_message("Successfully Added file to chal: {}".format(chal_id), ephemeral=True)

if TESTING_MODE == "1":
    client.run(TEST_TOKEN)
else:
    client.run(TOKEN)
