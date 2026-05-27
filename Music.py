import discord
from discord.ext import commands
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import asyncio

# --- TWINKLE MUSIC CONFIGURATION ---
SPOTIFY_ID = "fd7935bcefb449d4af624151e9412a69"
SPOTIFY_SECRET = "5a29d25806b740c0b0f2d68051aaf645"
DISCORD_TOKEN = "MTUwODg3NjM4NTIxMTM4Mzg4OQ.GFISIi.ROY8wmC7uRuzMPmfKH44LAKbzvNGuKzZ-kBefM"

# --- SYSTEM SETUP ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Connect securely to Spotify API
auth_manager = SpotifyClientCredentials(client_id=SPOTIFY_ID, client_secret=SPOTIFY_SECRET)
sp = spotipy.Spotify(auth_manager=auth_manager)

@bot.event
async def on_ready():
    print(f"=====================================")
    print(f" SYSTEM ONLINE: TwinkleMusic (TM)    ")
    print(f" Logged in as: {bot.user.name}       ")
    print(f"=====================================")

@bot.command(name="play")
async def play(ctx, *, search_query: str = None):
    """Advanced search command to pull track data directly from Spotify."""
    if not search_query:
        await ctx.send("❌ **TwinkleMusic Error:** Please specify a song name! Example: `!play Stay`")
        return

    status_msg = await ctx.send(f"🔍 **TwinkleMusic** is digging into Spotify for: `{search_query}`...")

    try:
        # Run API request asynchronously to prevent Discord bot lag
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, 
            lambda: sp.search(q=search_query, limit=1, type='track')
        )
        
        tracks = results.get('tracks', {}).get('items', [])
        
        if not tracks:
            await status_msg.edit(content=f"❌ **TwinkleMusic:** No track matches found for `{search_query}`.")
            return
            
        # Parse out data points flawlessly
        track = tracks[0]
        track_name = track.get('name', 'Unknown Track')
        artist_name = track['artists'][0].get('name', 'Unknown Artist')
        track_url = track.get('external_urls', {}).get('spotify', '')
        album_name = track.get('album', {}).get('name', 'Single')
        
        if not track_url:
            await status_msg.edit(content="❌ **TwinkleMusic Error:** Link extraction failed for this song.")
            return

        # Return a premium, clean layout message
        response = (
            f"🎵 **TwinkleMusic (TM) Track Found!**\n\n"
            f"**• Title:** {track_name}\n"
            f"**• Artist:** {artist_name}\n"
            f"**• Album:** {album_name}\n"
            f"🔗 **Spotify Link:** {track_url}"
        )
        
        await status_msg.edit(content=response)
        
    except Exception as e:
        await status_msg.edit(content=f"⚠️ **TwinkleMusic API Exception:** `{str(e)}`")

@bot.event
async def on_command_error(ctx, error):
    """Safety net to catch typing bugs."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ **TwinkleMusic:** Command missing arguments.")
    else:
        print(f"TM Runtime Log: {error}")

bot.run(DISCORD_TOKEN)

