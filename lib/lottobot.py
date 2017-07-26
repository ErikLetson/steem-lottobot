import piston, os, time, random

_CONFIGPATH = os.path.join('data', 'config')
_KILLPATH = os.path.join('data', 'kill')

#make kill file if it does not exist
open(_KILLPATH, 'w').close()

class Lottobot(object):

    def __init__(self):

        with open(_CONFIGPATH, 'r') as cf:

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

        self.steem = piston.Steem(self.node_addr, keys = ckeys)

        self.account = piston.account.Account(self.account_name, steem_instance = self.steem)

        #get the last index. history tracking will start from there
        for item in self.account.history():
            
            self.most_recent_index = item['index']
        
        self.on = True

        #data
        self.urls = []
        self.next_urls = []#after we hit the 2hr mark, store urls for next lotto

        #stats
        self.lotto = 0#current lottery (iterates after a winner)
        self.check_pass = 0#iterated each time we check for transfers (resets after a winner)

        #run the bot
        self.run()

    def run(self):

        while self.on:

            time.sleep(10)

            #Check the kill file for an external kill command
            with open(_KILLPATH, 'r') as kf:

                for line in kf.readlines():

                    if line[0:4] == 'KILL':

                        self.on = False

            #if a kill command was detectected, end the loop
            if not self.on:

                #open file for output writing
                with open(self.output_file, 'at') as outfile:

                    outfile.write('Successfully killed lottobot!\n')

                break

            with open(self.output_file, 'at') as outfile:

                outfile.write(str(time.ctime()) + "\n")
                outfile.write("Begin pass #" + str(self.check_pass) + " of lottery #" + str(self.lotto) + "\n")

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

                            if self.check_pass > 720:

                                self.next_urls.append(post_id)

                                with open(self.output_file, 'at') as outfile:

                                    outfile.write('This post will be eligible for the next lottery\n\n')

                            else:

                                self.urls.append(post_id)

                                with open(self.output_file, 'at') as outfile:

                                    outfile.write('This post is eligible for the current lottery\n\n')

                            #resteem bonus chance
                            rs_chance = random.randint(0, 20)

                            if rs_chance == random.randint(0, 20):

                                try:

                                    self.steem.resteem(post_id, account = self.account_name)

                                    with open(self.output_file, 'at') as outfile:
                                        
                                        outfile.write("Post " + str(post_id) + " wins a bonus resteem!\n")

                                    try:

                                        body = "Congratulations! This post won a bonus resteem from @" + str(self.account_name) + "! Everytime a post is entered into @" + str(self.account_name) + "'s lottery, there is a chance for it to win a bonus resteem, in addition to the jackpot of a 100% upvote from @" + str(self.account_name) + ". Do you have a post you would like to nominate for the lottery? Just send 0.1 SBD or STEEM to @" + str(self.account_name) + " and place the url of the post you want to nominate in the memo. Good luck! WARNING: @" + str(self.account_name) + "is an instance of SteemLottoBot, which is still under development. Use at your own risk!"
                                        
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

            if self.check_pass > 900:#appx 2.5 hrs

                with open(self.output_file, 'at') as outfile:

                    outfile.write("Choosing winner...\n")

                self.choose_winner()

                with open(self.output_file, 'at') as outfile:

                    outfile.write("Reseting...\n")

                self.check_pass = 0
                self.lotto += 1
                self.urls = self.next_urls
                self.next_urls = []

                with open(self.output_file, 'at') as outfile:

                    outfile.write("Beginning lottery #" + str(self.lotto) + "\n\n")           

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

                    body = "Congratulations! This post has been awarded a 100% upvote by @" + str(self.account_name) + "! This post was the winner of lottery #" + str(self.lotto) + ", which had a total of " + str(total_entries) + " entries. @" + str(self.account_name) + " always has a lottery going on! If you would like to nominate a post for the current lottery, just send 0.1 SBD or STEEM to @" + str(self.account_name) + ", and include the url of the post you would like to nominate as a memo. Good luck! WARNING: @" + str(self.account_name) + "is an instance of SteemLottoBot, which is still under development. Use at your own risk!"

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
        
