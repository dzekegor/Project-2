# Distributed Systems Project-2 by Matvey Poltarykhin (BS18-SE-01) and Egor Gubanov (BS18-DS-01)

### Client(shell.py) is written by Egor Gubanov
### Storage and naming server logic is implemented by Matvey Poltarykhin

## Distributed File System has the following architecture:
![Architecture Scheme](https://lux.loli.net/2020/10/13/2020-10-13-07-52-00240ac1e846cfb221.png)

## How to use client application
1. Start
```
python3 shell.py
```
2. Commands
   Clear root directory
   - `$ init`
   
   Create empty file
   - `$ mkfile <path>`
     
   Show file content
   - `$ cat <path>`
   
   Send file from local machine to remote file system
   - `send <path> <absolute remote path>`
     
   Delete file
   - `delfile <path>`
   
   Show file info
   - `info <absolute path>`
     
   Copy file
   - `cp <path-from> <path-to>`
     
   Move file
   - `mv <path-from/file> <path-to>`
     
   Go to directory
   - `cd <path>`
     
   Show files and directories list
   - `ls <path>`
     
   Create empty directory
   - `mkdir <path>`
     
   Remove directory
   - `deldir <path>`
