from discord.ext import commands, tasks
import discord
import secrets
import sqlite3
import asyncio
import random

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

'''
authorid for discord user id
member.name for discord username
member.display_name for nickname
'''

waffles_db = secrets.database_name

con = sqlite3.connect(waffles_db)
con.execute("PRAGMA foreign_keys = 1")
cursor = con.cursor()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
activity=discord.Game(name='Hello There')

#bot = discord.Client(intents=intents, activity=discord.Game(name='Hello There'))
bot = commands.Bot(command_prefix='!', intents=intents, activity=activity)

@bot.event
async def on_ready():
    print(f'Logged on as {bot.user}!')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    elif message.author != bot.user:
        if message.content == 'ping':
            print(message.author.display_name)
            print(f'Message from {message.author} | The content is: {message.content} | Message id: {message.id} |',
            'author id:', message.author.id,'| name:', message.author.name)
            await message.channel.send('pong :sunglasses:')
        else:
            await bot.process_commands(message)


@bot.event
async def on_message_delete(message):
    msg = f'{message.author.name} {message.guild} has deleted the message: {message.content}'
    print (f'{message.author.name} {message.guild} has deleted the message: {message.content}')
    await message.channel.send(msg)


@bot.command()
async def roll(ctx, dice: str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await ctx.send('Format has to be in NumberdNumber! Such as 8d6 for Fireball')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    nickname_scores_data = [ctx.author.id, ctx.author.name, 1]
    await ctx.send(f'{ctx.author.mention} rolled {result} | {nickname_scores_data}')

@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")

# The meat of the SQLLITE testing

@bot.command()
async def opt_in(ctx, opt_message: str):
    try:
        if opt_message != "me":
            await ctx.send(f"HEY! {ctx.author.mention} Usage: !opt_in me")
        else:
            cursor.execute(f'SELECT * FROM "discord_users" WHERE discord_user_id={ctx.author.id}')
            user_in_main_table = cursor.fetchone()
            if user_in_main_table is None:
                insert_discord_users(con, 'discord_users', {'discord_user_id': ctx.author.id,
                        'user_name': ctx.author.name,
                        'average_score': 0,
                        'max_score': 0,
                        'min_score': 0,
                        'latest_score': 0,
                        'standard_deviation': 0,
                        'range': 0,
                        'interquartile_range': 0,
                        'largest_outlier': 0,
                        'smallest_outlier': 0})     
            ctx.command = bot.get_command("add_to_nicknames_table")
            await bot.invoke(ctx)  # invoke the command above
    except Exception:
        await clear_error()
        print(opt_message)
        await ctx.send(f"HEY! {ctx.author.mention} Usage: !opt_in me")
        return

@opt_in.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"HEY! {ctx.author.mention} Usage: !opt_in me")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send('** are you lost?**')


@bot.command()
async def add_to_nicknames_table(ctx):
    print("send to add_to_nickname_table worked")
    await ctx.send(ctx.author.id, ctx.member.display_name, 4)

    cursor.execute(f'SELECT * FROM "discord_users" WHERE discord_user_id={ctx.author.id}')
    print("execute was successful")
    nickname_in_scores_table = cursor.fetchone()
    if nickname_in_scores_table is None:
        insert_nickanme_scores(con, 'nickname_scores', {'discord_user_id': {ctx.author.id}, 'FOREIGN KEY discord_users REFERENCES': ctx.author.id,
                        'nickname': ctx.display_name, 'score': 4})

        await ctx.send(f'Success + {ctx.author.mention}!')
    else:
        clear_error()
        await ctx.send(f"HEY! {ctx.author.mention} Usage: !opt_in me")
        return



@bot.event    
async def on_member_update(before, after):
    print('member1')
    print(f'before: {before}, | nick {before.nick} | display name {before.display_name} | ID {before.id} | {before.name}')
    print(f'after: {after}, | nick {after.nick} | display name {after.display_name} | ID {after.id} | {after.name}')
    print('member2')

@bot.event
async def on_user_update(before, after):
    print(after)
    print(before)
    print('user')

@bot.event
async def on_member_join(member):
    guild = member.guild
    if guild.system_channel is not None:
        to_send = (f'Welcome {member.mention} to {guild.name}! You can opt_in to the',
        'nickname rating system! Don\'t worry you can always opt back out and I will',
        'delete your data automatically. If you want to opt in simply say:',
        '!opt_in me')
        await guild.system_channel.send(to_send)
        print(member)


# I appreciate StackOverflow
def insert_discord_users(con, table, row):
    cols = ', '.join('"{}"'.format(col) for col in row.keys())
    vals = ', '.join(':{}'.format(col) for col in row.keys())
    sql = 'INSERT OR IGNORE INTO "{0}" ({1}) VALUES ({2})'.format(table, cols, vals)
    con.cursor().execute(sql, row)
    con.commit()
    print ('New entry added')


def insert_nickanme_scores(con, table, row):
    cols = ', '.join('"{}"'.format(col) for col in row.keys())
    vals = ', '.join(':{}'.format(col) for col in row.keys())
    sql = 'INSERT OR IGNORE INTO "{0}" ({1}) VALUES ({2})'.format(table, cols, vals)
    con.cursor().execute(sql, row)
    con.commit()

bot.run(secrets.mytoken)