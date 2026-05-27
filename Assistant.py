import discord
from discord.ext import commands
import asyncio
import aiohttp
from collections import deque
from datetime import datetime

# --- SSL SHIELD FOR ANDROID ---
async def custom_start(*args, **kwargs):
    connector = aiohttp.TCPConnector(ssl=False)
    bot.http.connector = connector
    await bot.login(bot.http.token)
    await bot.connect()

intents = discord.Intents.default()
intents.messages = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Server protective queue systems
message_queue = deque()
is_processing = False

async def process_queue():
    global is_processing
    while message_queue:
        is_processing = True
        msg, question = message_queue.popleft()
        
        async with msg.channel.typing():
            try:
                user_name = msg.author.name.lower()
                
                # Stable Chat Engine
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
                
                system_prompt = (
                    f"You are TA, a witty, cool AI assistant bot built by twinkleiszone. "
                    f"You are talking to {msg.author.name} inside a Discord channel. "
                )
                if user_name == "twinkleiszone":
                    system_prompt += "twinkleiszone is your master and creator. Call them Boss, show maximum respect, and be helpful!"
                else:
                    system_prompt += "If anyone asks who made you, proudly say that twinkleiszone is your master."

                payload = {"contents": [{"parts": [{"text": f"{system_prompt}\n\nUser Question: {question}"}]}]}
                
                async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                    async with session.post(url, headers={"Content-Type": "application/json"}, json=payload, params={"key": GEMINI_API_KEY}) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            ai_reply = data['candidates'][0]['content']['parts'][0]['text']
                            
                            if len(str(ai_reply)) > 1900:
                                ai_reply = ai_reply[:1900] + "... [Truncated]"
                            
                            # --- 👑 THE ORIGINAL MAIN CORE TITLE BAR LAYOUT 👑 ---
                            embed = discord.Embed(
                                description=ai_reply,
                                # Signature Gold border for you, Discord Blurple for members
                                color=discord.Color.from_rgb(255, 215, 0) if user_name == "twinkleiszone" else discord.Color.from_rgb(114, 137, 218),
                                timestamp=datetime.utcnow()
                            )
                            
                            # Dynamically fetch avatars to link with the title block
                            bot_avatar = str(bot.user.avatar_url_as(format="png")) if bot.user.avatar else None
                            author_avatar = str(msg.author.avatar_url_as(format="png")) if msg.author.avatar else None
                            
                            # Sets the header title bar cleanly with the profile icon
                            embed.set_author(name="TA MAIN AI CORE", icon_url=bot_avatar)
                            
                            # Custom footer authorization tag layout
                            footer_text = f"👑 Creator Access: twinkleiszone" if user_name == "twinkleiszone" else f"Requested by {msg.author.name}"
                            embed.set_footer(text=footer_text, icon_url=author_avatar)
                            
                            await msg.reply(embed=embed)
                        else:
                            await msg.reply("⚠️ AI is busy dealing with server traffic. Hold on!")
            except Exception as e:
                print(f"Queue Run Error: {e}")
                await msg.reply(f"❌ `SYSTEM ERROR:` {e}")
        
        # Protective server delay pacing
        await asyncio.sleep(2) 
    is_processing = False

@bot.event
async def on_ready():
    print(f"==========================================")
    print(f"🚀 TA EMBED ENGINE ACTIVE!")
    print(f"👑 Titled Visual Styles Fully Restored.")
    print(f"==========================================")

@bot.event
async def on_message(message):
    if message.author.bot or not message.content.lower().startswith("ta "):
        return

    question = message.content[3:].strip()
    user_name = message.author.name.lower()
    
    # Fast-blocking image scanner to prevent API flooding
    is_image = any(t in question.lower() for t in ["draw", "image", "picture", "paint"])
    if is_image:
        embed = discord.Embed(
            description="❌ Image generation is disabled to keep the text core running fast!",
            color=discord.Color.from_rgb(255, 215, 0) if user_name == "twinkleiszone" else discord.Color.from_rgb(114, 137, 218),
            timestamp=datetime.utcnow()
        )
        bot_avatar = str(bot.user.avatar_url_as(format="png")) if bot.user.avatar else None
        author_avatar = str(message.author.avatar_url_as(format="png")) if message.author.avatar else None
        
        embed.set_author(name="TA MAIN AI CORE", icon_url=bot_avatar)
        footer_text = f"👑 Creator Access: twinkleiszone" if user_name == "twinkleiszone" else f"Requested by {message.author.name}"
        embed.set_footer(text=footer_text, icon_url=author_avatar)
        await message.reply(embed=embed)
        return

    message_queue.append((message, question))
    if not is_processing:
        await process_queue()

# =========================================================
# ⚙️ DROP YOUR KEYS HERE! (SCROLL TO THE VERY BOTTOM)
# =========================================================
GEMINI_API_KEY = ""
DISCORD_BOT_TOKEN = ""

bot.http.token = DISCORD_BOT_TOKEN
bot.loop.run_until_complete(custom_start())
          
