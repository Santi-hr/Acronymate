# Acronymate
Helpful script to aid with the generation of acronym tables from word documents

## What is its purpose?
This script was created after the tedious task of reviewing several documents at work and having to extract and define the same acronyms in all of them.

The script extracts the acronyms from any *.docx* file. It analyzes all paragraphs and tables, including those with "Track Changes" enabled. Acronymate also provides a "database" for definitions to ensure consistency. Once a new acronym is added its definition will appear automatically the next time it is found in another document. This way no time is wasted in manually searching everytime how exactly that acronym was defined. Finally, it generates an acronym table in *.docx* format that eases copying it to the final document.

It also detects and process an already existing acronym table to import new definitions and avoid detecting those listed acronyms as needed if they only appear in that table.

The script is thought to be used with colleagues keeping the database file in a shared folder. Some degree of protection is added to prevent overwriting others changes.

The current user interface is a plain console, but with plenty of options and quite user-friendly. For example, for each acronym all appearances with context are shown, so it's easy to see where it was used on the document. The interface looks like this:  
![User interface](https://raw.githubusercontent.com/Santi-hr/Acronymate/master/other/User_Interface_Example.jpg)

The user interface is provided in english and spanish. Use the configuration to select language.
If you are processing documents that are not in the supported languages, please check if the regex in *common/defines* contains all the special characters your language uses.


### And what does the name mean?
Acronym + mate :)

## Status
Currently, the script is very polished and the core works well. However, I think there is still some room for improvement before releasing a v1.0.0. I have several improvements in my TODO list like better support for multiple users (Keeping track if the "database" is in use), upgrading the console to a GUI, etc.

If the script proves to be useful I will invest more time to it.

# How to use
Launch *acronymateCmd.py*, or the precompiled executable for Windows, and follow the instructions of the user interface.
Currently, all user interaction is done through the console. Use the command 'h' to get help. 

## Word Integration
To facilitate its use a Word macro is available in the folder "other".
This macro allows to easily extract the acronyms of the active document and save time otherwise lost looking for the executable file.

Before using the macro some variables need to be defined. Read the comments on the same file.

## Requirements (Python script)
To run the program as a python script the modules *python-docx* and *lxml* are required. The versions are specified in the *requirements.txt* file.
