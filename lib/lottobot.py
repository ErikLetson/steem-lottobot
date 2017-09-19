import piston, os, time, random
from piston.blog import Blog

_CONFIGPATH = os.path.join('data', 'config')
_COMPATH = os.path.join('data', 'command')
_SETUPPATH = os.path.join('data', 'setup')

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

        #data
        self.urls = []
        self.next_urls = []#after we hit the 2hr mark, store urls for next lotto
        self.longlotto_entrants = []#usernames who are eligible for the longlotto
        self.longlotto_resteemers = []#those who resteemed the longlotto post

        #stats
        self.lotto = 0#current lottery (iterates after a winner)
        self.check_pass = 0#iterated each time we check for transfers (resets after a winner)
        self.lotto_length = 900#total # of passes
        self.holdover_threshold = 720#pass to carry over further entrants to next lotto
        self.sleep_time = 10#rough number of seconds to delay between passes

        self.longlotto_number = 0#current longlotto (iterated every week at default)
        #self.longlotto_dividend = 68#the number that the check pass is divided by to see if it is time to decide the longlotto
        self.longlotto_prize = 25#in SBD
        self.longlotto_ongoing = False
        self.current_longlotto_post_id = None

        self.total_earnings_steem = 0
        self.total_earnings_sbd = 0

        self.steem_minimum = 0
        self.sbd_minimum = 0.001#cannot be 0

        #run the bot
        self.run()

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

    def reward(self):

        try:

            self.steem.claim_reward_balance(account = self.account_name)

        except Exception:

            pass#alert somehow here

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

                    defaults[i] = int(defaults[i])

                self.lotto = defaults.pop(0)
                self.check_pass = defaults.pop(0)

    def remember_setup(self):

        with open(self.setup_path, 'w') as sf:

            sf.write(str(self.lotto) + '\n')
            sf.write(str(self.check_pass))

    def post_longlotto(self):

        ptitle = "Weekly @" + str(self.account_name) + " Special Lottery #" + str(self.longlotto_number) + "! (GRAND PRIZE OF " + str(self.longlotto_prize) + " SBD!)"
        pbody = ""
        pauthor = self.account_name
        ptags = ["contest", "steemit", "steem", "lottobot", "money"]
        
        self.steem.post(ptitle, pbody, author = pauthor, tags = ptags)

        #clear history
        self.steem.transfer(self.account_name, self.sbd_minimum, "SBD", account = self.account_name)

        ##Get the post id of this post
        b = Blog(self.account_name, self.steem)
        self.current_longlotto_post_id = "https://steemit.com/" + str(ptags[0]) + "/" + str(b[0])

    def check_longlotto_entries(self):

        pass

    def end_longlotto(self):

        pass
        
    def run(self):

        self.setup_run()

        while self.on:

            time.sleep(self.sleep_time)

            #Check the runcoms
            self.check_run_commands()

            #if a kill command was detectected, end the loop
            if not self.on:

                self.remember_setup()

                #open file for output writing
                with open(self.output_file, 'at') as outfile:

                    outfile.write('Successfully killed lottobot!\n')

                break

            #if the lottery is evenly divisible by the dividend, then a week has passed,
            #so we choose a weekly winner
            #if self.lotto % self.longlotto_dividend == 0 and self.check_pass == 0:

            #check the time. If it is Saturday at 3:00PM, start the longlotto
            tm = time.gmtime()#hour is index 3, weekday is index 5
            
            if tm[6] == 5 and tm[3] == 15 and not self.longlotto_ongoing:

                self.longlotto_ongoing = True
            
                self.post_longlotto()

            #check if the longlotto is over
            elif tm[6] == 5 and tm[3] == 12 and self.longlotto_ongoing:

                self.longlotto_ongoing = False

                self.end_longlotto()

            #check for longlotto entrants
            if self.longlotto_ongoing:

                self.check_longlotto_entries()

            with open(self.output_file, 'at') as outfile:

                outfile.write(str(time.ctime()) + "\n")
                outfile.write("Begin pass #" + str(self.check_pass) + " of lottery #" + str(self.lotto) + "\n\n")
                outfile.write("Remaining passes: " + str(900 - self.check_pass) + " (appx. end: " + time.strftime("%H:%M %p", time.localtime(((10 * self.lotto_length)- (10 * self.check_pass)) + time.time())) + ")\n")#make 900 settable in config
                outfile.write("Current entrants: " + str(len(self.urls)) + "\n\n")

            #Check the history of the account we are associated with
            for item in self.account.history():

                if item['index'] > self.most_recent_index:
                    
                    self.most_recent_index = item['index']

                    if item['type'] == 'transfer':

                        with open(self.output_file, 'at') as outfile:

                            outfile.write("Found transfer. Validating...\n")

                        #validate url
                        try:

                            post_id = item['memo'][item['memo'].index('@'):len(item['memo'])]
                            self.steem.get_post(post_id)

                            cash = float(item['amount'][0:item['amount'].index(' ')])

                            if cash < 0.1:
                                
                                raise Exception

                        #If an error is encountered, log it and abandon the url
                        except Exception:

                            with open(self.output_file, 'at') as outfile:

                                outfile.write("Invalid url, post id, or cash amount" + "\n")
                                outfile.write("Memo recieved: " + item['memo'] + "\n")
                                outfile.write("Sender: " + item['from'] + "\n")
                                outfile.write("Amount recieved: " + item['amount'] + "\n")
                                outfile.write("Dumping entry data to log file...\n")

                            with open(self.error_file, 'at') as f:#'a' for 'append'
                                
                                f.write(str(time.ctime()) + "\n")
                                f.write(str(item) + '\n')
                                f.write("----------\n")
                                f.write("----------\n")
                                
                        #else, url is valid
                        else:

                            with open(self.output_file, 'at') as outfile:
                                
                                outfile.write(str(post_id) + " is valid!\n")
                                outfile.write("Cash recieved: " + str(item['amount']) + "\n")

                            if self.check_pass >= self.holdover_threshold:

                                self.next_urls.append(post_id)

                                with open(self.output_file, 'at') as outfile:

                                    outfile.write('This post will be eligible for the next lottery\n\n')

                            else:

                                self.urls.append(post_id)

                                with open(self.output_file, 'at') as outfile:

                                    outfile.write('This post is eligible for the current lottery\n\n')

                            #resteem bonus chance
                            rs_chance = random.randint(0, 20)

                            with open(self.output_file, 'at') as outfile:
                                        
                                outfile.write("Roll for bonus resteem!\n")
                                outfile.write("Rolled a " + str(rs_chance) + "\n")

                            if rs_chance == random.randint(0, 20):

                                try:

                                    self.steem.resteem(post_id, account = self.account_name)

                                    with open(self.output_file, 'at') as outfile:
                                        
                                        outfile.write("Post " + str(post_id) + " wins a bonus resteem!\n")

                                    try:

                                        body = "Congratulations! This post won a bonus resteem from @" + str(self.account_name) + "! Everytime a post is entered into @" + str(self.account_name) + "'s lottery, there is a chance for it to win a bonus resteem, in addition to the jackpot of a 100% upvote from @" + str(self.account_name) + ". Do you have a post you would like to nominate for the lottery? Just send 0.1 SBD or STEEM to @" + str(self.account_name) + " and place the url of the post you want to nominate in the memo. Good luck!"
                                        
                                        self.steem.reply(post_id, body, author = self.account_name)

                                    except Exception:

                                        with open(self.output_file, 'at') as outfile:

                                            outfile.write("Failed to comment on resteemed post " + str(post_id) + "\n")
                                            outfile.write("Aborting...\n")
                                            outfile.write("Logging to error file...\n\n")

                                        #log it
                                        with open(self.error_file, 'at') as f:

                                            f.write(str(time.ctime()) + "\n")
                                            f.write("Failed to comment on resteemed post " + str(post_id) + "\n")
                                            f.write("----------\n")
                                            f.write("----------\n")

                                except Exception:

                                    with open(self.output_file, 'at') as outfile:

                                        outfile.write("An error occured while trying to resteem " + str(post_id) + "\n")
                                        outfile.write("Resteem failed\n")
                                        outfile.write("Logging to error file...\n\n")

                                    #log it
                                    with open(self.error_file, 'at') as f:

                                        f.write(str(time.ctime()) + "\n")
                                        f.write("Failed to resteem post " + str(post_id) + "\n")
                                        f.write("----------\n")
                                        f.write("----------\n")

            with open(self.output_file, 'at') as outfile:
                
                outfile.write("End pass #" + str(self.check_pass) + "\n\n")
            
            self.check_pass += 1

            if self.check_pass == self.holdover_threshold - 1:#last pass before carryover

                with open(self.output_file, 'at') as outfile:

                    outfile.write("Beginning 'clear' transfer...\n")

                try:
                    
                    self.steem.transfer(self.account_name, self.sbd_minimum, "SBD", account = self.account_name)

                    with open(self.output_file, 'at') as outfile:
                        
                        outfile.write("Lotto entrants cleared.\n")
                        outfile.write("Entrants will now be added to upcoming lottery.\n")
                        outfile.write("\n")

                except Exception:

                    with open(self.output_file, 'at') as outfile:

                        outfile.write("Failed to transfer 'clear' ammount to self.\n")
                        outfile.write("Aborting...\n")
                        outfile.write("Logging to error file...\n\n")

                    #log it
                    with open(self.error_file, 'at') as f:

                        f.write(str(time.ctime()) + "\n")
                        f.write("Failed to transfer to self.\n")
                        f.write("----------\n")
                        f.write("----------\n")

            if self.check_pass > self.lotto_length:#appx 2.5 hrs (default)

                with open(self.output_file, 'at') as outfile:

                    outfile.write("Choosing winner...\n")

                self.choose_winner()

                #Withdraw any extant account rewards, then transfer a certain
                #amount to the 'associated' account
                self.reward()

                if self.run_next:

                    with open(self.output_file, 'at') as outfile:

                        outfile.write("Reseting...\n")

                    self.check_pass = 0
                    self.lotto += 1
                    self.urls = self.next_urls
                    self.next_urls = []

                    #check for weekly contest entrants
                    ####TODO

                    #begin next lottery
                    with open(self.output_file, 'at') as outfile:

                        outfile.write("Beginning lottery #" + str(self.lotto) + "\n\n")

                else:

                    #open file for output writing
                    with open(self.output_file, 'at') as outfile:

                        outfile.write("Successfully killed lottobot following lotto #" + str(self.lotto) + "!\n")

                    break

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

                with open(self.output_file, 'at') as outfile:

                    outfile.write("The winner is... " + str(self.urls[index]) + "\n\n")

                with open(self.winners_file, 'at') as lwf:

                    lwf.write(str(time.ctime()) + "\n")
                    lwf.write("Lotto #" + str(self.lotto) + " winner:\n")
                    lwf.write(str(self.urls[index]) + "\n")
                    lwf.write("Data dump:\n")
                    lwf.write(str(dat) + "\n")
                    lwf.write("----------\n")
                    lwf.write("----------\n")

                #make a comment
                try:

                    body = "Congratulations! This post has been awarded a 100% upvote by @" + str(self.account_name) + "! This post was the winner of lottery #" + str(self.lotto) + ", which had a total of " + str(total_entries) + " entries. @" + str(self.account_name) + " always has a lottery going on! If you would like to nominate a post for the current lottery, just send 0.1 SBD or STEEM to @" + str(self.account_name) + ", and include the url of the post you would like to nominate as a memo. Good luck!"

                    self.steem.reply(str(self.urls[index]), body, author = self.account_name)

                except Exception:

                    with open(self.output_file, 'at') as outfile:

                        outfile.write("Failed to reply to winning post with a comment.\n")
                        outfile.write("Body of comment was: " + body + "\n")
                        outfile.write("Post id was: " + str(self.urls[index]) + "\n")
                        outfile.write("Aborting comment...")
                        outfile.write("Logging to error file...\n\n")

                    #log it
                    with open(self.error_file, 'at') as f:

                        f.write(str(time.ctime()) + "\n")
                        f.write("Failed to comment on winning post " + str(self.urls[index]) + "\n")
                        f.write("Body of comment was: " + body + "\n")
                        f.write("----------\n")
                        f.write("----------\n")

            except Exception:

                with open(self.output_file, 'at') as outfile:

                    outfile.write("Cannot upvote " + str(self.urls[index]) + "\n")
                    outfile.write("Removing...\n\n")

                self.urls.pop(index)#pop takes an index

            else:

                votable = True

        #handle the issue of an invalid list of urls
        if len(self.urls) == 0:

            with open(self.output_file, 'at') as outfile:

                outfile.write("Lottery is invalidated!\n")
                outfile.write("No URLs found!\n\n")
        
