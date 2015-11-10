
import os
import glob

newest = max(glob.iglob('data/history/history_AAPL*'), key=os.path.getctime)

print newest