import pathlib

LOCAL_DIRECTORY = pathlib.Path(__file__).parent
MESSAGE_QUEUE_DIRECTORY = LOCAL_DIRECTORY / "message_queue"
MESSAGE_PROCESSING_DIRECTORY = LOCAL_DIRECTORY / "messages_processing"

import json
import os
import random
import time

try:
    import discord
except ImportError as e:
    discord = None

def color(r, g, b):
    return (r << 16) | (g << 8) | (b)

type_colors = {
    'user_injection': color(255, 255, 255),
    'user_first_injection': color(255, 255, 255),
    
    'session_open': color(255, 255, 255),
    'session_close': color(0, 0, 0),
    
    'site_view': color(255, 255, 255),
    
    'log_error': color(250, 88, 70),
    
    
    
    'login': color(255, 255, 255),
}
known_types = type_colors.keys()

def get_new_message_filename():
    now = time.time()
    try_prevent_duplicate = random.randint(0, 999_999_999)
    return f"{now:.14f}_{try_prevent_duplicate:09d}" 

def parse_message_filename(fname):
    return float(fname.split("_")[0])

def get_message_embed(msg):
    if discord is None:
        raise NotImplementedError("Discord.py is not installed.")
    
    embed = discord.Embed()
    ping = False
    
    if ("user" in msg) or ("session" in msg):
        user = msg.get("user")
        session = msg.get("session")
        
        if user and session:
            embed.description = f"**[{session['platform'].upper()}]**\n**{'(PAID) ' if user['subscribed'] else ''}[User {user['id']}]({user['link']}):** [Stripe Customer]({user['stripe_link']}), [Session: `{session['id'][:8]}`]({session['link']})"
        elif user:
            embed.description = f"**{'(PAID) ' if user['subscribed'] else ''}[User {user['id']}]({user['link']}):** [Stripe Customer]({user['stripe_link']})"
        else: # session
            embed.description = f"**[{session['platform'].upper()}]** **[User {user['id']}]({user['link']})** [Session: `{session['id'][:8]}`]({session['link']})"
    
    t = msg["type"]
    if t in known_types:
        embed.color = type_colors[t]
    
    if t in ("user_injection", "user_first_injection"):
        embed.title = "User Injected" if t == "user_injection" else "User First Injection"
    elif t == "log_error":
        embed.title = f"ERROR [{msg.get('code', 0):X}-{msg.get('uuid', '*UNKNOWN*')}]"
        embed.add_field(
            name = 'Description',
            value = msg.get('description', '*UNKNOWN*'),
            inline = False
        )
        embed.add_field(
            name = 'Message',
            value = msg.get('message', '*UNKNOWN*'),
            inline = False
        )
    elif t == "session_open":
        embed.title = f"Session Opened (login)"
        embed.add_field(
            name = "Session Id",
            value = f"session_{msg.get('session_id', 'unknown')}",
            inline = False
        )
    elif t == "session_close":
        embed.title = f"Session Closed (logout)"
        
        seconds = msg.get("length", 0)
        embed.add_field(
            name = "Time Spent Injected",
            value = f"{int(seconds / 3600):02d}:{int((seconds / 60) % 60):02d}:{int(seconds % 60):02d}",
            inline = True
        )
        embed.add_field(
            name = "Session Id",
            value = f"session_{msg.get('session_id', 'unknown')}",
            inline = True
        )
    elif t == "login":
        embed.title = "User Login"
    else:
        return discord.Embed(
            title = f"Unknown Message Type `{t}`",
            description = json.dumps(msg, indent = 2),
            color = color(250, 88, 70)
        ), True
    
    if 'ip' in msg:
        embed.set_footer(text = f"IP ADDRESS: {msg['ip']}")
    
    return embed, ping

def pop():
    messages = set(os.listdir(MESSAGE_QUEUE_DIRECTORY)) - {".gitignore"}
    if len(messages) == 0:
        return None, None, None
    
    # get the oldest one (which should be sent first)
    message_timestamp, message_filename = min((parse_message_filename(fname), fname) for fname in messages)
    with open(MESSAGE_QUEUE_DIRECTORY / message_filename, "r") as file:
        message = json.load(file)
    
    # move file into processing queue
    # if an error occurs while sending the message,
    # the message will get stuck here and never be deleted
    # or tried to be re-sent
    os.rename(
        MESSAGE_QUEUE_DIRECTORY / message_filename,
        MESSAGE_PROCESSING_DIRECTORY / message_filename
    )
    
    return message, message_timestamp, message_filename

def done_processing(message_filename):
    os.remove(MESSAGE_PROCESSING_DIRECTORY / message_filename)

def send_message(message_type, **kwargs):
    message = dict(
        **{"type": message_type},
        **kwargs
    )
    
    fname = MESSAGE_QUEUE_DIRECTORY / get_new_message_filename()
    with open(fname, "w") as file:
        json.dump(message, file)
    
    return fname