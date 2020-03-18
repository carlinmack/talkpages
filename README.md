# Classifying Actors on Wikipedia Talk Pages

👉 [Project Page](https://meta.wikimedia.org/wiki/Research:Classifying_Actors_on_Talk_Pages#Goals)

## Contents

* [Introduction](#Introduction)
  * [Current Status](#Current-Status)
* [Requirements and installation](#Requirements-and-installation)
  * [Software](#Software)
  * [Hardware](#Hardware)
* [Usage](#Usage)
* [Contributions](#Contributions)
   
## Introduction

This project is a collection of scripts that creates a database of edits for a  Wikipedia namespace.

This is challenging as Wikipedia serves its dumps in ~200MB archives
which extract to ~40GB XML files. For this reason, the aim is for the
scripts to parallelise and to remove as much unnecessary information as
possible before importing to the database.

Another aim of this project is to create documentation to promote research into Wikipedia. 
This can be performed in a variety of areas such as:
|                             |                                                                                                                                         |
|-----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| Classification              | InProceedings (Javanmardi2011): Vandalism detection in Wikipedia: a high-performing, feature-rich model and its reduction through Lasso |
| Digital Humanities          | Article (schneider2010content): A content analysis: How Wikipedia talk pages are used                                                   |
| Natural Language Processing | InProceedings (Rawat2019): Automatic Detection of Online Abuse and Analysis of Problematic Users in Wikipedia                           |
| Network Analysis            | InProceedings (Massa2011): Social networks of wikipedia                                                                                 |
| Prediction                  | Article (MartinezOrtuno): Sentiment as a Predictor of Wikipedia Editor Activity                                                         |


#### Current Status

This project currently:

* Downloads dumps from the fastest mirror
* Splits them into 40 partitions for parallel processing
* Parses and extracts features and imports them to a database. If there are errors they are logged to the database

In the future I aim to add:

* Stable parallel processing
* Allow selection via arguments of wiki, namespace, dump
* Allow users to provide their own option files for the database so they don't have to edit code.
* Allow users to pass in a filename directly to splitwiki or parse. 
* Allow users to be able to direct output to somewhere other than a database.

## Requirements and installation

#### Software 

You need Python >3.5 and the ability to run bash scripts. If you are on Windows, I highly
recommend installing [WSL](https://docs.microsoft.com/en-us/windows/wsl/install-win10). 

Additionally you need to have a MySQL database, which you can hopefully have set up for you by an administrator. If not start from [here](https://dev.mysql.com/doc/refman/8.0/en/installing.html). 

#### Hardware

The resulting database has about 100x reduction in size from the extracted dump. Additionally different namespaces have different requirements - there are relatively few edits on namespaces other than main. Therefore it may be possible to create a database of all edits on non-main namespaces on consumer hardware. 

## Usage

To create a list of dumps, download the first, partition it and add the partition names to a database run.

```
python talkpages.py
```
> Make sure to edit the database connection first so that it can connect to the database

To parse the next dump and add it's features to the database run:

```
python parse.py
```

To split the first dump in the dumps/ folder into ~40 partitions in the partitions/ folder run:

```
python splitwiki.py
```

👉 [Documentation of all available modules ](/carlinmack/talkpages/blob/master/DOCUMENTATION.md)

## Contributions

I gladly accept contributions via GitHub pull requests, however please include documentation of the use case with your PR.
