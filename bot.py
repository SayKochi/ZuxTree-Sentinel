import nextcord
from nextcord.ext import commands
import os
import uvicorn
from fastapi import FastAPI, Request
from datetime import datetime
import asyncio
import json

# --- [ ZUXTREE SENTINEL v3.0 ] ---
# Configuration loaded from environment variables (HEROKU Config Vars)
TOKEN = os.getenv("DISCORD_TOKEN")
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0"))
PREFIX = "!"

# 1. BOT SETUP
intents = nextcord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# 2. FASTAPI SETUP (The Logic Bridge for Lua)
app = FastAPI()

@bot.event
async def on_ready():
    print(f"✅ [SYSTEM] ZuxTree Sentinel is LIVE: {bot.user}")
    activity = nextcord.Activity(type=nextcord.ActivityType.watching, name="ZuxTree Users 👑")
    await bot.change_presence(activity=activity)

@app.post("/log")
async def handle_lua_log(request: Request):
    try:
        data = await request.json()
        # Data expected: { uid, username, world, action, hwid }
        uid = data.get("uid", "Unknown")
        user = data.get("username", "Guest")
        world = data.get("world", "N/A")
        action = data.get("action", "Executing Script")
        hwid = data.get("hwid", "Unknown")
        
        channel = bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            embed = nextcord.Embed(
                title="🛡️ LIVE ACTIVITY FEED",
                description=f"User **{user}** is active!",
                color=0xc0392b,
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url="https://bkohyhwdcszazytvtlri.supabase.co/storage/v1/object/public/global_config/z_shield.png")
            embed.add_field(name="🧬 UID", value=f"`{uid}`", inline=False)
            embed.add_field(name="🌍 World", value=f"**{world}**", inline=True)
            embed.add_field(name="🤖 Status", value=f"**{action}**", inline=True)
            embed.add_field(name="💻 HWID", value=f"`{hwid[:20]}`", inline=False)
            embed.set_footer(text="ZUXTREE ULTIMATE GATEWAY", icon_url=bot.user.avatar.url if bot.user.avatar else None)
            
            # Send message asynchronously to Discord
            bot.loop.create_task(channel.send(embed=embed))
            
        return {"status": "success", "message": "Log broadcasted to Discord"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"🏓 Pong! Latency: **{round(bot.latency * 1000)}ms**")

@bot.command(name="users")
async def users(ctx):
    # This can be expanded to fetch live data from Neon/Supabase later
    await ctx.send("📊 **System Syncing...** Monitoring all ZuxTree entry points.")

@app.get("/")
def home():
    return {"status": "online", "app": "ZuxTree Bridge API"}

# --- [ SERVER RUNNER ] ---
if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Run Uvicorn (Web API) and Bot simultaneously
    port = int(os.getenv("PORT", 8000))
    config = uvicorn.Config(app=app, host="0.0.0.0", port=port, loop="asyncio")
    server = uvicorn.Server(config)
    
    loop.create_task(server.serve())
    bot.run(TOKEN)
