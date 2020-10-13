# Distributed Systems Project-2 by Matvey Poltarykhin (BS18-SE-01) and Egor Gubanov (BS18-DS-01)

### Client(shell.py) is written by Egor Gubanov
### Storage and naming server logic is implemented by Matvey Poltarykhin

## Distributed File System has the following architecture:
![Image of Yaktocat](https://downloader.disk.yandex.ru/preview/7b610d55ff27bed0103bc16a9d7cff8733e8770e0a1dc55ac1498998e26cb425/5f856caf/Y9NQ2NpW1YBw1cjVlVNCKF6yyrwB1ybtL2ZG7Y5pTLgV14YrPdMQwnMIqTFrHs8IusMZ4PjHh0qlkUj90DwxLA==?uid=0&filename=2020-10-13+07-52-00.PNG&disposition=inline&hash=&limit=0&content_type=image%2Fpng&tknv=v2&owner_uid=219202647&size=2048x2048)

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
