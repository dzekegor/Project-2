# Distributed Systems Project-2 by Matvey Poltarykhin (BS18-SE-01) and Egor Gubanov (BS18-DS-01)

### Client(shell.py) is written by Egor Gubanov
### Storage and naming server logic is implemented by Matvey Poltarykhin

## Distributed File System has the following architecture:
![Alt Text](/home/mahler/2020-10-13%2007-52-00.PNG)

## How to use client application
1. Start
```
python3 shell.py
```
2. Commands
   - `$ init`
     
     Deletes everything from root directory
   - `$ mkfile <absolute path>`
     
     Creates an empty file in the given directory
   - `$ cat <absolute path>`
   
     Reads a file in the given directory
   - `send <absolute local path> <absolute remote path>`
     
     Sends a file from host to server
   - `delfile <absolute path>`
   
     Deletes a file from a given directory
   - `info <absolute path>`
     
     Returns an information about given file
   - `cp <path-from> <path-to>`
     
     Copies a file from given path to the given path
   - `mv <path-from> <path-to>`
     
     Moves a file from given path to the given path
   - `cd <path>`
     
     Opens the given directory
   - `ls <path>`
     
     Reads the given directory
   - `mkdir <absolute path>`
     
     Creates a directory
   - `deldir <absolute path>`
     
     Deletes a directory
