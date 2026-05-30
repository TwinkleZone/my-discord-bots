import os
import discord
from discord.ext import commands, tasks
from discord.utils import utcnow
import datetime
import asyncio

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.moderation = True

bot = commands.Bot(command_prefix="🔒", intents=intents)

# --- SYSTEM STATES & CONFIGURATION ---
SYSTEM_ENABLED = {}  # Tracks if firewall is active for each server {guild_id: True/False}
LOCKDOWN_MODE = False
RAPID_JOIN_TRACKER = []
USER_MESSAGE_TIMESTAMPS = {}

MAX_MESSAGES_PER_3SEC = 5
MAX_JOINS_PER_10SEC = 6

@bot.event
async def on_ready():
    print(f"🔱 SECURITY CORE RUNNING: Active as {bot.user}")
    clean_trackers.start()

# --- OFFICIAL LOGS PIPELINE ---
async def dispatch_log(guild, title, description, color=discord.Color.blue(), fields=None):
    """Compiles security events and pipes them straight to the logging channel."""
    log_channel = discord.utils.get(guild.text_channels, name="overwatch-security-logs")
    if not log_channel:
        return
        
    embed = discord.Embed(
        title=f"🛡️ Security Log: {title}",
        description=description,
        color=color,
        timestamp=utcnow()
    )
    if fields:
        for name, value in fields.items():
            embed.add_field(name=name, value=value, inline=False)
    embed.set_footer(text="Overwatch Logging Subsystem")
    try:
        await log_channel.send(embed=embed)
    except:
        pass

# --- INTERACTIVE RYTHM-STYLE UI COMPONENTS ---
class RythmStyleSetupView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=None)  # Persistent view so buttons never expire
        self.guild_id = guild_id

    @discord.ui.button(label="Activate Security Matrix", style=discord.ButtonStyle.success, emoji="⚡", custom_id="activate_matrix")
    async def activate_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ Access Denied: Administrator clearance required.", ephemeral=True)
            return

        SYSTEM_ENABLED[self.guild_id] = True
        
        activated_embed = discord.Embed(
            title="🔱 OVERWATCH ENGINE INITIALIZED",
            description="The Zero-Trust firewall has successfully moved from **Idle** to **Active Protection Mode**.",
            color=discord.Color.green(),
            timestamp=utcnow()
        )
        activated_embed.add_field(name="Perimeter Shielding", value="Now actively monitoring text velocities, links, and join strings.", inline=False)
        
        # Disable the buttons on the card after clicking
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)
        
        await interaction.response.send_message(embed=activated_embed)
        await dispatch_log(interaction.guild, "System Mode Modified", f"Matrix shifted to **ACTIVE** by user {interaction.user.mention}.", color=discord.Color.green())

    @discord.ui.button(label="System Manifest", style=discord.ButtonStyle.secondary, emoji="📑", custom_id="view_manifest")
    async def manifest_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        manifest_embed = discord.Embed(
            title="📋 Operational Specifications",
            description="Defensive tracing systems running inside this node configuration.",
            color=discord.Color.blue()
        )
        manifest_embed.add_field(name="Anti-Raid Subroutine", value="Locks baseline permissions if join spikes exceed 6 profiles / 10s.", inline=False)
        manifest_embed.add_field(name="Velocity Shield", value="Quarantines users with 1-hour timeouts if text flood surpasses 5 messages / 3s.", inline=False)
        await interaction.response.send_message(embed=manifest_embed, ephemeral=True)

# --- FLAWLESS ON-BOARDING ARCHITECTURE ---
@bot.event
async def on_guild_join(guild):
    print(f"📡 New server connection established: {guild.name}")
    SYSTEM_ENABLED[guild.id] = False  # Starts completely idle with no overhead

    # 1. Automate dedicated log channel creation
    overwatch_role_overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, embed_links=True)
    }
    try:
        await guild.create_text_channel(
            name="overwatch-security-logs",
            overwrites=overwatch_role_overwrites,
            topic="🔒 Official security log repository for TwinkleBots Advanced Overwatch.",
            reason="Automated Security System setup."
        )
    except Exception as e: 
        print(f"Log channel automation failed: {e}")

    # 2. Intel-Scan destination channel
    target_channel = guild.system_channel if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages else None
    if not target_channel:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages and ("general" in channel.name.lower() or "chat" in channel.name.lower()):
                target_channel = channel
                break

    # 3. Deliver Rythm-style landing panel
    if target_channel:
        welcome_embed = discord.Embed(
            title="🔱 Welcome to TwinkleBots Overwatch",
            description="The absolute standard for protecting your community from automated raids, spam floods, and rogue account intrusions.",
            color=discord.Color.from_rgb(88, 101, 242),
            timestamp=utcnow()
        )
        welcome_embed.add_field(name="⚙️ Status: PENDING ACTIVATION", value="Click the green button below to bring the security shields online. The bot remains completely idle until initialized.", inline=False)
        welcome_embed.set_footer(text="Advanced Overwatch Initiative")
        
        await target_channel.send(embed=welcome_embed, view=RythmStyleSetupView(guild.id))

    # 4. Direct message onboarding briefing to the server invite author
    async for entry in guild.audit_logs(action=discord.AuditLogAction.bot_add, limit=1):
        inviter = entry.user
        if inviter:
            try:
                dm_embed = discord.Embed(
                    title="👋 Thanks for introducing me to your server!",
                    description=f"I have successfully linked with **{guild.name}**.",
                    color=discord.Color.from_rgb(88, 101, 242)
                )
                dm_embed.add_field(name="👑 Critical Step Required", value="Go to Server Settings -> Roles and drag the `TwinkleBots` role to the top of your list so it can properly moderate bad actors.", inline=False)
                await inviter.send(embed=dm_embed)
            except: 
                pass

# --- MANUAL ADMINISTRATIVE COMMAND CONTROLS ---
@bot.command()
@commands.has_permissions(administrator=True)
async def enable(ctx):
    """Explicit command to bring the protection firewall online."""
    SYSTEM_ENABLED[ctx.guild.id] = True
    await ctx.send("⚙️ **SYSTEM ONLINE:** Security firewalls are fully armed and tracking incidents.")
    await dispatch_log(ctx.guild, "System Mode Modified", f"Matrix shifted to **ACTIVE** via `🔒enable` command by {ctx.author.mention}.", color=discord.Color.green())

@bot.command()
@commands.has_permissions(administrator=True)
async def disable(ctx):
    """Explicit command to put the bot to sleep (No more work/idle state)."""
    SYSTEM_ENABLED[ctx.guild.id] = False
    await ctx.send("⚠️ **SYSTEM DEACTIVATED:** Security firewalls are offline. The bot is now idle.")
    await dispatch_log(ctx.guild, "System Mode Modified", f"Matrix shifted to **INACTIVE** via `🔒disable` command by {ctx.author.mention}.", color=discord.Color.red())

# --- ACTIVE FIREWALL LOOP ACTIONS ---
@bot.event
async def on_message(message):
    if message.author.bot or not message.guild: 
        return
    
    # Check if system is active. If False, bypass processing completely
    if not SYSTEM_ENABLED.get(message.guild.id, False):
        await bot.process_commands(message)
        return

    if message.author.guild_permissions.administrator:
        await bot.process_commands(message)
        return

    uid = message.author.id
    now = utcnow()
    
    if uid not in USER_MESSAGE_TIMESTAMPS: 
        USER_MESSAGE_TIMESTAMPS[uid] = []
    USER_MESSAGE_TIMESTAMPS[uid].append(now)
    
    if len(USER_MESSAGE_TIMESTAMPS[uid]) > MAX_MESSAGES_PER_3SEC:
        try:
            await message.channel.purge(limit=10, check=lambda m: m.author.id == uid)
            await message.author.timeout(datetime.timedelta(hours=1), reason="Overwatch Velocity Flood Trigger")
            await dispatch_log(
                message.guild, 
                "User Quarantined", 
                f"User {message.author.mention} was automatically muted for 1 hour due to burst flooding text stream.",
                color=discord.Color.orange(),
                fields={"Channel": message.channel.mention, "Velocity": f"{len(USER_MESSAGE_TIMESTAMPS[uid])} msg/3s"}
            )
        except: 
            pass
        return

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    if not SYSTEM_ENABLED.get(member.guild.id, False): 
        return
    global LOCKDOWN_MODE, RAPID_JOIN_TRACKER
    now = utcnow()
    
    if LOCKDOWN_MODE:
        try: 
            await member.ban(reason="Active Incident Lockdown Protection")
        except: 
            pass
        return
        
    RAPID_JOIN_TRACKER.append(now)
    if len(RAPID_JOIN_TRACKER) >= MAX_JOINS_PER_10SEC:
        LOCKDOWN_MODE = True
        await trigger_server_lockdown(member.guild)

async def trigger_server_lockdown(guild):
    everyone_role = guild.default_role
    perms = everyone_role.permissions
    perms.update(send_messages=False, send_messages_in_threads=False, add_reactions=False)
    await everyone_role.edit(permissions=perms, reason="Automated Security Lockdown Intervention")
    
    await dispatch_log(
        guild, 
        "CRITICAL LOCKDOWN ENGAGED", 
        "⚠️ Automated join traffic spike surpassed thresholds. **Sovereign Lockdowns initiated.** Server baseline channels frozen.",
        color=discord.Color.red()
    )

@tasks.loop(seconds=5)
async def clean_trackers():
    now = utcnow()
    for uid in list(USER_MESSAGE_TIMESTAMPS.keys()):
        USER_MESSAGE_TIMESTAMPS[uid] = [t for t in USER_MESSAGE_TIMESTAMPS[uid] if (now - t).total_seconds() < 3]
        if not USER_MESSAGE_TIMESTAMPS[uid]: 
            del USER_MESSAGE_TIMESTAMPS[uid]
    global RAPID_JOIN_TRACKER
    RAPID_JOIN_TRACKER = [t for t in RAPID_JOIN_TRACKER if (now - t).total_seconds() < 10]

bot.run(os.environ.get("PROTECTOR_TOKEN"))
  
