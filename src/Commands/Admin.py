from CheckForUpdates import updateBot
from EmbedHelper import AdminEmbed, ErrorEmbed, QueueUpdateEmbed
from typing import List
from Types import Team
from bot import __version__
from discord import Role, Embed, Member, channel as Channel
import Queue
from Commands.Utils import updateLeaderboardChannel
from Leaderboard import brokenQueue as breakQueue, reportMatch


def brokenQueue(roles: List[Role], mentions: List[Member]) -> Embed:
    """
        Removes the active match that the mentioned player is in.

        Parameters:
            roles: List[discord.Role] - The roles of the author of the message.
            mentions: List[dicord.Member] - The list of members mentioned in the message.

        Returns:
            dicord.Embed - The embedded message to respond with.
    """

    if (Queue.isBotAdmin(roles)):
        if (len(mentions) != 1):
            return ErrorEmbed(
                title="Could Not Remove Queue",
                desc="You must mention one player who is in the match you want to remove."
            )
        else:
            msg = breakQueue(mentions[0])

            if (":white_check_mark:" in msg):
                return QueueUpdateEmbed(
                    title="Popped Queue Removed",
                    desc="The popped queue has been removed from active matches."
                )

            return ErrorEmbed(
                title="Could Not Remove Queue",
                desc=msg
            )
    else:
        return AdminEmbed(
            title="Permission Denied",
            desc="You do not have the strength to break queues. Ask an admin if you need to break a queue."
        )


async def forceReport(mentions: List[Member], roles: List[Role], lbChannel: Channel, *arg) -> Embed:
    if (Queue.isBotAdmin(roles)):
        if (len(mentions) == 1):
            if (len(arg) == 2 and (str(arg[1]).lower() == Team.BLUE or str(arg[1]).lower() == Team.ORANGE)):

                player = mentions[0]
                msg = reportMatch(player, arg[1], True)
                
                if (":x:" in msg):
                    return ErrorEmbed(
                        title="Match Not Found",
                        desc=msg[4:]
                    )

                if (":white_check_mark:" in msg):

                    try:
                        # if match was reported successfully, update leaderboard channel
                        await updateLeaderboardChannel(lbChannel)
                    except Exception as e:
                        print("! Norm does not have access to update the leaderboard.", e)

                return AdminEmbed(
                    title="Match Force Reported Successfully",
                    desc="You may now re-queue."
                )
            else:
                return ErrorEmbed(
                    title="You Must Report A Valid Team",
                    desc="You did not supply a valid team to report."
                )
        else:
            return ErrorEmbed(
                title="Could Not Report The Match",
                desc="You must mention one player who is in the match you want to report."
            )
    else:
        return ErrorEmbed(
            title="Permission Denied",
            desc="You do not have the strength to force report matches. Ask an admin if you need to force report a match."
        )


def update(roles: List[Role]) -> Embed:
    """
        Middleware function to check author's permissions before running the update script.
        Parameters:
            roles: List[discord.Role] - The roles of the author of the message.
        Returns:
            dicord.Embed - The embedded message to respond with.
    """
    if(Queue.isBotAdmin(roles)):
        updateBot()
        return AdminEmbed(
            title="Already Up to Date",
            desc="Current version: v{0}".format(__version__)
        )

    return AdminEmbed(
        title="Permission Denied",
        desc="You do not have permission to check for updates."
    )


def clear(roles: List[Role]) -> Embed:
    """
        Clears the current queue if the author has the Bot Admin role.

        Parameters:
            roles: List[discord.Role] - The roles of the author of the message.

        Returns:
            dicord.Embed - The embedded message to respond with.
    """
    if(Queue.isBotAdmin(roles)):
        Queue.clearQueue()
        return AdminEmbed(
            title="Queue Cleared",
            desc="The queue has been cleared by an admin.  <:UNCCfeelsgood:538182514091491338>"
        )

    return ErrorEmbed(
        title="Permission Denied",
        desc="You do not have permission to clear the queue."
    )


def kick(mentions: List[Member], roles: List[Role]) -> Embed:
    """
        Kicks the mentioned player from the queue. Requires Bot Admin role.

        Parameters:
            mentions: List[discord.Member] - The mentions in the message.
            roles: List[discord.Role] - The roles of the author of the message.

        Returns:
            dicord.Embed - The embedded message to respond with.
    """
    if (not Queue.isBotAdmin(roles)):
        return ErrorEmbed(
            title="Permission Denied",
            desc="You do not have the leg strength to kick other players."
        )

    if (len(mentions) != 1):
        return ErrorEmbed(
            title="Did Not Mention a Player",
            desc="Please mention a player in the queue to kick."
        )

    if (Queue.queueAlreadyPopped()):
        return ErrorEmbed(
            title="Queue Already Popped",
            desc="Can't kick players while picking teams."
        )

    if (Queue.getQueueLength() == 0):
        return ErrorEmbed(
            title="Queue is Empty",
            desc="The queue is empty, what are you doing?"
        )

    player = mentions[0]
    if (Queue.isPlayerInQueue(player)):
        Queue.removeFromQueue(player)
        return AdminEmbed(
            title="Kicked Player",
            desc="Removed " + player.display_name + " from the queue"
        )

    return ErrorEmbed(
        title="User Not in Queue",
        desc="To see who is in current queue, type: **!list**"
    )


# Disabling command as it does not work with the new executable.
# TODO: Find a new way to restart Norm since he is now an executable
def restart():
    return AdminEmbed(
        title="Command Diasbled",
        desc="This command is temporarily disabled."
    )

    # if(Queue.isBotAdmin(ctx.message.author.roles)):
    #     await ctx.send("Bot restarting...hopefully this fixes everything <:UNCCfeelsgood:538182514091491338>")
    #     os.remove("./data/queue.json")
    #     print("Restarting...")
    #     subprocess.call(["python", ".\\src\\bot.py"])
    #     sys.exit()
    # else:
    #     await ctx.send("You do not have permission to restart me.")
