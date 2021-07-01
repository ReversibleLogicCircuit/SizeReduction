import random

def rand_sbox(n):
    nLen = 1 << n
    nList = list(range(nLen))
    result = []
    
    for num in range(nLen, 0, -1):
        ranVal = random.randint(0,nLen)
        pos = ranVal % num
        
        result.append(nList[pos])
        nList.pop(pos)
    
    return result