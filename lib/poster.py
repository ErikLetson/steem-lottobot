import piston, os, datetime, time
from piston.blog import Blog

class Poster(object):
    """
    Makes automated posts about lottobot's stats. Created by
    Lottobot object.
    """

    def __init__(self, master, template):#'master' is a lottobot instance, template is a file passed from lottobot

        self.master = master
        self.template = template

    def postify_lottos(self, data):

        chunk = "<br/>"

        #order the numbers first
        for lot in sorted(data):
            
            chunk += "<li># " + str(data)
            chunk += " (from " + str(data["start"]) + " to " + str(data["end"]) + "):"
            chunk += " Winner - " + str(data["winner"]) + ";"
            chunk += " Total entrants - " + str(data["entrants"]) + "</li>

        chunk += "<br/>"

        return chunk

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
        title = title.format(
            date = str(datetime.datetime.now().date()),
            acct = str(self.master.account_name),
            llnum = str(self.master.longlotto_number),
            prize = str(self.master.longlotto_prize),
            champ = str(self.master.longlotto_current_champ))
        body = body.format(
            date = str(datetime.datetime.now().date()),
            acct = str(self.master.account_name),
            llnum = str(self.master.longlotto_number),
            prize = str(self.master.longlotto_prize),
            champ = str(self.master.longlotto_current_champ))

        #return post
        return [title, body, tags]

    def check(self):
        """
        Check if it is time to create a post. If it is,
        do it.
        """

        pass

    def post(self):
        """
        Make a post automatically.
        """

        post = self.parse_post(template)

        ptitle = post[0]
        pbody = post[1]
        pauthor = self.master.account_name
        ptags = post[2]

        #self.master.steem.post()
