

import numpy as np
import matplotlib.pyplot as plt
 
N = 5
 
boys = (0, 35, 30, 35, 27)
girls = (25, 32, 34, 20, 25)
ind = range(N)   
width = 0.35 
 
p1 = plt.bar(ind, boys, width)
p2 = plt.bar(ind, girls, width, bottom = boys)
 
plt.ylabel('Contribution')
plt.title('Contribution by the teams')
plt.xticks(ind, ('T1', 'T2', 'T3', 'T4', 'T5'))
plt.yticks(np.arange(0, 81, 10))
plt.legend((p1[0], p2[0]), ('boys', 'girls'))
 
plt.show()