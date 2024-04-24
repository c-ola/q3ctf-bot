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
OWNER_USER_ID = os.getenv('OWNER_USER_ID')


class Qutpy(commands.Bot):
    def __init__(self, *, command_prefix, intents: discord.Intents):
        help_command = commands.DefaultHelpCommand(show_parameter_descriptions=True)

        super().__init__(command_prefix=command_prefix,
                         intents=intents, help_command=help_command)
        self.challenges = load_challenges()
        # for chal in self.challenges.values():
        #    print("----------------------")
        #    chal.print()
        #    print("----------------------")

    async def verifyChal(self, ctx, name: str):
        if name not in self.challenges:
            await ctx.message.channel.send("Invalid Challenge " + name)
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
async def submit(ctx: discord.Interaction, name: str, flag_guess: str):
    chal = None
    if name in client.challenges:
        chal = client.challenges[name]
    else:
        await ctx.response.send_message("Invalid Challenge " + name, ephemeral=True)
        return

    response = ""
    if chal.verify(flag_guess):
        response = "Congrats! You found the flag!"
        member = ctx.user
        print("User {} found the flag for {}".format(member, chal.name))
        if chal.role_id is not None and member is not None and discord.utils.get(ctx.guild.roles, name=chal.role_id) is not None:
            print("Adding role {} to user {}".format(chal.role_id, member))
            role = discord.utils.get(ctx.guild.roles, name=chal.role_id)
            await member.add_roles(role)
    else:
        response = "Yikes, wrong flag :p. try again?"

    await ctx.response.send_message(response, ephemeral=True)


# This command lets you initially create a challenge with a command
# Note: arguments have to be lower case
# TODO: add attributes, this could be done in the modify command
@client.tree.command(name="create",
                     description="Creates a new challenge"
                     )
async def createchal(ctx: discord.Interaction,
                     name: str,
                     flag: str,
                     message: Optional[str],
                     role_id: Optional[str],
                     file: Optional[str],
                     points: Optional[int],
                     save_chal: Optional[bool]=False
                     ):

    # This should be changed to something else, maybe a env var
    role = discord.utils.get(ctx.guild.roles, name="CTF-EXEC")
    if role not in ctx.user.roles:
        await ctx.response.send_message("User cannot use this command: incorrect permissions")
        return

    if name in client.challenges:
        await ctx.response.send_message("challenge with same id already exists", ephemeral=true)
        return

    name.replace('./', '')
    name.replace('../', '')
    chal = Chal(name, flag, message, role_id, [file], points)
    client.challenges[name] = chal
    if save_chal:
        if chal.save_chal():
            print("saved challenge to challenge directory")
        else:
            print("Error creating the challenge")
            await ctx.response.send_message("Could not create chal".format(name), ephemeral=True)
            return
    await ctx.response.send_message("Successfully Created Challenge: {}".format(name), ephemeral=True)


# TODO: ADD COMMAND TO JUST UPLOAD A YAML FILE
@client.tree.command(name="modify",
                     description=
                     """
                     Command used to modify properties of a challenge. 
                     """
                     )
async def modifychal(ctx: discord.Interaction,
                     name: str,
                     new_name: Optional[str],
                     flag: Optional[str],
                     message: Optional[str],
                     role_id: Optional[str],
                     file: Optional[str],
                     points: Optional[int],
                     attribute_name: Optional[str],
                     attribute_value: Optional[str],
                     save_chal: Optional[bool]=False,
                     append_file: Optional[bool]=False
                     ):
    role = discord.utils.get(ctx.guild.roles, name="CTF-EXEC")
    if role not in ctx.user.roles:
        await ctx.response.send_message("User cannot use this command: incorrect permissions")
        return

    if name not in client.challenges:
        await ctx.response.send_message("Invalid challenge Id: does not exist", ephemeral=True)
        return

    chal = client.challenges[name]

    if new_name is not None:
        new_name.replace('./', '')
        new_name.replace('../', '')
        chal.name = new_name
        client.challenges[name] = None
        client.challenges[new_name] = chal

    if attribute_name is not None:
        chal.attributes[attribute_name] = attribute_value
    if flag is not None:
        chal.flag = flag
    if message is not None:
        chal.description = message
    if role_id is not None:
        chal.role_id = role_id
    if points is not None:
        chal.points = points
    if file is not None:
        if append_files:
            chal.files.append(file)
        else:
            chal.files = [file]
    if save_chal:
        if chal.save_chal():
            print("successfully saved modified challenge")
        else:
            print("Error saving modified challenge")
            await ctx.response.send_message("Could not save chal".format(name), ephemeral=True)
            return
    await ctx.response.send_message("Successfully modified Challenge: {}".format(name), ephemeral=True)


if TESTING_MODE == "1":
    client.run(TEST_TOKEN)
else:
    client.run(TOKEN)
