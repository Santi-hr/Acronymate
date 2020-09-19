# Acronymate
Helpful script to aid with the generation of acronym tables from word documents

## What is its purpose?
This script was created after the tedious task of reviewing several documents at work and having to process the same acronyms in all of them.

The script extracts the acronyms from the .docx, shows you where they are found giving context and provides a "database" for definitions. Once you add a new acronym its definition will appear automatically the next time it is found in another document. This allows for not wasting time searching again how exactly that acronym was defined and ensures consistency. Finally, it generates an acronym table in docx format that eases copying it to the final document.

The script is thought to be used with colleagues keeping the database file in a shared folder. Some degree of protection is added to prevent overwriting others changes.

The user interface looks like this:
![User interface](https://raw.githubusercontent.com/Santi-hr/Acronymate/master/other/User_Interface_Example.jpg)

The script analyzes all paragraphs and tables, including those with "Track Changes" enabled. It can also process an already existing acronym table to import definitions and avoid detecting those listed acronyms as used.

### And what does the name mean?
Acronym + mate :)

# Status
This is a work in progress. Currently the script has a only a Spanish command line interface. I have several improvements in my TODO list like a translation (at least to English), better support for multiple users (Keeping track if the "database" is in use), upgrading to a GUI (Probably tkinter), etc.
If the script proves to be useful I will invest more time to it. 

# How to use
Launch 'mainScript.py' and follow the instructions. Currently all user interaction is done through the console. Use the command 'h' to get help. 

Detailed documentation and instructions comming soon.

