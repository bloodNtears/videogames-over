from discord.ext import commands
import discord
from threading import Thread




class VoiceListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        active_users = dict()  # all users who are in voice chat rn; structure: {user1: join_time, user2: join_time ...}

        pairs = dict()  # dict of pairs related to a specific voice channel;
        # structure: {voice_channel1_id: [user1, user2, user3],
        # voice_channel2_id: [user4, user5, user6]
        # }

        # for example:
        # if user1 leaves, we scan pairs dict
        # 1) start function fill_db with ([user1, join_time], [user2, join_time]) and ([user1, join_time], [user3, join_time])
        # 2) delete user1 from active_users dict

        # разобраться с переключением в другой войс

        if before.channel != after.channel and after.channel is not None:
            print(member.name, 'has connected to', after.channel.name, '\n')
            # database request + start timer
        elif before.channel != after.channel or after.channel is None:
            print(member.name, 'has disconnected from', before.channel.name, '\n')
            # database request + stop timer


        if before.self_mute is False and after.self_mute is True:
            print(member.name, 'has muted in', before.channel.name, '\n')
        if before.self_mute is True and after.self_mute is False:
            print(member.name, 'has unmuted in', before.channel.name, '\n')


def setup(bot):
    bot.add_cog(VoiceListener(bot))
