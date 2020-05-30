# telegramFileManager
File Manager using [pyrogram](https://github.com/pyrogram/pyrogram) library that
uses Telegram servers for storing
files. This program has an advanced ncurses interface, ability to transfer files
larger than 1.5G and more!

## This project is a WIP!!!

## Features
* Ability to show downloading and uploading progress
* Ability to transfer files larger than 1.5G (telegram's limit) 
* Intuitive and fast scrolling when selecting uploaded files
* Fast downloading and uploading of files (10Mbit UP | 15Mbit DOWN)
* Ability to upload/download multiple files at once (after 4 there if no speed
benefit)
* Canceling and resuming file transfer progress
* Interface that is similar to `rtorrent`

## Installing requirements
```pip3 install -r requirements.txt -U```

### Or if you want to install them manually:

* Pyrogram ~~(pip3 install -U pyrogram)~~ The stable release will probably not
work, you need to use the development branch instead
(`pip3 install -U https://github.com/pyrogram/pyrogram/archive/develop.zip`)
* TgCrypto (`pip3 install -U tgcrypto`) (Recommended: used by `pyrogram`)


## Installing telegramFileManager
* Do `make install` to compile the dependencies and install the program in
`/usr/local/bin` (if you don't have root permissions, give `install_path=<dir>`
argument where `<dir>` is a path you can write to and is in your `$PATH`
variable) 

### In order to get app_id and api_hash
* Log in to your Telegram core: https://my.telegram.org
* Go to 'API development tools' and fill out the form
* You will get the api_id and api_hash parameters required for user
authorization
* Enter your api_id and api_hash in your config file
* Optional: Obtain the channel_id in which to store the files (you can use
"me" instead to store them in Your Saved Messages)


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