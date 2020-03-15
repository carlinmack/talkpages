"""
This script looks in the dumps/ directory and splits the first file into 40
partitions by default. This can be changed by adjusting the parameters to split()

Please run pip install -r requirements.txt before running this script.
"""
import glob
import os
import subprocess

# import click
from tqdm import trange


def countLines(file):
    """Returns the estimated number of lines in a dump using wcle.sh"""
    print("counting lines: ", file)
    lines = int(subprocess.check_output(["./wcle.sh", file]))

    return lines


# @click.command()
# @click.option(
#     "-n", "--number", default=40,
# )
# @click.option(
#     "-o", "--outputfolder",
# )
# @click.option(
#     "-d", "--deletedump", default=False, is_flag=True,
# )
def split(number=40, inputFolder="dumps", outputFolder="partitions", deleteDump=True):
    """Splits Wikipedia dumps into smaller partitions. Creates a file
    partitions.txt with the created partitions

    Parameters
    ----------
    number: intr - the number of partitionst to split into
    inputFolder: str - the folder where the xml dumps are
    outputFolder: str - the folder where the partitions should be output to
    deleteDump: boolean - whether to delete the dump after successfully splitting
    """
    files = glob.glob(inputFolder + "/*.xml*")
    file = files[0]
    fileName = file[6:]

    lines = countLines(file)

    chunkSize = lines / number * 0.75

    header = """<mediawiki xmlns="http://www.mediawiki.org/xml/export-0.10/"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.mediawiki.org/xml/export-0.10/ http://www.mediawiki.org/xml/export-0.10.xsd" 
    version="0.10" xml:lang="en">
    <siteinfo>
    <sitename>Wikipedia</sitename>
    <dbname>enwiki</dbname>
    <base>https://en.wikipedia.org/wiki/Main_Page</base>
    <generator>MediaWiki 1.35.0-wmf.11</generator>
    <case>first-letter</case>
    <namespaces>
        <namespace key="-2" case="first-letter">Media</namespace>
        <namespace key="-1" case="first-letter">Special</namespace>
        <namespace key="0" case="first-letter" />
        <namespace key="1" case="first-letter">Talk</namespace>
        <namespace key="2" case="first-letter">User</namespace>
        <namespace key="3" case="first-letter">User talk</namespace>
        <namespace key="4" case="first-letter">Wikipedia</namespace>
        <namespace key="5" case="first-letter">Wikipedia talk</namespace>
        <namespace key="6" case="first-letter">File</namespace>
        <namespace key="7" case="first-letter">File talk</namespace>
        <namespace key="8" case="first-letter">MediaWiki</namespace>
        <namespace key="9" case="first-letter">MediaWiki talk</namespace>
        <namespace key="10" case="first-letter">Template</namespace>
        <namespace key="11" case="first-letter">Template talk</namespace>
        <namespace key="12" case="first-letter">Help</namespace>
        <namespace key="13" case="first-letter">Help talk</namespace>
        <namespace key="14" case="first-letter">Category</namespace>
        <namespace key="15" case="first-letter">Category talk</namespace>
        <namespace key="100" case="first-letter">Portal</namespace>
        <namespace key="101" case="first-letter">Portal talk</namespace>
        <namespace key="108" case="first-letter">Book</namespace>
        <namespace key="109" case="first-letter">Book talk</namespace>
        <namespace key="118" case="first-letter">Draft</namespace>
        <namespace key="119" case="first-letter">Draft talk</namespace>
        <namespace key="446" case="first-letter">Education Program</namespace>
        <namespace key="447" case="first-letter">Education Program talk</namespace>
        <namespace key="710" case="first-letter">TimedText</namespace>
        <namespace key="711" case="first-letter">TimedText talk</namespace>
        <namespace key="828" case="first-letter">Module</namespace>
        <namespace key="829" case="first-letter">Module talk</namespace>
        <namespace key="2300" case="first-letter">Gadget</namespace>
        <namespace key="2301" case="first-letter">Gadget talk</namespace>
        <namespace key="2302" case="case-sensitive">Gadget definition</namespace>
        <namespace key="2303" case="case-sensitive">Gadget definition talk</namespace>
    </namespaces>
    </siteinfo>\n"""

    footer = "\n</mediawiki>\n"

    with open(file) as inFile:
        i = 0
        inPage = False
        moreFile = True

        for index in trange(number, desc=fileName, unit=" partition"):
            if not moreFile:
                break

            partitionName = fileName + "." + str(index)
            outputFileName = os.path.join(outputFolder, partitionName)

            with open("partitions.txt", "a+") as partitions:
                partitions.write(partitionName + "\n")

            if not os.path.exists(outputFolder):
                os.mkdir(outputFolder)

            with open(outputFileName, "w+") as outFile:
                outFile.write(header)

                for line in inFile:
                    moreFile = False

                    if line == "  <page>\n":
                        inPage = True
                    if inPage:
                        i = i + 1
                        outFile.write(line)
                    if i > chunkSize:
                        if line == "  </page>\n":
                            i = 0
                            moreFile = True
                            break

                outFile.write(footer)

    if deleteDump:
        os.remove(file)


if __name__ == "__main__":
    split()
