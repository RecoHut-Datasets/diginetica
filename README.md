# diginetica
Diginetica Dataset

### Storing and Reading compressed pickle files (to save space)
```python
import bz2
import pickle
import _pickle as cPickle

def save_pickle(data, title):
 with bz2.BZ2File(title + '.pbz2', 'w') as f: 
    cPickle.dump(data, f)

def load_pickle(path):
    data = bz2.BZ2File(path+'.pbz2', 'rb')
    data = cPickle.load(data)
    return data
```