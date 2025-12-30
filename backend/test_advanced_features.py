"""
测试高级数据库功能
包括：事务、触发器、视图、存储过程
"""
import requests
import json

BASE_URL = 'http://localhost:5001/api'

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_create_order_transaction():
    """测试订单创建（事务处理）"""
    print_section("1. 测试订单创建事务")
    
    # 获取第一个用户和第一个商品
    users = requests.get(f'{BASE_URL}/users').json()
    products = requests.get(f'{BASE_URL}/products').json()
    
    if len(users) < 2 or len(products) < 1:
        print("❌ 需要至少2个用户和1个商品")
        return
    
    buyer = users[0]
    product = products[0]
    
    print(f"买家: {buyer['username']} (余额: ¥{buyer['balance']})")
    print(f"商品: {product['title']} (价格: ¥{product['price']})")
    print(f"商品状态: {product['status']}")
    
    # 创建订单
    order_data = {
        'product_id': product['id'],
        'buyer_id': buyer['id']
    }
    
    response = requests.post(f'{BASE_URL}/orders', json=order_data)
    if response.status_code == 201:
        order = response.json()
        print(f"\n✅ 订单创建成功！")
        print(f"订单ID: {order['id']}")
        print(f"订单状态: {order['status']}")
        
        # 检查商品状态是否自动更新（触发器）
        updated_product = requests.get(f'{BASE_URL}/products/{product['id']}').json()
        print(f"\n🔄 触发器效果：")
        print(f"商品状态已自动更新: {product['status']} → {updated_product['status']}")
        
        return order['id']
    else:
        print(f"❌ 订单创建失败: {response.json()}")
        return None

def test_complete_order_transaction(order_id):
    """测试订单完成（事务处理：扣款+改状态）"""
    print_section("2. 测试订单完成事务（触发器自动扣款）")
    
    # 获取订单信息
    order = requests.get(f'{BASE_URL}/orders/{order_id}').json()
    buyer_id = order['buyer_id']
    seller_id = order['seller_id']
    amount = order['amount']
    
    # 获取交易前余额
    buyer_before = requests.get(f'{BASE_URL}/users/{buyer_id}').json()
    seller_before = requests.get(f'{BASE_URL}/users/{seller_id}').json()
    
    print(f"交易前余额:")
    print(f"  买家 {buyer_before['username']}: ¥{buyer_before['balance']}")
    print(f"  卖家 {seller_before['username']}: ¥{seller_before['balance']}")
    print(f"  交易金额: ¥{amount}")
    
    # 完成订单
    response = requests.put(f'{BASE_URL}/orders/{order_id}/complete')
    if response.status_code == 200:
        print(f"\n✅ 订单完成成功！")
        
        # 获取交易后余额
        buyer_after = requests.get(f'{BASE_URL}/users/{buyer_id}').json()
        seller_after = requests.get(f'{BASE_URL}/users/{seller_id}').json()
        
        print(f"\n🔄 触发器效果（自动扣款）:")
        print(f"  买家 {buyer_after['username']}: ¥{buyer_before['balance']} → ¥{buyer_after['balance']} (扣除 ¥{amount})")
        print(f"  卖家 {seller_after['username']}: ¥{seller_before['balance']} → ¥{seller_after['balance']} (增加 ¥{amount})")
        
        # 检查商品状态
        product = requests.get(f'{BASE_URL}/products/{order['product_id']}').json()
        print(f"  商品状态: {product['status']}")
    else:
        print(f"❌ 订单完成失败: {response.json()}")

def test_hot_products_view():
    """测试热门商品视图"""
    print_section("3. 测试热门商品视图")
    
    response = requests.get(f'{BASE_URL}/hot-products')
    if response.status_code == 200:
        products = response.json()
        print(f"✅ 热门商品（按留言数和浏览量排序）:")
        for i, p in enumerate(products, 1):
            print(f"  {i}. {p['title']} - 留言数: {p['message_count']}, 浏览: {p['views']}")
    else:
        print(f"❌ 获取失败")

def test_user_report_procedure():
    """测试用户月度报告存储过程"""
    print_section("4. 测试用户月度报告存储过程")
    
    users = requests.get(f'{BASE_URL}/users').json()
    
    for user in users[:3]:  # 测试前3个用户
        response = requests.get(f'{BASE_URL}/user-report/{user["id"]}')
        if response.status_code == 200:
            report = response.json()
            print(f"\n📊 {report['username']} 的月度报告:")
            print(f"  本月购买: {report['month_buy_count']} 笔, 金额: ¥{report['month_buy_amount']}")
            print(f"  本月出售: {report['month_sell_count']} 笔, 金额: ¥{report['month_sell_amount']}")
            print(f"  当前余额: ¥{report['current_balance']}")

def test_user_stats_view():
    """测试用户统计视图"""
    print_section("5. 测试用户统计视图")
    
    response = requests.get(f'{BASE_URL}/user-stats')
    if response.status_code == 200:
        stats = response.json()
        print(f"✅ 用户交易统计:")
        for s in stats[:5]:
            print(f"\n  {s['username']}:")
            print(f"    购买次数: {s['buy_count']}, 总支出: ¥{s['total_spent']}")
            print(f"    出售次数: {s['sell_count']}, 总收入: ¥{s['total_earned']}")
            print(f"    当前余额: ¥{s['balance']}")

def test_constraints():
    """测试数据库约束"""
    print_section("6. 测试数据库约束")
    
    # 测试价格约束（价格必须 > 0）
    print("测试1: 价格约束（price > 0）")
    invalid_product = {
        'title': '测试商品',
        'description': '测试',
        'price': -10,  # 无效价格
        'category': 'other',
        'seller_id': 1
    }
    response = requests.post(f'{BASE_URL}/products', json=invalid_product)
    if response.status_code != 201:
        print(f"  ✅ 约束生效: 拒绝了负价格商品")
    else:
        print(f"  ❌ 约束失效")
    
    # 测试余额不足
    print("\n测试2: 余额约束（购买时余额不足）")
    users = requests.get(f'{BASE_URL}/users').json()
    products = requests.get(f'{BASE_URL}/products').json()
    
    if users and products:
        # 找一个余额不足的场景（假设商品价格很高）
        expensive_product = {
            'title': '超贵商品',
            'description': '测试余额约束',
            'price': 99999,
            'category': 'other',
            'seller_id': users[0]['id']
        }
        p_response = requests.post(f'{BASE_URL}/products', json=expensive_product)
        if p_response.status_code == 201:
            product = p_response.json()
            order_data = {
                'product_id': product['id'],
                'buyer_id': users[1]['id']
            }
            o_response = requests.post(f'{BASE_URL}/orders', json=order_data)
            if o_response.status_code != 201:
                print(f"  ✅ 约束生效: {o_response.json()['error']}")

def main():
    print("\n" + "="*60)
    print("  🚀 校园二手交易平台 - 高级数据库功能测试")
    print("="*60)
    
    try:
        # 1. 测试订单创建事务
        order_id = test_create_order_transaction()
        
        # 2. 测试订单完成事务（触发器）
        if order_id:
            test_complete_order_transaction(order_id)
        
        # 3. 测试视图
        test_hot_products_view()
        
        # 4. 测试存储过程
        test_user_report_procedure()
        
        # 5. 测试用户统计视图
        test_user_stats_view()
        
        # 6. 测试约束
        test_constraints()
        
        print("\n" + "="*60)
        print("  ✅ 所有测试完成！")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")

if __name__ == '__main__':
    main()
