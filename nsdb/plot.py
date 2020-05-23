"""
This script ....
"""
import argparse
import os
import matplotlib.pyplot as plt

import Database


def partitionStatus(cursor, i, plotDir, dataDir):
    plt.figure()
    figname = plotDir + str(i)

    query = """SELECT status, count(id)
    FROM partition
    GROUP BY status;"""

    cursor.execute(query,)
    data = cursor.fetchall()
    with open(dataDir + str(i) + ".txt", "w") as file:
        file.write(str(data))
    plt.title("Status of parsing partitions")
    plt.xlabel("Status")
    plt.ylabel("Number of Partitions")
    plt.bar(*zip(*data))
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def distributionOfMainEdits(cursor, i, plotDir, dataDir):
    figname = plotDir + str(i)
    plt.figure()

    query = """SELECT
    (SELECT count(*) FROM user WHERE number_of_edits = 0),
    (SELECT count(*) FROM user WHERE number_of_edits = 1),
    (SELECT count(*) FROM user WHERE number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE number_of_edits > 100);"""
    columns = ["no edits", "1 edit", "2-10 edits", "11-100 edits", ">100 edits"]
    cursor.execute(query,)
    data = cursor.fetchall()
    data = list(*data)
    with open(dataDir + str(i) + ".txt", "w") as file:
        file.write(str(data))

    total = sum(data)
    data = list(map(lambda x: x * 100 / total, data))

    plt.title("Distribution of edits in main space")
    plt.xlabel("Number of edits by user")
    plt.ylabel("Percentage")
    plt.bar(columns, data)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def distributionOfTalkEdits(cursor, i, plotDir, dataDir):
    figname = plotDir + str(i)
    plt.figure()

    query = """SELECT
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits = 0),
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits = 1),
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 1 and talkpage_number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 10 and talkpage_number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE talkpage_number_of_edits > 100);"""
    columns = ["no edits", "1 edit", "2-10 edits", "11-100 edits", ">100 edits"]
    cursor.execute(query,)
    data = cursor.fetchall()
    data = list(*data)
    with open(dataDir + str(i) + ".txt", "w") as file:
        file.write(str(data))

    total = sum(data)
    data = list(map(lambda x: x * 100 / total, data))

    plt.title("Distribution of edits in talk space")
    plt.xlabel("Talk Page Edits")
    plt.ylabel("Percentage")
    plt.bar(columns, data)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def numberOfEditsPerNamespace(cursor, i, plotDir, dataDir):
    figname = plotDir + str(i)
    plt.figure()

    query = """SELECT namespace, count(page_id)
    AS 'count'
    FROM page
    GROUP BY namespace;"""
    cursor.execute(query,)
    data = cursor.fetchall()
    data = list(map(lambda x: (str(x[0]), x[1]), data))

    with open(dataDir + str(i) + ".txt", "w") as file:
        file.write(str(data))

    plt.title("Number of edits per namespace")
    plt.xticks(rotation=45)
    plt.xlabel("Namespace")
    plt.ylabel("Number of Pages (log)")
    plt.yscale("log")
    plt.bar(*zip(*data))
    plt.savefig(figname + "-log", bbox_inches="tight", pad_inches=0.25)

    plt.ylabel("Number of Pages (linear)")
    plt.yscale("linear")
    plt.bar(*zip(*data))
    plt.savefig(figname + "-linear", bbox_inches="tight", pad_inches=0.25)


def editsMainTalkNeither(cursor, i, plotDir, dataDir, totalUsers, dryrun):
    figname = plotDir + str(i)
    plt.figure()

    query = """SELECT
    (select count(*) as target from user
    WHERE talkpage_number_of_edits > 0 and number_of_edits > 0),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits = 0 and number_of_edits > 0),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits > 0 and number_of_edits = 0),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits = 0 and number_of_edits = 0);"""
    columns = [
        "edits mainspace\nand talkspace",
        "edits mainspace\nnot talkspace",
        "edits talkspace\nnot mainspace",
        "edits neither",
    ]
    if not dryrun:
        cursor.execute(query,)
        data = cursor.fetchall()
        data = list(*data)
        with open(dataDir + str(i) + ".txt", "w") as file:
            file.write(str(data))
    else:
        data = [1824008, 47503455, 1058214, 4407]
    data = list(map(lambda x: x * 100 / totalUsers, data))

    plt.title("Namespaces that users edit")
    plt.ylabel("Percentage")
    plt.bar(columns, data)

    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def numMainTalkEditsForBiggestUsers(cursor, i, plotDir, dataDir):
    figname = plotDir + str(i)
    plt.figure()

    mainspace = """SELECT username, number_of_edits FROM user
    where bot is null order by number_of_edits desc limit 10;"""
    talkspace = """SELECT username, talkpage_number_of_edits FROM user
    where bot is null order by talkpage_number_of_edits desc limit 10;"""
    cursor.execute(mainspace,)
    mainspaceData = cursor.fetchall()

    with open(dataDir + str(i) + "-mainspace.txt", "w") as file:
        file.write(str(mainspaceData))

    cursor.execute(talkspace,)
    talkspaceData = cursor.fetchall()

    with open(dataDir + str(i) + "-talkspace.txt", "w") as file:
        file.write(str(talkspaceData))

    plt.title("Number of main and talk edits for the biggest editors")
    plt.bar(*zip(*mainspaceData), label="mainspace edits")
    plt.bar(*zip(*talkspaceData), label="talkspace edits")
    plt.xticks(rotation=45)
    plt.legend(loc="upper right")
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def numMainTalkEditsForBiggestBots(cursor, i, plotDir, dataDir):
    figname = plotDir + str(i)
    plt.figure()

    mainspace = """SELECT username, number_of_edits FROM user
    where bot is true order by number_of_edits desc limit 10;"""
    talkspace = """SELECT username, talkpage_number_of_edits FROM user
    where bot is true order by talkpage_number_of_edits desc limit 10;"""
    cursor.execute(mainspace,)
    mainspaceData = cursor.fetchall()

    with open(dataDir + str(i) + "-mainspace.txt", "w") as file:
        file.write(str(mainspaceData))

    cursor.execute(talkspace,)
    talkspaceData = cursor.fetchall()

    with open(dataDir + str(i) + "-talkspace.txt", "w") as file:
        file.write(str(talkspaceData))

    plt.title("Number of main and talk edits for the biggest bots")
    plt.bar(*zip(*mainspaceData), label="mainspace edits")
    plt.bar(*zip(*talkspaceData), label="talkspace edits")
    plt.xticks(rotation=45)
    plt.legend(loc="upper right")
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def numMainTalkEditsForBiggestIPs(cursor, i, plotDir, dataDir):
    figname = plotDir + str(i)
    plt.figure()

    mainspace = """SELECT ip_address, number_of_edits FROM user
    where ip_address is not null order by number_of_edits desc limit 10;"""
    talkspace = """SELECT ip_address, talkpage_number_of_edits FROM user
    where ip_address is not null order by talkpage_number_of_edits desc limit 10;"""
    cursor.execute(mainspace,)
    mainspaceData = cursor.fetchall()
    # data = list(*data)
    with open(dataDir + str(i) + "-mainspace.txt", "w") as file:
        file.write(str(mainspaceData))

    cursor.execute(talkspace,)
    talkspaceData = cursor.fetchall()

    with open(dataDir + str(i) + "-talkspace.txt", "w") as file:
        file.write(str(talkspaceData))

    plt.title("Number of main and talk edits for the biggest IP editors")
    plt.bar(*zip(*mainspaceData), label="mainspace edits")
    plt.bar(*zip(*talkspaceData), label="talkspace edits")
    plt.xticks(rotation=45)
    plt.legend(loc="upper right")
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def distributionOfMainEditsUserBots(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i)
    plt.figure()

    columns = ["no edits", "1 edit", "2-10 edits", "11-100 edits", ">100 edits"]
    mainspaceUser = """SELECT
    (SELECT count(*) FROM user WHERE bot is null
    and number_of_edits = 0),
    (SELECT count(*) FROM user WHERE bot is null
    and number_of_edits = 1),
    (SELECT count(*) FROM user WHERE bot is null
    and number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE bot is null
    and number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE bot is null
    and number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(mainspaceUser,)
        mainspaceUserData = cursor.fetchall()
        mainspaceUserData = list(*mainspaceUserData)
        with open(dataDir + str(i) + "-mainspace-user.txt", "w") as file:
            file.write(str(mainspaceUserData))
    else:
        mainspaceUserData = [1062617, 23477689, 22217652, 3267197, 363346]

    mainspaceBot = """SELECT
    (SELECT count(*) FROM user WHERE bot is true
    and number_of_edits = 0),
    (SELECT count(*) FROM user WHERE bot is true
    and number_of_edits = 1),
    (SELECT count(*) FROM user WHERE bot is true
    and number_of_edits > 1 and number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE bot is true
    and number_of_edits > 10 and number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE bot is true
    and number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(mainspaceBot,)
        mainspaceBotData = cursor.fetchall()
        mainspaceBotData = list(*mainspaceBotData)
        with open(dataDir + str(i) + "-mainspace-bot.txt", "w") as file:
            file.write(str(mainspaceBotData))
    else:
        mainspaceBotData = [340, 101, 272, 211, 995]

    talkspaceUser = """SELECT
    (SELECT count(*) FROM user WHERE bot is null
    and talkpage_number_of_edits = 0),
    (SELECT count(*) FROM user WHERE bot is null
    and  talkpage_number_of_edits = 1),
    (SELECT count(*) FROM user WHERE bot is null
    and  talkpage_number_of_edits > 1 and talkpage_number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE bot is null
    and  talkpage_number_of_edits > 10 and talkpage_number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE bot is null
    and  talkpage_number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(talkspaceUser,)
        talkspaceUserData = cursor.fetchall()
        talkspaceUserData = list(*talkspaceUserData)
        with open(dataDir + str(i) + "-talkspace-user.txt", "w") as file:
            file.write(str(talkspaceUserData))
    else:
        talkspaceUserData = [47506831, 1585186, 1092212, 169881, 34391]

    talkspaceBot = """SELECT
    (SELECT count(*) FROM user WHERE bot is true
    and talkpage_number_of_edits = 0),
    (SELECT count(*) FROM user WHERE bot is true
    and  talkpage_number_of_edits = 1),
    (SELECT count(*) FROM user WHERE bot is true
    and  talkpage_number_of_edits > 1 and talkpage_number_of_edits <= 10),
    (SELECT count(*) FROM user WHERE bot is true
    and  talkpage_number_of_edits > 10 and talkpage_number_of_edits <= 100),
    (SELECT count(*) FROM user WHERE bot is true
    and  talkpage_number_of_edits > 100);"""
    if not dryrun:
        cursor.execute(talkspaceBot,)
        talkspaceBotData = cursor.fetchall()
        talkspaceBotData = list(*talkspaceBotData)
        with open(dataDir + str(i) + "-talkspace-bot.txt", "w") as file:
            file.write(str(talkspaceBotData))
    else:
        talkspaceBotData = [1367, 63, 119, 103, 267]

    fig, axs = plt.subplots(4)
    fig.suptitle("Distribution of edits across name spaces for bots and users")
    axs[0].set_title("user edits in main space")
    axs[0].bar(columns, mainspaceUserData)
    axs[1].set_title("bot edits in main space")
    axs[1].bar(columns, mainspaceBotData)
    axs[2].set_title("user edits in talk space")
    axs[2].bar(columns, talkspaceUserData)
    axs[3].set_title("bot edits in talk space")
    axs[3].bar(columns, talkspaceBotData)
    fig.tight_layout()
    plt.gcf().set_size_inches(5, 10)
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def editsMainTalkNeitherUserBots(cursor, i, plotDir, dataDir, dryrun=False):
    figname = plotDir + str(i)
    plt.figure()

    columns = [
        "edits mainspace\nand talkspace",
        "edits mainspace\nnot talkspace",
        "edits talkspace\nnot mainspace",
        "edits neither",
    ]

    users = """SELECT
    (select count(*) as target from user
    WHERE talkpage_number_of_edits > 0 and number_of_edits > 0 and bot is null),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits = 0 and number_of_edits > 0 and bot is null),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits > 0 and number_of_edits = 0 and bot is null),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits = 0 and number_of_edits = 0 and bot is null);"""
    if not dryrun:
        cursor.execute(users,)
        userData = cursor.fetchall()
        userData = list(*userData)
        with open(dataDir + str(i) + "-user.txt", "w") as file:
            file.write(str(userData))
    else:
        userData = [1823460, 47502424, 1058210, 4407]

    bots = """SELECT
    (select count(*) as target from user
    WHERE talkpage_number_of_edits > 0 and number_of_edits > 0 and bot is true),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits = 0 and number_of_edits > 0 and bot is true),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits > 0 and number_of_edits = 0 and bot is true),
    (select count(*) as target from user
    WHERE talkpage_number_of_edits = 0 and number_of_edits = 0 and bot is true);"""
    if not dryrun:
        cursor.execute(bots,)
        botData = cursor.fetchall()
        botData = list(*botData)
        with open(dataDir + str(i) + "-bot.txt", "w") as file:
            file.write(str(botData))
    else:
        botData = [548, 1031, 4, 336]
    plt.title("Namespaces that users edit")

    fig, axs = plt.subplots(2)
    axs[0].set_title("Namespaces that users edit")
    axs[0].bar(columns, userData)
    axs[1].set_title("Namespaces that bots edit")
    axs[1].bar(columns, botData)
    fig.tight_layout()
    plt.gcf().set_size_inches(8, 8)
    plt.savefig(figname, bbox_inches="tight", pad_inches=0.25)


def plot(plotDir: str = "../plots/", dryrun=False):
    """A function"""
    if not os.path.exists(plotDir):
        os.mkdir(plotDir)

    dataDir = plotDir + "data/"
    if not os.path.exists(dataDir):
        os.mkdir(dataDir)

    if not dryrun:
        database, cursor = Database.connect()
    else:
        cursor = 0

    # Constants
    if not dryrun:
        query = """SELECT count(*)
        FROM user;"""
        cursor.execute(query,)
        totalUsers = cursor.fetchone()[0]

    # 0
    i = 0
    # partitionStatus(cursor, i, plotDir, dataDir)

    # 1
    i = i + 1
    # distributionOfMainEdits(cursor, i, plotDir, dataDir)

    # 2
    i = i + 1
    # distributionOfTalkEdits(cursor, i, plotDir, dataDir)

    # 3
    i = i + 1
    # numberOfEditsPerNamespace(cursor, i, plotDir, dataDir)

    # 4
    i = i + 1
    # editsMainTalkNeither(cursor, i, plotDir, dataDir, totalUsers)

    # 5
    i = i + 1
    # numMainTalkEditsForBiggestUsers(cursor, i, plotDir, dataDir)

    # 6
    i = i + 1
    # numMainTalkEditsForBiggestBots(cursor, i, plotDir, dataDir)

    # 7
    i = i + 1
    # numMainTalkEditsForBiggestIPs(cursor, i, plotDir, dataDir)

    # 8
    i = i + 1
    # distributionOfMainEditsUserBots(cursor, i, plotDir, dataDir, dryrun)

    # 0
    i = i + 1
    # editsMainTalkNeitherUserBots(cursor, i, plotDir, dataDir, dryrun)

    if not dryrun:
        cursor.close()
        database.close()


def defineArgParser():
    """Creates parser for command line arguments"""
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--dryrun",
        help="Don't use a database, no partitions will be deleted",
        action="store_true",
    )

    parser.add_argument(
        "-d", "--dir", help="Output plotDirectory for figures", default="../plots/",
    )

    return parser


if __name__ == "__main__":

    argParser = defineArgParser()
    clArgs = argParser.parse_args()

    plot(
        plotDir=clArgs.dir, dryrun=clArgs.dryrun,
    )