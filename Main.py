from discord.ext import commands, tasks
import discord
from dataclasses import dataclass
from datetime import datetime, timedelta
import pytz

MAX_SESSION_TIME_MINUTES = 30
CHANNEL_ID = 735326540962725908  # Replace with your actual channel ID
TIMEZONE = pytz.timezone('America/Chicago')  # Replace with your actual timezone

@dataclass
class Session:
    is_active: bool = False
    start_time: datetime = None
    last_reminder_message: discord.Message = None

class SessionCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = Session()
        self.break_reminder.start()

    def cog_unload(self):
        self.break_reminder.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Hello! bot is ready!")
        channel = self.bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send("Yo!")

    @tasks.loop(minutes=MAX_SESSION_TIME_MINUTES)
    async def break_reminder(self):
        channel = self.bot.get_channel(CHANNEL_ID)
        if channel and self.session.is_active:
            if self.session.last_reminder_message:
                await self.session.last_reminder_message.delete()

            reminder_message = await channel.send(
                f'**Take a break!** You\'ve been studying for {MAX_SESSION_TIME_MINUTES} minutes. Use `!time` to check the time remaining.'
            )
            self.session.last_reminder_message = reminder_message

    @commands.command()
    async def start(self, ctx):
        if self.session.is_active:
            await ctx.send("A session is already active!")
        else:
            self.session.is_active = True
            self.session.start_time = datetime.now(TIMEZONE)
            human_readable_time = self.session.start_time.strftime("%H:%M:%S")
            await ctx.send(f'📚 Study session started at {human_readable_time}. Use `!time` to check the time remaining.')

    @commands.command()
    async def end(self, ctx):
        if not self.session.is_active:
            await ctx.send("No session is active!")
            return

        if self.session.last_reminder_message:
            await self.session.last_reminder_message.delete()

        self.session.is_active = False
        end_time = datetime.now(TIMEZONE)
        duration = end_time - self.session.start_time
        await ctx.send(f'🎉 Session ended after {duration}. Great job!')

    @commands.command()
    async def time(self, ctx):
        if not self.session.is_active:
            await ctx.send("No session is currently active.")
        else:
            current_time = datetime.now(TIMEZONE)
            remaining_time = self.session.start_time + timedelta(minutes=MAX_SESSION_TIME_MINUTES) - current_time
            await ctx.send(f'⏰ Time remaining in the current session: {remaining_time}')

    @start.before_invoke
    async def before_start(self, ctx):
        if self.break_reminder.is_running():
            self.break_reminder.stop()

    @end.before_invoke
    async def before_end(self, ctx):
        if self.break_reminder.current_loop == 0:
            return
        if not self.break_reminder.is_running():
            self.break_reminder.start()

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return  # Ignore CommandNotFound errors

def setup(bot):
    bot.add_cog(SessionCommands(bot))
