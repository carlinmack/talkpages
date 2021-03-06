## Namespace Database

This project is a collection of scripts that creates a database of edits for a  Wikipedia namespace.

👉 Wikipedia Research Page - [Classifying Actors on Wikipedia Talk Pages](https://meta.wikimedia.org/wiki/Research:Classifying_Actors_on_Talk_Pages#Goals)

This is challenging as Wikipedia serves its dumps in ~200MB archives
which extract to ~40GB XML files. For this reason, the aim is for the
scripts to parallelise and to only import necessary information to the database.

> If there is a feature you'd like, or a roadblock to you using this, please [create an issue!](https://github.com/carlinmack/NamespaceDatabase/issues/new)

**Example Queries**
|                           |                       |                       |
|---------------------------|-----------------------|-----------------------|
| ![image](plots/11-distributionOfEditsPerNamespace.png) | ![image](plots/19-averageAllSpecial.png) | ![image](plots/21-compositionOfUser.png) |

👉 View all plots - [Plotting Wikipedia Data](https://carlinmack.com/blog/article/wikipediaplots/)

## Contents

* [Current Status](#Current-Status)
* [Requirements and installation](#Requirements-and-installation)
  * [Software](#Software)
  * [Hardware](#Hardware)
* [Usage](#Usage)
* [Contributions](#Contributions)


#### Current Status

This project currently:

* Allow selection of wiki, namespace, dump, among other parameters 
* Downloads dumps from the fastest mirror
* Splits them into partitions for parallel processing
* Parses, extracts and imports features in parallel into a MySQL database. Errors are logged to a log file unless it stops the parsing of the partition in which it is logged to the database.
* Allow users to be able to direct output to text file.

In the future I aim to add:

* Allow users to provide their own option files for the database so they don't have to edit code.
* Allow users to pass in a filename directly to splitwiki or parse. 

## Requirements and installation

#### Software 

You need Python >3.5 and the ability to run bash scripts. If you are on Windows you will need to install [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10). 

Additionally, you need to have a MySQL database, which you can hopefully have set up for you by an administrator. If not, start from [here](https://dev.mysql.com/doc/refman/8.0/en/installing.html). 

#### Hardware

The resulting database has at least 100x reduction in size from the extracted dump. Additionally, different namespaces have different requirements - there are relatively few edits on namespaces other than main. Therefore, it may be possible to create a database of all edits on non-main namespaces on consumer hardware. 

## Usage

Enter a command prompt in the top level of the directory, run:

```
python -m pip install -r requirements.txt
```

If a database is not set up, you can test the program with:

```
python nsdb.py --test --dryrun
```

This writes output to text files rather than the database. Due to the `test` parameter this will only download and parse one archive under 50MB. The output of this is currently not valid for creating a database as a dummy foreign key of -1 is used for user_table_id.

If a database is set up, edit the database connection in Database.py and test the connection:

```
python Database.py
```

Once this returns the database and cursor succesfully, find out the values for the parameters to be passed to nsdb.py:
* wiki is the name of the wiki, for example enwiki, frwiki, zhwiktionary, etc
* dump is the date of the dump that you want to use. Leave this blank to use the most recent. If you are planning to run this to completion, set this parameter so that your database is consistent
* namespaces is the list of namespaces which you would like to create a database for.
* dataDir parameter is where you would like the partitions to be stored. It's likely that you would want to set this to the path of external storage. If enough space is available on your computer set this to `../`.
* maxSpace is the free storage that you would like this to use
* freeCores to the number of cores you do not want the program to use

To create a list of dumps then, in parallel, download and insert the features into the database, include relevant parameters as follows:

```
python nsdb.py [-w WIKI] [-d DUMP] [-n NAMESPACES [NAMESPACES ...]] [-D DATADIR] [-s MAXSPACE] [-c FREECORES]
```

If dumps are extracted, they can also be parsed manually and it's features can be added to the database with:

```
python parse.py [-p PARTITIONNAME] [-d PARTITIONSDIR] [-n NAMESPACES [NAMESPACES ...]] [-i PARALLELID]
```

To split the first dump in the `dumps/` folder into ~40 partitions in the `partitions/` folder run:

```
python splitwiki.py [-n NUMBER] [-f FILENAME] [-i INPUTFOLDER] [-o OUTPUTFOLDER] [--keepDump] 
```

👉 [Documentation of all available modules](DOCUMENTATION.md)

👉 [Schema of the database](schema.md)

## Contributions

I gladly accept contributions via GitHub pull requests! Please create an issue first so 
I can advise you :)
