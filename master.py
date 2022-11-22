from discord.ext import commands
import discord as d

client = commands.Bot(intents=d.Intents.default(),command_prefix = '!', help_command=None)

@client.event
async def on_ready():
    print(f'{client.user} has Awoken!')

@client.command()
async def deletechannel(ctx, channel: d.TextChannel):
    mbed = d.Embed(
        title   =   'Success',
        description = f'Channel: {channel} has been deleted',
    )
    if ctx.author.guild_permissions.manage_channels:
        await ctx.send(embed=mbed)
        await channel.delete()

@client.command()
async def createchannel(ctx, channelName):
    guild = ctx.guild
    print("create channel ", channelName)
    mbed = d.Embed(
        title   =   'Success',
        description = "{}has been successfully created.".format(channelName)
    )
    if ctx.author.guild_permissions.manage_channels:
        await guild.create_text_channel(name='{}'.format(channelName))
        await ctx.send(embed=mbed)

client.run('MTAzOTAwODI4Mzc2NTI0MzkzNA.GqFEtZ.SKqkRgKg4NejJG07siKKeYQMSf6HohhIMq6S3g')