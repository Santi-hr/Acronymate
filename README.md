# Acronymate
Helpful script to aid in the acronym definition table generation from word documents

## What is its purpose?
This script was created after the tedious task of reviewing several documents at work and having to process the same acronyms in all of them.

The script extracts the acronyms from the .docx, shows you where they are found giving context and provides a "database" for definitions. Once you add a new acronym the definition will be awaiting for the next time it appears in another document. This way there is no need to lose time searching again how exactly that acronym was defined. Finally it generates an acronym table in docx format for ease of copying it to the final document.

The script is thought to be used with colleages keeping the database file in a shared folder. Some degree of protection is added to prevent overwriting others changes.

### And what does the name means?
Acronym + mate :)

# Status
This is a work in progress. Currently the script has a spanish command line interface. I have several improvements in my todo list like a translation (at least to English), better support for multiple users (Keeping track if the "database" is in use), upgrading to a GUI (Probably tkinter), etc.
Also I'm aware of some issues that need some work. The most critical is that acronyms are not found in pending to be approved changes.
If the script proves to be useful I will invest more time to it. 

# How to use
Launch 'mainScript.py' and follow the instructions. Currently all user interaction is done using the console. Use the command 'h' to get help. 

Detailed documentation and instructions comming soon.

