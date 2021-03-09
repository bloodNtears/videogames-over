from discord.ext import commands
import discord
import datetime
import sqlite3


def fill_id_table(member):
    conn = sqlite3.connect('projectdis.db')
    cur = conn.cursor()
    cur.execute('''SELECT * FROM UsersID WHERE ds_id = ?''', (member.id,))
    exists = cur.fetchone()
    if not exists:
        cur.execute('''INSERT OR IGNORE INTO UsersID (user, ds_id) Values ( ?, ? )''', (member, member.id,))
    print(exists)
    conn.commit()
    conn.close()


def fill_time_db(member1, join_time1, member2, join_time2):
    conn = sqlite3.connect('projectdis.db')
    cur = conn.cursor()
    user1_id = cur.execute('SELECT user_id from UsersID WHERE ds_id = ?', (member1.id,)).fetchone()
    user2_id = cur.execute('SELECT user_id from UsersID WHERE ds_id = ?', (member2.id,)).fetchone()


class VoiceListener(commands.Cog):
    def __init__(self, bot):
        self.active_users = dict()
        self.pairs = dict()
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        # active_users = dict()  # all users who are in voice chat rn; structure: {user1: join_time, user2: join_time ...}
        # pairs = dict()  # dict of pairs related to a specific voice channel;
        # structure: {voice_channel1_id: [user1, user2, user3],
        # voice_channel2_id: [user4, user5, user6]
        # }

        # for example:
        # if user1 leaves, we scan pairs dict
        # 1) start function fill_db with ([user1, join_time], [user2, join_time]) and ([user1, join_time], [user3, join_time])
        # 2) delete user1 from active_users dict

        # разобраться с переключением в другой войс

        if before.channel != after.channel:
            if before.channel is None:
                print(member.name, 'has connected to', after.channel.name, '\n')

                fill_id_table(member)

                self.active_users[member.id] = datetime.datetime.now().time()
                print(self.active_users)

                self.pairs.setdefault(after.channel.id, []).append(member.id)
                print(self.pairs)

            elif after.channel is not None:
                print(member.name, 'has disconnected from', before.channel.name, '\n')
                print(member.name, 'has connected to', after.channel.name, '\n')
                # заполняем бд данными из active_users
                self.pairs[before.channel.id].remove(member.id)
                if not self.pairs[before.channel.id]:
                    del self.pairs[before.channel.id]
                self.active_users[member.id] = datetime.datetime.now().time()
                print(self.active_users)
                self.pairs.setdefault(after.channel.id, []).append(member.id)
                print(self.pairs)
            else:
                print(member.name, 'has disconnected from', before.channel.name, '\n')
                try:
                    del self.active_users[member.id]
                    del self.pairs[before.channel.id]
                except Exception as e:
                    print(e)
                    pass
                print(self.active_users)
                print(self.pairs)

        '''
        if before.self_mute is False and after.self_mute is True:
            print(member.name, 'has muted in', before.channel.name, '\n')
        if before.self_mute is True and after.self_mute is False:
            print(member.name, 'has unmuted in', before.channel.name, '\n')
        '''


def setup(bot):
    bot.add_cog(VoiceListener(bot))
