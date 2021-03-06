__author__ = "Matt Wells (Tux) / Austin Baker (h)"
__copyright__ = "Copyright 2021, MIT License"
__credits__ = "Matt Wells (Tux) / Austin Baker (h)"
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Matt Wells (Tux) / Austin Baker (h)"
__email__ = "mattwells878@gmail.com / noise.9no@gmail.com"
__credits__ = "Forked from https://github.com/ClamSageCaleb/UNCC-SIX-MANS to be modified for UNCC event with Dreamhack."

import asyncio
import AWSHelper as AWS
from DataFiles import getDiscordToken, getChannelIds
from EmbedHelper import ErrorEmbed, AdminEmbed, HelpEmbed
from asyncio import sleep as asyncsleep
import discord
from discord.ext.commands import Bot, CommandNotFound
from random import randint
from time import sleep
from typing import List
from Commands import EasterEggs, SixMans, Testing, Admin, Utils
from discord.embeds import Embed
from Queue import getBallChaserList

# Bot prefix and Discord Bot token
BOT_PREFIX = ("!")

# Creates the Bot with name 'client'
client = Bot(command_prefix=BOT_PREFIX)
client.remove_command('help')

pikaO = 1

# Channel ID's
LEADERBOARD_CH_ID = -1
QUEUE_CH_ID = -1
REPORT_CH_ID = -1

# Leaderboard Channel Object
LB_CHANNEL: discord.channel = None

"""
    Discord Events
"""


@client.event
async def on_message(message: discord.Message):
    isReport = "!report" in message.content.lower()
    if (message.author != client.user):

        if (
            isReport and
            QUEUE_CH_ID != -1 and
            message.channel.id == QUEUE_CH_ID and
            message.channel.id != REPORT_CH_ID
        ):
            channel = client.get_channel(message.channel.id)
            await channel.send(embed=ErrorEmbed(
                title="Can't Do That Here",
                desc="You can only report matches in the <#{0}> channel.".format(REPORT_CH_ID)
            ))

        elif (
            not isReport and
            REPORT_CH_ID != -1 and
            message.channel.id == REPORT_CH_ID and
            message.channel.id != QUEUE_CH_ID
        ):
            channel = client.get_channel(message.channel.id)
            await channel.send(embed=ErrorEmbed(
                title="Can't Do That Here",
                desc="You can only use that command in the <#{0}> channel.".format(QUEUE_CH_ID)
            ))
        else:
            await client.process_commands(message)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandNotFound):
        return
    print(error)


@client.event
async def on_ready():
    global LB_CHANNEL

    await client.change_presence(activity=discord.Game(name="6 mans"))
    print("Logged in as " + client.user.name + " version " + __version__)

    try:
        channel = client.get_channel(QUEUE_CH_ID)
        await channel.send(embed=AdminEmbed(
            title="Norm@Dreamhack Started",
            desc="Current version: v{0}".format(__version__)
        ))
    except Exception as e:
        print("! Norm does not have access to post in the queue channel.", e)

    try:
        AWS.readRemoteLeaderboard()
        if (LEADERBOARD_CH_ID != -1):
            LB_CHANNEL = client.get_channel(LEADERBOARD_CH_ID)
            # update leaderboard channel when remote leaderboard pulls
            await Utils.updateLeaderboardChannel(LB_CHANNEL)
    except Exception as e:
        # this should only throw an exception if the Leaderboard file does not exist or the credentials are invalid
        print(e)


async def stale_queue_timer():
    await client.wait_until_ready()
    channel = client.get_channel(QUEUE_CH_ID)

    while True:

        embeds = SixMans.checkQueueTimes()

        if (embeds is not None):
            try:
                for embed in embeds:
                    await channel.send(embed=embed)
            except Exception as e:
                print("! Norm does not have access to post in the queue channel.", e)
                return

        await asyncsleep(60)  # check queue times every minute

"""
    Discord Commands - Queue Commands
"""


@client.command(name='q', aliases=['addmepapanorm', 'Q', 'addmebitch', 'queue', 'join'], pass_context=True)
async def q(ctx, *arg):
    players = getBallChaserList()
    response = SixMans.playerQueue(ctx.message.author, REPORT_CH_ID, *arg)
    author = ctx.message.author

    if (response.sendPrivately):
        async def sendPrivateMsg(playerId: str):
            user = await client.fetch_user(playerId)
            if (not user.bot):
                await user.send(embed=response.embed)

        players.append(author)
        # perform each async task synchronously since we don't care about order of completion
        await asyncio.wait([sendPrivateMsg(str(p.id)) for p in players])

    await ctx.send(embed=response.embed)


@client.command(name='leave', aliases=['yoink', 'gtfo', 'getmethefuckouttahere'], pass_context=True)
async def leave(ctx):
    await ctx.send(embed=SixMans.leave(ctx.message.author))


@client.command(name='kick', aliases=['remove', 'yeet'], pass_context=True)
async def kick(ctx):
    await ctx.send(embed=Admin.kick(ctx.message.mentions, ctx.message.author.roles))


@client.command(name='flip', aliases=['coinflip', 'chance', 'coin'], pass_context=True)
async def coinFlip(ctx):
    if (randint(1, 2) == 1):
        await q(ctx)
    else:
        await leave(ctx)


@client.command(name='listq', aliases=['list', 'listqueue', 'show', 'showq', 'showqueue', 'inq', 'sq', 'lq', 'status', 'showmethefknqueue', '<:who:599055076639899648>'], pass_context=True)  # noqa
async def listq(ctx):
    await ctx.send(embed=SixMans.listQueue(ctx.message.author))


# @client.command(name='rnd', aliases=['random', 'idontwanttopickteams', 'fuckcaptains'], pass_context=True)
# async def random(ctx):
#     await ctx.send(embed=SixMans.random(ctx.message.author))


# @client.command(name='captains', aliases=['cap', 'iwanttopickteams', 'Captains', 'captain', 'Captain', 'Cap'], pass_context=True)  # noqa
# async def captains(ctx):
#     await ctx.send(embed=SixMans.captains(ctx.message.author))


# @client.command(name='pick', aliases=['add', 'choose', '<:pick:628999871554387969>'], pass_context=True)
# async def pick(ctx):
#     embeds = SixMans.pick(ctx.message.author, ctx.message.mentions)
#     for embed in embeds:
#         await ctx.send(embed=embed)


@client.command(name="report", pass_contex=True)
async def reportMatch(ctx, *arg):
    await ctx.send(embed=await SixMans.report(ctx.message.author, LB_CHANNEL, *arg))


@client.command(name="forceReport", aliases=["fr", "force"], pass_context=True)
async def forceReport(ctx, *arg):
    await ctx.send(embed=await Admin.forceReport(ctx.message.mentions, ctx.message.author.roles, LB_CHANNEL, *arg))


@client.command(name="leaderboard", aliases=["lb", "standings", "rank", "rankings", "stonks"], pass_contex=True)
async def showLeaderboard(ctx, *arg):
    await ctx.send(embed=SixMans.leaderboard(ctx.message.author, ctx.message.mentions, LEADERBOARD_CH_ID, *arg))


@client.command(name="brokenq", aliases=["requeue", "re-q"], pass_contex=True)
async def removeLastPoppedQueue(ctx):
    await ctx.send(embed=Admin.brokenQueue(ctx.message.author.roles, ctx.message.mentions))


@client.command(name='clear', aliases=['clr', 'reset'], pass_context=True)
async def clear(ctx):
    await ctx.send(embed=Admin.clear(ctx.message.author.roles))


@client.command(name="fill", pass_context=True)
async def fill(ctx):
    if (__debug__):
        await ctx.send(embed=Testing.fill(ctx.message.author.roles))


@client.command(name="fillCap", pass_context=True)
async def fillCap(ctx):
    if (__debug__):
        await ctx.send(embed=Testing.fillCap(ctx.message.author.roles))


@client.command(name="flipCap", pass_context=True)
async def flipCap(ctx):
    if (__debug__):
        await ctx.send(embed=Testing.flipCap(ctx.message.author.roles))


@client.command(name="flipReport", pass_context=True)
async def flipReport(ctx):
    if (__debug__):
        await ctx.send(embed=Testing.flipReport(ctx.message.author.roles))


@client.command(name='restart', aliases=['restartbot'], pass_context=True)
async def restart(ctx):
    await ctx.send(embed=Admin.restart())


@client.command(name="update", pass_context=True)
async def update(ctx):
    await ctx.send(embed=AdminEmbed(
        title="Checking For Updates",
        desc="Please hang tight."
    ))
    await ctx.send(embed=Admin.update(ctx.message.author.roles))


"""
    Discord Commands - Easter Eggs
"""


@client.command(name='twan', aliases=['<:twantheswan:540327706076905472>'], pass_context=True)
async def twan(ctx):
    await ctx.send(EasterEggs.Twan())


@client.command(name='sad', aliases=[':('], pass_context=True)
async def sad(ctx):
    await ctx.send(EasterEggs.Sad())


@client.command(name='smh', aliases=['myhead'], pass_context=True)
async def smh(ctx):
    await ctx.send(EasterEggs.Smh())


@client.command(name='turhols', aliases=['<:IncognitoTurhol:540327644089155639>'], pass_context=True)
async def turhols(ctx):
    await ctx.send(EasterEggs.Turhols())


@client.command(name='pika', aliases=['<:pika:538182616965447706>'], pass_context=True)
async def pika(ctx):
    await ctx.send(EasterEggs.Pika())


@client.command(name='zappa', aliases=['zapp', 'zac', '<:zappa:632813684678197268>', '<:zapp:632813709579911179>'], pass_context=True)  # noqa
async def zappa(ctx):
    await ctx.send(EasterEggs.Zappa())


@client.command(name='duis', pass_context=True)
async def duis(ctx):
    await ctx.send(EasterEggs.Duis())


@client.command(name='normq', pass_context=True)
async def normq(ctx):
    messages: List[str or Embed] = EasterEggs.NormQ()
    for msg in messages:
        if (isinstance(msg, Embed)):
            await ctx.send(embed=msg)
        else:
            await ctx.send(msg)


@client.command(name='teams', aliases=['uncc'], pass_context=True)
async def teams(ctx):
    await ctx.send(EasterEggs.Teams())


@client.command(name='8ball', aliases=['norm', 'asknorm', 'eight_ball', 'eightball', '8-ball'], pass_context=True)
async def eight_ball(ctx):
    await ctx.send(EasterEggs.EightBall(ctx.message.author))


@client.command(name='fuck', aliases=['f', 'frick'], pass_context=True)
async def fuck(ctx):
    await ctx.send("u")


@client.command(name="help", pass_context=True)
async def help(ctx):
    await ctx.send(embed=HelpEmbed())


"""
    Main function
"""


def main():
    global LEADERBOARD_CH_ID, QUEUE_CH_ID, REPORT_CH_ID

    token = getDiscordToken()
    if (token == ""):
        print("No Discord Bot token provided.")
    AWS.init()

    channels = getChannelIds()
    LEADERBOARD_CH_ID = channels["leaderboard_channel"]
    QUEUE_CH_ID = channels["queue_channels"]
    REPORT_CH_ID = channels["report_channels"]

    if (QUEUE_CH_ID != -1):
        client.loop.create_task(stale_queue_timer())
    else:
        print("Stale queue feature disabled as no queue channel id was specified.")

    try:
        client.run(token)
    except discord.errors.LoginFailure:
        print(
            "! There was an error with the token you provided. Please verify your bot token and try again.\n"
            "If you need help locating the token for your bot, visit https://www.writebots.com/discord-bot-token/"
        )
        sleep(5)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
