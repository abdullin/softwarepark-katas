import sys
from collections import defaultdict
from datetime import datetime
import numpy as np    


HISTORY = defaultdict(list)  

# Let's parse and load the training data
with open("s02e03_train.csv") as f:
    lines = f.readlines()
    
    
    for line in lines[1:]:
        transport, time, a, b, speed = line.strip().split(",")
        speed = float(speed)
        # 1859-11-26 19:43:31
        time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
      
        HISTORY[(a,b)].append((time,speed))

# this is our map with computed data
MAP = {}

for (a,b), history in HISTORY.items():
    speeds = [x[1] for x in history]
    times = [x[0].time().hour for x in history]

    model = np.poly1d(np.polyfit(times, speeds, 3))

    MAP[(a,b)] = model


errors = 0
count = 0
with open("s02e03_test.csv") as f:
    lines = f.readlines()
    for line in lines[1:]:
        count +=1
        
        transport, time, a, b, observed = line.strip().split(",")
        observed = float(observed)
        # 1859-11-26 19:43:31
        time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    
        model = MAP[(a, b)]
        predicted = model(time.time().hour)
        
        
        errors += (predicted - observed) * (predicted - observed)
        
print(f"MSE is {errors/count}")


