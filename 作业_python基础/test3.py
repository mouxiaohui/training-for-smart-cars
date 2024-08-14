brand1 = {
    'name': 'BrandA',
    'price': 2000,
    'reputation': 4,
    'sales': 10900
}

brand2 = {
    'name': 'BrandB',
    'price': 1500,
    'reputation': 3.5,
    'sales': 20100
}


def compareBrands(brand1, brand2):
    brand1_cb = 0
    brand2_cb = 0

    print("先比较两者价格")
    if brand1['price'] < brand2['price']:
        print(f"{brand1['name']}价格更低")
        brand1_cb += 1
    elif brand1['price'] > brand2['price']:
        print(f"{brand2['name']}价格更低")
        brand2_cb += 1
    else:
        print("两者价格一样")

    print("\n比较两者销量")   
    if brand1['sales'] < brand2['sales']:
        print(f"{brand2['name']}销量更高")
        brand2_cb += 1
    elif brand1['sales'] > brand2['sales']:
        print(f"{brand1['name']}销量更高")
        brand1_cb += 1
    else:
        print("两者销量一样")
    
    print("\n比较两者口碑")
    if brand1['reputation'] < brand2['reputation']:
        print(f"{brand2['name']}口碑更高")
        brand2_cb += 1
    elif brand1['reputation'] > brand2['reputation']:
        print(f"{brand1['name']}口碑更高")
        brand1_cb += 1
    else:
        print("两者口碑一样")
    
    if brand1_cb > brand2_cb:
        print("\n综合比较来说更推荐购买{}".format(brand1["name"]))
    else:
        print("\n综合比较来说更推荐购买{}".format(brand2["name"]))


compareBrands(brand1, brand2)
