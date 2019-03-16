import matplotlib
import matplotlib.pyplot as plt
import numpy as np

N = 6
x = np.linspace(0, 1, 10)
cmap = plt.cm.viridis
for i in range(1, N):
    plt.plot(x, i * x + i, color = cmap(i/N))
plt.legend(loc='best')
plt.show()
