"""
This script finds the fastest mirror, downloads and splits one Wikipedia
dump.

This script relies on running in a bash environment. Windows users are
encouraged to install Windows Subsystem for Linux.

This tool uses a MySQL database.

Please run pip install -r requirements.txt before running this script.
"""

import multiprocessing
import os
import re
import subprocess
import time
import traceback
from datetime import datetime
from sys import argv
from typing import List
from urllib import request

import Database
import parse
from mirrors import fastest
from splitwiki import split


def parseError(error):
    """Logs errors from parse processes to a file"""
    currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("error/parseError.txt", "a+") as outFile:
        outFile.write(currenttime + "\n\n")
        outFile.write(str(error) + "\n\n")
        outFile.write(traceback.format_exc() + "\n\n")


def splitError(error):
    """Logs errors from split processes to a file"""
    currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open("error/splitError.txt", "a+") as outFile:
        outFile.write(currenttime + "\n\n")
        outFile.write(str(error) + "\n\n")
        outFile.write(traceback.format_exc() + "\n\n")


def createDumpsFile(listOfDumps: str, wiki: str = "enwiki", dump: str = "20200401"):
    """Creates dumps.txt if it doesn't exist"""

    if not os.path.isfile(listOfDumps):
        mirror = "https://dumps.wikimedia.org/"

        if dump == "":
            # find latest
            pass

        url = mirror + wiki + "/" + dump
        content = request.urlopen(url).read().decode("utf-8")
        dumps = re.findall('(?<=href="/).*pages-meta-history.*7z(?=")', content)

        with open(listOfDumps, "w") as file:
            for d in dumps:
                file.write(d + "\n")


def countLines(file: str) -> int:
    """Returns the number of lines in a file using wc from bash"""
    wordCount = subprocess.check_output(["wc", "-l", file]).decode("utf-8")
    lines = int(wordCount.split(" ")[0])

    return lines


def downloadFirstDump(
    dump: str, listOfDumps: str, archivesDir: str, dumpsDir: str
) -> str:
    """Downloads the first dump in dumps.txt if it is not already present
    in the dumps directory"""

    with open(listOfDumps) as file:
        firstLine = file.readline().strip()
        fileName = re.findall(r"\/([^\/]*)$", firstLine)[0]
        print(fileName)

        data = file.read().splitlines(True)

    # delete first line
    with open(listOfDumps, "w") as file:
        file.writelines(data)

    if not os.path.exists(dumpsDir + fileName[:-3]):
        fastestMirror = fastest(dump)

        subprocess.run(
            ["wget", "-nc", "-nv", "-P", archivesDir, fastestMirror + firstLine]
        )

    return fileName


def extractFile(fileName: str, archivesDir: str, dumpsDir: str):
    """Unzip if not already extracted, delete if extracted

    Execution takes 5-15 minutes as a guideline"""
    if not os.path.exists(dumpsDir + fileName[:-3]):
        subprocess.run(["7z", "e", archivesDir + fileName, "-o" + dumpsDir, "-aos"])

    if os.path.exists(archivesDir + fileName):
        os.remove(archivesDir + fileName)

    return fileName[:-3]


def splitFile(
    fileName: str, queue, dumpsDir: str, partitionsDir: str, numPartitions: int
):
    """Split a dump into a number of partitions"""
    database, cursor = Database.connect()

    split(
        fileName=fileName,
        queue=queue,
        cursor=cursor,
        inputFolder=dumpsDir,
        outputFolder=partitionsDir,
        number=numPartitions,
    )

    cursor.close()
    database.close()


def checkDiskSpace(dataDir: str) -> int:
    """Returns the size of the data directory"""
    try:
        space = int(
            subprocess.check_output(["du", "-s", dataDir], stderr=subprocess.STDOUT)
            .split()[0]
            .decode("utf-8")
        )
    except:
        space = 999999999

    return space


def outstandingJobs() -> int:
    """Returns number of jobs with status 'todo' or 'failed'"""
    query = "SELECT count(*) FROM partition WHERE status = 'todo';"
    database, cursor = Database.connect()
    try:
        cursor.execute(query)
    except BrokenPipeError:
        numJobs = 0
        database.close()
    except Exception as e:
        print("fuck", flush=True)
        print(str(e), flush=True)
    else:
        numJobs = cursor.fetchone()[0]

        cursor.close()
        database.close()

    return numJobs


def jobsDone() -> bool:
    """Returns True if all jobs are done"""
    query = "SELECT count(*) FROM partition WHERE status = 'running' OR status = 'todo'"
    database, cursor = Database.connect()
    try:
        cursor.execute(query)
    except BrokenPipeError:
        database.close()
        numJobs = 1
    else:
        numJobs = cursor.fetchone()[0]

        cursor.close()
        database.close()

    return numJobs == 0


def markLongRunningJobsAsError():
    """Marks jobs that take over 15 minutes as error.

    This doesn't halt execution but does allow the job to be requeued."""
    query = """UPDATE partition
               SET status = 'failed', error = 'Timed out' 
               WHERE status = 'running'
               AND TIMESTAMPDIFF(MINUTE,start_time_1,CONVERT_TZ(NOW(),'+00:00','-4:00')) > 15;"""
    database, cursor = Database.connect()
    try:
        # unsure why multi has to be true here but it does ¯\_(ツ)_/¯
        cursor.execute(query, multi=True)
    except BrokenPipeError:
        database.close()
        return

    cursor.close()
    database.close()


def removeDoneJobs(partitionsDir: str):
    """Remove partitions that are completed"""
    query = "SELECT file_name FROM partition WHERE status = 'done'"
    database, cursor = Database.connect()
    try:
        cursor.execute(query)
    except BrokenPipeError:
        database.close()
        return

    output = cursor.fetchall()

    for file in output:
        fileName = partitionsDir + file[0]
        if os.path.exists(fileName):
            try:
                os.remove(fileName)
            except FileNotFoundError:
                pass

    cursor.close()
    database.close()


def restartJobs():
    """NOT IMPLEMENTED - Restart jobs labelled failed, mark them as restarted"""
    return
    query = "SELECT file_name FROM partition WHERE status = 'failed'"
    database, cursor = Database.connect()
    try:
        cursor.execute(query)
    except BrokenPipeError:
        database.close()
        return

    output = cursor.fetchall()

    for file in output:
        file = file[0]

        # start jobs

        currenttime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        query = """UPDATE partition
            SET
                status = "restarted",
                start_time_1 = %s
            WHERE file_name = %s;"""
        cursor.execute(query, (currenttime, file))

    cursor.close()
    database.close()


def main(
    parallelID: str = 0,
    numParallel: int = 1,
    dataDir: str = "/bigtemp/ckm8gz/",
    maxSpace: int = 600,
    freeCores: int = 0,
):
    """Download a list of dumps if it doesn't exist. If there are no dumps,
    download one and split it, then process the dump on multiple threads

    Parameters
    ----------
    parallelID: str - set when called from the slurm script. Slurm is used for running 
        this tool in a distributed fashion.
    numParallel: int - set when called from the slurm script.
    dataDir: str - directory where the dumps, partitions etc will be stored. If you
        are using this on a personal computer, I recommend using '../'. If external
        storage is available you should enter the path here.
    maxSpace: int - maximum number of gigabytes that you would like the program to use.
        At minimum this should be 50gB.
    freeCores: int - the number of cores you don't want to be used. For best results 
        set this to zero."""
    wiki = "enwiki/"
    dump = "20200401/"

    listOfDumps = "../dumps.txt"  # not stored in data dir as it stores state

    dumpsDir = os.path.join(dataDir, "dumps/")
    archivesDir = os.path.join(dataDir, "archives/")
    partitionsDir = os.path.join(dataDir, "partitions/")

    namespaces = [1]

    print("main")
    cores = max(multiprocessing.cpu_count() - freeCores, 1)
    print(cores)
    queue = multiprocessing.Manager().Queue()

    if cores > 4:
        # cores - 3 as 1 thread to run nsdb.py and 2 to run splitwiki
        # min, max ensures that it is within 1 and 10
        numParseCores = min(max(cores - 3, 1), 10)
    else:
        numParseCores = max(cores - 2, 1)

    if numParallel > 1:
        numSplitCores = min(max(cores - 1 - numParseCores, 1), 3)
    else:
        numSplitCores = max(cores - 1 - numParseCores, 1)

    numPartitions = 8 * numParseCores

    parser = multiprocessing.Pool(numParseCores)
    splitter = multiprocessing.Pool(numSplitCores)

    for _ in range(numParseCores):
        parser.apply_async(
            parse.multiprocess,
            (partitionsDir, namespaces, queue, parallelID),
            error_callback=parseError,
        )

    createDumpsFile(listOfDumps, wiki, dump)

    # while (things-to-do or jobs still running)
    while countLines(listOfDumps) > 0 or jobsDone():
        # if countLines(listOfDumps) > 0:
        print("before")
        if (
            not os.path.exists(dumpsDir)
            or len(os.listdir(dumpsDir)) < numParallel * 3
            or len(splitter._cache) < numSplitCores
        ):
            print("download")
            tick = time.time()
            fileName = downloadFirstDump(dump, listOfDumps, archivesDir, dumpsDir)
            print(
                "--- Downloading %s took %s seconds ---"
                % (fileName, time.time() - tick)
            )

            tick = time.time()
            fileName = extractFile(fileName, archivesDir, dumpsDir)
            print(
                "--- Extracting %s took %s seconds ---" % (fileName, time.time() - tick)
            )

            splitter.apply_async(
                splitFile,
                (fileName, queue, dumpsDir, partitionsDir, numPartitions),
                error_callback=splitError,
            )

        numJobs = outstandingJobs()
        diskSpace = checkDiskSpace(dataDir)

        if jobsDone():
            print("sleeping", flush=True)
        #     break

        # While (jobs labelled todo|error > threads or no-more-files or no-more-space)
        while numJobs > 30 * numParallel or diskSpace > (maxSpace * 1000000):
            print("in")
            markLongRunningJobsAsError()

            removeDoneJobs(partitionsDir)

            # restartJobs()

            time.sleep(30)
            numJobs = outstandingJobs()
            diskSpace = checkDiskSpace(dataDir)

        time.sleep(5)

    # clean up Pool
    print("=== EXIT ===")


if __name__ == "__main__":
    if len(argv) > 1:
        jobId = argv[1]
        numParallel = int(argv[2])
        main(jobId, numParallel)
    else:
        main()
