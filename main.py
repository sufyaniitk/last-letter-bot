import asyncio
import discord
import pandas as pd
import pickle5 as pickle
import urllib.request
import ssl
import warnings

from bs4 import BeautifulSoup as bs

warnings.filterwarnings("ignore")
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

def cindex(ch):
    # returns position of channel in channels.pkl
    f = open('word/channels.pkl', 'rb')
    s = pickle.load(f)
    s = s.index(ch)
    f.close()
    return s

def exists(v, f):
    # check if v exists in a pickle list f
    file_ = open(f, 'rb')
    s = pickle.load(file_)
    file_.close()
    if v in s: return True
    else: return False

def insertlist(v, f):
    # append v to a pickle list f
    file_ = open(f, 'rb')
    s = pickle.load(file_)
    file_.close()

    s.append(v)
    file_ = open(f, 'wb')
    pickle.dump(s, file_)
    file_.close()

def insertdict(v, f):
    # saves v with a filler value in pickle dictionary f
    file_ = open(f, 'rb')
    s = pickle.load(file_)
    file_.close()

    s[v] = ["a", 1]
    file_ = open(f, 'wb')
    pickle.dump(s, file_)
    file_.close()

def pullout(v, f):
    # removes v from a pickle list f
    # returns True if successful, ie v was in f to begin with
    file_ = open(f, 'rb')
    s = pickle.load(file_)
    file_.close()

    try:
        i = s.index(v)
        s.remove(v)
        file_ = open(f, 'wb')
        pickle.dump(s, file_)
        file_.close()
        return [True, i]
    
    except ValueError:
        return [False, 2]

def isaword(w):
    # checks if a word exists
    # True if it does

    gcontext = ssl.SSLContext()

    url = "https://www.thesaurus.com/browse/" + w
    gcontext = ssl.SSLContext()

    try:
        bs(urllib.request.urlopen(url, context=gcontext).read(), "lxml")
        return True

    except urllib.error.HTTPError:
        return False

def lastlettermatches(cid, w, au):
    # checks whether last-letter-first-letter rule is followed
    # True if it is

    file_ = open('word/letters.pkl', 'rb')
    s = pickle.load(file_)
    s = s[cid]
    file_.close()

    if w[0] == s[0] and au != s[1]: return True
    else: return False

def lastletter(cid):
    # returns the last letter of a channel

    file_ = open('word/letters.pkl', 'rb')
    s = pickle.load(file_)
    s = s[cid][0]
    file_.close()
    return s

def userrule(cid, au):
    # rule that a user can't play twice in a row
    # True if followed
    f = open('word/letters.pkl', 'rb')
    s = pickle.load(f)
    s = s[cid][1]

    if s != au: return True
    else: return False

def uniqueword(cid, w):
    # checks if words was used in channel
    # True if user used unique word

    df = pd.read_pickle('word/words.pkl')
    e = w in df.columns
    if not e: return True # word not in dataframe
    else:
        # word in dataframe, e is 1
        s = cindex(cid)
        r = df[w][s]
        return (r^e) 
        # if r is 1, word was used, returns 1^1 (False); if r is 0, word wasn't used, returns 1^0 (True)

async def updateuniqueworddf(cid, w):
    # update channel value of a word from 0 to 1 if it exists
    # add a column for the word if doesn't already exist

    f = open('word/channels.pkl', 'rb')
    s = pickle.load(f)
    l = len(s)
    s = s.index(cid)
    f.close()

    # this codeblock returns the channel's position in the dataframe
    # (which is consistent with channels.pkl, dont worry)

    df = pd.read_pickle('word/words.pkl')
    if w in df.columns:
        df[w][s] = 1
        df["1"][s] += 1
        df.to_pickle('word/words.pkl')
    else:
        lz = [0]*(l)
        lz[0] = 1
        lz[s] = 1
        df["1"][s] += 1
        df.insert(len(df.columns), w, lz, allow_duplicates=True)
        df.to_pickle('word/words.pkl')

async def resetchannel(cid):
    # reset word count of a channel
    # global word count of users remains unaffected

    s = cindex(cid)

    f = open('word/letters.pkl', 'rb')
    t = pickle.load(f)
    f.close()
    t[cid] = ['a', 1]

    g = open('word/letters.pkl', 'wb')
    pickle.dump(t, g)
    g.close()

    df = pd.read_pickle('word/words.pkl')
    for w in df.columns:
        df[w][s] = 0
    df.to_pickle('word/words.pkl')

    df = pd.read_pickle('word/lb.pkl')
    for u in df.columns:
        df[u][s] = 0
    df.to_pickle('word/lb.pkl')

async def hasadmin(au, sv):
    # pretty straightforward
    m = await sv.fetch_member(au)
    return (('administrator', True) in m.guild_permissions)

async def sendlb(lb, rank, sv, au, ch):
    # sends the top scorers in a server
    # also sends the rank of user requesting, if it exists

    em = discord.Embed(colour=0x0000ff, description="**Leaderboard for " + sv + "**\n \n")
    w = sorted(lb[1])[::-1]
    finallb = [[], w]
    i = 0

    while i<5:
        try: 
            finallb[0].append(lb[0][lb[1].index(w[i])])
            lb[1][lb[1].index(w[i])] = 0
            i += 1
        except IndexError:
            break

    for i in range(len(finallb[0])):
        em.description += "`" + str(i+1) + ".` <@" + str(finallb[0][i]) + "> - `" + str(finallb[1][i]) + "` words \n"
    
    if not rank: em.description += "\n <@" + str(au) + ">, you have 0 words! Try playing sometime uwu"
    else: em.description += "\n <@" + str(au) + ">, you're placed number `" + str(rank) + "` on the leaderboard!"

    await ch.send(embed=em)

async def updatelbdf(cid, u):
    # updates local and global word count of a user

    df = pd.read_pickle('word/lb.pkl')
    f = open('word/channels.pkl', 'rb')
    s = pickle.load(f)
    l = len(s)
    s = s.index(cid)
    f.close()
    try:
        df[u][0] += 1
        df[u][s] += 1
    except:
        # user not in dataframe
        lz = [0] * l
        lz[0] = 1
        lz[s] = 1
        df.insert(len(df.columns), u, lz, allow_duplicates=True)

    df.to_pickle('word/lb.pkl')

f = open('id.pkl', 'rb')
bot = pickle.load(f)
f.close()

@client.event
async def on_message(message):
    ch = message.channel
    au = message.author.id
    mnt = "<@" + str(au) + ">"
    isadmin = await hasadmin(au, message.guild)
    if not(au == bot):
        if message.content.startswith('c!help'):

            em = discord.Embed(color=0x00ff00, description='`Command List`')
            em.description += '\n `c!add`: Add channel to start word game **admin**'
            em.description += '\n `c!remove`: Remove channel **admin**'
            em.description += '\n `c!reset`: Reset word count and leaderboard for channel **admin**'
            em.description += '\n \n \n `c!count`: Return unique words used in the channel'
            em.description += '\n `c!lb`: Shows the (server) leaderboard'
            # em.description += '\n `c!vote`: Vote'
            # em.description += '\n `c!invite`: Invite'

            # i did not write this.
    
            await message.channel.send(embed=em)
        
        if message.content == ('c!count'):
            df = pd.read_pickle('word/words.pkl')
            s = cindex(ch.id)

            c = df["1"][s]
            msg = "`" + str(c) + "` **unique words used in this channel!**"
            em = discord.Embed(colour=0x0000ff, description=msg)
            msg = await ch.send(embed=em)
            await asyncio.sleep(2)
            await msg.delete()
            await message.delete()

        if message.content == ('c!reset'):
            # reset words of a channel
            if isadmin:
                await resetchannel(ch.id)
                await ch.send("**The channel has been reset! You may start with the letter a.**")
                await message.delete()
            
            else:
                msg = await ch.send(mnt + " **you do not have permissions for this!**")
                await asyncio.sleep(2)
                msg.delete()
                message.delete()

        if message.content == ('c!add'):
            # add new channel

            if isadmin:
                if exists(ch.id, 'word/channels.pkl'):
                    # channel already added
                    await ch.send("Channel already added.")
        
                else:
                    if not exists(message.guild.id, 'word/servers.pkl'):
                        # channel not already added
                        insertlist(ch.id, 'word/channels.pkl')
                        insertlist(message.guild.id, 'word/servers.pkl')
                        insertdict(ch.id, 'word/letters.pkl')
                        # add to non df files

                        df = pd.read_pickle('word/words.pkl')
                        col = df.columns
                        lz = [0] * len(col)
                        df2 = pd.DataFrame([lz], columns=col)
                        df3 = df.append(df2, ignore_index=True)
                        df3.to_pickle('word/words.pkl')
                        # adds a row for the channel to the unique word dataframe

                        df = pd.read_pickle('word/lb.pkl')
                        col = df.columns
                        lz = [0] * len(col)
                        df2 = pd.DataFrame([lz], columns=col)
                        df3 = df.append(df2, ignore_index=True)
                        df3.to_pickle('word/lb.pkl')
                        # adds a row for the channel to the leaderboard dataframe

                        await ch.send("Channel added! :D")
                        await ch.send("You may start the game! The letter is **a**.")
                    
                    else:
                        msg = await ch.send("**You already have a channel added in this server!**")
                        await asyncio.sleep(2)
                        await msg.delete()
                        await message.delete()
                
            else:
                msg = await ch.send(mnt + " **you do not have permissions for this!**")
                await asyncio.sleep(2)
                await msg.delete()
                await message.delete()

    
        if message.content == ('c!remove'):
            if isadmin:
                if exists(ch.id, 'word/channels.pkl'):
                    # channel exists
                    a = pullout(ch.id, 'word/channels.pkl')
                    b = pullout(message.guild.id, 'word/servers.pkl')

                    f = open('word/letters.pkl', 'rb')
                    s = pickle.load(f)
                    f.close()
                    s.pop(ch.id, None)
                    f = open('word/letters.pkl', 'wb')
                    pickle.dump(s, f)
                    f.close()
                    # this codeblock removes the channel from letters.pkl

                    f = open('word/channels.pkl', 'rb')
                    x = pickle.load(f)
                    x = len(x)
                    f.close()

                    renamedict = {}
                    exit = 0
                    while not(exit):
                        i = 0
                        while i < a[1]:
                            renamedict[i] = i
                            i+=1
                        while i<x:
                            renamedict[i+1] = i
                            i+=1
                        exit = 1

                    df = pd.read_pickle('word/words.pkl')
                    df = df.drop(a[1])
                    df = df.rename(index=renamedict)
                    df.to_pickle('word/words.pkl')

                    df = pd.read_pickle('word/lb.pkl')
                    df = df.drop(a[1])
                    df = df.rename(index=renamedict)
                    df.to_pickle('word/lb.pkl')
                    # removes channel from dataframes
                    # re-indexes dataframes for consistency with channels.pkl

                    await ch.send("Channel removed.")

                else:
                    # channel doesn't exist 
                    await ch.send("Channel wasn't added!")
            
            else:
                msg = await ch.send(mnt + " **you do not have permissions for this!**")
                await asyncio.sleep(2)
                await msg.delete()
                await message.delete()
        
        if message.content == 'c!lb' or message.content == 'c!leaderboard' and exists(ch.id, 'word/channels.pkl'):
            df = pd.read_pickle('word/lb.pkl')
            lb = [[], []]
            rank = 0
            
            s = cindex(ch.id)

            for u in df.columns:
                if df[u][s] != 0: 
                    lb[0].append(u)
                    lb[1].append(df[u][s])
            
            if len(lb[0]) == 0: await ch.send("**Send some messages first!**")
            else:
                w = sorted(lb[1])[::-1]
                u = lb[0]
                if au not in u:
                    await sendlb(lb, rank, message.guild.name, au, ch)
                else:
                    rank = w.index(lb[1][lb[0].index(au)]) + 1 # there has to be a better way of doing this
                    await sendlb(lb, rank, message.guild.name, au, ch)
    
        if not(message.content.startswith("c!")) and exists(ch.id, 'word/channels.pkl') and len(message.content) != 0:
            # actual game codeblock
            word = message.content.lower()
            emoji = '\N{White Heavy Check Mark}'

            if isaword(word) and lastlettermatches(ch.id, word, au):
                # two rules followed, check for repetition

                if uniqueword(ch.id, word):
                    f = open('word/letters.pkl', 'rb')
                    s = pickle.load(f)
                    f.close()
                    s[ch.id] = [word[len(word)-1:], au]
                    f = open('word/letters.pkl', 'wb')
                    pickle.dump(s, f)
                    f.close()
                    # above codeblock updates last letter, and last user

                    await updateuniqueworddf(ch.id, word)
                    await updatelbdf(ch.id, au)
                    await message.add_reaction(emoji)

                else:
                    msg = await ch.send(mnt + " **the word " + word + " has already been used!**")
                    await asyncio.sleep(2)
                    await msg.delete()
                    await message.delete()

            elif not(isaword(word)):
                # not a word
                msg = await ch.send(mnt + " **" + word + " is not a word!**")
                await asyncio.sleep(2)
                await msg.delete()
                await message.delete()

            else:
                # either user played twice
                # or first letter didn't match

                if userrule(ch.id, au):
                    msg = await ch.send(mnt + " ** The first letter of your word should be " + lastletter(ch.id) + "!**")
                else:
                    msg = await ch.send(mnt + " **It's not your turn!**")
                await asyncio.sleep(2)
                await msg.delete()
                await message.delete()

f = open('token.pkl', 'rb')
v = pickle.load(f)
f.close()

client.run(v)
