"""
初始化测试数据脚本
运行此脚本可以快速生成测试用户和商品数据
"""
from models import SessionLocal, User, Product, ProductCategory, ProductStatus, Favorite, Review, Order, OrderStatus
from datetime import datetime, timedelta
import random

def clear_data():
    """清空所有数据"""
    db = SessionLocal()
    try:
        # 按照外键依赖顺序删除
        db.query(Review).delete()
        db.query(Favorite).delete()
        db.query(Order).delete()
        db.query(Product).delete()
        db.query(User).delete()
        db.commit()
        print("✅ 已清空所有数据")
    finally:
        db.close()

def create_users():
    """创建测试用户"""
    db = SessionLocal()
    try:
        users_data = [
            {
                'username': '张三',
                'email': 'zhangsan@campus.edu',
                'phone': '13800138001',
                'student_id': '2021001',
                'avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=zhangsan'
            },
            {
                'username': '李四',
                'email': 'lisi@campus.edu',
                'phone': '13800138002',
                'student_id': '2021002',
                'avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=lisi'
            },
            {
                'username': '王五',
                'email': 'wangwu@campus.edu',
                'phone': '13800138003',
                'student_id': '2021003',
                'avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=wangwu'
            },
            {
                'username': '赵六',
                'email': 'zhaoliu@campus.edu',
                'phone': '13800138004',
                'student_id': '2021004',
                'avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=zhaoliu'
            },
            {
                'username': '钱七',
                'email': 'qianqi@campus.edu',
                'phone': '13800138005',
                'student_id': '2021005',
                'avatar': 'https://api.dicebear.com/7.x/avataaars/svg?seed=qianqi'
            }
        ]
        
        user_ids = []
        for user_data in users_data:
            user = User(**user_data)
            user.set_password('test1234')  # 设置默认密码
            db.add(user)
            db.flush()  # 立即获取 ID
            user_ids.append(user.id)
        
        db.commit()
        print(f"✅ 已创建 {len(user_ids)} 个测试用户")
        return user_ids
    finally:
        db.close()

def create_products(user_ids):
    """创建测试商品"""
    db = SessionLocal()
    try:
        products_data = [
            # 教材书籍
            {
                'title': '高等数学教材（上下册）',
                'description': '同济大学第七版，9成新，无笔记无划线，适合大一新生使用',
                'price': 35.0,
                'original_price': 68.0,
                'category': ProductCategory.BOOKS,
                'image_url': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400',
                'location': '东区宿舍楼下'
            },
            {
                'title': '大学英语四级真题集',
                'description': '星火英语，包含近10年真题，附赠听力音频，几乎全新',
                'price': 20.0,
                'original_price': 45.0,
                'category': ProductCategory.BOOKS,
                'image_url': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?w=400',
                'location': '图书馆门口'
            },
            {
                'title': 'Python编程从入门到实践',
                'description': '第二版中文版，适合编程初学者，书籍保存完好',
                'price': 45.0,
                'original_price': 89.0,
                'category': ProductCategory.BOOKS,
                'image_url': 'https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400',
                'location': '西区教学楼'
            },
            
            # 电子产品
            {
                'title': 'iPad 2020款 128G',
                'description': '使用一年，成色良好，无磕碰，配原装充电器和保护壳',
                'price': 2200.0,
                'original_price': 3299.0,
                'category': ProductCategory.ELECTRONICS,
                'image_url': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400',
                'location': '南区宿舍'
            },
            {
                'title': '小米蓝牙耳机 Air 2 SE',
                'description': '全新未拆封，多买了一个，低价转让',
                'price': 80.0,
                'original_price': 149.0,
                'category': ProductCategory.ELECTRONICS,
                'image_url': 'https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=400',
                'location': '北区食堂'
            },
            {
                'title': '罗技无线鼠标 M185',
                'description': '使用半年，功能正常，适合办公学习',
                'price': 35.0,
                'original_price': 69.0,
                'category': ProductCategory.ELECTRONICS,
                'image_url': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400',
                'location': '东区宿舍'
            },
            {
                'title': '机械键盘 青轴',
                'description': '黑爵品牌，RGB背光，手感极佳，因换笔记本出售',
                'price': 150.0,
                'original_price': 299.0,
                'category': ProductCategory.ELECTRONICS,
                'image_url': 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=400',
                'location': '西区宿舍'
            },
            
            # 生活用品
            {
                'title': '宿舍小风扇',
                'description': 'USB充电款，静音设计，夏天必备神器',
                'price': 25.0,
                'original_price': 49.0,
                'category': ProductCategory.DAILY,
                'image_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400',
                'location': '东区宿舍'
            },
            {
                'title': '台灯护眼灯',
                'description': '三档调光，保护视力，适合晚上学习使用',
                'price': 40.0,
                'original_price': 89.0,
                'category': ProductCategory.DAILY,
                'image_url': 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400',
                'location': '南区宿舍'
            },
            {
                'title': '保温杯 500ml',
                'description': '膳魔师品牌，保温效果好，外观无损',
                'price': 60.0,
                'original_price': 129.0,
                'category': ProductCategory.DAILY,
                'image_url': 'https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400',
                'location': '北区食堂'
            },
            
            # 运动器材
            {
                'title': '瑜伽垫 加厚款',
                'description': '10mm厚度，防滑耐用，适合健身瑜伽使用',
                'price': 35.0,
                'original_price': 79.0,
                'category': ProductCategory.SPORTS,
                'image_url': 'https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=400',
                'location': '体育馆'
            },
            {
                'title': '羽毛球拍 双拍',
                'description': '李宁品牌，含3个羽毛球，适合初学者',
                'price': 80.0,
                'original_price': 159.0,
                'category': ProductCategory.SPORTS,
                'image_url': 'https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?w=400',
                'location': '体育馆'
            },
            {
                'title': '篮球 斯伯丁',
                'description': '7号标准球，室内外两用，9成新',
                'price': 60.0,
                'original_price': 129.0,
                'category': ProductCategory.SPORTS,
                'image_url': 'https://images.unsplash.com/photo-1546519638-68e109498ffc?w=400',
                'location': '篮球场'
            },
            
            # 服装配饰
            {
                'title': '双肩背包',
                'description': '大容量，适合装书本和电脑，几乎全新',
                'price': 45.0,
                'original_price': 99.0,
                'category': ProductCategory.CLOTHING,
                'image_url': 'https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400',
                'location': '东区宿舍'
            },
            {
                'title': '运动鞋 耐克',
                'description': '42码，穿过3次，几乎全新，因尺码不合转让',
                'price': 280.0,
                'original_price': 599.0,
                'category': ProductCategory.CLOTHING,
                'image_url': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400',
                'location': '南区宿舍'
            }
        ]
        
        product_ids = []
        for i, product_data in enumerate(products_data):
            # 随机分配卖家 ID
            seller_id = random.choice(user_ids)
            product_data['seller_id'] = seller_id
            
            # 随机设置浏览次数
            product_data['views'] = random.randint(10, 200)
            
            # 随机设置一些商品为已售出或已下单
            if i % 7 == 0:
                product_data['status'] = ProductStatus.SOLD
            elif i % 5 == 0:
                product_data['status'] = ProductStatus.ORDERED
            else:
                product_data['status'] = ProductStatus.AVAILABLE
            
            product = Product(**product_data)
            db.add(product)
            db.flush()
            product_ids.append({'id': product.id, 'seller_id': seller_id, 'status': product_data['status']})
        
        db.commit()
        print(f"✅ 已创建 {len(product_ids)} 个测试商品")
        return product_ids
    finally:
        db.close()

def create_favorites(user_ids, product_ids):
    """创建测试收藏数据"""
    db = SessionLocal()
    try:
        favorites_count = 0
        
        # 为每个用户创建一些收藏
        for user_id in user_ids:
            # 随机选择3-5个商品收藏（不包括自己的商品）
            available_products = [p for p in product_ids if p['seller_id'] != user_id]
            num_favorites = random.randint(3, min(5, len(available_products)))
            selected_products = random.sample(available_products, num_favorites)
            
            for product in selected_products:
                favorite = Favorite(
                    user_id=user_id,
                    product_id=product['id']
                )
                db.add(favorite)
                favorites_count += 1
        
        db.commit()
        print(f"✅ 已创建 {favorites_count} 条收藏记录")
        return favorites_count
    finally:
        db.close()

def create_orders_and_reviews(user_ids, product_ids):
    """创建测试订单和评价数据"""
    db = SessionLocal()
    try:
        orders_count = 0
        reviews_count = 0
        
        # 创建一些已完成的订单
        available_for_order = [p for p in product_ids if p['status'] == ProductStatus.AVAILABLE]
        
        for i in range(min(5, len(available_for_order))):
            # 随机选择买家和商品
            buyer_id = random.choice(user_ids)
            available_products = [p for p in available_for_order if p['seller_id'] != buyer_id]
            
            if not available_products:
                continue
                
            product_info = random.choice(available_products)
            available_for_order.remove(product_info)  # 避免重复使用
            
            # 获取商品对象
            product = db.query(Product).filter(Product.id == product_info['id']).first()
            if not product:
                continue
            
            # 创建订单
            order = Order(
                product_id=product.id,
                buyer_id=buyer_id,
                seller_id=product.seller_id,
                amount=product.price,
                status=OrderStatus.COMPLETED,
                completed_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            db.add(order)
            db.flush()
            orders_count += 1
            
            # 更新商品状态
            product.status = ProductStatus.SOLD
            
            # 为部分订单创建评价
            if random.random() > 0.3:  # 70%的订单有评价
                review = Review(
                    product_id=product.id,
                    order_id=order.id,
                    reviewer_id=buyer_id,
                    rating=random.randint(4, 5),  # 4-5星好评
                    comment=random.choice([
                        '商品质量很好，卖家人也很nice！',
                        '物美价廉，非常满意！',
                        '和描述一致，推荐购买！',
                        '交易顺利，下次还会光顾！',
                        '性价比很高，值得购买！'
                    ])
                )
                db.add(review)
                reviews_count += 1
        
        db.commit()
        print(f"✅ 已创建 {orders_count} 个订单")
        print(f"✅ 已创建 {reviews_count} 条评价")
        return orders_count, reviews_count
    finally:
        db.close()

def main():
    """主函数"""
    print("🚀 开始初始化测试数据...")
    print()
    
    # 清空现有数据
    clear_data()
    print()
    
    # 创建用户
    user_ids = create_users()
    print()
    
    # 创建商品
    product_ids = create_products(user_ids)
    print()
    
    # 创建收藏
    favorites_count = create_favorites(user_ids, product_ids)
    print()
    
    # 创建订单和评价
    orders_count, reviews_count = create_orders_and_reviews(user_ids, product_ids)
    print()
    
    print("🎉 测试数据初始化完成！")
    print(f"   - 用户数: {len(user_ids)}")
    print(f"   - 商品数: {len(product_ids)}")
    print(f"   - 收藏数: {favorites_count}")
    print(f"   - 订单数: {orders_count}")
    print(f"   - 评价数: {reviews_count}")
    print()
    print("💡 提示:")
    print("   - 测试账号: zhangsan@campus.edu")
    print("   - 测试密码: test1234")
    print("   - 现在可以启动应用查看效果了")

if __name__ == '__main__':
    main()
