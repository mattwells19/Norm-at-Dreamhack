from os import path, mkdir, getenv
from pathlib import Path
from tinydb import TinyDB


basePath = path.join(Path.home(), "SixMans")
configPath = path.join(basePath, "config.json")
dataPath = path.join(basePath, "data.json")

if (not path.exists(basePath)):
    mkdir(basePath)

db = TinyDB(dataPath, indent=2)
currQueue = db.table("queue")
activeMatches = db.table("activeMatches")
leaderboard = db.table("leaderboard")


def getDiscordToken() -> str:
    token = getenv('token')

    return token


def getChannelIds() -> dict:
    return {
        "queue_channels": int(getenv("queue_channels", -1)),
        "report_channels": int(getenv("report_channels", -1)),
        "leaderboard_channel": int(getenv("leaderboard_channel", -1)),
    }
