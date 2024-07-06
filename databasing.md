### Files

When written, the bot utilised Python's `pickle` library to store five datasets.
- `channels.pkl`
- `servers.pkl`
- `lb.pkl` (or `leaderboard.pkl`)
- `letters.pkl`
- `words.pkl`

#### Storage and Purpose

i. `channels.pkl` stores channel objects that are currently active in the game. The structure used is a list, and the channels are stored by their `id`. The bot uses this to avoid interrupting conversations and limit the game to dedicated channels.

ii. `servers.pkl` stores a list of `guild id`s of servers that have a channel with the game active. This prevents a server from having multiple channels open with the game active.

iii. `lb.pkl` stores a `pandas DataFrame`, say`df`. `df[i][j]` stores how many words the user with `userid = j` has sent in the channel with `channelid = i`. This is super redundant now that I see it, although the intention was to have some way to extract a global leaderboard if necessary. Indeed, a user's total word count is stored in `df[0][j]`

iv. `letters.pkl` stores a `dict`ionary. Each entry is of the form `channelid: [last_letter, user]`

v. `words.pkl` stores another `pandas DataFrame`, say `df2`. `df2[i][j]` stores whether the word `j` has been used in channel `i`.

#### Consistency
A remarkable fact is the bot ensures that for each channel id `ch`, its index in `channels.pkl`, `lb.pkl`, and `words.pkl` is the same. The way this is implemented means `letters.pkl` being a dictionary is redundant, but oh well. I didn't spot that.

### Some code snippets
(Warning: horrible naming practices and a nightmare for someone used to static typing ahead)

The snippets I'm presenting here are of the admin commands, such as adding, removing, and resetting a channel.

#### Adding a channel
Once the bot has ensured the use requesting the addition has admin permissions and that the guild has no other channels active, the bot does one last check and runs the following codeblock:
```py
if not exists(message.guild.id, 'word/servers.pkl'):
  # channel not already added
  insertlist(ch.id, 'word/channels.pkl') # add channel id to the list
  insertlist(message.guild.id, 'word/servers.pkl') # add server id to the list
  insertdict(ch.id, 'word/letters.pkl') # add the channel to the dict
  # add to non df files

  df = pd.read_pickle('word/words.pkl') # load words.pkl to add a row for the channel
  col = df.columns
  lz = [0] * len(col) # new row is initialised to 0
  df2 = pd.DataFrame([lz], columns=col) # take the row
  df3 = df.append(df2, ignore_index=True) # append it
  df3.to_pickle('word/words.pkl') # save it
  # adds a row for the channel to the unique word dataframe

  df = pd.read_pickle('word/lb.pkl') # do the same for lb
  col = df.columns
  lz = [0] * len(col)
  df2 = pd.DataFrame([lz], columns=col)
  df3 = df.append(df2, ignore_index=True)
  df3.to_pickle('word/lb.pkl')
  # adds a row for the channel to the leaderboard dataframe

  await ch.send("Channel added! :D")
  await ch.send("You may start the game! The letter is **a**.")
```

#### Removing a channel
After doing the necessary checks, the bot needs to remove the channel and server ids from the lists and remove the row, right? **Wrong.** You see, the dataframe rows are not indexed by channel ids directly, but rather by `0, 1, 2, 3, ...` etc. And since these indices are consistent with `channels.pkl`, it is **vital** that consistency is maintained.

Why? Because of this neat Python bug/feature.
```py
>>> df
   0  1
0  1  1
1  2  2
2  3  3
>>> df.drop(1)
   0  1
0  1  1
2  3  3
```

The indices stay. So, a reindexing is needed, which is what we do.

```py
if exists(ch.id, 'word/channels.pkl'):
  # channel exists
  a = pullout(ch.id, 'word/channels.pkl') # removing from list is straightforward
  b = pullout(message.guild.id, 'word/servers.pkl') # pullout returns index when successful
  
  f = open('word/letters.pkl', 'rb')
  s = pickle.load(f)
  f.close()
  s.pop(ch.id, None) # removal from dict is straightforward
  f = open('word/letters.pkl', 'wb')
  pickle.dump(s, f)
  f.close()
  # this codeblock removes the channel from letters.pkl
  
  f = open('word/channels.pkl', 'rb')
  x = pickle.load(f)
  x = len(x) # new length of channels after removal for reindexing
  f.close()
  
  renamedict = {} # will be used to reindex
  exit = 0
  while not(exit):
      i = 0
      while i < a[1]: # while I'm behind the removed channel, indices stay
          renamedict[i] = i
          i+=1
      while i<x:
          renamedict[i+1] = i # otherwise they get shifted back
          i+=1
      exit = 1
  
  df = pd.read_pickle('word/words.pkl')
  df = df.drop(a[1]) # remove row
  df = df.rename(index=renamedict) # reindex
  df.to_pickle('word/words.pkl') # repackage
  
  df = pd.read_pickle('word/lb.pkl') # do same for lb
  df = df.drop(a[1])
  df = df.rename(index=renamedict)
  df.to_pickle('word/lb.pkl')
  # removes channel from dataframes
  # re-indexes dataframes for consistency with channels.pkl
  
  await ch.send("Channel removed.")
```

#### Resetting a channel
This is perhaps the easiest job of all. So much so we just let a subroutine handle it

```py
async def resetchannel(cid):
    # reset word count of a channel
    # global word count of users remains unaffected

    s = cindex(cid) # grab index of the channel

    f = open('word/letters.pkl', 'rb')
    t = pickle.load(f)
    f.close()
    t[cid] = ['a', 1] # reset the last letter to a and last user to an id that allows anyone to play

    g = open('word/letters.pkl', 'wb')
    pickle.dump(t, g) # dump modified dict
    g.close()

    df = pd.read_pickle('word/words.pkl')
    for w in df.columns:
        df[w][s] = 0 # reset word counts
    df.to_pickle('word/words.pkl')

    df = pd.read_pickle('word/lb.pkl')
    for u in df.columns:
        df[u][s] = 0 # reset channel specific word count of user, not affecting global
    df.to_pickle('word/lb.pkl')
```

Pretty inefficient when you are active in multiple channels and inevitably have hundreds or even thousands of words. But criticisms and solutions are for a different doc.

Let's have another (super inefficient) implementation that demonstrates a little more about why these tables were designed the way they were.

#### Requesting Leaderboards

```py
if message.content == 'c!lb' or message.content == 'c!leaderboard' and exists(ch.id, 'word/channels.pkl'):
  df = pd.read_pickle('word/lb.pkl')
  lb = [[], []]
  rank = 0
  
  s = cindex(ch.id)
  
  for u in df.columns: # for user
      if df[u][s] != 0: # if he has played
          lb[0].append(u) # consider him
          lb[1].append(df[u][s]) # and his wordcount
  
  if len(lb[0]) == 0: await ch.send("**Send some messages first!**") # if no one has played, no issue
  else:
      w = sorted(lb[1])[::-1] # sort the active members (why God)
      u = lb[0] # this is some flagging
      if au not in u:
          await sendlb(lb, rank, message.guild.name, au, ch)
      else:
          rank = w.index(lb[1][lb[0].index(au)]) + 1 # there has to be a better way of doing this
          # whats happening here is I first look for the author in my 2d list
          # I then see how many words he has sent
          # and then I search for the index (first instance) of that count in the sorted lb
          # so this was my way of implementing dense ranking
          await sendlb(lb, rank, message.guild.name, au, ch) # this is a subroutine that nicely formats the leaderboard
```

So that concludes this, a small demonstration of design choices and why they were thought to be useful.
