'''
    https://github.com/Rapptz/discord.py/issues/5209#issuecomment-778118150
'''
import platform, asyncio
if platform.system() == 'Windows':
	asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

'''
    IMPORTS
'''
import traceback
import message_manager
import sys, subprocess, os, time, pathlib, json
import discord, inspect, typing
from discord.ext import commands
from discord.ext import tasks
import random
import re

LOCAL_DIRECTORY = pathlib.Path(__file__).parent
ACTIVITY_FILE = LOCAL_DIRECTORY / "active.txt"
API_TOKEN_FILE = LOCAL_DIRECTORY / "api_token.pkey"
ERROR_LOG_DIRECTORY = LOCAL_DIRECTORY / "errors"
MUTE_DIRECTORY = LOCAL_DIRECTORY / "mutes"
REBOOT_MESSAGE_FILE = LOCAL_DIRECTORY / "reboot_data.txt"

'''
    ENSURE THAT THE BOT ISN'T ALREADY RUNNING
'''
try:
    with open(ACTIVITY_FILE, "r") as f:
        contents = f.read()
    if time.time() - float(contents) < 30:
        quit()
except (OSError, ValueError) as e:
    pass # file doesn't exist or is invalid (bot isn't running)

'''
    THE BOT
'''
with open(API_TOKEN_FILE, "r") as file:
    DISCORD_API_TOKEN = file.read()
CMD_PREFIX = ";"

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.members = True

bot = commands.Bot(command_prefix = CMD_PREFIX, chunk_guilds_at_startup = False, intents = intents)

'''
    UTILS
'''
class ChannelGetter:
    def __init__(self, id_):
        self.id_ = id_
        self.channel = None
    
    def __get__(self, obj, objtype = None):
        self.channel = self.channel or bot.get_channel(self.id_)
        return self.channel

class GuildGetter:
    def __init__(self, id_):
        self.id_ = id_
        self.guild = None
    
    def __get__(self, obj, objtype = None):
        self.guild = self.guild or bot.get_guild(self.id_)
        return self.guild

class Channels:
    api_log = ChannelGetter(929589739936436244)
    bot_log = ChannelGetter(914522904690049084)
    suggestions = ChannelGetter(794035889171857438)
    announcements = ChannelGetter(794035592001880064)

class Guilds:
    particle = GuildGetter(777280297422028801)

class Roles:
    owner = 777280631146807378
    developer = 794044687085338624
    moderator = 794044623353937951
    muted = 929590288660463687

class Users:
    uhyeah = 342191494872039424
    okay = 405499157076508672

def color(r, g, b):
    return (r << 16) | (g << 8) | (b)

def get_cmds_embed():
    embed = discord.Embed(color = color(30, 35, 40))
    embed.add_field(name = f"{CMD_PREFIX}cmds", value = "@everyone\nSend this message.", inline = False)
    embed.add_field(name = f"{CMD_PREFIX}ping", value = "@everyone\nReply \"Pong!\" and show bot ping time.", inline = False)
    embed.add_field(name = f"{CMD_PREFIX}mute `user` `time`", value = f"<@&{Roles.moderator}>\nMute `@user` for `time` i.e. `15 minutes` or `1h`.", inline = False)
    embed.add_field(name = f"{CMD_PREFIX}unmute `user`", value = f"<@&{Roles.moderator}>\nUnmute a muted `@user`.", inline = False)
    embed.add_field(name = f"{CMD_PREFIX}reboot `full?`", value = f"<@&{Roles.developer}>\nReboots the bot. Will take up to a minute to start back up.", inline = False)
    embed.add_field(name = f"{CMD_PREFIX}purge `count`", value = f"<@&{Roles.owner}>\nDelete the most recent `count` messages in this channel.", inline = False)
    return embed

async def log_error_to_discord(exc, formatted):
    await Channels.bot_log.send(
        f"<@&{Roles.developer}> An error has occurred. Please view the logs for full traceback.", 
        embed = discord.Embed(
            color = color(250, 88, 70),
            title = exc.__class__.__name__,
            description = "\n".join(map(str, exc.args))
        )
    )

def log_error_to_file(exc, formatted):
    try:
        with open(ERROR_LOG_DIRECTORY / str(time.time()), "w") as file:
            file.write(f"{exc.__class__.__name__} -> {', '.join(map(str, exc.args))}\n\n")
            file.write(formatted)
    except Exception as e:
        print(traceback.format_exc(), file = sys.stderr)

def handle_exceptions(func):
    if asyncio.iscoroutinefunction(func):
        async def decorated(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                formatted = traceback.format_exc()
                
                # it's fine if the discord logger fails
                try:
                    await log_error_to_discord(e, formatted)
                except:
                    pass
                
                # not fine if file logger fails
                log_error_to_file(e, formatted)
    else:
        def decorated(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                formatted = traceback.format_exc()
                
                # not fine if file logger fails
                log_error_to_file(e, formatted)
    
    # make it difficult to see a difference between the functions
    decorated.__name__ = func.__name__
    decorated.__doc__ = func.__doc__
    decorated.__signature__ = inspect.signature(func)
    
    return decorated

PING_RECORDS = {}
def get_next_nonce():
    return random.randint(1_000_000_000, 1_000_000_000_000)

def record_pong_sent(nonce):
    PING_RECORDS[nonce] = time.time()

def check_pong(nonce):
    if nonce in PING_RECORDS:
        time_sent = PING_RECORDS[nonce]
        del PING_RECORDS[nonce]
        return time.time() - time_sent
    else:
        return None

def get_mute_filename(uid):
    return str(uid).casefold().strip()

def is_muted(uid):
    active_mutes = set(os.listdir(MUTE_DIRECTORY)) - {".gitignore"}
    fname = get_mute_filename(uid)
    if fname not in active_mutes:
        return None
    
    with open(MUTE_DIRECTORY / fname, "r") as file:
        return float(file.read()) - time.time()

def log_mute(uid, until):
    with open(MUTE_DIRECTORY / get_mute_filename(uid), "w") as file:
        file.write(str(float(until)))

def remove_mute(uid):
    os.remove(MUTE_DIRECTORY / get_mute_filename(uid))

def format_time(seconds): # 3 days, 4 hours and 5 seconds
    integral, decimal, decimal_magnitude = 0, 0, 0
    past = False
    if isinstance(seconds, str):
        past = seconds.startswith("-")
        if past:
            seconds = seconds[1:]
        
        if "." in seconds:
            [integral, decimal] = seconds.split(".")
            decimal_magnitude = len(decimal)
            integral, decimal = int(integral), int(decimal)
        else:
            integral = int(seconds)
    else:
        past = seconds < 0
        seconds = abs(seconds)
        
        integral, decimal = seconds // 1, seconds % 1
        decimal_magnitude = 0
        while decimal % 1 != 0:
            decimal *= 10
            decimal_magnitude += 1
        decimal = int(decimal)
    
    integral_labels = [
        ["millennium", "millennia", 31_536_000_000],
        ["century", "centuries", 3_153_600_000],
        ["decade", "decades", 315_360_000],
        ["year", "years", 31_536_000],
        ["week", "weeks", 604_800],
        ["day", "days", 86_400],
        ["hour", "hours", 3_600],
        ["minute", "minutes", 60],
        ["second", "seconds", 1]
    ]
    decimal_labels = [
        ["millisecond", "milliseconds", 3],
        ["microsecond", "microseconds", 6],
        ["nanosecond", "nanoseconds", 9]
        # not showing smaller units so that numbers like 123.999999999999999999974 will get rounded
    ]
    decimal_precision = decimal_labels[-1][-1]
    
    if decimal_magnitude > decimal_precision:
        offset_decimal = 10 ** (decimal_magnitude - decimal_precision)
        round_using = decimal % offset_decimal
        if round_using >= offset_decimal * 0.5: # round up
            decimal //= offset_decimal
            decimal += 1 # might have been 999999
            if decimal >= 10 ** (decimal_precision + 1):
                decimal = 0
                decimal_magnitude = 0
                integral += 1
        else: # round down
            decimal //= offset_decimal
        decimal_magnitude = decimal_precision
        
    # remove trailing zeros on decimal
    while decimal % 10 == 0 and decimal_magnitude > 0:
        decimal //= 10
        decimal_magnitude -= 1
    
    if integral == 0 and decimal == 0:
        return "now"
    
    sections = []
    for [singular, plural, period] in integral_labels:
        if integral >= period:
            count = integral // period
            integral %= period
            sections.append("%d %s" % (count, singular if count == 1 else plural))
    
    for i in range(len(decimal_labels)):
        if decimal_magnitude > 0:
            [singular, plural, magnitude] = decimal_labels[i]
            relative_magnitude = magnitude - (0 if i == 0 else decimal_labels[i - 1][-1])
            
            count = 0
            if decimal_magnitude > relative_magnitude:
                count = decimal // 10 ** (decimal_magnitude - relative_magnitude)
            else:
                count = decimal * 10 ** (relative_magnitude - decimal_magnitude)
            
            decimal %= 10 ** (decimal_magnitude - relative_magnitude)
            decimal_magnitude -= relative_magnitude
            
            if count > 0:
                sections.append("%d %s" % (count, singular if count == 1 else plural))
    
    out = ""
    if len(sections) == 1:
        out = sections[0]
    else:
        out = ", ".join(sections[:-1]) + " and " + sections[-1]
    
    if past:
        out += " ago"
    
    return out

'''
    COMMANDS
'''
@bot.command()
@handle_exceptions
async def cmds(ctx):
    await ctx.reply(embed = get_cmds_embed(), mention_author = False)

@bot.command()
@handle_exceptions
async def ping(ctx):
    nonce = get_next_nonce()
    record_pong_sent(nonce)
    
    try:
        await ctx.reply(
            "Pong!",
            embed = discord.Embed(
                title = f"Processing...",
                description = f"This should take less than a second. Nonce: {nonce}"
            ),
            mention_author = False,
            nonce = nonce
        )
    except:
        check_pong(nonce) # delete the record
        raise

time_unit_conversions = {
    "s": 1, "sec": 1, "secs": 1, "second": 1, "seconds": 1,
    "m": 60, "min": 60, "mins": 60, "minute": 60, "minutes": 60,
    "h": 3600, "hr": 3600, "hrs": 3600, "hour": 3600, "hours": 3600,
    "d": 86_400, "day": 86_400, "days": 86_400,
    "month": 2_592_000, "months": 2_592_000,
    "y": 31_536_000, "yr": 31_536_000, "yrs": 31_536_000, "year": 31_536_000, "years": 31_536_000,
    "decade": 315_360_000, "decades": 315_360_000,
    "century": 3_153_600_000, "centuries": 3_153_600_000,
    "millennium": 31_536_000_000, "millennia":  31_536_000_000
}
@bot.command()
@commands.has_role("Moderator")
@handle_exceptions
async def mute(ctx, user: discord.Member, *, period: str):
    period_regex = fr"\s*(\d+(?:\.\d+)?)\s*({'|'.join(sorted(time_unit_conversions.keys(), key=len, reverse=True))})?\s*(.*)\s*"
    period_match = re.match(period_regex, period)
    
    if period_match:
        qty, unit, reason = period_match.groups()
    else:
        qty, unit, reason = '1', 'hours', None
    input_period = ' '.join(str(x) for x in (qty, unit) if x)
    
    if '.' in qty:
        qty = float(qty)
        qty_formatted = f"{qty:,.7f}"
    else:
        qty = int(qty)
        qty_formatted = f"{qty:,d}"
    
    period = qty * time_unit_conversions.get(unit, 60)
    
    # if they're already muted, just up the time
    try:
        remove_mute(user.id)
    except OSError: # they were not already muted
        await user.add_roles(discord.Object(Roles.muted))
    log_mute(user.id, time.time() + period)
    
    reason = reason or "No reason given."
    
    log_mute(user.id, time.time() + period)
    await user.add_roles(discord.Object(Roles.muted))
    
    embed = discord.Embed(
        title="Muted",
        description=f"{user.mention} has been <@&{Roles.muted}> for \"{input_period}\"."
    )
    embed.add_field(
        name="Time",
        value=format_time(period),
        inline=False
    )
    embed.add_field(
        name="Reason",
        value=reason,
        inline=False
    )
    await ctx.reply(
        embed=embed,
        mention_author = False
    )

@bot.command()
@commands.has_role("Moderator")
@handle_exceptions
async def unmute(ctx, user: discord.Member):
    mute_etr = is_muted(user.id)
    if mute_etr is None:
        await ctx.reply(
            f"That person isn't muted.",
            mention_author = False
        )
        return
    mute_etr = round(max(1, mute_etr))
    
    formatted = format_time(mute_etr)
    
    await user.remove_roles(discord.Object(Roles.muted))
    remove_mute(user.id)
    await ctx.reply(
        f"{user.mention} has been unmuted early. They still had {formatted} remaining on their mute.",
        mention_author = False
    )

@bot.command()
@commands.has_role("Developer")
@handle_exceptions
async def reboot(ctx, full: typing.Optional[str]):
    full = isinstance(full, str) and full.casefold() == "full".casefold()
    
    if full:
        next_cron_interval = round(60 - (time.time() % 60))
        if next_cron_interval < 3:
            next_cron_interval = 60
        reboot_message = await ctx.reply(f"Goodbye! I should be back in about {format_time(next_cron_interval + 3)}.", mention_author = False)
    else:
        reboot_message = await ctx.reply("I'll be right back...", mention_author = False)
    
    await bot.close()
    
    try:
        with open(ACTIVITY_FILE, "w") as f:
            f.write("0.0")
    except:
        pass
    
    try:
        with open(REBOOT_MESSAGE_FILE, "w") as file:
            file.write(f"{ctx.channel.id:d} {reboot_message.id:d} {time.time():f}")
    except:
        pass
    
    if not full:
        os.system('/bin/sh -c cd /var/www/particle_bot && python3.9 main.py >> /var/www/particle_bot/bot.log 2>&1 &')

@bot.command()
@commands.has_role("Owner")
@handle_exceptions
async def purge(ctx, message_count: int):
    await ctx.channel.purge(limit = message_count + 1)
    await ctx.channel.send(
        f"{message_count} {'message was' if message_count == 1 else 'messages were'} just purged by {ctx.author.mention}.",
        allowed_mentions = discord.AllowedMentions(users = [])
    )

'''
    EVENTS
'''
@bot.event
async def on_connect():
    try:
        with open(REBOOT_MESSAGE_FILE, "r") as file:
            channel_id, message_id, timestamp = file.read().split()
        
        channel_id = int(channel_id)
        message_id = int(message_id)
        timestamp = float(timestamp)
        
        channel = bot.get_channel(channel_id)
        while not channel:
            await asyncio.sleep(0.1)
            channel = bot.get_channel(channel_id)
        
        await channel.send(
            f"I'm back! It took {time.time() - timestamp:.1f} seconds to reboot.",
            reference = discord.MessageReference(message_id = message_id, channel_id = channel_id, fail_if_not_exists = False),
            mention_author = False
        )
    except:
        pass
    
    try:
        os.remove(REBOOT_MESSAGE_FILE)
    except:
        pass

@bot.event
@handle_exceptions
async def on_message(message):
    # check ping commands
    if message.author == bot.user:
        ping_time = check_pong(message.nonce)
        if ping_time is not None:
            await message.edit(
                content = f"Pong!",
                embed = discord.Embed(
                    title = f"Ping Time: {ping_time * 1000:.0f} ms",
                    description = f"It took {ping_time * 1000:.0f} milliseconds for this message to reach Discord's servers, be processed, and return to my servers."
                )
            )
        
        return
    
    if message.author.bot:
        return
    
    if message.channel == Channels.suggestions:
        await message.add_reaction("\N{Thumbs Up Sign}")
        await message.add_reaction("\N{Thumbs Down Sign}")
        return
    
    if message.channel == Channels.announcements:
        await message.add_reaction("\N{Thumbs Up Sign}")
        return
    
    if message.content.startswith(CMD_PREFIX):
        await bot.process_commands(message)
        return

    if f"<@{bot.user.id}>" in message.content or f"<@!{bot.user.id}>" in message.content: # not using message.mentions because that includes reply pings
        await message.channel.send(
            f"Hi {message.author.mention}! My prefix is `{CMD_PREFIX}`, try sending `{CMD_PREFIX}cmds` to see what I can do.",
            reference = message,
            mention_author = True
        )
        return

@bot.event
@handle_exceptions
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply(
            f"Invalid command. Try sending `{CMD_PREFIX}cmds` to see the allowed commands.",
            mention_author = False
        )
        return
    
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply(
            f"You don't have permission to use that command! Try sending `{CMD_PREFIX}cmds` to see what the requirements are.",
            mention_author = False
        )
        return
        
    await ctx.reply(
        "An error has occurred while processing that command.",
        embed = discord.Embed(
            title = error.__class__.__name__,
            description = " ".join(error.args),
            color = color(250, 88, 70)
        ),
        mention_author = False
    )

'''
    LOGGING/TASKS
'''

# write the current time to file, and ensure that no instance of the bot is currently running
last_logged_active_value = None
@tasks.loop(seconds = 1)
@handle_exceptions
async def activity_logger():
    global last_logged_active_value
    
    try:
        if last_logged_active_value is not None:
            with open(ACTIVITY_FILE, "r") as f:
                assert last_logged_active_value == f.read(), "Another bot has overwritten the activity file."
            
        with open(ACTIVITY_FILE, "w") as f:
            last_logged_active_value = str(time.time())
            f.write(last_logged_active_value)
        
    except Exception as e:
        # just log out and allow another instance to start up
        # that's a better solution than allowing multiple instances to exist
        await bot.close()

@tasks.loop(seconds = 1)
@handle_exceptions
async def message_logger():
    if not all((Channels.api_log, Channels.bot_log)):
        return

    # get next message
    message, ts, fname = message_manager.pop()
    if message is None:
        return
    
    # send the message
    embed, ping = message_manager.get_message_embed(message)
    await Channels.api_log.send(
        f"<@!{Roles.developer}>\n" * ping + f"<t:{ts:.0f}:D> at <t:{ts:.0f}:T> (<t:{ts:.0f}:R>)",
        embed = embed
    )
    
    message_manager.done_processing(fname)

@tasks.loop(seconds = 1)
@handle_exceptions
async def unmute_checker():
    if not all((Channels.bot_log, Guilds.particle)):
        return

    # list all messages in queue
    mutes = set(os.listdir(MUTE_DIRECTORY)) - {".gitignore"}
    
    for mute in mutes:
        etr = is_muted(mute)
        if etr is None or etr > 0:
            continue
        
        member = Guilds.particle.get_member(int(mute)) or await Guilds.particle.fetch_member(int(mute))
        
        if member is not None:
            await member.remove_roles(discord.Object(Roles.muted))
            remove_mute(mute)
            await Channels.bot_log.send(f"<@!{mute}> has been unmuted.")
        else:
            remove_mute(mute)
            await Channels.bot_log.send(
                f"<@&{Roles.moderator}>\nFailed to unmute <@!{mute}>, perhaps they left the server? "
                f"If not, then please manually `{CMD_PREFIX}unmute` them."
            )

# TODO: make cool status?
@tasks.loop(minutes = 10)
@handle_exceptions
async def status_setter():
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.playing, name = "HTTPS://A4G4.COM"))

@bot.event
async def on_ready():
    await bot.wait_until_ready()
    
    unmute_checker.start()
    message_logger.start()
    status_setter.start()

'''
    RUN
'''
@handle_exceptions
def main():
    activity_logger.start()
    bot.run(DISCORD_API_TOKEN)

main()