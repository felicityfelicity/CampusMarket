from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Enum, ForeignKey, CheckConstraint, Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from config import Config
import enum

# 导入 openGauss 兼容性补丁
import opengauss_patch

Base = declarative_base()

# 创建数据库引擎
engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)
SessionLocal = sessionmaker(bind=engine)

class ProductStatus(enum.Enum):
    """商品状态枚举"""
    AVAILABLE = "available"  # 在售
    ORDERED = "ordered"      # 已下单
    SOLD = "sold"           # 已完成

class ProductCategory(enum.Enum):
    """商品分类枚举"""
    BOOKS = "books"              # 教材书籍
    ELECTRONICS = "electronics"  # 电子产品
    DAILY = "daily"             # 生活用品
    SPORTS = "sports"           # 运动器材
    CLOTHING = "clothing"       # 服装配饰
    OTHER = "other"             # 其他

class OrderStatus(enum.Enum):
    """订单状态枚举"""
    PENDING = "pending"      # 待支付
    PAID = "paid"           # 已支付
    COMPLETED = "completed" # 已完成
    CANCELLED = "cancelled" # 已取消
class User(Base):
    """用户模型"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20))
    student_id = Column(String(20), unique=True)
    avatar = Column(String(200), default='https://api.dicebear.com/7.x/avataaars/svg?seed=default')
    balance = Column(Numeric(10, 2), default=1000.00, nullable=False)
    last_password_change = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 约束：余额必须 >= 0
    __table_args__ = (
        CheckConstraint('balance >= 0', name='check_balance_positive'),
    )
    
    # 关联关系
    products = relationship("Product", back_populates="seller", cascade="all, delete-orphan", foreign_keys="Product.seller_id")
    messages_sent = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    messages_received = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")
    orders_as_buyer = relationship("Order", foreign_keys="Order.buyer_id", back_populates="buyer")
    orders_as_seller = relationship("Order", foreign_keys="Order.seller_id", back_populates="seller")
    reviews = relationship("Review", back_populates="reviewer")
    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password):
        """设置密码（使用简单的哈希）"""
        import hashlib
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.last_password_change = datetime.utcnow()
    
    def check_password(self, password):
        """验证密码"""
        import hashlib
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    def can_change_password(self):
        """检查是否可以修改密码（每月一次）"""
        from datetime import timedelta
        if not self.last_password_change:
            return True
        time_since_last_change = datetime.utcnow() - self.last_password_change
        return time_since_last_change.days >= 30
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'phone': self.phone,
            'student_id': self.student_id,
            'avatar': self.avatar,
            'balance': float(self.balance) if self.balance else 0.0,
            'can_change_password': self.can_change_password(),
            'last_password_change': self.last_password_change.isoformat() if self.last_password_change else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Product(Base):
    """商品模型"""
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    original_price = Column(Numeric(10, 2))
    category = Column(Enum(ProductCategory), nullable=False)
    status = Column(Enum(ProductStatus), default=ProductStatus.AVAILABLE)
    image_url = Column(String(2000))
    location = Column(String(100))
    views = Column(Integer, default=0)
    seller_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 约束：价格必须 > 0
    __table_args__ = (
        CheckConstraint('price > 0', name='check_price_positive'),
    )
    
    # 关联关系
    seller = relationship("User", back_populates="products", foreign_keys=[seller_id])
    orders = relationship("Order", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    favorites = relationship("Favorite", back_populates="product", cascade="all, delete-orphan")
    
    def to_dict(self, include_seller=True):
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': float(self.price) if self.price else 0.0,
            'original_price': float(self.original_price) if self.original_price else None,
            'category': self.category.value if self.category else None,
            'status': self.status.value if self.status else None,
            'image_url': self.image_url,
            'location': self.location,
            'views': self.views,
            'seller_id': self.seller_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_seller and self.seller:
            result['seller'] = {
                'id': self.seller.id,
                'username': self.seller.username,
                'avatar': self.seller.avatar,
                'phone': self.seller.phone
            }
        return result

class Order(Base):
    """订单模型"""
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    buyer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    seller_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # 关联关系
    product = relationship("Product", back_populates="orders")
    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="orders_as_buyer")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="orders_as_seller")
    review = relationship("Review", back_populates="order", uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'amount': float(self.amount) if self.amount else 0.0,
            'status': self.status.value if self.status else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'product': self.product.to_dict(include_seller=False) if self.product else None,
            'buyer': {
                'id': self.buyer.id,
                'username': self.buyer.username,
                'avatar': self.buyer.avatar
            } if self.buyer else None,
            'seller': {
                'id': self.seller.id,
                'username': self.seller.username,
                'avatar': self.seller.avatar
            } if self.seller else None,
            'review': self.review.to_dict() if self.review else None
        }

class Message(Base):
    """消息模型"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text, nullable=False)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'))
    is_read = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联关系
    sender = relationship("User", foreign_keys=[sender_id], back_populates="messages_sent")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="messages_received")
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'product_id': self.product_id,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sender': {
                'id': self.sender.id,
                'username': self.sender.username,
                'avatar': self.sender.avatar
            } if self.sender else None,
            'receiver': {
                'id': self.receiver.id,
                'username': self.receiver.username,
                'avatar': self.receiver.avatar
            } if self.receiver else None
        }

class Review(Base):
    """商品评价模型"""
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rating = Column(Integer, nullable=False)  # 评分 1-5
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 约束：评分必须在 1-5 之间
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )
    
    # 关联关系
    product = relationship("Product", back_populates="reviews")
    order = relationship("Order", back_populates="review")
    reviewer = relationship("User", back_populates="reviews")
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'order_id': self.order_id,
            'reviewer_id': self.reviewer_id,
            'rating': self.rating,
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'reviewer': {
                'id': self.reviewer.id,
                'username': self.reviewer.username,
                'avatar': self.reviewer.avatar
            } if self.reviewer else None,
            'product': {
                'id': self.product.id,
                'title': self.product.title
            } if self.product else None
        }

class Favorite(Base):
    """商品收藏模型"""
    __tablename__ = 'favorites'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 约束：同一用户不能重复收藏同一商品
    __table_args__ = (
        CheckConstraint('user_id != product_id', name='check_not_self_favorite'),
    )
    
    # 关联关系
    user = relationship("User", back_populates="favorites")
    product = relationship("Product", back_populates="favorites")
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'product': self.product.to_dict(include_seller=True) if self.product else None
        }

def init_db():
    """初始化数据库表"""
    Base.metadata.create_all(engine)
    print("数据库表创建成功！")
    
    # 创建视图、触发器和存储过程
    create_views()
    create_triggers()
    create_procedures()

def create_views():
    """创建数据库视图"""
    from sqlalchemy import text
    
    db = SessionLocal()
    try:
        # 创建热门商品视图（根据留言数排序）
        db.execute(text("""
            CREATE OR REPLACE VIEW v_hot_products AS
            SELECT 
                p.id,
                p.title,
                p.price,
                p.category,
                p.status,
                p.seller_id,
                p.views,
                COUNT(m.id) as message_count
            FROM products p
            LEFT JOIN messages m ON m.product_id = p.id
            WHERE p.status = 'AVAILABLE'
            GROUP BY p.id, p.title, p.price, p.category, p.status, p.seller_id, p.views
            ORDER BY message_count DESC, p.views DESC
            LIMIT 5;
        """))
        
        # 创建用户交易统计视图
        db.execute(text("""
            CREATE OR REPLACE VIEW v_user_stats AS
            SELECT 
                u.id,
                u.username,
                u.balance,
                COUNT(DISTINCT CASE WHEN o.buyer_id = u.id THEN o.id END) as buy_count,
                COUNT(DISTINCT CASE WHEN o.seller_id = u.id THEN o.id END) as sell_count,
                COALESCE(SUM(CASE WHEN o.buyer_id = u.id AND o.status = 'COMPLETED' THEN o.amount ELSE 0 END), 0) as total_spent,
                COALESCE(SUM(CASE WHEN o.seller_id = u.id AND o.status = 'COMPLETED' THEN o.amount ELSE 0 END), 0) as total_earned
            FROM users u
            LEFT JOIN orders o ON u.id = o.buyer_id OR u.id = o.seller_id
            GROUP BY u.id, u.username, u.balance;
        """))
        
        db.commit()
        print("✅ 视图创建成功")
    except Exception as e:
        print(f"⚠️  视图创建警告: {e}")
        db.rollback()
    finally:
        db.close()

def create_triggers():
    """创建数据库触发器"""
    from sqlalchemy import text
    
    db = SessionLocal()
    try:
        # 触发器：订单完成时自动更新商品状态和用户余额
        db.execute(text("""
            CREATE OR REPLACE FUNCTION process_order_completion()
            RETURNS TRIGGER AS $$
            BEGIN
                IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
                    -- 更新商品状态为已完成
                    UPDATE products SET status = 'sold' WHERE id = NEW.product_id;
                    
                    -- 扣除买家余额
                    UPDATE users SET balance = balance - NEW.amount WHERE id = NEW.buyer_id;
                    
                    -- 增加卖家余额
                    UPDATE users SET balance = balance + NEW.amount WHERE id = NEW.seller_id;
                    
                    -- 设置完成时间
                    NEW.completed_at = NOW();
                END IF;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))
        
        db.execute(text("""
            DROP TRIGGER IF EXISTS trigger_order_completion ON orders;
            CREATE TRIGGER trigger_order_completion
            BEFORE UPDATE ON orders
            FOR EACH ROW
            EXECUTE FUNCTION process_order_completion();
        """))
        
        # 触发器：订单创建时自动更新商品状态为已下单
        db.execute(text("""
            CREATE OR REPLACE FUNCTION process_order_creation()
            RETURNS TRIGGER AS $$
            BEGIN
                UPDATE products SET status = 'ordered' WHERE id = NEW.product_id;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """))
        
        db.execute(text("""
            DROP TRIGGER IF EXISTS trigger_order_creation ON orders;
            CREATE TRIGGER trigger_order_creation
            AFTER INSERT ON orders
            FOR EACH ROW
            EXECUTE FUNCTION process_order_creation();
        """))
        
        db.commit()
        print("✅ 触发器创建成功")
    except Exception as e:
        print(f"⚠️  触发器创建警告: {e}")
        db.rollback()
    finally:
        db.close()

def create_procedures():
    """创建存储过程"""
    from sqlalchemy import text
    
    db = SessionLocal()
    try:
        # 存储过程：计算用户本月交易总额
        db.execute(text("""
            CREATE OR REPLACE FUNCTION sp_user_report(user_id_param INTEGER)
            RETURNS TABLE(
                user_id INTEGER,
                username VARCHAR,
                month_buy_count BIGINT,
                month_sell_count BIGINT,
                month_buy_amount NUMERIC,
                month_sell_amount NUMERIC,
                current_balance NUMERIC
            ) AS $$
            BEGIN
                RETURN QUERY
                SELECT 
                    u.id,
                    u.username,
                    COUNT(DISTINCT CASE WHEN o.buyer_id = u.id AND o.created_at >= DATE_TRUNC('month', CURRENT_DATE) THEN o.id END) as month_buy_count,
                    COUNT(DISTINCT CASE WHEN o.seller_id = u.id AND o.created_at >= DATE_TRUNC('month', CURRENT_DATE) THEN o.id END) as month_sell_count,
                    COALESCE(SUM(CASE WHEN o.buyer_id = u.id AND o.created_at >= DATE_TRUNC('month', CURRENT_DATE) THEN o.amount ELSE 0 END), 0) as month_buy_amount,
                    COALESCE(SUM(CASE WHEN o.seller_id = u.id AND o.created_at >= DATE_TRUNC('month', CURRENT_DATE) THEN o.amount ELSE 0 END), 0) as month_sell_amount,
                    u.balance as current_balance
                FROM users u
                LEFT JOIN orders o ON u.id = o.buyer_id OR u.id = o.seller_id
                WHERE u.id = user_id_param
                GROUP BY u.id, u.username, u.balance;
            END;
            $$ LANGUAGE plpgsql;
        """))
        
        db.commit()
        print("✅ 存储过程创建成功")
    except Exception as e:
        print(f"⚠️  存储过程创建警告: {e}")
        db.rollback()
    finally:
        db.close()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
