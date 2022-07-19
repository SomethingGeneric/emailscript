import traceback,os,shutil
from os import listdir
from os.path import isfile
from random import randint

# Pycord
import discord
from discord.ext import commands, tasks

# Kind've discord related
from pretty_help import DefaultMenu, PrettyHelp

# Pip
from imap_tools import MailBox

OWNER_ID = 117445905572954121
LOG_CHANNEL_ID = 973422153095606272
host = "tar.black"
port = 993 # assumes SSL/TLS
email = "matt@tar.black"
password = open(".password").read().strip()
mb_name = "INBOX"

intents = discord.Intents.default()
intents.members = True

# Start event handling and bot creation
bot = commands.Bot(
    command_prefix=commands.when_mentioned,
    description="Something's always fucked",
    intents=intents,
    owner_id=OWNER_ID,
)

helpmenu = DefaultMenu("◀️", "▶️", "❌")
bot.help_command = PrettyHelp(
    no_category="Commands", navigation=helpmenu, color=discord.Colour.blurple()
)


# Startup event
@bot.event
async def on_ready():
    print("Bot go brr")
    cogs_dir = "cogs"
    for extension in [
        f.replace(".py", "") for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))
    ]:
        try:
            bot.load_extension(cogs_dir + "." + extension)
        except Exception as e:
            print(f"Failed to load extension {extension}.")
            traceback.print_exc()
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=" you fuck up."
        )
    )
    email_task.start()


@bot.event
async def on_message(message):
    if message.author != bot.user:
        await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    print("Error in command: " + str(error))
    await ctx.send("Something went sideways: ```" + str(error) + "```")


@bot.command()
async def removecog(ctx, name):
    """Un-load a cog that was loaded by default."""
    if await bot.is_owner(ctx.message.author):
        await ctx.send("Ok, I'll try to disable `" + name + "`")
        try:
            bot.remove_cog(name)
            print("Disabled cog: " + name)
            await ctx.send("Done", "Disabled: `" + name + "`.")
        except Exception as e:
            await ctx.send(
                "Something went wrong: `" + str(e) + "`."
            )
    else:
        await ctx.send("You can't use this.")


@bot.command()
async def ping(ctx):
    await ctx.send("pong")


@bot.command()
async def block_sender(ctx, addr=None):
    if addr is None:
        await ctx.send("```" + open("annoying_senders").read().strip() + "```")
    else:
        with open("annoying_senders", "a+") as f:
            f.write("\n" + addr + "\n")
        await ctx.send("Added `" + addr + "` to the blocked list.")


@bot.command()
async def block_phrase(ctx, phrase=None):
    if phrase is None:
        await ctx.send("```" + open("annoying").read().strip() + "```")
    else:
        with open("annoying", "a+") as f:
            f.write("\n" + phrase + "\n")
        await ctx.send("Added `" + phrase + "` to the blocked list.")


@bot.command()
async def do_clean(ctx):
    await email_clean()


@tasks.loop(seconds=3600.0)
async def email_task():
    if email_task.current_loop != 0:
        await email_clean()


async def email_clean():
    annoying = open("annoying").read().strip().split("\n")
    annoying_senders = open("annoying_senders").read().strip().split("\n")
    email_channel = bot.get_channel(LOG_CHANNEL_ID)
    await email_channel.send("Starting to clean email.")
    deleted_total = 0
    msgs_total = 0
    with MailBox(host).login(email, password, mb_name) as mailbox:
        for msg in mailbox.fetch(reverse=True):
            msgs_total += 1
            print(msg.subject, msg.date_str, msg.from_, msg.uid)
            for phrase in annoying:
                if phrase in msg.subject:
                    mailbox.delete(msg.uid)
                    deleted_total += 1
            for sender in annoying_senders:
                if sender in msg.from_:
                    mailbox.delete(msg.uid)
                    deleted_total += 1
            if not msg.subject.isascii():
                mailbox.delete(msg.uid)
                deleted_total += 1
    if deleted_total != 0:
        await email_channel.send("Total deleted: " + str(deleted_total))
    else:
        await email_channel.send("No messages deleted.")
    await email_channel.send("Total messages scanned: " + str(msgs_total))


@email_task.before_loop
async def before_status_task():
    await bot.wait_until_ready()


bot.run(open(".token").read())
