# Lab Unzipper
A set of tools to take a zip file downloaded from MyCourses and extract it to
a set of folders setup in a 'LastName, FirstName' format. There are 3 main
tools, 2 of which can be easily ran at the same time using a command line flag.
- The Basic Unzipping Utility
- The Config Builder
- The Test Builder/Copier

|       Term       |                                               Definition                                              |
|------------------|:-----------------------------------------------------------------------------------------------------:|
|Initial Extraction| The extraction of the MyCourses .zip but before the unzipping of the individual student's zipped files|
|   MyCourses ZIP  |                                The .zip file downloaded from MyCourses                                |
|  Student's Zips  |                   The Collection of Zipped Files initially inside the MyCourses Zip                   |

## LabUnzipper Guide
The Unzipper has two modes zip and directory. Once the initial extraction
is complete, the both do the same thing.

|Optional Args|Description|
|------------------|:-----------------------------------------------------------------------------------------------------:|
|-v|Changes the Verbosity to output more diagnostic information|
|   MyCourses ZIP  |                                The .zip file downloaded from MyCourses                                |
|  Student's Zips  |                   The Collection of Zipped Files initially inside the MyCourses Zip                   |


### Zip

Usage:`python <DIRECTORY_TO_LABUNZIPPER.PY> zip '<DIRECTORY_TO_MYCOURSES_ZIP>'`

Takes a directory to a zip file and will do an inital extraction of that file.
It will set up the created directory 

### Directory

Usage:`python <DIRECTORY_TO_LABUNZIPPER.PY> directory '<DIRECTORY_TO_STUDENTS_ZIPS>'`

### Both

## WARNINGS
- The program will only accept the last submitted item by the student, all
other versions will be removed, so if their last submission is outside an 
allowed window, you must manually remove the .zip files you do not want graded
