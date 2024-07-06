The few I noticed in conditionals and storage etc I've pointed out in the respective documents. This is more directed toward "how I would completely restructure the storage knowing what I know now"

Now admittedly I do not know much about permanent storage in C++ as Python provides with `pickle`. Although if there were, this storage can be made compact, and faster. I am aware that there are frameworks that allow Python bindings to C++ but do not have experience working with them. So yeah, this is all assuming that the implementation details are trivial, which they're probably not.

To store active channels, one could use a lookup table implemented via folders. Have 100-1000 folders depending on the first few digits of the channelid, and in each of these folders, one can put in permanent storage file (PSF) for each active channel object with matching prefix. 

Now, C++ can do this lookup much, much faster than Python. In case of an even larger number of guilds (unlikely) one can include a PSF os a `std::set` storing `long long` channel IDs with matching prefix and do a lookup there, or increase the number of folders, or both.

With first `n` digits being prefix folders (assuming each id is a fixed `m` digits with `m > n`) the lookup is simplified to $\lg(10^{m - n}) \sim \lg (m - n)$ time complexity, as opposed to $\mathcal O (\text{num(channels)})$ 

Leaderboard statistics can be stored with `std::priority_queue`s, which takes $\lg (\text{num(users)})$ memory for both global and local leaderboards. This is faster than counting from a 2d `std::vector` and sorting it and reaccessing elements for dense ranking, especially as a given user will only be active in a few channels, making our 2d array ineffective since it is actually a sparse table.

The PSF of a given channel can store a `game_channel` object which stores a `std::set` of used words, the id of the user who last played and a `char` storing the last letter used. In the global statistics folder, we can have a dedicated PSF for another `std::priority_queue` of words used globally. The priority queue can be implemented via a max heap sorted by frequency. This heap and the set object in the PSF will *almost eliminate* the need to look up words, since the set and priority queue will provide fast lookups for words that have been seen globally with more frequency.

Overall, these data structures can be used to better implement the bot than just simple indexing consistency. All I need to learn is wrapping and permanent storae and how to get my bot famous enough that may sample is large enough for these solutions to actually be more feasible than their current implementation.
