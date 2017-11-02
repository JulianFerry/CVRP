import random
import numpy as np

data_list = [0,1,2,3,4,5]

random.shuffle(data_list)

new_list=[]
for i in range(0, 6, 3):
    new_list.append(data_list[i:i+3])



print(new_list)