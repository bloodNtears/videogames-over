from VoiceListener import *
import json
import re
from itertools import combinations

TOKEN = 'ODA0Njk3NTYxNzc2MjU5MDgy.YBQHAQ.JRFl-R2Fwyqk7oVy27W8UV1m4ew'


class MyClient(commands.Bot):
    async def on_ready(self):
        def cfg():
            f = open('cfg.json','r')
            data = f.read()
            f.close()
            js = json.loads(data)
            new_guild = js["NEW_GUILD"]
            guild_name = js["GUILD_NAME"]
            if new_guild == 1:
                js["NEW_GUILD"] = 0
                f = open('cfg.json', 'w')
                js_dump = json.dumps(js)
                f.write(js_dump)
                f.close()
            return new_guild, guild_name



        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        NEW_GUILD, GUILD_NAME = cfg()
        if NEW_GUILD == 1:
            guilds = bot.guilds
            for guild in guilds:
                if guild.name == GUILD_NAME:
                    true_guild = guild
                    print(guild.name.upper())
                    id_data(true_guild)
                    time_data()
                    break

    # dm
    async def on_member_join(self, member):
        def add_id_data(member):
            print('ADDING USER IN unique_ids')
            conn = sqlite3.connect('optimZenly.db')
            cur = conn.cursor()
            exists = cur.execute('SELECT * FROM unique_ids WHERE ds_id = ?', (member.id,)).fetchone()
            if not exists:
                cur.execute('''INSERT INTO unique_ids (name, ds_id) VALUES (?,?)''', (member.name, member.id))
            user_id = cur.execute(f'SELECT * FROM unique_ids WHERE ds_id = {member.id}').fetchone()[0]
            print(exists)
            conn.commit()
            conn.close()
            return user_id

        def add_time_data(user_id):
            print('ADDING IN TIME')
            conn = sqlite3.connect('optimZenly.db')
            cur = conn.cursor()
            data = cur.execute('SELECT user_id FROM unique_ids').fetchall()
            data = [row[0] for row in data]
            pairs = [(user_id, table_id) for table_id in data]
            print(pairs)
            for pair in pairs:
                req = 'INSERT INTO users (user1, user2) VALUES (?, ?)'
                cur.execute(req, pair)
            conn.commit()
            conn.close()

        user_id = add_id_data(member)
        # print(user_id)
        add_time_data(user_id)
        await member.send(f'Hi {member.name}, welcome to the club')


def id_data(guild):
    print('id data'.upper())
    members = guild.members
    names = [member.name for member in members]
    ds_ids = [member.id for member in members]
    count = guild.member_count

    conn = sqlite3.connect('optimZenly.db')
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS unique_ids')
    cur.execute('''CREATE TABLE "unique_ids" (
        "user_id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        "name" TEXT NOT NULL,
    "ds_id"	INTEGER NOT NULL UNIQUE
    );''')

    for i in range(count):
        cur.execute('''INSERT OR IGNORE INTO unique_ids (name, ds_id) Values ( ?, ? )''', (names[i], ds_ids[i],))
    conn.commit()
    conn.close()


def time_data():
    print('TIME DATA 1')
    conn = sqlite3.connect('optimZenly.db')
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS users')
    cur.execute('''CREATE TABLE "users" (
    "user1"	INTEGER NOT NULL,
    "user2"	INTEGER NOT NULL,
    "time"	INTEGER
    );''')
    data = cur.execute('SELECT user_id FROM unique_ids').fetchall()
    data = [row[0] for row in data]
    print(data)
    pairs = list(combinations(data, 2))
    print("PAIRS", pairs)
    for pair in pairs:
        req = 'INSERT INTO users (user1, user2) VALUES (?, ?)'
        cur.execute(req, pair)
    conn.commit()
    conn.close()


bot = MyClient(command_prefix='!', intents=discord.Intents.all())

setup_voice(bot)


@bot.command(help="Check time u have spent with ur friend. Call !time @friend_nick")
async def time(ctx, friend):
    guild = ctx.guild
    ds_id1 = ctx.message.author.id
    friend = friend.strip()
    try:
        ds_id2 = int(re.findall(r'[0-9]+', friend)[0])
    except Exception as e:
        await ctx.send('Example of command: !time @ur_friend')
        return 1
    print(ds_id1, ds_id2, friend)

    name1 = ctx.message.author.name
    name2 = discord.utils.get(guild.members, id=ds_id2)
    if name2 is None:
        await ctx.send(f'Your friend is not a member of {guild.name} right now!')
        return 1
    name2 = name2.name

    conn = sqlite3.connect('optimZenly.db')
    cur = conn.cursor()
    user1_id = cur.execute('''SELECT * FROM unique_ids WHERE ds_id = ?''', (ds_id1,)).fetchone()[0]
    user2_id = cur.execute('''SELECT * FROM unique_ids WHERE ds_id = ?''', (ds_id2,)).fetchone()[0]
    # print(user1_id, user2_id)
    time_together = cur.execute(f'SELECT time FROM users WHERE user1 = {user1_id} AND user2 = {user2_id}').fetchone()[0]
    # print('TT',time_together)
    conn.commit()
    conn.close()
    if time_together is None:
        time_together = 0
    await ctx.send(f'{name1} and {name2} have spent {time_together} minutes together!')


bot.run(TOKEN)
