import time
t = time.time()
print(t)
timeArray = time.localtime(t)
print(timeArray)
TimeFormat = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
print(TimeFormat)