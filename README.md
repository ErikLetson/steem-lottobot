# Steem Lottobot

Lottobot is a simple command line automated program that will run a lottery on the Steem network. Lottobot can
recieve urls (in the form of memos attached to Steem or SBD transfers made to an account it uses) and add
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
option `h`). First, you will want to give Lottobot an account to hold its lottery with, so enter option `a` into the 
configurator. Next, you will want to give Lottobot access to the private WIF keys from that account 
so that it can operate it. The only keys that Lottobot *needs* access to are the posting key and the memo key. If
you want to use the "associated account" feature to make automatic transfers to another account, Lottobot will
also need your active key. Enter option `k` to pass keys to Lottobot.

NOTE: Keys that you pass to Lottobot are stored in plain text (in the file `data/config`) so that Lottobot can
act without having to ask for your credentials. THIS CAN BE A SECURITY RISK!

After configuring Lottobot, simply run the file `start.py` to begin. Lottobot will output messages to a series
of log files located in the `data` directory.

Lottobot can accept some commands while running. These commands are passed to Lottobot using the `runcom.py` file,
which is also called the runtime commander. Using the runtime commander is the recommended way to stop a running 
instance of Lottobot. To stop (kill) Lottobot immediately, enter `k` into the runtime commander, or to kill it at
the end of the current lottery, enter `n`.

To enter a post in Lottobot's lottery, simply send a transfer of at least 0.1 SBD or STEEM to the account that
Lottobot is set to use, and include the URL of the post in the memo of the transfer. Lottobot will then
automatically enter the post in the lottery! If there is a problem with the transfer, Lottobot will output an
error message to `error.log` and continue with the lottery.

IMPORTANT NOTE: Lottobot cannot return currency it recieves. If you send it an incorrect amount of currency, or
you include a malformed or incorrect memo, Lottobot will not be able to return your money! Be extra cautious
and ensure that you enter all information correctly!

ABOUT THE WEEKLY LOTTERY: Lottobot holds a weekly lottery in addition to its normal lottery. This weekly lottery
is mostly automatic. The only thing you should have to interfere with is the posts that Lottobot makes as part
of its weekly lottery. The contents of these posts are determined by the files `llstart` and `llend` in the `data`
directory. The syntax of these two files is as follows:

* The first line is the title of the post
* The next 5 lines are the tags of the post
* The final line is the body.

In addition, you will also see certain terms enclosed in curly braces (`{}`). These are variables. Here is a list
of the currently legal variables:

* `{acct}` = The name of the account (no `@` symbol)
* `{llnum}` = The current Weekly Lottery number
* `{prize}` = The current prize amount
* `{champ}` = The current Weekly Lottery champion (winner)

To change the value of the prize offered by Lottobot for the weekly lottery, simply change the first line of the
file `prize` in the `data` directory. This line should contain only a number. Note that this number is in SBD. If
an incorrect value is entered here (a non-number, for example), Lottobot will default to using 25 SBD as the
grand prize.

NOTE: The weekly lottery is relatively new and untested. Some kinks may exist. Additionally, it is not the most
friendly part of Lottobot's interface. Improvements are planned for the future.

## Contributions

Contributions are always welcome! Be sure you read [the license](LICENSE.txt) and that you sign [the signoff](SIGNOFF.txt) file.

Also, if you use Lottobot or a modified version of it to run a lottery yourself, I would love to hear from you! You can email me at
hmagellan (at) tutamail (dot) com.

## License

Steem Lottobot and all associated files are licensed under the MIT (Expat) license. You can find a copy of the
license included with Steem Lottobot [here](LICENSE.txt)
