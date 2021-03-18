from VoiceListener import *
from cfg import NEW_SERVER
import re

TOKEN = 'ODA0Njk3NTYxNzc2MjU5MDgy.YBQHAQ.Yfdcns4294m2zS2XdoUU9sVViO0'


class MyClient(commands.Bot):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        if NEW_SERVER:
            guilds = bot.guilds
            for guild in guilds:
                if guild.name == 'test_bot_fiverr':
                    true_guild = guild
                    print(guild.name.upper())
                    id_data(true_guild)
                    time_data()
                    break
            f = open('cfg.py', 'w')
            f.write('NEW_SERVER = False\n')
            f.close()

    # dm
    async def on_member_join(self, member):
        def add_id_data(member):
            """
            writes member.name, member.id and autoincrement local id if member is not in UsersID table
            :param member: discord.Member
            :return: user_id
            """
            print('adding user_id in UsersID'.upper())
            conn = sqlite3.connect('projectdis.db')
            cur = conn.cursor()
            cur.execute('''SELECT * FROM UsersID WHERE ds_id = ?''', (member.id,))
            exists = cur.fetchone()
            if not exists:
                cur.execute('''INSERT OR IGNORE INTO UsersID (user, ds_id) Values ( ?, ? )''',
                            (member.name, member.id,))
            user_id = cur.execute(f'SELECT * FROM UsersID WHERE ds_id = {member.id}').fetchone()[0]
            print(exists)
            conn.commit()
            conn.close()
            return user_id

        def add_time_data(user_id):
            """
            takes user_id that was created in add_id_table
            creates column in Time table if not exists
            inserts primary key user_id from UsersID table
            :param user_id: integer
            :return:
            """
            print('adding in time'.upper())
            conn = sqlite3.connect('projectdis.db')
            cur = conn.cursor()
            lst = cur.execute('select * from Time')
            names = [description[0] for description in cur.description]
            if 'u' + str(user_id) not in names:
                req = 'ALTER TABLE Time ADD u' + str(user_id) + ' INTEGER;'
                cur.execute(req)
                req = f'INSERT INTO Time (User_id) Values ({user_id})'
                cur.execute(req)
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

    conn = sqlite3.connect('projectdis.db')
    cur = conn.cursor()
    cur.execute('DROP TABLE IF EXISTS UsersID')
    cur.execute('''CREATE TABLE "UsersID" (
    "user_id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    "user"	TEXT NOT NULL,
    "ds_id"	INTEGER NOT NULL UNIQUE
    );''')

    for i in range(count):
        cur.execute('''INSERT OR IGNORE INTO UsersID (user, ds_id) Values ( ?, ? )''', (names[i], ds_ids[i],))
    conn.commit()
    conn.close()


def time_data():
    print('time_data'.upper())
    flag = False
    if not flag:
        conn = sqlite3.connect('projectdis.db')
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS Time')
        cur.execute('''CREATE TABLE "Time" (
        "User_id"	INTEGER NOT NULL,
        PRIMARY KEY("User_id")
        );''')
        data = cur.execute('SELECT * FROM UsersID').fetchall()
        user_ids = [row[0] for row in data]
        for user_id in user_ids:
            req = 'ALTER TABLE Time ADD u' + str(user_id) + ' INTEGER;'
            cur.execute(req)
        for user_id in user_ids:
            req = 'INSERT INTO Time (' + 'u' + ', u'.join([str(i) for i in user_ids]) + ') Values (' + ' ,'.join(
                ['?' for i in range(len(user_ids))]) + ')'
            cur.execute(req, (tuple([None for i in range(len(user_ids))])))
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

    conn = sqlite3.connect('projectdis.db')
    cur = conn.cursor()
    user_id1 = cur.execute('''SELECT * FROM UsersID WHERE ds_id = ?''', (ds_id1,)).fetchone()[0]
    user_id2 = cur.execute('''SELECT * FROM UsersID WHERE ds_id = ?''', (ds_id2,)).fetchone()[0]
    print(user_id1, user_id2)
    time_together = cur.execute('SELECT * FROM Time WHERE User_id = ?', (user_id1,)).fetchall()[0][user_id2]
    print(time_together)
    conn.commit()
    conn.close()
    if time_together is None:
        time_together = 0
    await ctx.send(f'{name1} and {name2} have spent {time_together} minutes together!')


bot.run(TOKEN)
