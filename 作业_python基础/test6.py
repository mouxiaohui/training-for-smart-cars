total_amount = float(input("请输入购物总金额: "))
is_follow_store = False
if int(input("请输入是否关注店铺(1:关注，0:不关注):")) == 1:
    is_follow_store = True

free_shipping = False

if total_amount >= 500:
    discount = 100
    free_shipping = True
elif total_amount >= 300:
    discount = 50
    free_shipping = True
elif total_amount >= 100:
    discount = 20
    free_shipping = True
else:
    discount = 0

if is_follow_store: discount += 10

print(f"您的折扣为:{discount}")

if free_shipping:
    print("包邮")
else:
    print("邮费增加10元")
