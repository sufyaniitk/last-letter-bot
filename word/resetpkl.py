# Originally for testing purposes
# resets pickle files to original, desired state
# pickle's "bug not feature" of not pushing empty objects
# is then utilised to store global stats


import pickle
import pandas as pd

df = pd.DataFrame({"1": ["b"]})
df.to_pickle('words.pkl')

df = pd.DataFrame({"1": ["seven"]})
df.to_pickle('lb.pkl')

f = open('letters.pkl', 'wb')
a = {"a": ["1", "2"]}
pickle.dump(a, f)
f.close()

g = open('channels.pkl', 'wb')
b = ["b"]
pickle.dump(b, g)
g.close()

h = open('servers.pkl', 'wb')
c = ['c']
pickle.dump(c, h)
h.close()
