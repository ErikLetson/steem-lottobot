# Steem Lottobot

Lottobot is a simple command line automated program that will run a lottery on the Steem network. Lottobot can
recieve urls (in the form of memos attached to Steem or SBD transfers made to an associated account) and add
them to a pool of potential lottery winners. When the lottery is over, Lottobot will pick a random winner to
give a 100% upvote to, then begin a new lottery automatically. Lottobot is implemented in Python 3.x with the
Piston library and is licensed under the MIT (Expat) License.

## Contents

1. [Requirements](#requirements)
2. [Usage](#Usage)
3. [Contributions](#contributions)
4. [License](#license)

## Requirements

You will need Python (version 3.4.2 or later) and Piston (version 0.5.4 or later) to run Lottobot. You can
download a copy of Python [here](https://www.python.org/). Piston is available in [a repository on GitHub](https://github.com/xeroc/piston-lib).
However, the easiest way to install Piston is by using [pip](https://pypi.python.org/pypi/pip/). Run the command `pip3 install piston-lib`
to obtain a copy of the Piston library. For more information about installing the Piston library, refer to the installation instructions located 
[here](http://lib.piston.rocks/en/develop/installation.html).

## Usage

Before starting Lottobot, you should run the included file `configurator.py` and set up your configuration. The
configurator has several options (to see a complete list of options, as well as some more general help, enter 
option `h`). First, you will want to give Lottobot an account to associate with, so enter option `a` into the 
configurator. Next, you will want to give Lottobot access to the private WIF keys associated with that account 
so that it can operate it. The only keys that Lottobot *needs* access to are the posting key and the memo key. If
you want to use the "associated account" feature to make automatic transfers to another account, Lottobot will
also need your active key. Enter option `k` to pass keys to Lottobot.

NOTE: Keys that you pass to Lottobot are stored in plain text (in the file `data/config`) so that Lottobot can
act without having to ask for your credentials. THIS CAN BE A SECURITY RISK!

After configuring Lottobot, simply run the file `start.py` to begin. Lottobot will output messages to a series
of log files located in the `data` directory.

Lottobot can accept some commands while running. These commands are passed to Lottobot using the `runcom.py` file.
Using this file is the recommended way to stop a running instance of Lottobot. To stop (kill) Lottobot immediately,
enter `k` into the runtime commander (`runcom.py`), or to kill it at the end of the current lottery, enter `n`.

To enter a post in Lottobot's lottery, simply send a transfer of at least 0.1 SBD or STEEM to the account that
you associated Lottobot with, and include the url of the post in the memo of the transfer. Lottobot will then
automatically enter the post in the lottery! If there is a problem with the transfer, Lottobot will output an
error message to `error.log` and continue with the lottery.

IMPORTANT NOTE: Lottobot cannot return currency it recieves. If you send it an incorrect amount of currency, or
you include a malformed or incorrect memo, Lottobot will not be able to return your money! Be extra cautious
and ensure that you enter all information correctly!

## Contributions

Contributions are always welcome! Be sure you read [the license](LICENSE.txt) and that you sign [the signoff](SIGNOFF.txt) file.

## License

Steem Lottobot and all associated files are licensed under the MIT (Expat) license. You can find a copy of the
license included with Steem Lottobot [here](LICENSE.txt)
