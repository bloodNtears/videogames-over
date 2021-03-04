from discord.ext import commands
import discord


class VoiceListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

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
