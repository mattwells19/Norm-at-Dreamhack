from discord import Embed, Member, channel as Channel
import Queue
import Leaderboard
from typing import List
from Types import Team
from math import ceil
from EmbedHelper import \
    ErrorEmbed,\
    QueueUpdateEmbed,\
    InfoEmbed,\
    CaptainsAlreadySetEmbed,\
    CaptainsPopEmbed,\
    PlayersSetEmbed
from Commands.Utils import generateLobbyDetails, updateLeaderboardChannel, orangeTeamPick, blueTeamPick


class PlayerQueueResponse:
    embed = None
    sendPrivately = False


def playerQueue(player: Member, reportChannelId: int, *arg) -> PlayerQueueResponse:
    """
        Adds the author to the Queue for the specified amount of time.

        Parameters:
            player: discord.Member - The author of the message. The person being removed from the queue.
            *arg: tuple - The args passed into the client function.

        Returns:
            dicord.Embed - The embedded message to respond with.
    """
    queue_length = Queue.getQueueLength()
    response = PlayerQueueResponse()

    try:
        queueTime = int(arg[0]) if len(arg) > 0 else 60
    except ValueError:  # if someone doesn't input a number we default to 60 minutes
        queueTime = 60

    # this converts the input to the next highest value of 10
    # ex: 14 -> 20, 9 -> 10, -5 -> 10, 3 -> 10
    queueTime = int(ceil(queueTime / 10)) * 10

    # minimum queue time of 10 minutes and maximum of 60 minutes
    if (queueTime < 10):
        queueTime = 10
    elif (queueTime > 60):
        queueTime = 60

    if (Queue.isPlayerInQueue(player)):
        Queue.resetPlayerQueueTime(player, queueTime)
        response.embed = QueueUpdateEmbed(
            title="Already in Queue, Queue Time Reset",
            desc="You're already in the queue, but your queue time has been reset to {0} minutes.".format(queueTime),
        )

    elif (Leaderboard.getActiveMatch(player) is not None):
        if (reportChannelId != -1):
            response.embed = ErrorEmbed(
                title="Match Still Active",
                desc="Your previous match has not been reported yet."
                " Report your match in <#{0}> and try again.".format(reportChannelId),
            )
        else:
            response.embed = ErrorEmbed(
                title="Match Still Active",
                desc="Your previous match has not been reported yet."
                " Report your match and try again.",
            )

    elif (queue_length == 0):
        Queue.addToQueue(player, queueTime)

        response.embed = QueueUpdateEmbed(
            title="Queue Started",
            desc="{0} wants to queue!\n\nQueued for {1} minutes.\n\n"
            "Type **!q** to join".format(player.mention, queueTime),
        )

    elif (queue_length == 5):
        Queue.addToQueue(player, queueTime)
        randomTeamsEmbed = random()
        response.embed = randomTeamsEmbed
        response.sendPrivately = True

    else:
        Queue.addToQueue(player, queueTime)
        playerList = Queue.getQueueList()

        response.embed = QueueUpdateEmbed(
            title="Player Added to Queue",
            desc=player.mention + " has been added to the queue for " + str(queueTime) + " minutes."
        ).add_field(
            name="Current Queue " + str(queue_length + 1) + "/6",
            value=playerList
        )

    return response


def leave(player: Member) -> Embed:
    """
        Removes author from the Queue.

        Parameters:
            player: discord.Member - The author of the message. The person being removed from the queue.

        Returns:
            dicord.Embed - The embedded message to respond with.
    """
    username = player.display_name

    if (Queue.queueAlreadyPopped()):
        return ErrorEmbed(
            title="Queue Already Popped",
            desc="TOO LATE! You should've left before captains were picked."
        )

    if (Queue.isPlayerInQueue(player)):

        Queue.removeFromQueue(player)
        playerList = Queue.getQueueList()

        if(Queue.getQueueLength() != 0):
            return QueueUpdateEmbed(
                title="Player Left Queue",
                desc=username + " has left the queue."
            ).add_field(
                name="Remaining Players (" + str(Queue.getQueueLength()) + "/6)",
                value=playerList
            )

        return QueueUpdateEmbed(
            title="Player Left Queue",
            desc=username + " has left the queue.\n\n"
            "Queue is now empty."
        )

    return ErrorEmbed(
        title="Not in Queue",
        desc="You are not in the queue, type **!q** to join"
    )


def listQueue(player: Member):
    """
        Lists the players currently in the queue with timestamps. Will show captains if captains are set.

        Parameters:
            player: dicord.Member - The author of the message.

        Returns:
            dicord.Embed - The embedded message to respond with.
    """
    if (Queue.getQueueLength() == 0):
        return QueueUpdateEmbed(
            title="Queue is Empty",
            desc="Join the queue by typing **!q**"
        )
    if (Queue.queueAlreadyPopped()):
        return captains(player)

    playerList = Queue.getQueueList()
    return QueueUpdateEmbed(
        title="Current Queue (" + str(Queue.getQueueLength()) + "/6)",
        desc=playerList
    )


def captains(player: Member):
    """
        Pops the queue and randomly assigns two captains. Will show captains if captains are already set.

        Parameters:
            player: dicord.Member - The author of the message.

        Returns:
            dicord.Embed - The embedded message to respond with.
    """
    if (Queue.getQueueLength() != 6):
        return ErrorEmbed(
            title="Queue is Not Full",
            desc="You cannot pop a queue until is full."
        )

    if (not Queue.isPlayerInQueue(player)):
        return ErrorEmbed(
            title="Not in Queue",
            desc="You are not in the queue, therefore you cannot pop the queue."
        )

    blueCap, orangeCap = Queue.captainsPop()
    playerList = Queue.getQueueList(includeTimes=False)

    if (Queue.queueAlreadyPopped()):
        blueTeam, _ = Queue.getTeamList()

        return CaptainsAlreadySetEmbed(
            blueCap,
            orangeCap,
            Team.BLUE if len(blueTeam) == 1 else Team.ORANGE,
            playerList
        )

    return CaptainsPopEmbed(
        blueCap,
        orangeCap,
        playerList
    )


def random():
    """
        Pops the queue and randomly assigns players to teams.

        Returns:
            dicord.Embed - The embedded message to respond with.
    """
    # if (Queue.queueAlreadyPopped()):
    #     return ErrorEmbed(
    #         title="Captains Already Chosen",
    #         desc="You cannot change your mind once you pick captains."
    #     )

    # if (Queue.getQueueLength() != 6):
    #     return ErrorEmbed(
    #         title="Queue is Not Full",
    #         desc="You cannot pop a queue until is full."
    #     )

    # if (not Queue.isPlayerInQueue(player)):
    #     return ErrorEmbed(
    #         title="Not in Queue",
    #         desc="You are not in the queue, therefore you cannot pop the queue."
    #     )

    blueTeam, orangeTeam = Queue.randomPop()
    lobbyDetails = generateLobbyDetails()
    Leaderboard.startMatch(blueTeam, orangeTeam)
    return PlayersSetEmbed(blueTeam, orangeTeam, lobbyDetails)


def leaderboard(author: Member, mentions: List[Member], lbChannelId: int, *arg) -> Embed:
    """
        Shows the leaderboard. Shows top 5 if no one mentioned. Shows player stats if mentioned or used keyword "me".

        Parameters:
            author: discord.Member - The author of the message
            mentions: List[discord.Member] - The mentions in the message.
            *arg - The rest of the args in the message.

        Returns:
            dicord.Embed - The embedded message to respond with.
    """
    playerMentioned: bool = len(mentions) == 1
    selfRank: bool = len(arg) == 1 and arg[0] == "me"

    if (playerMentioned or selfRank):

        player = mentions[0] if playerMentioned else author

        players_rank = Leaderboard.showLeaderboard(player)

        if (type(players_rank) == str):
            return InfoEmbed(
                title="Leaderboard Placement for {0}".format(player.name),
                desc=players_rank
            )

        return ErrorEmbed(
            title="No Matches Played",
            desc="{0} hasn't played any matches and won't show up on the leaderboard.".format(players_rank.mention)
        )

    if (len(arg) == 0 and len(mentions) == 0):
        viewFullLb = "\nTo see the full leaderboard, visit <#{0}>.".format(lbChannelId) if (lbChannelId != -1) else ""
        return InfoEmbed(
            title="UNCC 6 Mans | Top 5",
            desc=Leaderboard.showLeaderboard(limit=5) + viewFullLb
        )

    return ErrorEmbed(
        title="Leaderboard Command Help",
        desc="Mention someone to see their rank, use 'me' to see your rank,"
        " include nothing to see the top 5 on the leaderboard."
    )


async def report(player: Member, lbChannel: Channel, *arg) -> Embed:
    """
        Used to report the winning team of the series.

        Parameters:
            player: discord.Member - The author of the message.
            lbChannel: discord.Channel - The specified leaderboard channel object

        Returns:
            dicord.Embed - The embedded message to respond with.
    """
    if (len(arg) == 1 and (str(arg[0]).lower() == Team.BLUE or str(arg[0]).lower() == Team.ORANGE)):
        msg = Leaderboard.reportMatch(player, arg[0])

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

            return QueueUpdateEmbed(
                title="Match Reported",
                desc=msg[19:]
            )

        return InfoEmbed(
            title="Match Reported, Needs Confirmation",
            desc=msg
        )

    return ErrorEmbed(
        title="Incorrect Report Format",
        desc="Report only accepts 'blue' or 'orange' as the winner of the match.\n\n"
        "Use the format: `!report blue`"
    )


def pick(player: Member, mentions: List[Member]) -> List[Embed]:
    """
        Assigns picked players to their respective teams.

        Parameters:
            player: discord.Member - The author of the message
            mentions: List[discord.Member] - The mentions in the message. The players picked.

        Returns:
            List[dicord.Embed] - A list of embedded messages to respond with.
    """
    if (not Queue.queueAlreadyPopped()):
        return ErrorEmbed(
            title="Captains Not Set",
            desc="If queue is full, please type **!captains**"
        )

    blueCap, orangeCap = Queue.captainsPop()

    if (Queue.validateBluePick(player)):
        return [blueTeamPick(mentions, blueCap, orangeCap)]

    if (Queue.validateOrangePick(player)):
        return orangeTeamPick(mentions, blueCap, orangeCap)

    blueTeam, _ = Queue.getTeamList()
    if (len(blueTeam) == 1):
        return [ErrorEmbed(
            title="Not the Blue Captain",
            desc="You are not ???? BLUE Team Captain ????\n\n"
            "???? BLUE Team Captain ???? is: " + blueCap.mention
        )]

    return [ErrorEmbed(
        title="Not the Orange Captain",
        desc="You are not ???? ORANGE Team Captain ???? \n\n"
        "???? ORANGE Team Captain ???? is: " + orangeCap.mention
    )]


def checkQueueTimes() -> List[Embed] or None:
    """
        Checks the queue times for each player and returns warning or removal embeds if applicable

        Parameters:
            None.

        Returns:
            List[Embed] or None - A list of embeds to send or nothing
    """
    if (Queue.getQueueLength() == 0 or Queue.queueAlreadyPopped()):
        return None

    warn_players, removed_players = Queue.checkQueueTimes()

    if (len(warn_players) == 0 and len(removed_players) == 0):
        return None

    embeds = []

    if (len(warn_players) > 0):
        warn_str = ",".join([player.mention for player in warn_players])
        embeds.append(InfoEmbed(
            title="Stale Player Queue Warning",
            desc=warn_str + " will be removed from the queue in 5 minutes.\n\n"
            "To stay in the queue, type **!q**"
        ))

    if (len(removed_players) > 0):
        rem_str = ",".join([player.mention for player in removed_players])
        playerList = Queue.getQueueList()
        if(Queue.getQueueLength() != 0):
            embeds.append(QueueUpdateEmbed(
                title="Queue Stale Players Removed",
                desc=rem_str + " have been removed from the queue."
            ).add_field(
                name="Remaining Players (" + str(Queue.getQueueLength()) + "/6)",
                value=playerList
            ))
        else:
            embeds.append(QueueUpdateEmbed(
                title="Queue Stale Players Removed",
                desc=rem_str + " have been removed from the queue.\n\n" + "Queue is now empty."
            ))

    return embeds
