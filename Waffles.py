from discord.ext import commands, tasks
import discord
import secrets

print(f'bot api version is {discord.__version__}')
# https://github.com/Rapptz/discord.py/blob/master/examples/background_task.py
# https://github.com/Rapptz/discord.py/tree/master/examples
# look into sanitizing the data

# ToDo:
# Sanitize the data
# Score the users name using both unique and non unique letters
# add command to print out their latest, avg, min, max, iqr, sd, number of saved usernames
# gdpr? https://www.reddit.com/r/discordapp/comments/8mazic/bots_that_violate_the_gdpr/ 
# I am tired, its 2:40 am. I should stop staying up late to code.

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = discord.Client(intents=intents, activity=discord.Game(name='Hello There'))
bot = commands.Bot(intents=intents, command_prefix='!')

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.author != bot.user:
        if message.content == 'ping':
            print(message.author.display_name)
            print(f'Message from {message.author} | The content is: {message.content} | Message id: {message.id} | author id: {message.author.id}')
            await message.channel.send('pong :sunglasses:')


@bot.event    
async def on_member_update(before, after):
    print('member1')
    print(f'before: {before}, | nick {before.nick} | "display name {before.display_name}" | ID {before.id} | {before.name}')
    print(f'after: {after}, | nick {after.nick} | display name {after.display_name} | ID {after.id} | {after.name}')
    print('member2')

@bot.event
async def on_user_update(before, after):
    print(after)
    print(before)
    print('user')

@bot.event
async def on_message_delete(message):
    msg = f'{message.author} {message.guild} {message.author} {message.activity} has deleted the message: {message.content}'
    await message.channel.send(msg)


@bot.event
async def my_message(ctx, mem : discord.Member, maessage: discord.Message, usr: discord.User):
    channel = maessage.channel
    msg1 = f'({mem.nick} {mem.name} {maessage.content} {usr.id} {usr.display_name})'
    print({mem.nick}, {mem.name}, {maessage.content})
    await bot.say(msg1)


    if maessage.content == 'ping':
        await bot.say('pong')



@bot.event
async def on_member_join(self, member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = f'Welcome {member.mention} to {guild.name}!'
        await guild.system_channel.send(to_send)
        print(member)



bot.run(secrets.mytoken)