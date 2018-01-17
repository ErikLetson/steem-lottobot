import piston, os, time, random, ast, shutil, datetime
from piston.blog import Blog
from . import poster

_CONFIGPATH = os.path.join('data', 'config')
_COMPATH = os.path.join('data', 'command')
_SETUPPATH = os.path.join('data', 'setup')
#_POSTPATH = os.path.join('data', 'post_template')

#make kill file if it does not exist
#open(_KILLPATH, 'w').close()

class Lottobot(object):

    def __init__(self, directory):

        self.config_path = os.path.join(directory, _CONFIGPATH)
        self.command_path = os.path.join(directory, _COMPATH)
        self.setup_path = os.path.join(directory, _SETUPPATH)

        try:

            with open(self.config_path, 'r') as cf:

                ckeys = [x for x in cf.readlines()]

                #remove \n
                for i in range(0, len(ckeys)):
                
                    if ckeys[i][len(ckeys[i]) - 1] == '\n':

                        ckeys[i] = ckeys[i][0:len(ckeys[i]) - 1]

                self.account_name = ckeys.pop(0)
                self.node_addr = ckeys.pop(0)

                self.output_file = ckeys.pop(0)
                self.winners_file = ckeys.pop(0)
                self.error_file = ckeys.pop(0)

                self.associated_account = ckeys.pop(0)

        except Exception:

            print("Failed to find data files. Have you run the configurator?")
            return None

        self.steem = piston.Steem(self.node_addr, keys = ckeys)

        self.account = piston.account.Account(self.account_name, steem_instance = self.steem)

        self.blockchain = piston.blockchain.Blockchain(self.steem)
        
        #get the last index. history tracking will start from there
        for item in self.account.history():
            
            self.most_recent_index = item['index']
        
        self.on = True
        self.run_next = True

        #get the longlotto prize
        try:
            
            with open(os.path.join('data', 'prize'), 'r') as p:

                prize = float(p.readline())

        except Exception:

            prize = 25#default value

        #data
        self.urls = []
        self.next_urls = []#after we hit the 2hr mark, store urls for next lotto
        self.longlotto_entrants = []#usernames who are eligible for the longlotto
        self.longlotto_resteemers = []#those who resteemed the longlotto post
        self.longlotto_upvoters = []#those who upvote the longlotto post

        #blacklists
        self.longlotto_blacklist = []

        #get blacklist
        with open(os.path.join('data', 'blacklist'), 'r') as blf:

            for line in blf.readlines():

                if line[len(line) - 1] == '\n':

                    line = line[0:len(line) - 1]

                if line != "":

                    self.longlotto_blacklist.append(line)
        
        #stats
        self.lotto = 0#current lottery (iterates after a winner)
        self.check_pass = 0#iterated each time we check for transfers (resets after a winner)
        self.lotto_length = 900#total # of passes
        #self.holdover_threshold = 720#pass to carry over further entrants to next lotto
        self.holdover_threshold_passed = False
        self.history_cleared = False
        self.sleep_time = 10#rough number of seconds to delay between passes

        self.longlotto_number = 1#current longlotto (iterated every week at default)
        #self.longlotto_dividend = 68#the number that the check pass is divided by to see if it is time to decide the longlotto
        self.longlotto_prize = prize#in SBD
        self.longlotto_ongoing = False
        self.current_longlotto_post_id = None
        self.longlotto_current_champ = ""
        self.longlotto_delay = 10
        self.longlotto_on = False#if true, a longlotto will start, if false, it wont

        self.start_block = -1
        self.end_block = -1

        self.total_earnings_steem = 0
        self.total_earnings_sbd = 0

        self.steem_minimum = 0
        self.sbd_minimum = 0.001#cannot be 0

        self.most_recent_winner = ""

        #output strings
        self.outstr = ""
        self.errstr = ""
        self.winstr = ""

        #time readjustment
        self.start_time = -1
        self.target_end_time = -1

        #Empty lotto fallback vals
        self.empty_start_block = -1
        self.empty_end_block = -1
        self.empty_started = False

        #daily info
        self.daily_data = {
            "num_lottos": 0,
            "total_entrants": 0,
            "total_winners": 0,
            "valid_winners": 0,
            "random_winners": 0,
            "lottos": {}
        }
        self.purged = False

        #poster object
        self.poster = poster.Poster(self, os.path.join('data', 'update_post'))

        #run the bot
        #catch errors
        try:
            
            self.run()

        except Exception as e:

            with open(self.error_file, 'at') as f:

                f.write("##################################\n")
                f.write("##################################\n")
                f.write(str(time.ctime()) + '\n')
                f.write("Lottobot failed! Error info: \n\n")
                f.write(str(e) + "\n\n")
                f.write("Lottobot will now exit...\n")
                f.write("##################################\n")
                f.write("##################################\n")

            try:

                self.remember_setup()

            except Exception:

                with open(self.error_file, 'at') as f:

                    f.write("Unable to save setup...\n\n")
                    f.write("---------------------------\n\n")

    def check_run_commands(self):
        """
        Check the runcom file for runtime commands, then
        execute them.
        """

        rewrite = False

        with open(self.command_path, 'r') as rf:

            for line in rf.readlines():

                if line[0:4] == 'KILL':

                    self.on = False

                    rewrite = True

                elif line[0:4] == 'NEXT':

                    self.run_next = False

                    rewrite = True

                elif line[0:4] == 'TXEN':

                    self.run_next = True

                    rewrite = True

                elif line[0:4] == 'TRIM':

                    self.trim_logs()

                    rewrite = True

        if rewrite:

            #rewrite
            open(self.command_path, 'w').close()

    def trim_logs(self):

        open(self.output_file, 'w').close()
        open(self.winners_file, 'w').close()
        open(self.error_file, 'w').close()

    def purge_daily_data(self):

        self.daily_data = {
            "num_lottos": 0,
            "total_entrants": 0,
            "total_winners": 0,
            "valid_winners": 0,
            "random_winners": 0,
            "lottos": {}
        }
        self.purged = True

        self.outstr += "Purged daily data.\n\n"

    def archive_output_log(self):

        t = str(time.ctime())
        t = t.replace(":", "_")
        
        archive = "archive_" + t

        shutil.move(self.output_file, archive)

        #remake log
        open(self.output_file, 'w').close()

    def reward(self):

        try:

            self.steem.claim_reward_balance(account = self.account_name)

        except Exception:
                
            self.outstr += "Failed to withdraw reward balance. \n"
            self.outstr += "Writing to error log...\n"
                
            self.errstr += str(time.ctime()) + ": \n"
            self.errstr += "Failed to claim reward balance. Perhaps there is none available?\n"
            self.errstr += "----------------------------\n"

        if self.associated_account != 'None':

            balances = self.steem.get_balances(account = self.account_name)
            stm = float(balances['balance'])
            sbd = float(balances['sbd_balance'])

            if stm > self.steem_minimum:

                self.steem.transfer(self.associated_account, stm - self.steem_minimum, 'STEEM', memo = 'Automatic transfer', account = self.account_name)

            if sbd > (self.sbd_minimum + self.longlotto_prize):

                self.steem.transfer(self.associated_account, sbd - (self.sbd_minimum + self.longlotto_prize), 'SBD', memo = 'Automatic transfer', account = self.account_name)

    def setup_run(self):

        with open(self.setup_path, 'r') as sf:

            defaults = [x for x in sf.readlines()]

            if len(defaults) > 0:

                #remove \n, change type
                for i in range(0, len(defaults)):
                
                    if defaults[i][len(defaults[i]) - 1] == '\n':

                        defaults[i] = defaults[i][0:len(defaults[i]) - 1]

                    try:
                        
                        defaults[i] = int(defaults[i])

                    except Exception:

                        try:

                            defaults[i] = ast.literal_eval(defaults[i])

                        except Exception:

                            with open(self.error_file, 'at') as f:

                                f.write(str(time.ctime()) + "\n")
                                f.write("Invalid data detected in setup file.\n")
                                f.write("Data was: " + str(defaults[i]) + " at position " + str(i) + "\n")
                                f.write("Ignoring...\n")
                                f.write("----------------\n\n")

                self.lotto = defaults.pop(0)
                self.check_pass = defaults.pop(0)

                self.urls = defaults.pop(0)
                self.longlotto_entrants = defaults.pop(0)

    def remember_setup(self):

        with open(self.setup_path, 'w') as sf:

            sf.write(str(self.lotto) + '\n')
            sf.write(str(self.check_pass) + '\n')

            #record urls even if empty
            sf.write(str(self.urls) + '\n')
            sf.write(str(self.longlotto_entrants))

    def parse_post(self, postfile):
        """
        Parse the contents of a post file
        according to Lottobot's simplistic
        syntax
        """

        title = ""
        tags = []
        body = ""

        #read from file
        with open(postfile, 'r') as post:

            title = post.readline()

            #I should be ashamed...
            tags.append(post.readline())
            tags.append(post.readline())
            tags.append(post.readline())
            tags.append(post.readline())
            tags.append(post.readline())

            body = post.readline()

        #format body & title
        title = title.format(date = str(datetime.datetime.now().date()), acct = str(self.account_name), llnum = str(self.longlotto_number), prize = str(self.longlotto_prize), champ = str(self.longlotto_current_champ))
        body = body.format(date = str(datetime.datetime.now().date()), acct = str(self.account_name), llnum = str(self.longlotto_number), prize = str(self.longlotto_prize), champ = str(self.longlotto_current_champ))

        #return post
        return [title, body, tags]
        
    def post_longlotto(self):

        #eventually allow you to set this path in the configurator
        post = self.parse_post(os.path.join('data', 'llstart'))

        ptitle = post[0]
        pbody = post[1]
        pauthor = self.account_name
        ptags = post[2]
        
        #try to make the post
        try:

            self.outstr += "Making longlotto post for longlotto #" + str(self.longlotto_number) + "\n"
        
            self.steem.post(ptitle, pbody, author = pauthor, tags = ptags)

        except Exception:

            self.outstr += "WARNING! Failed to make longlotto post!\n"
            self.outstr += "Dumping to error log...\n\n"

            self.errstr += str(time.ctime()) + ": \n"
            self.errstr += "Failed to make longlotto post!\n\n"
            self.errstr += " Title was..... " + str(ptitle) + "\n"
            self.errstr += " Tags were..... " + str(ptags) + "\n\n"
            self.errstr += "BODY: \n"
            self.errstr += str(pbody) + "\n\n"
            self.errstr += "THE LONGLOTTO WILL NOT BE ABLE TO FUNCTION WITHOUT THIS POST!\n"
            self.errstr += "FIX IMMEDIATELY!!\n"
            self.errstr += "------------------\n"

        #clear history (piston shortcoming)
        self.outstr += "Clearing history...\n\n"
                
        self.steem.transfer(self.account_name, self.sbd_minimum, "SBD", account = self.account_name)

        ##Get the post id of this post
        b = Blog(self.account_name, self.steem)
        self.current_longlotto_post_id = str(b[0].identifier)#this is not ideal, to say the least

        self.start_block = self.blockchain.get_current_block_num()

        self.outstr += "Post id of the longlotto post: " + str(self.current_longlotto_post_id) + "\n"
        self.outstr += "Initial checking block #: " + str(self.start_block) + "\n"
        self.outstr += "Longlotto is ready to begin!\n\n"
        
    def check_longlotto_entries(self):

        self.outstr += "Begin longlotto check...\n"

        self.end_block = self.blockchain.get_current_block_num()

        followers = self.account.get_followers()

        #check thru the blockchain for resteemers & upvoters
        if self.start_block >= 0:

            for b in self.blockchain.blocks(start = self.start_block, stop = self.end_block):

                #here, b is an entire block
                #first, get the transactions on block b
                transactions = b['transactions']

                #next, get the operations of each transaction on block b
                for tran in transactions:

                    ops = tran['operations']

                    #now, see if this is a custom json operation, and, if
                    #it is, see if it is also a 'reblog'. If so, check the
                    #post id to see if it is our post
                    if ops[0][0] == 'custom_json' and ops[0][1]['json'][2:8] == 'reblog':

                        #convert the ops[0][1]['json'] string to a list
                        jsn = ast.literal_eval(ops[0][1]['json'])

                        #if the author is our account and the post is our
                        #longlotto post, add to the resteemers list
                        idtf = "@" + str(jsn[1]['author']) + "/" + str(jsn[1]['permlink'])

                        if idtf == self.current_longlotto_post_id:

                            self.outstr += "New longlotto resteemer found!\n"
                            self.outstr += "Name: " + str(jsn[1]['account']) + "\n\n"

                            self.longlotto_resteemers.append(jsn[1]['account'])

                    #if not, check if it was an upvote on our post
                    elif ops[0][0] == 'vote' and ops[0][1]['weight'] > 0 and '@' + self.account_name + "/" + ops[0][1]['permlink'] == self.current_longlotto_post_id:

                        self.outstr += "New longlotto upvoter found!\n"
                        self.outstr += "Name: " + str(ops[0][1]['voter']) + "\n\n"

                        self.longlotto_upvoters.append(ops[0][1]['voter'])

        #with our lists of resteemers & upvoters updated, check against follower
        #list for entrants
        for f in followers:

            if f in self.longlotto_resteemers and f in self.longlotto_upvoters and not f in self.longlotto_blacklist:

                self.outstr += str(f) + " is eligible for the longlotto! Adding...\n\n"

                self.longlotto_entrants.append(f)

                self.longlotto_resteemers.remove(f)
                self.longlotto_upvoters.remove(f)

        #update info for next pass
        self.start_block = self.end_block + 1

        #Print some info about the longlotto
        self.outstr += "Current longlotto entrants: " + str(len(self.longlotto_entrants)) + "\n\n"

    def end_longlotto(self):

        valid = False

        while not valid and len(self.longlotto_entrants) > 0:
            
            #choose a random winner from among the entrants list
            total_entries = len(self.longlotto_entrants)

            random.shuffle(self.longlotto_entrants)

            index = random.randint(0, total_entries - 1)

            self.outstr += "Choosing longlotto winner...\n\n"

            #send the prize money to the winner
            try:
                
                self.steem.transfer(self.longlotto_entrants[index], self.longlotto_prize, "SBD", account = self.account_name, memo = "Congratulations! You were the winner of @" + str(self.account_name) + "'s weekly lottery number " + str(self.longlotto_number) + "! Your prize is " + str(self.longlotto_prize) + " SBD! Thanks for playing!")
                self.longlotto_current_champ = self.longlotto_entrants[index]

                self.winstr += str(time.ctime()) + "\n"
                self.winstr += "Longlotto #" + str(self.longlotto_number) + " winner:\n"
                self.winstr += str(self.longlotto_current_champ) + "\n"
                self.winstr += "----------\n"
                self.winstr += "----------\n"
                
            except Exception:

                self.outstr += "Failed to make transfer to longlotto winner @" + str(self.longlotto_entrants[index]) + "\n"
                self.outstr += "Recording in log file and bypassing...\n\n"

                self.errstr += str(time.ctime()) + ": \n"
                self.errstr += "Failed to award longlotto prize.\n"
                self.errstr += "Winner: " + str(self.longlotto_entrants[index]) + "\n"
                self.errstr += "------------------------------\n\n"

                self.longlotto_entrants.pop(index)

            else:#Validate longlotto winner and break loop

                valid = True

        #if the longlotto was valid
        if len(self.longlotto_entrants) > 0:

            #announcement post
            post = self.parse_post(os.path.join('data', 'llend'))
            
            wtitle = post[0]
            wbody = post[1]
            wauthor = self.account_name
            wtags = post[2]

            #try to make the post
            try:

                self.outstr += "Making longlotto winner post for longlotto #" + str(self.longlotto_number) + "\n"
            
                self.steem.post(wtitle, wbody, author = wauthor, tags = wtags)

            except Exception:

                self.outstr += "Unable to make longlotto winning post!\n"
                self.outstr += "Reporting to error file...\n\n"

                self.errstr += str(time.ctime()) + "\n"
                self.errstr += "Failed to make longlotto winning post!\n\n"
                self.errstr += " Title was..... " + str(wtitle) + "\n"
                self.errstr += " Tags were..... " + str(wtags) + "\n\n"
                self.errstr += "BODY: \n"
                self.errstr += str(wbody) + "\n\n"
                self.errstr += "------------------\n"
            
        #if it was invalid...
        else:

            self.outstr += "Longlotto #" +str(self.longlotto_number) + " is invalidated!\n"
            self.outstr += "No valid winner names found!\n\n"

            #Do something else here

        #Reset the values of the lottery
        self.longlotto_entrants = []#usernames who are eligible for the longlotto
        self.longlotto_resteemers = []#those who resteemed the longlotto post
        self.longlotto_upvoters = []
        self.longlotto_number += 1

        self.start_block = -1
        self.end_block = -1

    def write_to_logs(self):

        if self.outstr != "":

            with open(self.output_file, 'at') as outfile:
                outfile.write(self.outstr + "\n")

            self.outstr = ""

        if self.errstr != "":

            with open(self.error_file, 'at') as errfile:
                errfile.write(self.errstr + "\n")

            self.errstr = ""

        if self.winstr != "":

            with open(self.winners_file, 'at') as winfile:
                winfile.write(self.winstr + "\n")

            self.winstr = ""

    def readjust_for_time(self):

        #if this is a fresh loop
        if self.start_time == -1:

            self.outstr += "Setting up times...\n"

            #set current time as start time
            self.start_time = time.time()

            #set the end time as 2.5 hrs from then
            self.target_end_time = time.time() + ((self.lotto_length - self.check_pass) * self.sleep_time)

            self.outstr += "Start: " + str(time.ctime(self.start_time)) + "\n"
            self.outstr += "Target: " + str(time.ctime(self.target_end_time)) + "\n\n"

        #else, readjust time as needed
        elif (time.time() + ((self.lotto_length - self.check_pass) * self.sleep_time)) > self.target_end_time:

            self.outstr += "Readjusting...\n"

            mod = 1
            found = False

            #until we find a mod that brings us below the target, increment mod
            while not found:

                if self.start_time + ((self.lotto_length - mod) * self.sleep_time) < self.target_end_time:

                    found = True

                else:

                    mod += 1

            if found:

                self.lotto_length -= mod

                self.outstr += "Modifying # passes by -" + str(mod) + "\n"

            else:

                self.outstr += "No good times found...\n\n"

        #if we are less than 1/2 hour from the end of the lotto
        if self.target_end_time - time.time() <= 1800:

            self.holdover_threshold_passed = True

    def populate_empty_lotto(self):

        """
        Chooses random entrants if the lotto reaches
        its end while no entrants are available.
        """

        self.empty_end_block = self.blockchain.get_current_block_num()

        self.outstr += "Lotto is empty. Populating with recent posts...\n\n"

        if self.empty_start_block >= 0:

            for b in self.blockchain.blocks(start = self.empty_start_block, stop = self.empty_end_block):

                for t in b['transactions']:

                    for o in t['operations']:

                        if o[0] == 'comment' and o[1]['parent_author'] == '':

                            self.urls.append('@' + str(o[1]['author']) + '/' + str(o[1]['permlink']))

                            self.outstr += "Found empty potential winner: @" + str(o[1]['author']) + "\n\n"

    def run(self):

        self.setup_run()

        while self.on:

            time.sleep(self.sleep_time)

            #Check the runcoms
            self.check_run_commands()

            #check if it is midnight UTC, and if so, purge daily data & post update
            t = time.gmtime()

            if t[5] in range(0, 9) and not self.purged:#3
                self.outstr += "Purging data and posting update...\n\n"
                self.poster.post()
                self.purge_daily_data()
            elif t[5] != 0 and self.purged:
                self.outstr += "Reset purge flag...\n\n"
                self.purged = False

            #if a kill command was detectected, end the loop
            if not self.on:

                self.remember_setup()

                #open file for output writing
                self.outstr += 'Successfully killed lottobot!\n'
                self.write_to_logs()

                break

            self.outstr += str(time.ctime()) + "\n"
            self.outstr += "Begin pass #" + str(self.check_pass) + " of lottery #" + str(self.lotto) + "\n\n"
            self.outstr += "Remaining passes: " + str(self.lotto_length - self.check_pass) + " (appx. end: " + time.strftime("%H:%M %p", time.localtime(((self.sleep_time * self.lotto_length)- (self.sleep_time * self.check_pass)) + time.time())) + ")\n"#make 900 settable in config
            self.outstr += "Current entrants: " + str(len(self.urls)) + "\n\n"

            #if the lottery is evenly divisible by the dividend, then a week has passed,
            #so we choose a weekly winner
            #if self.lotto % self.longlotto_dividend == 0 and self.check_pass == 0:

            if self.longlotto_on:
                
                #check the time. If it is Monday at 3:00PM (USCT), start the longlotto
                tm = time.gmtime()#hour is index 3, weekday is index 5
                
                if tm[6] == 0 and tm[3] == 20 and not self.longlotto_ongoing:

                    self.longlotto_ongoing = True
                
                    self.post_longlotto()

                #check if the longlotto is over
                elif tm[6] == 0 and tm[3] == 17 and self.longlotto_ongoing:

                    self.longlotto_ongoing = False

                    self.end_longlotto()

                #check for longlotto entrants
                if self.longlotto_ongoing:

                    if self.longlotto_delay > 0:

                        self.longlotto_delay -= 1

                    else:

                        self.longlotto_delay = 10

                        self.check_longlotto_entries()

            #readjust if needed
            self.readjust_for_time()

            #Check the history of the account we are associated with
            for item in self.account.history():

                if item['index'] > self.most_recent_index:
                    
                    self.most_recent_index = item['index']

                    if item['type'] == 'transfer':

                        self.outstr += "Found transfer. Validating...\n"

                        #validate url
                        try:

                            post_id = item['memo'][item['memo'].index('@'):len(item['memo'])]
                            self.steem.get_post(post_id)

                            cash = float(item['amount'][0:item['amount'].index(' ')])

                            if cash < 0.1:
                                
                                raise Exception

                        #If an error is encountered, log it and abandon the url
                        except Exception:

                            self.outstr += "Invalid url, post id, or cash amount" + "\n"
                            self.outstr += "Memo recieved: " + item['memo'] + "\n"
                            self.outstr += "Sender: " + item['from'] + "\n"
                            self.outstr += "Amount recieved: " + item['amount'] + "\n"
                            self.outstr += "Dumping entry data to log file...\n"

                            self.errstr += str(time.ctime()) + "\n"
                            self.errstr += str(item) + '\n'
                            self.errstr += "----------\n"
                            self.errstr += "----------\n"
                                
                        #else, url is valid
                        else:

                            self.outstr += str(post_id) + " is valid!\n"
                            self.outstr += "Cash recieved: " + str(item['amount']) + "\n"

                            if self.holdover_threshold_passed:

                                self.next_urls.append(post_id)

                                self.outstr += 'This post will be eligible for the next lottery\n\n'

                            else:

                                self.urls.append(post_id)

                                self.outstr += 'This post is eligible for the current lottery\n\n'

                            #resteem bonus chance
                            rs_chance = random.randint(0, 20)

                            self.outstr += "Roll for bonus resteem!\n"
                            self.outstr += "Rolled a " + str(rs_chance) + "\n"

                            if rs_chance == random.randint(0, 20):

                                try:

                                    self.steem.resteem(post_id, account = self.account_name)

                                    self.outstr += "Post " + str(post_id) + " wins a bonus resteem!\n"

                                    try:

                                        body = "Congratulations! This post won a bonus resteem from @" + str(self.account_name) + "! Everytime a post is entered into @" + str(self.account_name) + "'s lottery, there is a chance for it to win a bonus resteem, in addition to the jackpot of a 100% upvote from @" + str(self.account_name) + ". Do you have a post you would like to nominate for the lottery? Just send 0.1 SBD or STEEM to @" + str(self.account_name) + " and place the url of the post you want to nominate in the memo. Learn more by reading the [introductory post](https://steemit.com/introduceyourself/@lottobot/introducing-lottobot-are-you-ready-to-win-big)! Good luck!"
                                        
                                        self.steem.reply(post_id, body, author = self.account_name)

                                    except Exception:

                                        self.outstr += "Failed to comment on resteemed post " + str(post_id) + "\n"
                                        self.outstr += "Aborting...\n"
                                        self.outstr += "Logging to error file...\n\n"

                                        #log it
                                        self.errstr += str(time.ctime()) + "\n"
                                        self.errstr += "Failed to comment on resteemed post " + str(post_id) + "\n"
                                        self.errstr += "----------\n"
                                        self.errstr += "----------\n"

                                except Exception:

                                    self.outstr += "An error occured while trying to resteem " + str(post_id) + "\n"
                                    self.outstr += "Resteem failed\n"
                                    self.outstr += "Logging to error file...\n\n"

                                    #log it
                                    self.errstr += str(time.ctime()) + "\n"
                                    self.errstr += "Failed to resteem post " + str(post_id) + "\n"
                                    self.errstr += "----------\n"
                                    self.errstr += "----------\n"

            self.outstr += "End pass #" + str(self.check_pass) + "\n\n"
            
            self.check_pass += 1

            #if self.check_pass == self.holdover_threshold - 1:#last pass before carryover
            if self.holdover_threshold_passed and not self.history_cleared:
                
                self.outstr += "Beginning 'clear' transfer...\n"

                try:
                    
                    self.steem.transfer(self.account_name, self.sbd_minimum, "SBD", account = self.account_name)

                    self.outstr += "Lotto entrants cleared.\n"
                    self.outstr += "Entrants will now be added to upcoming lottery.\n"
                    self.outstr += "\n"

                except Exception:

                    self.outstr += "Failed to transfer 'clear' ammount to self.\n"
                    self.outstr += "Aborting...\n"
                    self.outstr += "Logging to error file...\n\n"

                    #log it
                    self.errstr += str(time.ctime()) + "\n"
                    self.errstr += "Failed to transfer to self.\n"
                    self.errstr += "----------\n"
                    self.errstr += "----------\n"

                self.history_cleared = True

            #if we are within 10 passes of the end, and we are empty, and the history hasnt been cleared, start the empty pass
            if self.lotto_length - self.check_pass <= 10 and len(self.urls) == 0 and self.history_cleared and not self.empty_started:

                self.empty_start_block = self.blockchain.get_current_block_num()

                self.empty_started = True

            if self.check_pass > self.lotto_length:#appx 2.5 hrs (default)

                self.outstr += "Choosing winner...\n"

                ents = len(self.urls)

                if self.empty_started and len(self.urls) == 0:

                    self.populate_empty_lotto()

                self.choose_winner()

                self.daily_data["num_lottos"] += 1
                self.daily_data["total_entrants"] += ents

                if self.most_recent_winner != "":
                    self.daily_data["total_winners"] += 1

                self.daily_data["lottos"][str(self.lotto)] = {
                    "start": time.strftime("%H:%M %p", self.start_time),
                    "end": time.strftime("%H:%M %p", time.time()),
                    "entrants": str(ents),
                    "winner": self.most_recent_winner
                }

                #Withdraw any extant account rewards, then transfer a certain
                #amount to the 'associated' account
                self.reward()

                #archive logs
                try:
                    
                    self.archive_output_log()

                except Exception:

                    self.outstr += "Unable to archive output log. \n"
                    self.outstr += "Logging error... \n\n"

                    self.errstr += str(time.ctime()) + "\n"
                    self.errstr += "Unable to archive log. \n"
                    self.errstr += "------------------------\n\n"

                if self.run_next:

                    self.outstr += "Lottery concluded after " + str(self.lotto_length) + " passes. \n"
                    self.outstr += "Reseting...\n"

                    self.check_pass = 0
                    self.lotto += 1
                    self.urls = self.next_urls
                    self.next_urls = []
                    self.start_time = -1
                    self.target_end_time = -1
                    self.lotto_length = 900#reset necessary
                    self.holdover_threshold_passed = False
                    self.history_cleared = False
                    self.empty_start_block = -1
                    self.empty_end_block = -1
                    self.empty_started = False

                    #begin next lottery
                    self.outstr += "Beginning lottery #" + str(self.lotto) + "\n\n"

                else:

                    #open file for output writing
                    self.outstr += "Successfully killed lottobot following lotto #" + str(self.lotto) + "!\n"

                    self.remember_setup()

                    break

            #log everything
            self.write_to_logs()

    def choose_winner(self):

        #########################################################
        # This is a reasonably fair random selection            #
        #########################################################

        votable = False
        
        while not votable and len(self.urls) > 0:

            #predata
            total_entries = len(self.urls)
            
            #step 1: shuffle the list in place
            random.shuffle(self.urls)

            #step 2: choose a random index
            index = random.randint(0, len(self.urls) - 1)

            #step 3: upvote the chosen post! (with some error checking)
            try:
                
                dat = self.steem.vote(self.urls[index], 100, self.account_name)

                self.outstr += "The winner is... " + str(self.urls[index]) + "\n\n"
                self.most_recent_winner = str(self.urls[index])
                
                self.winstr += str(time.ctime()) + "\n"
                self.winstr += "Lotto #" + str(self.lotto) + " winner:\n"
                self.winstr += str(self.urls[index]) + "\n"
                self.winstr += "Data dump:\n"
                self.winstr += str(dat) + "\n"
                self.winstr += "----------\n"
                self.winstr += "----------\n"

                #make a comment
                try:

                    valid = True

                    if not self.empty_started:
    
                        body = "Congratulations! This post has been awarded a 100% upvote by @" + str(self.account_name) + "! This post was the winner of lottery #" + str(self.lotto) + ", which had a total of " + str(total_entries) + " entries. @" + str(self.account_name) + " always has a lottery going on! If you would like to nominate a post for the current lottery, just send 0.1 SBD or STEEM to @" + str(self.account_name) + ", and include the url of the post you would like to nominate as a memo. Learn more by reading the [introductory post](https://steemit.com/introduceyourself/@lottobot/introducing-lottobot-are-you-ready-to-win-big)! Good luck!"
                        
                    else:

                        body = "Congratulations! This post has been awarded a 100% upvote by @" + str(self.account_name) + "! This post was selected from among all recent posts as the winner of lottery #" + str(self.lotto) + ", which had no valid entrants. You can win again by entering in @" + str(self.account_name) + "'s regular lottery! To nominate a post for the regular lottery, just send 0.1 SBD or STEEM to @" + str(self.account_name) + ", and include the url of the post you would like to nominate as a memo. Learn more by reading the [introductory post](https://steemit.com/introduceyourself/@lottobot/introducing-lottobot-are-you-ready-to-win-big)! Good luck!"
                        valid = False
                        
                    self.steem.reply(str(self.urls[index]), body, author = self.account_name)

                    if valid:
                        self.daily_data["valid_winners"] += 1
                    else:
                        self.daily_data["random_winners"] += 1

                except Exception:

                    self.outstr += "Failed to reply to winning post with a comment.\n"
                    self.outstr += "Body of comment was: " + body + "\n"
                    self.outstr += "Post id was: " + str(self.urls[index]) + "\n"
                    self.outstr += "Aborting comment..."
                    self.outstr += "Logging to error file...\n\n"

                    #log it
                    self.errstr += str(time.ctime()) + "\n"
                    self.errstr += "Failed to comment on winning post " + str(self.urls[index]) + "\n"
                    self.errstr += "Body of comment was: " + body + "\n"
                    self.errstr += "----------\n"
                    self.errstr += "----------\n"

            except Exception:

                with open(self.output_file, 'at') as outfile:

                    self.outstr += "Cannot upvote " + str(self.urls[index]) + "\n"
                    self.outstr += "Removing...\n\n"

                self.urls.pop(index)#pop takes an index

            else:

                votable = True

        #handle the issue of an invalid list of urls
        if len(self.urls) == 0:

            self.outstr += "Lottery is invalidated!\n"
            self.outstr += "No URLs found!\n\n"

            self.most_recent_winner = ""
        
