# last-letter-bot
Repo for the Last Letter Discord Bot - originally made to replace a similar bot in one server locally. The bot was hosted on Heroku while their free service was still available.

Critical files like `token.pkl` are not uploaded, and other dataframe files are not fully initialised as I don't currently intend to deploy the bot again. This repo is here for showcasing, archiving, and to note down possible improvements to the program (of which there's admittedly a lot), in case I want to pick it up again.

### Test Flight

In case someone wants to test run this, you should head over to [Discord Developers Portal](https://discord.com/developers/applications), add a new application and grab its token. Save this token in a `pickle` file name `token.pkl` in the same directory as `main.py`. Make sure the application is a bot user. Further, add the bot to a server (link available on the portal) and grab its user id. This can be done by mentioning the bot and copying the raw text. It has the format `<@ user id >` and save it in `id.pkl`.

Then, just run the file. The initial few code snippets should handle everything. The bot should appear online. You can use the command `c!add` to make a channel active and play the game there.
