from VoiceListener import *
import json
import re
from itertools import combinations

TOKEN = 'ODA0Njk3NTYxNzc2MjU5MDgy.YBQHAQ.K2dT-QDfEwc8OkuSZTzt6KCusg4'


class MyClient(commands.Bot):
    async def on_ready(self):
        def cfg():
            f = open('cfg.json', 'r')
            data = f.read()
            f.close()
            js = json.loads(data)
            new_guild = js["NEW_GUILD"]
            guild_name = js["GUILD_NAME"]
            help_id = js["HELP_CHANNEL_ID"]
            if new_guild == 1:
                js["NEW_GUILD"] = 0
                f = open('cfg.json', 'w')
                js_dump = json.dumps(js)
                f.write(js_dump)
                f.close()
            return new_guild, guild_name, help_id

        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        NEW_GUILD, GUILD_NAME, HELP_ID = cfg()
        if NEW_GUILD == 1:
            guilds = bot.guilds
            for guild in guilds:
                if guild.name == GUILD_NAME:
                    true_guild = guild
                    print(guild.name.upper())
                    id_data(true_guild)
                    time_data()
                    channel = discord.utils.get(true_guild.channels, id=HELP_ID)
                    embed = discord.Embed(colour=discord.Colour.dark_green())
                    embed.add_field(name=':clock1:', value='React :clock1: to know time with everyone', inline=False)
                    message = await channel.send(embed=embed)
                    print(message)
                    await message.add_reaction('🕐')
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
    print(guild.id)
    ds_id1 = ctx.message.author.id
    friend = friend.strip()
    try:
        ds_id2 = int(re.findall(r'[0-9]+', friend)[0])
    except Exception as e:
        await ctx.send('Example of command: !time @ur_friend')
        return 1

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
    time_together = cur.execute(
        f'SELECT time FROM users WHERE user1 IN ({user1_id}, {user2_id}) AND user2 IN ({user1_id}, {user2_id})').fetchone()[
        0]
    conn.commit()
    conn.close()
    if time_together is None:
        time_together = 0
    await ctx.send(f'{name1} and {name2} have spent {time_together} minutes together!')


@bot.event
async def on_raw_reaction_add(payload):
    member = payload.member
    guild = member.guild
    user_name = member.name

    f = open('cfg.json', 'r')
    data = f.read()
    f.close()
    js = json.loads(data)
    help_id = js["HELP_CHANNEL_ID"]

    react_channel_id = payload.channel_id
    channel = bot.get_channel(guild.system_channel.id)
    help_channel = bot.get_channel(help_id)

    if react_channel_id != help_channel.id or member == bot.user:
        return
    if payload.emoji.name == '🕐':
        conn = sqlite3.connect('optimZenly.db')
        cur = conn.cursor()
        content = discord.Embed(title=f'{user_name} has spent that much time with friends!')
        content.set_thumbnail(url=member.avatar_url)

        user_id = cur.execute(f'SELECT user_id FROM unique_ids WHERE ds_id = {member.id}').fetchone()[0]
        user2_ids = cur.execute(f'SELECT user_id FROM unique_ids WHERE user_id != {user_id}').fetchall()
        no_time_flag = True
        for user2_id in user2_ids:
            time_together = cur.execute(
                f'SELECT time FROM users WHERE user1 IN ({user_id}, {user2_id[0]}) AND user2 IN ({user_id}, {user2_id[0]})').fetchone()[
                0]
            if time_together is None:
                continue
            else:
                no_time_flag = False
            user2_name = cur.execute(f'SELECT name FROM unique_ids WHERE user_id = {user2_id[0]}').fetchone()[0]
            content.add_field(name='with ' + user2_name, value=str(time_together) + ' minutes!', inline=False)

        conn.commit()
        conn.close()
        if no_time_flag:
            await channel.send(f'```{user_name} hasn\'t been in voice channel with anyone yet :(```')
        else:
            await channel.send(embed=content)


bot.run(TOKEN)
