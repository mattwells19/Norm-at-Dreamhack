from discord import Color, Embed
from Types import BallChaser, LobbyDetails, Team
from typing import List


def BaseEmbed(title: str, description: str, color: Color) -> Embed:
    return Embed(
        title=title,
        description=description,
        color=color,
    ).set_thumbnail(
        url="https://raw.githubusercontent.com/mattwells19/Norm-at-Dreamhack/main/media/norm_still.png"
    )


def ErrorEmbed(title: str, desc: str) -> Embed:
    return BaseEmbed(
        title=":x:\t{0}".format(title),
        description="{0}".format(desc),
        color=Color.red(),
    )


def QueueUpdateEmbed(title: str, desc: str) -> Embed:
    return BaseEmbed(
        title="{0}".format(title),
        description="{0}".format(desc),
        color=Color.green(),
    )


def AdminEmbed(title: str, desc: str) -> Embed:
    return BaseEmbed(
        title=":exclamation:\t{0}".format(title),
        description="{0}".format(desc),
        color=Color.dark_gold(),
    )


def InfoEmbed(title: str, desc: str) -> Embed:
    return BaseEmbed(
        title="{0}".format(title),
        description="{0}".format(desc),
        color=Color.blue(),
    )


def CaptainsAlreadySetEmbed(blueCap: BallChaser, orangeCap: BallChaser, teamToPick: Team, playerList: str) -> Embed:
    embed = InfoEmbed(
        title="Captains Already Set",
        desc="š· Blue Team Captain š·: " + blueCap.mention +
        "\n\nš¶ Orange Team Captain š¶: " + orangeCap.mention
    ).add_field(
        name="\u200b",
        value="\u200b",
        inline=False
    )

    if (teamToPick == Team.BLUE):
        embed.add_field(
            name="It is š· " + blueCap.name + "'s š· turn to pick",
            value="Type `!pick` and mention a player from the queue below.",
            inline=False
        )
    else:
        embed.add_field(
            name="It is š¶ " + orangeCap.name + "'s š¶ turn to pick",
            value="Please pick two players.\nEx: `!pick @Twan @Tux`",
            inline=False
        )

    embed.add_field(
        name="\u200b",
        value="\u200b",
        inline=False
    ).add_field(
        name="Available picks",
        value=playerList,
        inline=False
    )

    return embed


def CaptainsPopEmbed(blueCap: BallChaser, orangeCap: BallChaser, playerList: str) -> Embed:
    return QueueUpdateEmbed(
        title="Captains",
        desc="š· BLUE Team Captain š·: " + blueCap.mention +
        "\n\nš¶ ORANGE Team Captain š¶: " + orangeCap.mention
    ).add_field(
        name="\u200b",
        value="\u200b",
        inline=False
    ).add_field(
        name="š· " + blueCap.mention + " š· picks first",
        value="Type **!pick** and mention a player from the queue below.",
        inline=False
    ).add_field(
        name="\u200b",
        value="\u200b",
        inline=False
    ).add_field(
        name="Available picks",
        value=playerList,
        inline=False
    )


def PlayersSetEmbed(blueTeam: List[BallChaser], orangeTeam: List[BallChaser], lobbyDetails: LobbyDetails) -> Embed:
    return QueueUpdateEmbed(
        title="Teams are Set!",
        desc=""
    ).add_field(
        name="š· BLUE TEAM š·",
        value="\n".join([player.mention for player in blueTeam]),
        inline=False
    ).add_field(
        name="š¶ ORANGE TEAM š¶",
        value="\n".join([player.mention for player in orangeTeam]),
        inline=False
    ).add_field(
        name="\u200b",
        value="\u200b",
        inline=False
    ).add_field(
        name="LOBBY DETAILS",
        value="Username: {username}\nPassword: {password}\n\nBlue team makes the lobby, Orange team joins.".format(
            username=lobbyDetails.username, password=lobbyDetails.password),
        inline=False
    )


def HelpEmbed() -> Embed:
    return Embed(
        title="Norm@Dreamhack Commands",
        color=0x38761D
    ).add_field(
        name="!q",
        value="Adds you to the queue.",
        inline=False
    ).add_field(
        name="!leave",
        value="Removes you from the queue.",
        inline=False
    ).add_field(
        name="!list",
        value="Lists the current queue.",
        inline=False
    ).add_field(
        name="!report",
        value="Reports the result of your queue. Use this command followed by the color of the winning team.",
        inline=False
    ).add_field(
        name="!leaderboard",
        value="Shows the top 5 players on the leaderboard.",
        inline=False
    ).add_field(
        name="!leaderboard me",
        value="Shows your rank on the leaderboard.",
        inline=False
    ).add_field(
        name='!norm, !asknorm, or !8ball',
        value='Will respond to a yes/no question. Good for predictions',
        inline=False
    ).add_field(
        name="!help",
        value="This command :O",
        inline=False
    ).set_thumbnail(
        url="https://raw.githubusercontent.com/ClamSageCaleb/UNCC-SIX-MANS/master/media/49ers.png"
    ).set_footer(
        text="Developed by Tux and h"
    )
