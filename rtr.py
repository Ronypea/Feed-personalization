start = open ('queuemin.in')
result = open ('queuemin.out', 'a')
data = start.read().split('\n')
len = int(data[0])
queue = []
for i in range(len):
    if "+" in data[i+1]:
        queue.append(int(data[i+1][2:]))
    elif "-" in data[i+1]:
        queue.pop(0)
    else:
        result.write(str(min(queue)) + "\n")
start.close()
result.close()