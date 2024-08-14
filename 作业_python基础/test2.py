name = "牟唤增"
age = 23
height = 1.74
school = "宁波大学科学技术学院"
boys = 30
girls = 10

my_info = f"我叫{name}，我的年龄是{age}岁 身高{height}。我就读于{school}。"
info = my_info + "我们班男同学有%d人，女同学有%d人。共计%d人。" % (boys, girls, boys + girls)

print(info)