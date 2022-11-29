from columnar import columnar
import mysql.connector
import discord
import asyncio
import functools
import typing
import time

from discord.ext import commands

from dotenv import dotenv_values

vars = dotenv_values(".env")

whitelisted = vars["WHITELIST_IDS"]
syntax = vars["SYNTAX"]
TOKEN = vars["TOKEN"]

client = discord.Client(intents=discord.Intents.default())

clienter = commands.Bot(intents=discord.Intents.default(),command_prefix = '!', help_command=None)

config = {
    'user': vars["USERNAME"],
    'password': vars["PASSWORD"],
    'host': vars["HOSTNAME"],
    'database': vars["DATABASE"],
    'raise_on_warnings': True
}

try:
    cnx = mysql.connector.connect(**config)
    cnx.autocommit = True
    cursor = cnx.cursor()
    print("MySQL Connection Created Successfully")
except Exception as e:
    print("Error at:")
    print(e)
    print()
    print("Exiting...")
    exit()

# def to_thread(func: typing.Callable) -> typing.Coroutine:
#     @functools.wraps(func)
#     async def wrapper(*args, **kwargs):
#         loop = asyncio.get_event_loop()
#         wrapped = functools.partial(func, *args, **kwargs)
#         return await loop.run_in_executor(None, wrapper)
#     return wrapper


# @to_thread
# def blocking_func(t=1):
#     time.sleep(t)
#     return "some stuff"

def exec(query):
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        return str(e)
        # return ['ERR', e]


# @client.event
# async def on_message(message):
#     data = []
#     query = ""
#     if message.author == client.user:
#         return
#     if message.content.startswith(syntax):
#         if message.author.id not in whitelisted:
#             await message.channel.send(embed=discord.Embed(title="You are not authorized to use this bot",
#                                                            description='Please contact the bot hoster to add you to '
#                                                                        'the whitelisted members list',
#                                                            color=discord.Color.red()))
#             return
#         if message.content == syntax + "help":
#             await message.channel.send(
#                 embed=discord.Embed(title=client.user.name, description='https://devhints.io/mysql',
#                                     color=discord.Color.purple()))
#             return
#         for word in message.content.split():
#             query += word + " "
#         query = query.replace(syntax, '')

#         if query == " ":
#             await message.channel.send(
#                 embed=discord.Embed(title=client.user.name, description='Arguments are missing for the query',
#                                     color=discord.Color.red()))
#             return

#         output = exec(query)

#         if not output:
#             msg = await message.channel.send(
#                 embed=discord.Embed(description="Empty list returned", color=discord.Color.blue()))
#             return

#         if isinstance(output, list):
#             for result in output:
#                 sub_data = []
#                 for x in result:
#                     sub_data.append(x)
#                 data.append(sub_data)
#             await message.channel.send(columnar(data, no_borders=False))
#             # await message.channel.send(output)
#             return
#         else:
#             msg = await message.channel.send(
#                 embed=discord.Embed(title="MySQL Returned an Error", description=output, color=discord.Color.orange()))
#             await msg.add_reaction("⚠️")
#             return

def send_invite(prev_invites):
    query = "SELECT invites FROM  clans"
    cur_invites = exec(query)


@client.event
async def on_ready():
    print(f"Bot | Status:   Operational")
    print(f"Bot | ID:       {format(client.user.id)}")
    print(f"Bot | Name:     {format(client.user.name)}")
    print(f"Bot | Guilds:   {len(client.guilds)}")
    print(f"Bot Configurations set to:\n{config}")
    print(f"Bot is ready to use")
    # ? Custom Activity
    await client.change_presence(
        activity=discord.Activity(type=discord.ActivityType.listening, name="Syntax = " + syntax))
    cnt_query = "SELECT COUNT(*) FROM  clans"
    cname_query = "SELECT cname FROM  clans"
    invite_query = "SELECT invites FROM  clans"

    prev_clans_cnt = exec(cnt_query)
    prev_clans = exec(cname_query)
    prev_invites = exec(invite_query)
    print(prev_invites)

    while True:
        cur_clans_cnt = exec(cnt_query)
        cur_clans = exec(cname_query)

        if prev_clans_cnt == cur_clans_cnt:
            continue

        if (prev_clans_cnt > cur_clans_cnt):
            delete_clan_name = list(set(prev_clans) - set(cur_clans))
            print("clan deleted = ", delete_clan_name[0][0])
            
            for guild in client.guilds:
                existing_channel = discord.utils.get(guild.channels, name= delete_clan_name[0][0])
                existing_role = discord.utils.get(guild.roles, name = delete_clan_name[0][0])
                existing_leader_role = discord.utils.get(guild.roles, name ="{} Leader".format(delete_clan_name[0][0]))
                existing_coleader_role = discord.utils.get(guild.roles, name = "{} Co-Leader".format(delete_clan_name[0][0]))
                general_channel = discord.utils.get(guild.channels, name= "general")
            # if the channel exists
            if existing_role is not None:
                await existing_role.delete()
                await general_channel.send("Successfully deleted {}role".format(delete_clan_name[0][0]))
            if existing_leader_role is not None:
                await existing_leader_role.delete()
                await general_channel.send("Successfully deleted {}leader role".format(delete_clan_name[0][0]))
            if existing_coleader_role is not None:
                await existing_coleader_role.delete()
                await general_channel.send("Successfully deleted {}coleader role".format(delete_clan_name[0][0]))

            if existing_channel is not None:
                await existing_channel.delete()
                await general_channel.send(f"Successfully deleted channel {delete_clan_name[0][0]}!")
                
            # if the channel does not exist, inform the user
            else:
                await general_channel.send(f'No channel named, "{ delete_clan_name[0][0]}", was found')

        else:

            created_clan_name = list(set(cur_clans) - set(prev_clans))
            print("clan created: name = ", created_clan_name[0][0])

            await client.wait_until_ready()
            for guild in client.guilds:
                category = discord.utils.get(guild.categories, id=1010790802135453746)
                channel = await guild.create_text_channel(name=created_clan_name[0][0], category=category)
                role = await guild.create_role(name=created_clan_name[0][0])
                leader_role = await guild.create_role(name="{} Leader".format(created_clan_name[0][0]))
                coleader_role = await guild.create_role(name="{} Co-Leader".format(created_clan_name[0][0]))
                await channel.send(f"Successfully created channel and roles with {created_clan_name[0][0]}!")
        
        prev_clans = cur_clans
        prev_clans_cnt = cur_clans_cnt

        time.sleep(1)

@clienter.command()
async def createchannel(ctx, channelName):
    
    print('received message ',channelName)
    guild = ctx.guild

    mbed = discord.Embed(
        title   =   'Success',
        description = "{}has been successfully created.".format(channelName)
    )
    if ctx.author.guild_permissions.manage_channels:
        await guild.create_text_channel(name='{}'.format(channelName))
        await ctx.send(embed=mbed)

client.run(TOKEN)
