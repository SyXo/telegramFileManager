# telegramFileManager
File Manager using [pyrogram](https://github.com/pyrogram/pyrogram) library that
uses Telegram servers for storing
files. This program has an advanced ncurses interface, ability to transfer files
larger than 1.5G and more!

## This project is a WIP!!!

## Features
* Ability to show downloading and uploading progress
* Ability to transfer files larger than 1.5G (telegram's limit)
* Intuitive and fast scrolling when selecting uploaded files (WIP)
* Fast downloading and uploading of files (10Mbit UP | 15Mbit DOWN)
* Ability to upload/download multiple files at once (after 4 there if no speed
benefit) (WIP)
* Canceling and resuming file transfer progress (WIP)
* Interface that is similar to `rtorrent` (WIP)

## Installing requirements
```pip3 install -r requirements.txt -U```

### Or if you want to install them manually:
* Pyrogram ~~(pip3 install -U pyrogram)~~ The stable release will probably not
work, you need to use the development branch instead
(`pip3 install -U https://github.com/pyrogram/pyrogram/archive/develop.zip`)
* TgCrypto (`pip3 install -U tgcrypto`) (Recommended: used by `pyrogram`)


## Testing (currently only for GNU/Linux)
### The test generates a random file, uploads it to telegram, downloads it and then checks if the 2 files are the same
* Create a file in the script folder named `config.py` with the contents:
```
api_id = <app_id>
api_hash = <api_hash>
```
You can obtain these by following [Getting app_id and api_hash](https://github.com/BouncyMaster/telegramFileManager#getting-app_id-and-api_hash)
* Do `make test` to transfer a 3G file
* Additionally, you can give the `test_filesize=<size>` argument to specify size
* and/or `test_args=resume(1|2)` argument to check soft|force cancelling
* Example: `make test test_filesize=10G test_args=resume1`
* Your phone number and confirmation code will only be asked the first time
you run the tests, after that they will be saved as `a1.session` in the script
directory


## Installing telegramFileManager (WIP)
* Do `make install` to compile the dependencies and install the program in
`/usr/local/bin` (if you don't have root permissions, give `install_path=<dir>`
argument where `<dir>` is a path you can write to and is in your `$PATH`
variable) 

## Getting app_id and api_hash
* Log in to your [Telegram core](https://my.telegram.org)
* Go to 'API development tools' and fill out the form
* You will get the api_id and api_hash parameters required for user
authorization
* Enter your api_id and api_hash in your config file

## Donation
This project takes a lot of my time and donations would really motivate me to
continue working on this. You can donate either in bitcoin
```bitcoin:bc1q8h4r5vlje7yu4ya3vlslzju0td8zy0hayu0k6y```
or to my Payeer `P56752419`, any amount helps and i will be very thankful to you.

## TODO
* Make the `fileSelector` interface look like an actual file tree
(Currently shows all the files in one list)
* Verify if we can run this on multiple platforms (Currently only checked on Linux)

## End of the line
This is my first big project so please tell me if there are any mistakes I made.

What are you waiting for then? Go and store your legal Linux ISOs and have an
everliving archive of `Hannah Montana Linux` and `Puppy Linux` (the everliving
part is not guaranteed).