from VoiceListener import *
from cfg import NEW_SERVER



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
            print('adding in time'.upper())
            conn = sqlite3.connect('projectdis.db')
            cur = conn.cursor()
            lst = cur.execute('select * from Time')
            names = [description[0] for description in cur.description]
            if 'u' + str(user_id) not in names:
                req = 'ALTER TABLE Time ADD u' + str(user_id) + ' INTEGER;'
                cur.execute(req)
                # print('user_id - ', user_id)
                req = f'INSERT INTO Time (User_id) Values ({user_id})'
                # print(req)
                cur.execute(req)
            conn.commit()
            conn.close()
            # print(cur.description)

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

setup(bot)
bot.run(TOKEN)
