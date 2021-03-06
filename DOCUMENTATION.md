## Contents
* [Program execution](#program-execution)
* [nsdb.py](#module-nsdb)
* [parse.py](#module-parse)
* [splitwiki.py](#module-splitwiki)
* [Database.py](#module-database)

Program execution
-----------------
![program-flow-diagram](programflow.png)
----
Module [nsdb](nsdb/nsdb.py)
===========
This script finds the fastest mirror, downloads and splits one Wikipedia
dump.

This script relies on running in a bash environment. Windows users are
encouraged to install Windows Subsystem for Linux.

This tool uses a MySQL database.

Please run pip install -r requirements.txt before running this script.

**Usage:**
```
  nsdb.py [-h] [--test] [--dryrun] [-w WIKI] [-d DUMP] [-n NAMESPACES [NAMESPACES ...]] 
          [-i PARALLELID] [--numParallel NUMPARALLEL] [-D DATADIR] [-s MAXSPACE] 
          [-c FREECORES]
```
**Optional Arguments:**
```
  -h, --help
      show this help message and exit
  --test
      Only download one archive that is below 50MB in size
  --dryrun
      Don't use a database, no partitions will be deleted
  -w --wiki WIKI
      The name of the wiki you want to use [default: enwiki]
  -d --dump DUMP
      Which dump you want to use, a date string in the format YYYYMMDD. 
      By default will use the dump before latest.
  -n --namespaces NAMESPACES [NAMESPACES ...]
      Which namespaces you want to use, these are different for every wiki [default: 1]
  -i --parallelID PARALLELID
      Set when called from the slurm script [default: 0]
  -n --numParallel NUMPARALLEL
      Set when called from the slurm script [default: 1]
  -D --dataDir DATADIR
      Directory where the dumps, partitions etc will be stored [default: ../]
  -s --maxSpace MAXSPACE
      Max gigabytes that you would like the program to use. Min 50gB [default: 150]
  -c --freeCores FREECORES
      The number of cores you don't want to be used [default: 0]
```

Functions
---------

    
`checkDiskSpace(dataDir)`
:   Returns the size of the data directory

    
`countLines(file)`
:   Returns the number of lines in a file using wc from bash

    
`createDumpsFile(listOfDumps='../dumps.txt', wiki='enwiki', dump='', test=False)`
:   Creates dumps.txt if it doesn't exist

    
`defineArgParser()`
:   Creates parser for command line arguments

    
`downloadDump(dump, listOfDumps, archivesDir, dumpsDir)`
:   Downloads the first dump in dumps.txt if it is not already present
    in the dumps directory

    
`extractFile(fileName, archivesDir, dumpsDir)`
:   Unzip if not already extracted, delete if extracted
    
    Execution takes 5-15 minutes as a guideline

    
`findFastestMirror(dump='20200401', wiki='enwiki/')`
:   Gets a list of the fastest mirrors, downloads a single file from each
    and returns the fastest one.
    
    Execution takes 5-10 seconds as a guideline
    
    Returns
    -------
    fastestMirror: str - the url of the fastest mirror

    
`jobsDone()`
:   Returns True if all jobs are done

    
`main(wiki='enwiki/', dump='', namespaces=[1], parallelID=0, numParallel=1, dataDir='../', maxSpace=600, freeCores=0, dryRun=False, test=True)`
:   Download a list of dumps if it doesn't exist. If there are no dumps,
    download one and split it, then process the dump on multiple threads
    
    Parameters
    ----------
    wiki: str - The name of the wiki you want to use
    dump: str - Which dump you want to use, a date string in the format YYYYMMDD. By
        default will use the dump before latest.
    namespaces: List[int] - Which namespace should be used.
    parallelID: str - set when called from the slurm script. Slurm is used for running
        this tool in a distributed fashion.
    numParallel: int - set when called from the slurm script.
    dataDir: str - directory where the dumps, partitions etc will be stored. If you
        are using this on a personal computer, I recommend using '../'. If external
        storage is available you should enter the path here.
    maxSpace: int - maximum number of gigabytes that you would like the program to use.
        At minimum this should be 50gB.
    freeCores: int - the number of cores you don't want to be used. For best results
        set this to zero.

    
`markLongRunningJobsAsError()`
:   Marks jobs that take over 15 minutes as error.
    
    This doesn't halt execution but does allow the job to be requeued.

    
`outstandingJobs()`
:   Returns number of jobs with status 'todo' or 'failed'

    
`parseError(error)`
:   Logs errors from parse processes to a file

    
`removeDoneJobs(partitionsDir)`
:   Remove partitions that are completed

    
`restartJobs()`
:   NOT IMPLEMENTED - Restart jobs labelled failed, mark them as restarted

    
`splitError(error)`
:   Logs errors from split processes to a file

    
`splitFile(fileName, queue, dumpsDir, partitionsDir, numPartitions, dryRun)`
:   Split a dump into a number of partitions

-----


Module [parse](nsdb/parse.py)
============
This script allows the user to parse a dump from a database connection
and extract features to a database table.

This tool uses a MySQL database that is configured in the Database() module.

**Usage:**
```
  parse.py [-h] [--dryrun] [-p PARTITIONNAME] [-d PARTITIONSDIR] 
           [-n NAMESPACES [NAMESPACES ...]] [-i PARALLELID]
```
**Optional Arguments:**
```
  -h, --help
      show this help message and exit
  --dryrun
      Don't use a database, no partitions will be deleted
  -p --partitionName PARTITIONNAME
      Set when called from the slurm script [default: 0]
  -d --partitionsDir PARTITIONSDIR
      Where the partitions are stored [default: ../partitions/]
  -n --namespaces NAMESPACES [NAMESPACES ...]
      Namespaces of interest [default: 1]
  -i --parallelID PARALLELID
      Set when called from the slurm script [default: '']
```

Functions
---------

    
`checkReverted(detector, revision, cursor, undidRevision, target, editIdToUserId)`
:   Inserts reverted edits into the database for target namespace, otherwise 
    returns the user that was reverted

    
`cleanString(string)`
:   Removes special characters and unnecessary whitespace from text

    
`containsVulgarity(string)`
:   Returns whether text contains profanity based on a simple wordlist approach

    
`defineArgParser()`
:   Creates parser for command line arguments

    
`getDiff(old, new, parallel, partitionsDir)`
:   Returns the diff between two edits using wdiff
    
    Parameters
    ----------
    old : str - old revision
    new : str - new revision
    
    Returns
    -------
    added: str - all the text that is exclusively in the new revision
    deleted: str - all the text that is exclusively in the old revision
    parallel: str - id of the parallel process, 0 if not

    
`getDump(partitionsDir, cursor=0, partitionName='')`
:   Returns the next dump to be parsed from the database
    
    Parameters
    ----------
    cursor: MySQLCursor - cursor allowing CRUD actions on the DB connections
    
    Returns
    -------
    dump: class 'mwxml.iteration.dump.Dump' - dump file iterator
    fileName: str - fileName of dump

    
`longestCharSequence(string)`
:   Returns the length of the longest repeated character sequence in text

    
`longestWord(string)`
:   Returns the length of the longest word in text

    
`markAsNotFound(fileName)`
:   

    
`multiprocess(partitionsDir, namespaces, queue, jobId, dryRun=False)`
:   Wrapper around process to call parse in a multiprocessing pool

    
`parse(partitionName='', partitionsDir='../partitions/', namespaces=[1], parallel='', dryRun=False)`
:   Selects the next dump from the database, extracts the features and
    imports them into several database tables.
    
    Detailed extraction of features is performed for namespaces of interest.
    Pages that are not in the namespace of choice will instead only have the edits
    counted per user.
    
    Parameters
    ----------
    partitionsDir: str - where the partitions are stored
    namespaces : list[int] - Wikipedia namespaces of interest.
    parallel: str - whether to parse with multiple cores

    
`parseNonTargetNamespace(page, title, namespace, cursor, parallel='')`
:   Counts the number of edits each user makes and inserts them to the database.
    
    Parameters
    ----------
    page: mwtypes.Page
    title: str - Title of the page
    namespace: str - Namespace of the page
    cursor: MySQLCursor - cursor allowing CRUD actions on the DB connections
    parallel: str - id of process, hides progress bars if present

    
`parseTargetNamespace(page, title, namespace, cursor, parallel, partitionsDir)`
:   Extracts features from each revision of a page into a database
    
    Ignores edits that have been deleted like:
        https://en.wikipedia.org/w/index.php?oldid=614217720
    
    Parameters
    ----------
    page: mwtypes.Page
    title: str - Title of the page
    namespace: str - Namespace of the page
    cursor: MySQLCursor - cursor allowing CRUD actions on the DB connections
    parallel: str - id name of parallel slurm process, present if called from parallel,
      hides progress bars

    
`ratioCapitals(string)`
:   Returns the ratio of uppercase to lowercase characters in text

    
`ratioDigits(string)`
:   Returns the ratio of digits to all characters in text

    
`ratioPronouns(string)`
:   Returns the ratio of personal pronouns to all words in text

    
`ratioSpecial(string)`
:   Returns the ratio of special characters to all characters in text

    
`ratioWhitespace(string)`
:   Returns the ratio of whitespace to all characters in text

Classes
-------

`fileCursor(partitionName)`
:   

    ### Class variables

    `lastrowid`
    :

    `testFile`
    :

    ### Methods

    `execute(self, *args)`
    :

-----


Module [splitwiki](nsdb/splitwiki.py)
================
This script looks in the dumps/ directory and splits the first file into 40
partitions by default. This can be changed by adjusting the parameters to split()

**Usage:**
```
  splitwiki.py [-h] [--dryrun] [-n NUMBER] [-f FILENAME] [-i INPUTFOLDER] 
               [-o OUTPUTFOLDER] [--deleteDump DELETEDUMP]
```
**Optional Arguments:**
```
  -h, --help
      show this help message and exit
  --dryrun
      Don't use a database, no partitions will be deleted
  -n --number NUMBER
      Number of partitions to split the dump into [default: 10]
  -f --fileName FILENAME
      Which partition to split [default: '']
  -i --inputFolder INPUTFOLDER
      Location of the dumps [default: ../dumps/]
  -o --outputFolder OUTPUTFOLDER
      Location of the partitions [default: ../partitions/]
  --keepDump
      Don't delete the dump after splitting
```

Functions
---------

    
`addJobToDatabase(cursor, partitionName)`
:   Inserts partition into the database

    
`addJobToQueue(queue, jobId)`
:   Adds partition to the multiprocessing queue

    
`countLines(file)`
:   Returns the estimated number of lines in a dump using wcle.sh

    
`defineArgParser()`
:   Creates parser for command line arguments

    
`split(number=10, fileName='', inputFolder='../dumps/', outputFolder='../partitions/', deleteDump=True, queue=0, cursor=0, dryRun=False)`
:   Splits Wikipedia dumps into smaller partitions. Creates a file
    partitions.txt with the created partitions.
    
    The lower the number of partitions, the lower the total size of the partitions
    and the lower the running time to generate them. For this reason, it is recommended
    to set the number to a multiple of the number of processes running splitwiki.
    
    For example, splitting one dump:
    100 partitions - 5046 seconds - 39.2 GB
     50 partitions - 5002 seconds - 39.2 GB
     10 partitions - 4826 seconds - 37.2 GB
      5 partitions - 3820 seconds - 36   GB

-----


Module [Database](nsdb/Database.py)
===============
This module creates a database connection for other scripts to use.

The connection is configured in the private.cnf function. See public.cnf for an
example configuration.

Functions
---------

    
`connect()`
:   Connect to MySQL database using password stored in options file
    
    Returns
    -------
    database: MySQLConnection - connection to the MySQL DB
    cursor: MySQLCursor - cursor allowing CRUD actions on the DB connections

-----
