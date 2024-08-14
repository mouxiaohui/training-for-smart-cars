name = "丁真珍珠"
age = 23
sex = "男"
birthplace = "四川"
hobby = "骑马、唱歌、锅庄舞"

chances = 3

info = f'''
=================猜明星游戏=================
年龄: {age}
性别: {sex}
出生地: {birthplace}
爱好: {hobby}
'''

print(info)

while chances > 0:
    print("\n你有", chances, "次机会\n")

    guess_name = input("请输入你猜的明星:")
    if guess_name == name:
        print("猜对了!")
        break
    else:
        print("猜错了!")
        chances -= 1
    
    if chances == 0:
        print("你没有机会了")
