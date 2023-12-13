from discord.ext import commands
import discord
from dataclasses import dataclass
from datetime import datetime
import pytz
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
TIMEZONE = pytz.timezone('America/Chicago')  # CST timezone

@dataclass
class Session:
    is_active: bool = False
    start_time: int = 0

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
session = Session()

@bot.event
async def on_ready():
    print("Hello! bot is ready!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Yo!")

@bot.command()
async def start(ctx):
    if session.is_active:
        await ctx.send("A session is already active!")
    else:
        session.is_active = True
        session.start_time = datetime.now(TIMEZONE).timestamp()
        human_readable_time = datetime.now(TIMEZONE).strftime("%H:%M:%S")
        await ctx.send(f"Study session started at {human_readable_time}")

@bot.command()
async def end(ctx):  
    if not session.is_active:
        await ctx.send("No session is active!")
        return
    
    session.is_active = False
    end_time = datetime.now(TIMEZONE).timestamp()
    duration = end_time - session.start_time
    await ctx.send(f"Session ended after {duration} seconds")

bot.run(BOT_TOKEN)
