import sys
from collections import defaultdict
from datetime import datetime
import numpy as np    


HISTORY = defaultdict(list)  # port to roads

# Let's parse and load the map
# but that wouldn't be much fun
with open("s02e03_train.csv") as f:
    lines = f.readlines()
    
    
    for line in lines[1:]:
        transport, time, a, b, speed = line.strip().split(",")
        speed = float(speed)
        # 1859-11-26 19:43:31
        time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
      
        HISTORY[(a,b)].append((time,speed))
        
#HISTORY 


# this is our map
# key is the current location
# value is a list of (location, Time-to-travel)
MAP = {}  # port to roads



for (a,b), history in HISTORY.items():
    
   
    speeds = [x[1] for x in history]
    times = [x[0].time().hour for x in history]


    average_speed = sum(speeds)/len(history)
    
    coefs = np.poly1d(np.polyfit(times, speeds, 3))

    MAP[(a,b)] = (average_speed, coefs)
    
    






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
    
        
        predicted, coef = MAP[(a, b)]
        predicted = coef(time.time().hour)
        
        
        errors += (predicted - observed) * (predicted - observed)
        
print(f"MSE is {errors/count}")


