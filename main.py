import random
from VoiceListener import *

TOKEN = ''


class MyClient(commands.Bot):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    # in channel
    '''
    async def on_member_join(self, member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = 'Welcome {0.mention} to {1.name}!'.format(member, guild)
            await guild.system_channel.send(to_send)
    '''

    # dm
    async def on_member_join(self, member):
        def add_id_data(member):
            print('adding user_id in UsersID')
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
            print('adding in time')
            conn = sqlite3.connect('projectdis.db')
            cur = conn.cursor()
            lst = cur.execute('select * from Time')
            names = [description[0] for description in cur.description]
            if str(user_id) not in names:
                req = 'ALTER TABLE Time ADD sss' + str(user_id) + ' INTEGER;'
                cur.execute(req)
            # print(cur.description)

        user_id = add_id_data(member)
        print(user_id)
        add_time_data(user_id)
        await member.send(f'Hi {member.name}, welcome to the club')


bot = MyClient(command_prefix='!', intents=discord.Intents.all())
#setup(bot)

bot.run(TOKEN)
