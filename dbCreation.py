import os
import sqlite3

database_name = "Waffles_Bot.db"

# https://stackoverflow.com/questions/3247183/variable-table-name-in-sqlite
# https://bobby-tables.com/python
# todo make sure any data coming into DB is clean

if not os.path.exists(database_name):
    print(f"Creating database { database_name }")
    con = sqlite3.connect(database_name)
    cur = con.cursor()

    '''
        Walkng you through what is going on above. If the database does not exist it will create the database at the specified name.
        
        Once the database is created we make a columns list for both tables. The discord_user_id needs to be an integer, unique so 
        each user has only one value, not null, and it is the primary key. 
        
        For the nicknames_scores table we need the discord_user_id as a foreign key linking back to the discord_users table.

    '''

    users_columns = [
        "discord_user_id INTEGER UNIQUE NOT NULL PRIMARY KEY", "user_name", "average_score", "max_score", "min_score", "latest_score",
        "standard_deviation", "range", "interquartile_range", "largest_outlier", "smallest_outlier"]
    users_columns = ', '.join(users_columns)

    discord_users_create_string = ("CREATE TABLE if not exists discord_users(%s)" %users_columns)
    cur.execute(discord_users_create_string)


    nickname_scores_columns = [
        "discord_user_id", "nickname", "score", "FOREIGN KEY(discord_user_id) REFERENCES discord_users(discord_user_id)"]
    nickname_scores_columns = ', '.join(nickname_scores_columns)
    
    nickname_scores_columns_create_string = ("CREATE TABLE if not exists nickname_scores(%s)" %nickname_scores_columns)
    cur.execute(nickname_scores_columns_create_string)

    con.commit()

    print(f"{ database_name } creation is complete!")


elif os.path.exists(database_name):
    print(f"The database { database_name } exists")