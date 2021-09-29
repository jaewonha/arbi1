import pandas as pd
import numpy as np

ts1 = '2021/09/11'
arr1 = [ts1, 45173.68000000,46460.00000000,44742.06000000,46025.24000000]

ts2 = '2021/09/12'
arr2 = [ts2, 46025.23000000,46880.00000000,43370.00000000,44940.73000000]

df = pd.DataFrame([arr1, arr2], columns=['ts', 'o','h','l','c']).set_index('ts')
print(df)
