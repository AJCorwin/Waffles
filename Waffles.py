from discord.ext import commands, tasks
import discord
import my_secrets
import sqlite3
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

letter_values = {"a": 1, "c": 3, "b": 3, "e": 1, "d": 2, "g": 2, 
          "f": 4, "i": 1, "h": 4, "k": 5, "j": 8, "m": 3, 
          "l": 1, "o": 1, "n": 1, "q": 10, "p": 3, "s": 1, 
          "r": 1, "u": 1, "t": 1, "w": 4, "v": 4, "y": 4, 
          "x": 8, "z": 10}


waffles_db = my_secrets.database_name

con = sqlite3.connect(waffles_db)
con.execute("PRAGMA foreign_keys = 1")
cursor = con.cursor()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
activity=discord.Game(name='Hello There')

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
   await opt_in(ctx, opt_message)


async def opt_in(ctx, message: str):
    try:
        if message != "me":
            await ctx.send(f"HEY! {ctx.author.mention} Usage: !opt_in me")
        else:
            try:
                display_name = ctx.author.name
                whitelist = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
                cleaned_display_name = ''.join(filter(whitelist.__contains__, display_name))
                latest_score = 0
                await (username_score(ctx, message))
                discord_user_values = [ctx.author.id, cleaned_display_name, 0, 0, 0, latest_score, 0, 0, 0, 0, 0]
                sql = ''' INSERT INTO discord_users(discord_user_id, user_name, average_score, max_score, min_score, 
                latest_score, standard_deviation, range, interquartile_range, largest_outlier, smallest_outlier)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) '''
                cursor.execute(sql, discord_user_values)
                con.commit()
                await ctx.send(f"Hey {ctx.author.mention}! You have been added to the DB.")
            except:
                await ctx.send(f"Hey {ctx.author.mention} is already in the database. You're silly {ctx.author.mention}!")
    except Exception:
            print("internal DB error opt in def")

async def username_score(ctx, opt_message: str):
    latest_score = 0
    await(score_me(ctx, opt_message))
    return latest_score

@bot.command()
async def username_score(ctx, opt_message):
    latest_score = 0
    latest_score = await score_me(ctx, opt_message)
    if latest_score == 0:
        print("no score returned")
    elif latest_score is None:
        await ctx.send(f"Hey {ctx.author.mention} you have already tried that username, it is worth {latest_score}")
    else:
        await ctx.send(f"Hey {ctx.author.mention}! Your display name is worth {latest_score}")

async def score_me(ctx, message: str):
        latest_score = 0
        print(ctx.author.display_name)
        if ctx.author.display_name is None:
            display_name = ctx.author.name
        else:
            display_name = ctx.author.display_name
        display_name = display_name.lower()
        user_id = ctx.author.id
        whitelist = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        cleaned_display_name = ''.join(filter(whitelist.__contains__, display_name))
        try:
            sql_check = f''' SELECT score
                            FROM nickname_scores
                            WHERE discord_user_id=? 
                            AND nickname=?
        '''
            display_name_check = cursor.execute(sql_check, (user_id, display_name ))
            display_name_check = cursor.fetchone()[0]
            con.commit()
            print(display_name_check)
            return display_name_check
        except:
            try:
                if message != "me":
                    await ctx.send(f"HEY! {ctx.author.mention} Usage: !username_score me")
                else:
                    try:
                        cleaned_display_name = "".join(set(cleaned_display_name))
                        cleaned_display_name = ''.join(sorted(cleaned_display_name))
                        for letter in cleaned_display_name:
                            latest_score += letter_values[letter]
                            print(latest_score)
                        latest_score = latest_score
                        discord_scores_values = [ctx.author.id, display_name, latest_score]
                        sql_nickname_score_add = ''' 
                        INSERT OR REPLACE INTO nickname_scores(discord_user_id, nickname, score)
                        VALUES(?, ?, ?)
                        '''
                        cursor.execute(sql_nickname_score_add, discord_scores_values)
                        con.commit()
                        discord_user_update = '''UPDATE discord_users
                        SET latest_score=?
                        WHERE discord_user_id=?'''
                        cursor.execute(discord_user_update, (latest_score, ctx.author.id))
                        con.commit()
                        return latest_score
                        
                    except:
                        await ctx.send(f"Hey {ctx.author.mention} you shouldnt be here score_me")
            except Exception:
                    print("internal DB error score me def")

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

bot.run(my_secrets.mytoken)