from discord.ext import commands
import discord
from datetime import datetime, time, date, timedelta
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


def fill_time_db(member1, time1, member2, time2):
    print('ARGS', member1, time1, member2, time2)
    conn = sqlite3.connect('projectdis.db')
    cur = conn.cursor()
    user1_id = cur.execute('SELECT user_id from UsersID WHERE ds_id = ?', (member1,)).fetchone()[0]
    user2_id = cur.execute('SELECT user_id from UsersID WHERE ds_id = ?', (member2,)).fetchone()[0]
    cur_time = datetime.now()
    # delta_time = cur_time - timedelta(hours=time2.hour, minutes=time2.minute, seconds=time2.second)
    print('CURTIME', cur_time)
    if time2 > time1:
        delta_time = cur_time - timedelta(hours=time2.hour, minutes=time2.minute, seconds=time2.second)
    else:
        delta_time = cur_time - timedelta(hours=time1.hour, minutes=time1.minute, seconds=time1.second)
    delta_time = int(delta_time.hour * 60 + delta_time.minute + delta_time.second / 60)
    friends_time = cur.execute(f'SELECT u{user1_id} FROM Time WHERE User_id = {user2_id}').fetchone()[0]
    if friends_time is None:
        friends_time = 0
    req = f'UPDATE Time SET u{user1_id} = {delta_time + friends_time} WHERE User_id = {user2_id}'
    req2 = f'UPDATE Time SET u{user2_id} = {delta_time + friends_time} WHERE User_id = {user1_id}'
    cur.execute(req)
    cur.execute(req2)
    conn.commit()
    conn.close()


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

        if before.channel != after.channel:
            if before.channel is None:
                print(member.name, 'has connected to', after.channel.name, '\n')

                fill_id_table(member)

                self.active_users[member.id] = datetime.now()
                print('ACTIVE USERS', self.active_users)
                if after.channel.id not in  self.pairs.keys():
                    self.pairs.setdefault(after.channel.id, [member.id])
                else:
                    self.pairs[after.channel.id].append(member.id)
                print('PAIRS', self.pairs)

            elif after.channel is not None:
                print(member.name, 'has disconnected from', before.channel.name, '\n')
                print(member.name, 'has connected to', after.channel.name, '\n')
                # заполняем бд данными из active_users

                friends = self.pairs[before.channel.id].remove(member.id)
                for friend in friends:
                    fill_time_db(member.id, self.active_users[member.id], friend, self.active_users[friend])

                if not self.pairs[before.channel.id]:
                    del self.pairs[before.channel.id]
                self.active_users[member.id] = datetime.now()
                print(self.active_users)
                self.pairs.setdefault(after.channel.id, []).append(member.id)
                print(self.pairs)

            else:
                print(member.name, 'has disconnected from', before.channel.name, '\n')
                print('DEBUG', self.pairs[before.channel.id])
                self.pairs[before.channel.id].remove(member.id)
                friends = self.pairs[before.channel.id]
                print('FRIENDS', friends)
                if friends is not None:
                    for friend in friends:
                        fill_time_db(member.id, self.active_users[member.id], friend, self.active_users[friend])

                if not self.pairs[before.channel.id]:
                    del self.pairs[before.channel.id]
                if not self.active_users[member.id]:
                    del self.active_users[member.id]
                print('ACTIVE', self.active_users)
                print('PAIRS', self.pairs)

        '''
        if before.self_mute is False and after.self_mute is True:
            print(member.name, 'has muted in', before.channel.name, '\n')
        if before.self_mute is True and after.self_mute is False:
            print(member.name, 'has unmuted in', before.channel.name, '\n')
        '''


def setup(bot):
    bot.add_cog(VoiceListener(bot))
