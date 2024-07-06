### Conditionals on the game

After iterating through conditionals on a message being a command, and if the channel is currently active, the bot concludes that the users are trying to play the game, and so it enters the last group of conditionals.

The first conditional is 
```py
if isaword(word) and lastlettermatches(ch.id, word, au):
```
If the word is valid and `lastlettermatches` returns `True` (which happens iff last letter matches AND user doeesn't play twice), the bot checks if the word has been used before. If not, it calls the `updateuniquewordsdf` and `updatelbdf` subroutines, and updates the last letter (and user) for the channel, and finally reacts with a checkmark, indicating the word has been successfully registered.

If this conditional returns `False`, we immediately check whether the word is invalid.

If not, the bot has now finally recognised that either the user has played twice, or the first letter didn't match. Any of these can be checked with a simple lookup, and the bot sends the appropriate message back.

Condensing the snippet, we have this overall structure:

```py
if not(message.content.startswith("c!")) and exists(ch.id, 'word/channels.pkl') and len(message.content) != 0:
    # actual game codeblock
    word = message.content.lower()
    emoji = '\N{White Heavy Check Mark}'

    if isaword(word) and lastlettermatches(ch.id, word, au):
        # two rules followed, check for repetition

        if uniqueword(ch.id, word):
            # do updates
            await message.add_reaction(emoji)

        else:
            msg = await ch.send(mnt + " **the word " + word + " has already been used!**")

    elif not(isaword(word)):
        # not a word
        msg = await ch.send(mnt + " **" + word + " is not a word!**")

    else:
        # either user played twice
        # or first letter didn't match

        if userrule(ch.id, au):
            msg = await ch.send(mnt + " ** The first letter of your word should be " + lastletter(ch.id) + "!**")
        else:
            msg = await ch.send(mnt + " **It's not your turn!**")
```

In retrospect this can be simplified, but again, for a different day.
