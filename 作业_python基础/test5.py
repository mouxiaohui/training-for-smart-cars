import random

currency = 10
def generateRandomNum():
    return random.randint(0, 99)

while True:
    print("\n新一轮")
    num = generateRandomNum()

    while currency >= 2:
        print(f"你还拥有{currency}个币")
        guess = int(input("请输入你猜的数:"))
        currency -= 2

        if guess > num:
            print("猜大了")
        elif guess < num:
            print("猜小了")
        elif guess == num:
            currency += 10
            print("恭喜你猜对了!")
            break
        else:
            print("猜错了!")
    else:
        print("游戏币不足!")
        break
