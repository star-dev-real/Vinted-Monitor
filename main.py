import discord
from discord.ext import commands, tasks
import aiohttp
from discord.ext.commands import hybrid_command
from discord import app_commands
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from discord.ui import View, Button
from datetime import datetime

intents = discord.Intents(
    guilds=True,
    members=True,
    bans=True,
    emojis=True,
    integrations=True,
    webhooks=True,
    invites=True,
    voice_states=True,
    presences=True,
    messages=True,
    reactions=True,
    typing=True,
    message_content=True
)

bot = commands.Bot(command_prefix="!", intents=intents)

OWNERS_ID = [1365771505924964435, 1389686787412328729]

def dc_view(label, url):
    view = View()
    if url:
        button = Button(label=label, url=url)
        view.add_item(button)
    return view

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

    post_listing.start()
    post_specific.start()
    post_shoes.start()

@bot.hybrid_command(name="genkeys", description="Generate keys via the Flask API")
@app_commands.describe(amount="How many keys to generate?")
async def generate_keys(ctx: commands.Context, amount: int):
    try:
        await ctx.defer()

        headers = {"Content-Type": "application/json"}
        payload = {"amount": amount}

        async with aiohttp.ClientSession() as session:
            async with session.post("https://stardevreal.pythonanywhere.com/generate/secret/keys/api/v1", json=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    keys = data["generated_keys"]
                    formatted_keys = "\n".join(f"`{key}`" for key in keys)

                    await ctx.followup.send(f"✅ Successfully generated `{len(keys)}` key(s):\n{formatted_keys}")
                else:
                    error = await response.text()
                    await ctx.followup.send(f"❌ Failed with status {response.status}: {error}")
    except Exception as e:
        await ctx.followup.send(f"❌ Exception occurred: {str(e)}")



@bot.hybrid_command(name="getkey", description="Returns a key for a user")
async def getkey(
    ctx: commands.Context
):
    if ctx.author.id not in OWNERS_ID:
        return await ctx.interaction.response.send_message("❌ Only owners can use this command.", ephemeral=True)
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("https://stardevreal.pythonanywhere.com/get/key/api/v1") as response:
                if response.status == 200:
                    data = response.json()
                    await ctx.send(f"✅ Successfully got key!\nKey: ```{data.get("key", "Error")}")
                else:
                    error = await response.text()
                    await ctx.send(f"❌ Failed with status {response.status}: {error}")
    except Exception as e:
        error = await response.text()
        await ctx.send(f"❌ Error: {str(e)}")

def send_email(sender_email, sender_password, recipient_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["from"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  
            server.login(sender_email, sender_password)
            server.send_message(msg)

    except:
        pass

@bot.hybrid_command(name="respond", description="Respond to someone's contact.")
@app_commands.describe(
    email="The user's email",
    message="Your response/message to send the user"
)
async def send_response(
    ctx: commands.Context, 
    email: str,
    message: str
):
    if ctx.author.id not in OWNERS_ID:
        return await ctx.interaction.response.send_message("❌ Only owners can use this command.", ephemeral=True) 

    try:
        send_email(
            sender_email="starfnofficial@gmail.com",
            sender_password="ehjd myrv torp aodg",  
            recipient_email=email,
            subject="Thank you for contacting us!",
            body=message
        )
        await ctx.send(f"✅ Successfully sent email to `{email}`")
    except Exception as e:
        await ctx.send(f"❌ Failed to send email: `{str(e)}`")


@bot.hybrid_command(name="editnews", description="Edit a specific news slot on the website")
@discord.app_commands.describe(
    slot="News slot to update (1 = top, 2 = middle, 3 = bottom)",
    date="The date to show (e.g. July 4, 2025)",
    title="The title of the news post",
    content="Use | to split lines (e.g. Line 1|Line 2|Line 3)",
    contact_link="Optional link to contact page"
)
async def editnews(
    ctx: commands.Context,
    slot: int,
    date: str,
    title: str,
    content: str,
    contact_link: str = None
):
    await ctx.defer()

    if slot < 1 or slot > 3:
        await ctx.send("❌ Slot must be 1, 2, or 3.")
        return

    payload = {
        "slot": slot,
        "date": date,
        "title": title,
        "content": content
    }

    if contact_link:
        payload["contact_link"] = contact_link

    url = "http://stardevreal.pythonanywhere.com/api/change/news/content/secret/api" 
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status == 200:
                    await ctx.send(f"✅ News slot {slot} updated successfully!")
                else:
                    error = await resp.text()
                    await ctx.send(f"❌ Failed with status {resp.status}: {error}")
                    return
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

@bot.hybrid_command(name="fakelisting", description="Make a fake listing to troll someone")
@app_commands.describe(
    username="The person's name",
    title="The title of the product",
    image="The image of the product",
    profile_pic="The person's profile picture",
    desc="The description of the item",
    brand="The brand of the item",
    size="The size of the item",
    condition="The condition of the item",
    price="The price of the item",
    created="The day it was listed (e.g. '2025-07-07')"
)
async def fakelisting(
    ctx: commands.Context,
    username: str,
    title: str,
    image: str,
    profile_pic: str,
    desc: str,
    brand: str,
    size: str,
    condition: str,
    price: str,
    created: str
):
    if ctx.author.id not in OWNERS_ID:
        await ctx.interaction.response.send_message("❌ Only owners can use this command.", ephemeral=True)
        return

    channel = bot.get_channel(1391837082032410719)
    if channel is None:
        await ctx.send("⚠️ Channel not found.")
        return

    view = dc_view("💳 Buy", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")

    embed = discord.Embed(
        title=title,
        description=desc,
        color=0x1b00eb
    )
    embed.add_field(name="📑 Brand", value=brand, inline=True)
    embed.add_field(name="📏 Size", value=size, inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    embed.add_field(name="🧼 Condition", value=condition, inline=True)
    embed.add_field(name="💰 Price", value=price, inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    embed.add_field(name="✨ Feedbacks", value="⭐⭐⭐⭐⭐ (0)", inline=True)
    embed.add_field(name="⏳ Created", value=created, inline=True)
    embed.add_field(name="\u200b", value="\u200b", inline=True)

    embed.set_image(url=image)
    embed.set_thumbnail(url=profile_pic)
    embed.set_author(name=username)
    embed.set_footer(text="Made by Star", icon_url=bot.user.avatar.url if bot.user.avatar else None)

    await channel.send(embed=embed, view=view)
    await ctx.interaction.response.send_message("✅ Fake listing sent.", ephemeral=True)



async def get_list(api, params, headers):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(api, params=params, headers=headers) as response:
                response.raise_for_status()  
                return await response.json()
        except aiohttp.ClientResponseError as e:
            print(f"HTTP Error {e.status}: {e.message}")
            return []
        except aiohttp.ClientError as e:
            print(f"Network error: {str(e)}")
            return []


@tasks.loop(seconds=5)
async def post_listing():
    channel = bot.get_channel(1391837082032410719)
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en;q=0.9",
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ5c2p1cWJ2Y3R6a2hvZHdvbXBxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4OTMzMzQsImV4cCI6MjA1OTQ2OTMzNH0.q70zm3y4Tw4hBEGLbetTvf3TN1dnX90iVM9PPrILEpY",
        "x-client-info": "supabase-js-web/2.50.2",
        "Origin": "https://resellvault.co.uk",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ5c2p1cWJ2Y3R6a2hvZHdvbXBxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4OTMzMzQsImV4cCI6MjA1OTQ2OTMzNH0.q70zm3y4Tw4hBEGLbetTvf3TN1dnX90iVM9PPrILEpY",
        "accept-profile": "public",
        "Referer": "https://resellvault.co.uk/",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sec-fetch-dest": "empty",
        "Priority": "u=3, i",
        "Cache-Control": "no-store",
        "Connection": "keep-alive"
    }
    params = {"select": "*", "order": "created_at.desc", "limit": 1000}

    listings = await get_list("https://fysjuqbvctzkhodwompq.supabase.co/rest/v1/vinted_listings", params, headers)
    
    if listings and channel:
        for listing in listings:
            view = dc_view("💳Buy", listing.get('listing_url'))
            embed = discord.Embed(
                title=listing.get('title', 'No Title'),
                color=0x1b00eb
                )

            embed.add_field(name="📑Brand", value=listing.get('brand', 'N/A'), inline=True)
            embed.add_field(name="📏Size", value=listing.get('size', 'N/A'), inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  

            embed.add_field(name="🧼Condition", value=listing.get('condition', 'N/A'), inline=True)
            embed.add_field(name="💰Price", value=listing.get('price', 'N/A'), inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)

            embed.add_field(name="✨ Feedbacks", value=listing.get('feedbacks', 'N/A'), inline=True)
            embed.add_field(name="⏳Created", value=listing.get('created_at', 'N/A')[:10], inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  



            thumb_url = listing.get('thumbnail_url')
            user_photo = listing.get('user_photo_url')
            username = listing.get('username')

            if thumb_url:
                embed.set_image(url=thumb_url)
            if user_photo:
                embed.set_thumbnail(url=user_photo)
            if username:
                embed.set_author(name=username)
            embed.set_footer(text="Made by Star", icon_url=bot.user.avatar)

            await channel.send(embed=embed, view=view)

@tasks.loop(seconds=5)
async def post_specific():
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en;q=0.9",
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ5c2p1cWJ2Y3R6a2hvZHdvbXBxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4OTMzMzQsImV4cCI6MjA1OTQ2OTMzNH0.q70zm3y4Tw4hBEGLbetTvf3TN1dnX90iVM9PPrILEpY",
        "x-client-info": "supabase-js-web/2.50.2",
        "Origin": "https://resellvault.co.uk",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ5c2p1cWJ2Y3R6a2hvZHdvbXBxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4OTMzMzQsImV4cCI6MjA1OTQ2OTMzNH0.q70zm3y4Tw4hBEGLbetTvf3TN1dnX90iVM9PPrILEpY",
        "accept-profile": "public",
        "Referer": "https://resellvault.co.uk/",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sec-fetch-dest": "empty",
        "Priority": "u=3, i",
        "Cache-Control": "no-store",
        "Connection": "keep-alive"
    }
    params = {"select": "*", "order": "created_at.desc", "limit": 1000}

    listings = await get_list("https://fysjuqbvctzkhodwompq.supabase.co/rest/v1/vinted_listings", params, headers)
    
    if listings:
        for listing in listings:
            if listing.get('brand', 'N/A').lower() == 'nike':
                channel_id = 1392192645924913172
            elif listing.get('brand', 'N/A').lower() == 'ralph lauren':
                channel_id = 1392192844629938257
            elif listing.get('brand', 'N/A').lower() == 'jordan':
                channel_id = 1392193027883139163
            elif listing.get('brand', 'N/A').lower() == 'the north face':
                channel_id = 1392194137826132168
            elif listing.get('brand', 'N/A').lower() == 'adidas':
                channel_id = 1392195159827026070
            elif listing.get('brand', 'N/A').lower() == 'stone island':
                channel_id = 1392194866217488424
            elif listing.get('brand', 'N/A').lower() == 'tommy hilfiger':
                channel_id = 1392239906625032346
            elif listing.get('brand', 'N/A').lower() == 'carhartt':
                channel_id = 1392240339544440844
            elif listing.get('brand', 'N/A').lower() == 'c.p. company':
                channel_id = 1392240930878128190
            elif listing.get('brand', 'N/A').lower() == 'stüssy':
                channel_id = 1392241535067881493
            else:
                continue

            channel = bot.get_channel(channel_id)
            view = dc_view("💳Buy", listing.get('listing_url'))
            embed = discord.Embed(
                title=listing.get('title', 'No Title'),
                color=0x1b00eb
                )

            embed.add_field(name="📑Brand", value=listing.get('brand', 'N/A'), inline=True)
            embed.add_field(name="📏Size", value=listing.get('size', 'N/A'), inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  

            embed.add_field(name="🧼Condition", value=listing.get('condition', 'N/A'), inline=True)
            embed.add_field(name="💰Price", value=listing.get('price', 'N/A'), inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)

            embed.add_field(name="✨ Feedbacks", value=listing.get('feedbacks', 'N/A'), inline=True)
            embed.add_field(name="⏳Created", value=listing.get('created_at', 'N/A')[:10], inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  



            thumb_url = listing.get('thumbnail_url')
            user_photo = listing.get('user_photo_url')
            username = listing.get('username')

            if thumb_url:
                embed.set_image(url=thumb_url)
            if user_photo:
                embed.set_thumbnail(url=user_photo)
            if username:
                embed.set_author(name=username)
            embed.set_footer(text="Made by Star", icon_url=bot.user.avatar)

            await channel.send(embed=embed, view=view)

@tasks.loop(seconds=5)
async def post_shoes():
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en;q=0.9",
        "apikey": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ5c2p1cWJ2Y3R6a2hvZHdvbXBxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4OTMzMzQsImV4cCI6MjA1OTQ2OTMzNH0.q70zm3y4Tw4hBEGLbetTvf3TN1dnX90iVM9PPrILEpY",
        "x-client-info": "supabase-js-web/2.50.2",
        "Origin": "https://resellvault.co.uk",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 19_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.0 Mobile/15E148 Safari/604.1",
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZ5c2p1cWJ2Y3R6a2hvZHdvbXBxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM4OTMzMzQsImV4cCI6MjA1OTQ2OTMzNH0.q70zm3y4Tw4hBEGLbetTvf3TN1dnX90iVM9PPrILEpY",
        "accept-profile": "public",
        "Referer": "https://resellvault.co.uk/",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "sec-fetch-dest": "empty",
        "Priority": "u=3, i",
        "Cache-Control": "no-store",
        "Connection": "keep-alive"
    }
    params = {"select": "*", "order": "created_at.desc", "limit": 1000}

    listings = await get_list("https://fysjuqbvctzkhodwompq.supabase.co/rest/v1/vinted_listings", params, headers)
    keywords = ["jordans", "jordan", "air", "air maxes", "airmaxes", "airmax", "air max", "shoe", "shoes", "footwear", "dunks", "samba", "new balance", "shox", "sneakers", "sneaker", "converse", "skecher", "skechers"]

    if listings:
        for listing in listings:
            title = listing.get('title', 'N/A').lower()
            if not any(keyword in title for keyword in keywords):
                continue

            channel = bot.get_channel(1392208926677798984)
            view = dc_view("💳Buy", listing.get('listing_url'))
            embed = discord.Embed(
                title=listing.get('title', 'No Title'),
                color=0x1b00eb
                )

            embed.add_field(name="📑Brand", value=listing.get('brand', 'N/A'), inline=True)
            embed.add_field(name="📏Size", value=listing.get('size', 'N/A'), inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  

            embed.add_field(name="🧼Condition", value=listing.get('condition', 'N/A'), inline=True)
            embed.add_field(name="💰Price", value=listing.get('price', 'N/A'), inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)

            embed.add_field(name="✨ Feedbacks", value=listing.get('feedbacks', 'N/A'), inline=True)
            embed.add_field(name="⏳Created", value=listing.get('created_at', 'N/A')[:10], inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  



            thumb_url = listing.get('thumbnail_url')
            user_photo = listing.get('user_photo_url')
            username = listing.get('username')

            if thumb_url:
                embed.set_image(url=thumb_url)
            if user_photo:
                embed.set_thumbnail(url=user_photo)
            if username:
                embed.set_author(name=username)
            embed.set_footer(text="Made by Star", icon_url=bot.user.avatar)

            await channel.send(embed=embed, view=view)




bot.run("")
