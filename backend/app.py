from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from models import init_db, SessionLocal, User, Product, Message, Order, ProductStatus, ProductCategory, OrderStatus, Review, Favorite
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_, text
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# 初始化数据库
try:
    init_db()
    print("✅ 数据库连接成功！")
except Exception as e:
    print(f"❌ 数据库连接失败: {e}")

# ==================== 用户相关 API ====================

@app.route('/api/users', methods=['GET'])
def get_users():
    """获取所有用户"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        return jsonify([user.to_dict() for user in users])
    finally:
        db.close()

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户信息"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        return jsonify(user.to_dict())
    finally:
        db.close()

@app.route('/api/users', methods=['POST'])
def create_user():
    """创建新用户（注册）"""
    db = SessionLocal()
    try:
        data = request.json
        
        # 验证密码
        password = data.get('password')
        if not password:
            return jsonify({'error': '密码不能为空'}), 400
        
        # 密码验证：8位，必须包含数字和字母
        if len(password) != 8:
            return jsonify({'error': '密码必须是8位'}), 400
        
        has_digit = any(c.isdigit() for c in password)
        has_alpha = any(c.isalpha() for c in password)
        
        if not (has_digit and has_alpha):
            return jsonify({'error': '密码必须包含数字和字母'}), 400
        
        user = User(
            username=data['username'],
            email=data['email'],
            phone=data.get('phone'),
            student_id=data.get('student_id'),
            avatar=data.get('avatar', f'https://api.dicebear.com/7.x/avataaars/svg?seed={data["username"]}')
        )
        user.set_password(password)
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return jsonify(user.to_dict()), 201
    except IntegrityError:
        db.rollback()
        return jsonify({'error': '用户名或邮箱已存在'}), 400
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.json
        user.phone = data.get('phone', user.phone)
        user.student_id = data.get('student_id', user.student_id)
        user.avatar = data.get('avatar', user.avatar)
        
        db.commit()
        db.refresh(user)
        return jsonify(user.to_dict())
    finally:
        db.close()

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        db.delete(user)
        db.commit()
        return jsonify({'message': '删除成功'}), 200
    finally:
        db.close()

@app.route('/api/login', methods=['POST'])
def login():
    """用户登录"""
    db = SessionLocal()
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': '邮箱和密码不能为空'}), 400
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            return jsonify({'error': '邮箱不存在'}), 404
        
        if not user.check_password(password):
            return jsonify({'error': '密码错误'}), 401
        
        return jsonify(user.to_dict()), 200
    finally:
        db.close()

@app.route('/api/users/<int:user_id>/change-password', methods=['PUT'])
def change_password(user_id):
    """修改密码"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        data = request.json
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({'error': '旧密码和新密码不能为空'}), 400
        
        # 验证旧密码
        if not user.check_password(old_password):
            return jsonify({'error': '旧密码错误'}), 401
        
        # 检查是否可以修改密码
        if not user.can_change_password():
            days_since_change = (datetime.utcnow() - user.last_password_change).days
            days_remaining = 30 - days_since_change
            return jsonify({
                'error': f'每月只能修改一次密码，还需等待{days_remaining}天'
            }), 403
        
        # 验证新密码
        if len(new_password) != 8:
            return jsonify({'error': '密码必须是8位'}), 400
        
        has_digit = any(c.isdigit() for c in new_password)
        has_alpha = any(c.isalpha() for c in new_password)
        
        if not (has_digit and has_alpha):
            return jsonify({'error': '密码必须包含数字和字母'}), 400
        
        # 设置新密码
        user.set_password(new_password)
        db.commit()
        db.refresh(user)
        
        return jsonify({
            'message': '密码修改成功',
            'user': user.to_dict()
        }), 200
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# ==================== 商品相关 API ====================

@app.route('/api/products', methods=['GET'])
def get_products():
    """获取商品列表（支持筛选和搜索）"""
    db = SessionLocal()
    try:
        query = db.query(Product)
        
        # 分类筛选
        category = request.args.get('category')
        if category:
            query = query.filter(Product.category == ProductCategory(category))
        
        # 状态筛选（只有明确指定时才过滤）
        status = request.args.get('status')
        if status:
            query = query.filter(Product.status == ProductStatus(status.upper()))
        # 不再默认只显示 AVAILABLE 状态
        
        # 搜索
        search = request.args.get('search')
        if search:
            query = query.filter(or_(
                Product.title.ilike(f'%{search}%'),
                Product.description.ilike(f'%{search}%')
            ))
        
        # 卖家筛选
        seller_id = request.args.get('seller_id')
        if seller_id:
            query = query.filter(Product.seller_id == int(seller_id))
        
        # 排序
        sort = request.args.get('sort', 'newest')
        if sort == 'price_asc':
            query = query.order_by(Product.price.asc())
        elif sort == 'price_desc':
            query = query.order_by(Product.price.desc())
        elif sort == 'views':
            query = query.order_by(Product.views.desc())
        else:  # newest
            query = query.order_by(Product.created_at.desc())
        
        products = query.all()
        return jsonify([product.to_dict() for product in products])
    finally:
        db.close()

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """获取单个商品详情"""
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({'error': '商品不存在'}), 404
        
        # 增加浏览次数
        product.views += 1
        db.commit()
        
        return jsonify(product.to_dict())
    finally:
        db.close()

@app.route('/api/products', methods=['POST'])
def create_product():
    """发布新商品"""
    db = SessionLocal()
    try:
        data = request.json
        product = Product(
            title=data['title'],
            description=data['description'],
            price=float(data['price']),
            original_price=float(data.get('original_price', 0)) if data.get('original_price') else None,
            category=ProductCategory(data['category']),
            image_url=data.get('image_url'),
            location=data.get('location'),
            seller_id=data['seller_id']
        )
        db.add(product)
        db.commit()
        db.refresh(product)
        return jsonify(product.to_dict()), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """更新商品信息"""
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({'error': '商品不存在'}), 404
        
        data = request.json
        product.title = data.get('title', product.title)
        product.description = data.get('description', product.description)
        product.price = float(data.get('price', product.price))
        if 'original_price' in data:
            product.original_price = float(data['original_price']) if data['original_price'] else None
        if 'category' in data:
            product.category = ProductCategory(data['category'])
        if 'status' in data:
            product.status = ProductStatus(data['status'])
        product.image_url = data.get('image_url', product.image_url)
        product.location = data.get('location', product.location)
        
        db.commit()
        db.refresh(product)
        return jsonify(product.to_dict())
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """删除商品"""
    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({'error': '商品不存在'}), 404
        db.delete(product)
        db.commit()
        return jsonify({'message': '删除成功'}), 200
    finally:
        db.close()

# ==================== 消息相关 API ====================

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """获取消息列表"""
    db = SessionLocal()
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'error': '缺少用户ID'}), 400
        
        messages = db.query(Message).filter(
            or_(Message.sender_id == user_id, Message.receiver_id == user_id)
        ).order_by(Message.created_at.desc()).all()
        
        return jsonify([msg.to_dict() for msg in messages])
    finally:
        db.close()

@app.route('/api/messages', methods=['POST'])
def send_message():
    """发送消息"""
    db = SessionLocal()
    try:
        data = request.json
        message = Message(
            content=data['content'],
            sender_id=data['sender_id'],
            receiver_id=data['receiver_id'],
            product_id=data.get('product_id')
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return jsonify(message.to_dict()), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/messages/<int:message_id>/read', methods=['PUT'])
def mark_message_read(message_id):
    """标记消息为已读"""
    db = SessionLocal()
    try:
        message = db.query(Message).filter(Message.id == message_id).first()
        if not message:
            return jsonify({'error': '消息不存在'}), 404
        message.is_read = 1
        db.commit()
        return jsonify({'message': '已标记为已读'})
    finally:
        db.close()

# ==================== 统计相关 API ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取平台统计数据"""
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        total_products = db.query(Product).count()
        available_products = db.query(Product).filter(Product.status == ProductStatus.AVAILABLE).count()
        sold_products = db.query(Product).filter(Product.status == ProductStatus.SOLD).count()
        total_orders = db.query(Order).count()
        completed_orders = db.query(Order).filter(Order.status == OrderStatus.COMPLETED).count()
        
        return jsonify({
            'total_users': total_users,
            'total_products': total_products,
            'available_products': available_products,
            'sold_products': sold_products,
            'total_orders': total_orders,
            'completed_orders': completed_orders
        })
    finally:
        db.close()

# ==================== 订单相关 API ====================

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """获取订单列表"""
    db = SessionLocal()
    try:
        user_id = request.args.get('user_id', type=int)
        role = request.args.get('role')  # 'buyer' or 'seller'
        
        query = db.query(Order)
        
        if user_id and role == 'buyer':
            query = query.filter(Order.buyer_id == user_id)
        elif user_id and role == 'seller':
            query = query.filter(Order.seller_id == user_id)
        elif user_id:
            query = query.filter(or_(Order.buyer_id == user_id, Order.seller_id == user_id))
        
        orders = query.order_by(Order.created_at.desc()).all()
        return jsonify([order.to_dict() for order in orders])
    finally:
        db.close()

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """获取单个订单详情"""
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({'error': '订单不存在'}), 404
        return jsonify(order.to_dict())
    finally:
        db.close()

@app.route('/api/orders', methods=['POST'])
def create_order():
    """创建订单（事务处理）"""
    db = SessionLocal()
    try:
        data = request.json
        product_id = data['product_id']
        buyer_id = data['buyer_id']
        
        # 开始事务
        db.begin_nested()
        
        # 1. 使用 FOR UPDATE 锁定商品行，防止并发问题
        product = db.query(Product).filter(Product.id == product_id).with_for_update().first()
        if not product:
            db.rollback()
            return jsonify({'error': '商品不存在'}), 404
        
        # 2. 检查商品状态（必须是 AVAILABLE）
        if product.status != ProductStatus.AVAILABLE:
            db.rollback()
            status_text = {
                ProductStatus.ORDERED: '该商品已被预订',
                ProductStatus.SOLD: '该商品已售出'
            }.get(product.status, '商品不可购买')
            return jsonify({'error': status_text}), 400
        
        # 3. 检查买家余额
        buyer = db.query(User).filter(User.id == buyer_id).first()
        if not buyer:
            db.rollback()
            return jsonify({'error': '买家不存在'}), 404
        if buyer.balance < product.price:
            db.rollback()
            return jsonify({'error': '余额不足'}), 400
        
        # 4. 不能购买自己的商品
        if product.seller_id == buyer_id:
            db.rollback()
            return jsonify({'error': '不能购买自己的商品'}), 400
        
        # 5. 立即更新商品状态为 ORDERED（不等触发器）
        product.status = ProductStatus.ORDERED
        
        # 6. 创建订单
        order = Order(
            product_id=product_id,
            buyer_id=buyer_id,
            seller_id=product.seller_id,
            amount=product.price,
            status=OrderStatus.PENDING
        )
        db.add(order)
        
        # 提交事务
        db.commit()
        db.refresh(order)
        return jsonify(order.to_dict()), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/orders/<int:order_id>/complete', methods=['PUT'])
def complete_order(order_id):
    """完成订单（事务处理：扣款+改状态）"""
    db = SessionLocal()
    try:
        # 开始事务
        db.begin_nested()
        
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({'error': '订单不存在'}), 404
        
        if order.status == OrderStatus.COMPLETED:
            return jsonify({'error': '订单已完成'}), 400
        
        # 更新订单状态为已完成
        # 触发器会自动：
        # 1. 更新商品状态为 SOLD
        # 2. 扣除买家余额
        # 3. 增加卖家余额
        order.status = OrderStatus.COMPLETED
        
        db.commit()
        db.refresh(order)
        return jsonify(order.to_dict())
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/orders/<int:order_id>/cancel', methods=['PUT'])
def cancel_order(order_id):
    """取消订单"""
    db = SessionLocal()
    try:
        db.begin_nested()
        
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return jsonify({'error': '订单不存在'}), 404
        
        if order.status == OrderStatus.COMPLETED:
            return jsonify({'error': '已完成的订单不能取消'}), 400
        
        # 更新订单状态
        order.status = OrderStatus.CANCELLED
        
        # 恢复商品状态为可售
        product = db.query(Product).filter(Product.id == order.product_id).first()
        if product:
            product.status = ProductStatus.AVAILABLE
        
        db.commit()
        return jsonify(order.to_dict())
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

# ==================== 高级查询 API ====================

@app.route('/api/hot-products', methods=['GET'])
def get_hot_products():
    """获取热门商品（使用视图）"""
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT * FROM v_hot_products"))
        products = []
        for row in result:
            products.append({
                'id': row[0],
                'title': row[1],
                'price': float(row[2]),
                'category': row[3],
                'status': row[4],
                'seller_id': row[5],
                'views': row[6],
                'message_count': row[7]
            })
        return jsonify(products)
    finally:
        db.close()

@app.route('/api/user-report/<int:user_id>', methods=['GET'])
def get_user_report(user_id):
    """获取用户月度报告（使用存储过程）"""
    db = SessionLocal()
    try:
        result = db.execute(
            text("SELECT * FROM sp_user_report(:user_id)"),
            {'user_id': user_id}
        )
        row = result.fetchone()
        if not row:
            return jsonify({'error': '用户不存在'}), 404
        
        return jsonify({
            'user_id': row[0],
            'username': row[1],
            'month_buy_count': row[2],
            'month_sell_count': row[3],
            'month_buy_amount': float(row[4]),
            'month_sell_amount': float(row[5]),
            'current_balance': float(row[6])
        })
    finally:
        db.close()

@app.route('/api/user-stats', methods=['GET'])
def get_user_stats():
    """获取用户统计（使用视图）"""
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT * FROM v_user_stats"))
        stats = []
        for row in result:
            stats.append({
                'id': row[0],
                'username': row[1],
                'balance': float(row[2]),
                'buy_count': row[3],
                'sell_count': row[4],
                'total_spent': float(row[5]),
                'total_earned': float(row[6])
            })
        return jsonify(stats)
    finally:
        db.close()

# ==================== 健康检查 ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'status': 'healthy',
        'database': 'openGauss',
        'backend': 'Flask',
        'platform': '校园二手交易平台'
    })

# ==================== 评价相关 API ====================

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """获取评价列表"""
    db = SessionLocal()
    try:
        product_id = request.args.get('product_id', type=int)
        
        query = db.query(Review)
        if product_id:
            query = query.filter(Review.product_id == product_id)
        
        reviews = query.order_by(Review.created_at.desc()).all()
        return jsonify([review.to_dict() for review in reviews])
    finally:
        db.close()

@app.route('/api/reviews', methods=['POST'])
def create_review():
    """创建评价"""
    db = SessionLocal()
    try:
        data = request.json
        
        # 检查订单是否存在且已完成
        order = db.query(Order).filter(Order.id == data['order_id']).first()
        if not order:
            return jsonify({'error': '订单不存在'}), 404
        if order.status != OrderStatus.COMPLETED:
            return jsonify({'error': '只能评价已完成的订单'}), 400
        
        # 检查是否已经评价过
        existing_review = db.query(Review).filter(Review.order_id == data['order_id']).first()
        if existing_review:
            return jsonify({'error': '该订单已评价'}), 400
        
        review = Review(
            product_id=data['product_id'],
            order_id=data['order_id'],
            reviewer_id=data['reviewer_id'],
            rating=data['rating'],
            comment=data.get('comment', '')
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        return jsonify(review.to_dict()), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/products/<int:product_id>/reviews', methods=['GET'])
def get_product_reviews(product_id):
    """获取商品的所有评价"""
    db = SessionLocal()
    try:
        reviews = db.query(Review).filter(Review.product_id == product_id).order_by(Review.created_at.desc()).all()
        return jsonify([review.to_dict() for review in reviews])
    finally:
        db.close()

@app.route('/api/products/<int:product_id>/rating', methods=['GET'])
def get_product_rating(product_id):
    """获取商品平均评分"""
    db = SessionLocal()
    try:
        from sqlalchemy import func
        result = db.query(
            func.avg(Review.rating).label('avg_rating'),
            func.count(Review.id).label('review_count')
        ).filter(Review.product_id == product_id).first()
        
        return jsonify({
            'product_id': product_id,
            'avg_rating': float(result.avg_rating) if result.avg_rating else 0,
            'review_count': result.review_count
        })
    finally:
        db.close()

# ==================== 收藏相关 API ====================

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    """获取用户收藏列表"""
    db = SessionLocal()
    try:
        user_id = request.args.get('user_id', type=int)
        if not user_id:
            return jsonify({'error': '缺少用户ID'}), 400
        
        favorites = db.query(Favorite).filter(Favorite.user_id == user_id).order_by(Favorite.created_at.desc()).all()
        return jsonify([fav.to_dict() for fav in favorites])
    finally:
        db.close()

@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    """添加收藏"""
    db = SessionLocal()
    try:
        data = request.json
        user_id = data.get('user_id')
        product_id = data.get('product_id')
        
        if not user_id or not product_id:
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 检查商品是否存在
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return jsonify({'error': '商品不存在'}), 404
        
        # 不能收藏自己的商品
        if product.seller_id == user_id:
            return jsonify({'error': '不能收藏自己的商品'}), 400
        
        # 检查是否已收藏
        existing = db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.product_id == product_id
        ).first()
        
        if existing:
            return jsonify({'error': '已经收藏过该商品'}), 400
        
        favorite = Favorite(
            user_id=user_id,
            product_id=product_id
        )
        db.add(favorite)
        db.commit()
        db.refresh(favorite)
        return jsonify(favorite.to_dict()), 201
    except Exception as e:
        db.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.close()

@app.route('/api/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    """取消收藏"""
    db = SessionLocal()
    try:
        favorite = db.query(Favorite).filter(Favorite.id == favorite_id).first()
        if not favorite:
            return jsonify({'error': '收藏不存在'}), 404
        
        db.delete(favorite)
        db.commit()
        return jsonify({'message': '取消收藏成功'}), 200
    finally:
        db.close()

@app.route('/api/favorites/check', methods=['GET'])
def check_favorite():
    """检查是否已收藏"""
    db = SessionLocal()
    try:
        user_id = request.args.get('user_id', type=int)
        product_id = request.args.get('product_id', type=int)
        
        if not user_id or not product_id:
            return jsonify({'error': '缺少必要参数'}), 400
        
        favorite = db.query(Favorite).filter(
            Favorite.user_id == user_id,
            Favorite.product_id == product_id
        ).first()
        
        return jsonify({
            'is_favorited': favorite is not None,
            'favorite_id': favorite.id if favorite else None
        })
    finally:
        db.close()

@app.route('/api/products/<int:product_id>/favorite-count', methods=['GET'])
def get_favorite_count(product_id):
    """获取商品收藏数"""
    db = SessionLocal()
    try:
        count = db.query(Favorite).filter(Favorite.product_id == product_id).count()
        return jsonify({
            'product_id': product_id,
            'favorite_count': count
        })
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
