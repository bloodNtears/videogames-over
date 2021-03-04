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
        await member.send(f'Hi {member.name}, welcome to the club')


bot = MyClient(command_prefix='!', intents=discord.Intents.all())
setup(bot)

bot.run(TOKEN)
