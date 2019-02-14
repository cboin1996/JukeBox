import random
list = [7,4,6,5,1]



while len(list) - 1 >= 0:
    int = random.randint(0, len(list)-1)
    print(list)
    print(list[int])
    list.remove(list[int])
    input()
