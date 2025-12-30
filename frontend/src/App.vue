<template>
  <div class="app">
    <!-- 登录/注册页面 -->
    <div v-if="!isLoggedIn" class="auth-container">
      <div class="auth-box">
        <div class="auth-logo">
          <h1>🎓 <span class="logo-accent">校园二手</span></h1>
          <p style="color: #767676; font-size: 0.9rem">
            安全可信的校园交易平台
          </p>
        </div>

        <!-- 登录表单 -->
        <div v-if="authMode === 'login'">
          <h2 class="auth-title">登录</h2>
          <form @submit.prevent="handleLogin" class="auth-form">
            <div class="form-group">
              <label>邮箱</label>
              <input
                v-model="loginForm.email"
                type="email"
                placeholder="请输入注册时使用的邮箱"
                required
                :class="{ error: loginError }"
              />
            </div>
            <div class="form-group">
              <label>密码</label>
              <input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入8位密码"
                required
                maxlength="8"
                :class="{ error: loginError }"
              />
            </div>
            <div v-if="loginError" class="validation-message error">
              ⚠️ {{ loginError }}
            </div>
            <button type="submit" class="auth-submit">登录</button>
          </form>

          <div class="auth-switch">
            <p>还没有账号？</p>
            <button @click="authMode = 'register'" class="auth-switch-btn">
              创建新账号
            </button>
          </div>
        </div>

        <!-- 注册表单 -->
        <div v-else>
          <h2 class="auth-title">创建账号</h2>
          <form @submit.prevent="handleRegister" class="auth-form">
            <div class="form-group">
              <label>用户名</label>
              <input
                v-model="registerForm.username"
                type="text"
                placeholder="3-20个字符"
                required
                @blur="validateUsername"
                :class="{ error: usernameError }"
              />
              <div v-if="usernameError" class="validation-message error">
                ⚠️ {{ usernameError }}
              </div>
              <div
                v-else-if="registerForm.username && !usernameError"
                class="validation-message success"
              >
                ✓ 用户名可用
              </div>
            </div>

            <div class="form-group">
              <label>邮箱</label>
              <input
                v-model="registerForm.email"
                type="email"
                placeholder="请输入有效的邮箱地址"
                required
                @blur="validateEmail"
                :class="{ error: emailError }"
              />
              <div v-if="emailError" class="validation-message error">
                ⚠️ {{ emailError }}
              </div>
              <div
                v-else-if="registerForm.email && !emailError"
                class="validation-message success"
              >
                ✓ 邮箱格式正确
              </div>
            </div>

            <div class="form-group">
              <label>密码 *</label>
              <input
                v-model="registerForm.password"
                type="password"
                placeholder="8位密码，必须包含数字和字母"
                required
                maxlength="8"
                @input="validatePassword"
                @blur="validatePassword"
                :class="{ error: passwordError }"
              />
              <div v-if="passwordError" class="validation-message error">
                ⚠️ {{ passwordError }}
              </div>
              <div
                v-else-if="registerForm.password && !passwordError"
                class="validation-message success"
              >
                ✓ 密码符合要求
              </div>
            </div>

            <div class="form-group">
              <label>手机号（可选）</label>
              <input
                v-model="registerForm.phone"
                type="tel"
                placeholder="11位手机号"
                @blur="validatePhone"
                :class="{ error: phoneError }"
              />
              <div v-if="phoneError" class="validation-message error">
                ⚠️ {{ phoneError }}
              </div>
            </div>

            <div class="form-group">
              <label>学号（可选）</label>
              <input
                v-model="registerForm.student_id"
                type="text"
                placeholder="请输入学号"
              />
            </div>

            <button type="submit" class="auth-submit" :disabled="!isFormValid">
              创建账号
            </button>
          </form>

          <div class="auth-switch">
            <p>已有账号？</p>
            <button @click="authMode = 'login'" class="auth-switch-btn">
              返回登录
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主应用界面 -->
    <div v-else>
      <!-- 顶部导航栏 -->
      <header class="header">
        <div class="container">
          <div class="header-content">
            <h1 class="logo">🎓 校园二手</h1>
            <nav class="nav">
              <button
                v-for="tab in tabs"
                :key="tab.id"
                class="nav-btn"
                :class="{ active: activeTab === tab.id }"
                @click="switchTab(tab.id)"
              >
                {{ tab.icon }} {{ tab.name }}
              </button>
            </nav>
            <div class="user-info">
              <div class="user-welcome">
                <span
                  >你好，<strong>{{ currentUser?.username }}</strong></span
                >
                <button
                  @click="showChangePasswordModal = true"
                  class="change-password-btn"
                >
                  🔑 修改密码
                </button>
                <button @click="handleLogout" class="logout-btn">退出</button>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div class="container main-content">
        <!-- 首页 - 商品列表 -->
        <div v-if="activeTab === 'home'" class="tab-content">
          <div class="page-header">
            <h2>📦 商品市场</h2>
            <button class="btn btn-primary" @click="showPublishModal = true">
              ➕ 发布商品
            </button>
          </div>

          <!-- 搜索和筛选 -->
          <div class="filters">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="🔍 搜索商品..."
              class="search-input"
              @input="fetchProducts"
            />
            <select
              v-model="filterCategory"
              @change="fetchProducts"
              class="filter-select"
            >
              <option value="">全部分类</option>
              <option value="books">📚 教材书籍</option>
              <option value="electronics">💻 电子产品</option>
              <option value="daily">🏠 生活用品</option>
              <option value="sports">⚽ 运动器材</option>
              <option value="clothing">👕 服装配饰</option>
              <option value="other">📦 其他</option>
            </select>
            <select
              v-model="sortBy"
              @change="fetchProducts"
              class="filter-select"
            >
              <option value="newest">最新发布</option>
              <option value="price_asc">价格从低到高</option>
              <option value="price_desc">价格从高到低</option>
              <option value="views">浏览最多</option>
            </select>
          </div>

          <!-- 商品网格 -->
          <div v-if="products.length === 0" class="empty-state">
            <p>📭 暂无商品，快来发布第一个吧！</p>
          </div>
          <div v-else class="product-grid">
            <div
              v-for="product in products"
              :key="product.id"
              class="product-card"
            >
              <div
                class="product-image"
                :style="{
                  backgroundImage: `url(${
                    product.image_url ||
                    'https://via.placeholder.com/300x200?text=No+Image'
                  })`,
                }"
              >
                <span class="product-status" :class="product.status">
                  {{ getStatusText(product.status) }}
                </span>
              </div>
              <div class="product-info">
                <h3 class="product-title">{{ product.title }}</h3>
                <p class="product-desc">{{ product.description }}</p>
                <div class="product-meta">
                  <span class="product-price">¥{{ product.price }}</span>
                  <span
                    v-if="product.original_price"
                    class="product-original-price"
                  >
                    ¥{{ product.original_price }}
                  </span>
                </div>
                <div class="product-footer">
                  <div class="seller-info">
                    <img :src="product.seller?.avatar" class="seller-avatar" />
                    <span>{{ product.seller?.username }}</span>
                  </div>
                  <div class="product-stats">
                    <span>👁️ {{ product.views }}</span>
                  </div>
                </div>
                <div class="product-actions">
                  <button
                    class="btn btn-sm btn-primary"
                    @click="viewProduct(product)"
                  >
                    查看详情
                  </button>
                  <button
                    class="btn btn-sm btn-secondary"
                    @click="contactSeller(product)"
                  >
                    💬 联系
                  </button>
                  <button
                    v-if="product.seller_id !== currentUser?.id"
                    class="btn btn-sm"
                    :class="
                      isFavorited(product.id) ? 'btn-danger' : 'btn-outline'
                    "
                    @click="toggleFavorite(product)"
                    :title="isFavorited(product.id) ? '取消收藏' : '收藏商品'"
                  >
                    {{ isFavorited(product.id) ? "💔" : "❤️" }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 我的发布 -->
        <div v-if="activeTab === 'myProducts'" class="tab-content">
          <div class="page-header">
            <h2>📝 我的发布</h2>
            <button class="btn btn-primary" @click="showPublishModal = true">
              ➕ 发布新商品
            </button>
          </div>

          <div v-if="myProducts.length === 0" class="empty-state">
            <p>📭 您还没有发布任何商品</p>
          </div>
          <div v-else class="product-list">
            <div
              v-for="product in myProducts"
              :key="product.id"
              class="product-list-item"
            >
              <img
                :src="product.image_url || 'https://via.placeholder.com/100'"
                class="list-item-image"
              />
              <div class="list-item-content">
                <h3>{{ product.title }}</h3>
                <p>{{ product.description }}</p>
                <div class="list-item-meta">
                  <span class="price">¥{{ product.price }}</span>
                  <span class="status" :class="product.status">{{
                    getStatusText(product.status)
                  }}</span>
                  <span class="views">👁️ {{ product.views }}</span>
                </div>
              </div>
              <div class="list-item-actions">
                <button
                  class="btn btn-sm"
                  @click="editProduct(product)"
                  :disabled="
                    product.status === 'sold' || product.status === 'ordered'
                  "
                >
                  编辑
                </button>
                <button
                  v-if="product.status === 'available'"
                  class="btn btn-sm btn-danger"
                  @click="deleteProduct(product.id)"
                >
                  删除
                </button>
                <button
                  v-else
                  class="btn btn-sm btn-secondary"
                  disabled
                  title="已售出或已下单的商品不能删除"
                >
                  {{ product.status === "sold" ? "已售出" : "已下单" }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 我的收藏 -->
        <div v-if="activeTab === 'myFavorites'" class="tab-content">
          <div class="page-header">
            <h2>❤️ 我的收藏</h2>
          </div>

          <div v-if="favorites.length === 0" class="empty-state">
            <p>💔 您还没有收藏任何商品</p>
          </div>
          <div v-else class="product-grid">
            <div
              v-for="favorite in favorites"
              :key="favorite.id"
              class="product-card"
            >
              <div
                class="product-image"
                :style="{
                  backgroundImage: `url(${
                    favorite.product?.image_url ||
                    'https://via.placeholder.com/300x200?text=No+Image'
                  })`,
                }"
              >
                <span class="product-status" :class="favorite.product?.status">
                  {{ getStatusText(favorite.product?.status) }}
                </span>
              </div>
              <div class="product-info">
                <h3 class="product-title">{{ favorite.product?.title }}</h3>
                <p class="product-desc">{{ favorite.product?.description }}</p>
                <div class="product-meta">
                  <span class="product-price"
                    >¥{{ favorite.product?.price }}</span
                  >
                  <span
                    v-if="favorite.product?.original_price"
                    class="product-original-price"
                  >
                    ¥{{ favorite.product?.original_price }}
                  </span>
                </div>
                <div class="product-footer">
                  <div class="seller-info">
                    <img
                      :src="favorite.product?.seller?.avatar"
                      class="seller-avatar"
                    />
                    <span>{{ favorite.product?.seller?.username }}</span>
                  </div>
                  <div class="product-stats">
                    <span>👁️ {{ favorite.product?.views }}</span>
                  </div>
                </div>
                <div class="product-actions">
                  <button
                    class="btn btn-sm btn-primary"
                    @click="viewProduct(favorite.product)"
                  >
                    查看详情
                  </button>
                  <button
                    class="btn btn-sm btn-danger"
                    @click="toggleFavorite(favorite.product)"
                    title="取消收藏"
                  >
                    💔 取消收藏
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 我的订单 -->
        <div v-if="activeTab === 'myOrders'" class="tab-content">
          <div class="page-header">
            <h2>📦 我的订单</h2>
          </div>

          <div v-if="orders.length === 0" class="empty-state">
            <p>📭 您还没有任何订单</p>
          </div>
          <div v-else class="order-list">
            <div v-for="order in orders" :key="order.id" class="order-card">
              <div class="order-header">
                <div class="order-id-group">
                  <span class="order-id">订单号: #{{ order.id }}</span>
                  <span
                    v-if="order.seller_id === currentUser?.id"
                    class="order-role seller"
                  >
                    我是卖家
                  </span>
                  <span v-else class="order-role buyer"> 我是买家 </span>
                </div>
                <span class="order-status" :class="order.status">
                  {{ getOrderStatusText(order.status) }}
                </span>
              </div>
              <div class="order-content">
                <img
                  :src="
                    order.product?.image_url ||
                    'https://via.placeholder.com/100'
                  "
                  class="order-image"
                />
                <div class="order-info">
                  <h3>{{ order.product?.title }}</h3>
                  <p class="order-meta">
                    <span v-if="order.buyer_id === currentUser?.id">
                      卖家: {{ order.seller?.username }}
                    </span>
                    <span v-else> 买家: {{ order.buyer?.username }} </span>
                  </p>
                  <p class="order-time">
                    创建时间: {{ formatDate(order.created_at) }}
                  </p>
                  <p v-if="order.completed_at" class="order-time">
                    完成时间: {{ formatDate(order.completed_at) }}
                  </p>
                </div>
                <div class="order-price">
                  <span class="price-label">订单金额</span>
                  <span class="price-value">¥{{ order.amount }}</span>
                </div>
              </div>
              <div class="order-actions">
                <button
                  v-if="
                    order.status === 'pending' &&
                    order.seller_id === currentUser?.id
                  "
                  class="btn btn-sm btn-primary"
                  @click="completeOrder(order.id)"
                  title="确认收到款项并完成交易"
                >
                  ✅ 确认完成
                </button>
                <button
                  v-if="order.status === 'pending'"
                  class="btn btn-sm btn-danger"
                  @click="cancelOrder(order.id)"
                  title="取消此订单"
                >
                  ❌ 取消订单
                </button>
                <button
                  v-if="
                    order.status === 'completed' &&
                    order.buyer_id === currentUser?.id &&
                    !order.review
                  "
                  class="btn btn-sm btn-success"
                  @click="openReviewDialog(order)"
                  title="评价商品"
                >
                  ⭐ 评价
                </button>
                <button
                  v-if="order.review"
                  class="btn btn-sm btn-outline"
                  disabled
                  title="已评价"
                >
                  ✓ 已评价
                </button>
                <button
                  class="btn btn-sm btn-outline"
                  @click="viewProduct(order.product)"
                  title="查看商品详情"
                >
                  👁️ 查看商品
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 个人中心 -->
        <div v-if="activeTab === 'userCenter'" class="tab-content">
          <div class="page-header">
            <h2>👤 个人中心</h2>
          </div>

          <div class="user-center-container">
            <!-- 用户信息卡片 -->
            <div class="user-info-card">
              <div class="user-avatar-section">
                <img :src="currentUser?.avatar" class="user-avatar-large" />
                <h3>{{ currentUser?.username }}</h3>
                <p class="user-email">{{ currentUser?.email }}</p>
              </div>

              <div class="user-details">
                <div class="detail-row">
                  <span class="detail-label">📱 手机号：</span>
                  <div class="detail-value-group">
                    <span v-if="!editingInfo" class="detail-value">{{
                      currentUser?.phone || "未设置"
                    }}</span>
                    <input
                      v-else
                      v-model="editInfoForm.phone"
                      type="tel"
                      placeholder="11位手机号"
                      class="detail-input"
                      maxlength="11"
                    />
                  </div>
                </div>
                <div class="detail-row">
                  <span class="detail-label">🎓 学号：</span>
                  <div class="detail-value-group">
                    <span v-if="!editingInfo" class="detail-value">{{
                      currentUser?.student_id || "未设置"
                    }}</span>
                    <input
                      v-else
                      v-model="editInfoForm.student_id"
                      type="text"
                      placeholder="请输入学号"
                      class="detail-input"
                    />
                  </div>
                </div>
                <div class="detail-row">
                  <span class="detail-label">💰 账户余额：</span>
                  <span class="detail-value balance"
                    >¥{{ currentUser?.balance }}</span
                  >
                  <span class="detail-hint">（通过交易自动更新）</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">📅 注册时间：</span>
                  <span class="detail-value">{{
                    formatDate(currentUser?.created_at)
                  }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">🔑 上次修改密码：</span>
                  <span class="detail-value">{{
                    formatDate(currentUser?.last_password_change)
                  }}</span>
                </div>
                <div class="detail-row">
                  <span class="detail-label">🔐 密码修改状态：</span>
                  <span
                    class="detail-value"
                    :class="
                      currentUser?.can_change_password
                        ? 'can-change'
                        : 'cannot-change'
                    "
                  >
                    {{
                      currentUser?.can_change_password
                        ? "✅ 可以修改"
                        : "⏳ 需等待30天"
                    }}
                  </span>
                </div>
              </div>

              <div class="user-actions">
                <button
                  v-if="!editingInfo"
                  class="btn btn-secondary"
                  @click="startEditInfo"
                >
                  ✏️ 编辑信息
                </button>
                <button v-else class="btn btn-primary" @click="saveUserInfo">
                  💾 保存
                </button>
                <button
                  v-if="editingInfo"
                  class="btn btn-secondary"
                  @click="cancelEditInfo"
                >
                  ❌ 取消
                </button>
                <button
                  class="btn btn-primary"
                  @click="showChangePasswordModal = true"
                  :disabled="!currentUser?.can_change_password"
                  :title="
                    currentUser?.can_change_password
                      ? '修改密码'
                      : '每月只能修改一次密码'
                  "
                >
                  🔑 修改密码
                </button>
              </div>
            </div>

            <!-- 用户统计卡片 -->
            <div class="user-stats-card">
              <h3>📊 我的统计</h3>
              <div class="stats-grid">
                <div class="stat-item">
                  <div class="stat-number">{{ myProducts.length }}</div>
                  <div class="stat-text">发布商品</div>
                </div>
                <div class="stat-item">
                  <div class="stat-number">
                    {{
                      orders.filter((o) => o.buyer_id === currentUser?.id)
                        .length
                    }}
                  </div>
                  <div class="stat-text">购买订单</div>
                </div>
                <div class="stat-item">
                  <div class="stat-number">
                    {{
                      orders.filter((o) => o.seller_id === currentUser?.id)
                        .length
                    }}
                  </div>
                  <div class="stat-text">出售订单</div>
                </div>
                <div class="stat-item">
                  <div class="stat-number">
                    {{
                      myProducts.filter((p) => p.status === "available").length
                    }}
                  </div>
                  <div class="stat-text">在售商品</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 数据统计 -->
        <div v-if="activeTab === 'stats'" class="tab-content">
          <h2>📊 平台统计</h2>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-icon">👥</div>
              <div class="stat-value">{{ stats.total_users }}</div>
              <div class="stat-label">注册用户</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">📦</div>
              <div class="stat-value">{{ stats.total_products }}</div>
              <div class="stat-label">商品总数</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">✅</div>
              <div class="stat-value">{{ stats.available_products }}</div>
              <div class="stat-label">在售商品</div>
            </div>
            <div class="stat-card">
              <div class="stat-icon">💰</div>
              <div class="stat-value">{{ stats.sold_products }}</div>
              <div class="stat-label">已售商品</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 修改密码模态框 -->
      <div
        v-if="showChangePasswordModal"
        class="modal"
        @click.self="showChangePasswordModal = false"
      >
        <div class="modal-content">
          <div class="modal-header">
            <h2>🔑 修改密码</h2>
            <button class="close-btn" @click="showChangePasswordModal = false">
              ✕
            </button>
          </div>
          <form @submit.prevent="handleChangePassword" class="modal-body">
            <div class="form-group">
              <label>旧密码 *</label>
              <input
                v-model="changePasswordForm.oldPassword"
                type="password"
                placeholder="请输入当前密码"
                required
                maxlength="8"
              />
            </div>
            <div class="form-group">
              <label>新密码 * (8位，必须包含数字和字母)</label>
              <input
                v-model="changePasswordForm.newPassword"
                type="password"
                placeholder="请输入新密码"
                required
                maxlength="8"
                @input="validateNewPassword"
              />
              <div v-if="newPasswordError" class="validation-message error">
                ⚠️ {{ newPasswordError }}
              </div>
              <div
                v-else-if="changePasswordForm.newPassword && !newPasswordError"
                class="validation-message success"
              >
                ✓ 密码符合要求
              </div>
            </div>
            <div class="form-group">
              <label>确认新密码 *</label>
              <input
                v-model="changePasswordForm.confirmPassword"
                type="password"
                placeholder="请再次输入新密码"
                required
                maxlength="8"
              />
              <div
                v-if="
                  changePasswordForm.confirmPassword &&
                  changePasswordForm.newPassword !==
                    changePasswordForm.confirmPassword
                "
                class="validation-message error"
              >
                ⚠️ 两次输入的密码不一致
              </div>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-secondary"
                @click="showChangePasswordModal = false"
              >
                取消
              </button>
              <button
                type="submit"
                class="btn btn-primary"
                :disabled="!isChangePasswordValid"
              >
                确认修改
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- 发布商品模态框 -->
      <div
        v-if="showPublishModal"
        class="modal"
        @click.self="closePublishModal"
      >
        <div class="modal-content">
          <div class="modal-header">
            <h2>{{ editingProduct ? "编辑商品" : "发布新商品" }}</h2>
            <button class="close-btn" @click="closePublishModal">✕</button>
          </div>
          <form @submit.prevent="submitProduct" class="modal-body">
            <div class="form-group">
              <label>商品标题 *</label>
              <input
                v-model="productForm.title"
                placeholder="请输入商品标题"
                required
              />
            </div>
            <div class="form-group">
              <label>商品描述 *</label>
              <textarea
                v-model="productForm.description"
                placeholder="请详细描述商品信息"
                required
              ></textarea>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>售价 (元) *</label>
                <input
                  v-model.number="productForm.price"
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                  required
                />
              </div>
              <div class="form-group">
                <label>原价 (元)</label>
                <input
                  v-model.number="productForm.original_price"
                  type="number"
                  step="0.01"
                  placeholder="0.00"
                />
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label>商品分类 *</label>
                <select v-model="productForm.category" required>
                  <option value="">请选择分类</option>
                  <option value="books">📚 教材书籍</option>
                  <option value="electronics">💻 电子产品</option>
                  <option value="daily">🏠 生活用品</option>
                  <option value="sports">⚽ 运动器材</option>
                  <option value="clothing">👕 服装配饰</option>
                  <option value="other">📦 其他</option>
                </select>
              </div>
              <div class="form-group" v-if="editingProduct">
                <label>商品状态</label>
                <select v-model="productForm.status">
                  <option value="available">在售</option>
                  <option value="reserved">已预订</option>
                  <option value="sold">已售出</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label>交易地点</label>
              <input
                v-model="productForm.location"
                placeholder="例如：东区宿舍楼下"
              />
            </div>
            <div class="form-group">
              <label>商品图片链接</label>
              <input
                v-model="productForm.image_url"
                placeholder="https://example.com/image.jpg"
              />
              <div class="form-hint">
                💡 建议使用图床或直接图片链接（如 Unsplash、imgur 等）<br />
                ⚠️ 不要使用百度图片搜索链接，请右键复制图片地址
              </div>
            </div>
            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-secondary"
                @click="closePublishModal"
              >
                取消
              </button>
              <button type="submit" class="btn btn-primary">
                {{ editingProduct ? "保存" : "发布" }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- 商品详情模态框 -->
      <div
        v-if="showDetailModal"
        class="modal"
        @click.self="showDetailModal = false"
      >
        <div class="modal-content modal-large">
          <div class="modal-header">
            <h2>商品详情</h2>
            <button class="close-btn" @click="showDetailModal = false">
              ✕
            </button>
          </div>
          <div class="modal-body" v-if="selectedProduct">
            <div class="product-detail">
              <img
                :src="
                  selectedProduct.image_url || 'https://via.placeholder.com/400'
                "
                class="detail-image"
              />
              <div class="detail-info">
                <h2>{{ selectedProduct.title }}</h2>
                <div class="detail-price">
                  <span class="current-price"
                    >¥{{ selectedProduct.price }}</span
                  >
                  <span
                    v-if="selectedProduct.original_price"
                    class="original-price"
                  >
                    原价: ¥{{ selectedProduct.original_price }}
                  </span>
                </div>
                <div class="detail-meta">
                  <span class="badge">{{
                    getCategoryText(selectedProduct.category)
                  }}</span>
                  <span class="badge" :class="selectedProduct.status">{{
                    getStatusText(selectedProduct.status)
                  }}</span>
                  <span>👁️ {{ selectedProduct.views }} 次浏览</span>
                </div>
                <div class="detail-description">
                  <h3>商品描述</h3>
                  <p>{{ selectedProduct.description }}</p>
                </div>
                <div v-if="selectedProduct.location" class="detail-location">
                  <h3>📍 交易地点</h3>
                  <p>{{ selectedProduct.location }}</p>
                </div>
                <div class="detail-seller">
                  <h3>卖家信息</h3>
                  <div class="seller-card">
                    <img
                      :src="selectedProduct.seller?.avatar"
                      class="seller-avatar"
                    />
                    <div>
                      <p>
                        <strong>{{ selectedProduct.seller?.username }}</strong>
                      </p>
                      <p v-if="selectedProduct.seller?.phone">
                        📱 {{ selectedProduct.seller?.phone }}
                      </p>
                    </div>
                  </div>
                </div>

                <!-- 商品评价区域 -->
                <div v-if="productReviews.length > 0" class="detail-reviews">
                  <h3>📝 商品评价 ({{ productReviews.length }})</h3>
                  <div
                    v-for="review in productReviews"
                    :key="review.id"
                    class="review-item"
                  >
                    <div class="review-header">
                      <img
                        :src="review.reviewer?.avatar"
                        class="review-avatar"
                      />
                      <div class="review-info">
                        <strong>{{ review.reviewer?.username }}</strong>
                        <div class="review-rating">
                          <span
                            v-for="star in 5"
                            :key="star"
                            class="star"
                            :class="{ active: star <= review.rating }"
                          >
                            ⭐
                          </span>
                        </div>
                      </div>
                      <span class="review-date">{{
                        formatDate(review.created_at)
                      }}</span>
                    </div>
                    <p class="review-comment">{{ review.comment }}</p>
                  </div>
                </div>

                <!-- 购买按钮区域 -->
                <div class="detail-actions">
                  <button
                    v-if="
                      selectedProduct.status === 'available' &&
                      selectedProduct.seller_id !== currentUser?.id
                    "
                    class="btn btn-primary btn-block"
                    @click="purchaseProduct(selectedProduct)"
                  >
                    🛒 立即购买
                  </button>
                  <button
                    v-else-if="selectedProduct.seller_id === currentUser?.id"
                    class="btn btn-secondary btn-block"
                    disabled
                  >
                    这是您自己的商品
                  </button>
                  <button
                    v-else-if="selectedProduct.status === 'ordered'"
                    class="btn btn-secondary btn-block"
                    disabled
                  >
                    已被预定
                  </button>
                  <button
                    v-else-if="selectedProduct.status === 'sold'"
                    class="btn btn-secondary btn-block"
                    disabled
                  >
                    已售出
                  </button>
                  <button
                    class="btn btn-outline btn-block"
                    @click="contactSeller(selectedProduct)"
                  >
                    💬 联系卖家
                  </button>
                  <button
                    v-if="selectedProduct.seller_id !== currentUser?.id"
                    class="btn btn-block"
                    :class="
                      isFavorited(selectedProduct.id)
                        ? 'btn-danger'
                        : 'btn-outline'
                    "
                    @click="toggleFavorite(selectedProduct)"
                  >
                    {{
                      isFavorited(selectedProduct.id)
                        ? "💔 取消收藏"
                        : "❤️ 收藏商品"
                    }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 评价模态框 -->
      <div
        v-if="showReviewModal"
        class="modal"
        @click.self="showReviewModal = false"
      >
        <div class="modal-content">
          <div class="modal-header">
            <h2>⭐ 评价商品</h2>
            <button class="close-btn" @click="showReviewModal = false">
              ✕
            </button>
          </div>
          <form @submit.prevent="submitReview" class="modal-body">
            <div v-if="reviewingOrder" class="review-product-info">
              <img
                :src="
                  reviewingOrder.product?.image_url ||
                  'https://via.placeholder.com/80'
                "
                class="review-product-image"
              />
              <div>
                <h4>{{ reviewingOrder.product?.title }}</h4>
                <p>订单号: #{{ reviewingOrder.id }}</p>
              </div>
            </div>

            <div class="form-group">
              <label>评分 *</label>
              <div class="rating-input">
                <span
                  v-for="star in 5"
                  :key="star"
                  class="star"
                  :class="{ active: star <= reviewForm.rating }"
                  @click="reviewForm.rating = star"
                >
                  ⭐
                </span>
              </div>
              <small>{{ reviewForm.rating }} 星</small>
            </div>

            <div class="form-group">
              <label>评价内容</label>
              <textarea
                v-model="reviewForm.comment"
                placeholder="分享您的购买体验..."
                rows="4"
              ></textarea>
            </div>

            <div class="modal-footer">
              <button
                type="button"
                class="btn btn-secondary"
                @click="showReviewModal = false"
              >
                取消
              </button>
              <button type="submit" class="btn btn-primary">提交评价</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from "vue";
import axios from "axios";

const API_BASE = "/api";

// 认证状态
const isLoggedIn = ref(false);
const authMode = ref("login");
const loginForm = ref({ email: "", password: "" });
const registerForm = ref({
  username: "",
  email: "",
  password: "",
  phone: "",
  student_id: "",
});

// 验证错误
const loginError = ref("");
const usernameError = ref("");
const emailError = ref("");
const passwordError = ref("");
const phoneError = ref("");

// 状态管理
const activeTab = ref("home");
const currentUser = ref(null);

// 数据
const users = ref([]);
const products = ref([]);
const orders = ref([]);
const favorites = ref([]);
const productReviews = ref([]);
const stats = ref({
  total_users: 0,
  total_products: 0,
  available_products: 0,
  sold_products: 0,
});

// 筛选和搜索
const searchQuery = ref("");
const filterCategory = ref("");
const sortBy = ref("newest");

// 模态框
const showPublishModal = ref(false);
const showDetailModal = ref(false);
const showChangePasswordModal = ref(false);
const showReviewModal = ref(false);
const editingProduct = ref(null);
const selectedProduct = ref(null);
const reviewingOrder = ref(null);
const reviewForm = ref({
  rating: 5,
  comment: "",
});

// 修改密码表单
const changePasswordForm = ref({
  oldPassword: "",
  newPassword: "",
  confirmPassword: "",
});
const newPasswordError = ref("");

// 编辑个人信息
const editingInfo = ref(false);
const editInfoForm = ref({
  phone: "",
  student_id: "",
});

// 表单
const productForm = ref({
  title: "",
  description: "",
  price: 0,
  original_price: null,
  category: "",
  status: "available",
  image_url: "",
  location: "",
  seller_id: null,
});

// 标签页配置
const tabs = [
  { id: "home", name: "商品市场", icon: "🏪" },
  { id: "myProducts", name: "我的发布", icon: "📝" },
  { id: "myFavorites", name: "我的收藏", icon: "❤️" },
  { id: "myOrders", name: "我的订单", icon: "📦" },
  { id: "userCenter", name: "个人中心", icon: "👤" },
  { id: "stats", name: "数据统计", icon: "📊" },
];

// 计算属性
const myProducts = computed(() => {
  if (!currentUser.value) return [];
  return products.value.filter((p) => p.seller_id === currentUser.value.id);
});

const isFormValid = computed(() => {
  return (
    registerForm.value.username &&
    registerForm.value.email &&
    registerForm.value.password &&
    !usernameError.value &&
    !emailError.value &&
    !passwordError.value &&
    !phoneError.value
  );
});

const isChangePasswordValid = computed(() => {
  return (
    changePasswordForm.value.oldPassword &&
    changePasswordForm.value.newPassword &&
    changePasswordForm.value.confirmPassword &&
    changePasswordForm.value.newPassword ===
      changePasswordForm.value.confirmPassword &&
    !newPasswordError.value
  );
});

// 验证方法
const validateUsername = () => {
  const username = registerForm.value.username;
  if (!username) {
    usernameError.value = "";
    return;
  }
  if (username.length < 3 || username.length > 20) {
    usernameError.value = "用户名长度必须在3-20个字符之间";
    return;
  }
  if (!/^[a-zA-Z0-9\u4e00-\u9fa5_]+$/.test(username)) {
    usernameError.value = "用户名只能包含字母、数字、中文和下划线";
    return;
  }
  usernameError.value = "";
};

const validateEmail = () => {
  const email = registerForm.value.email;
  if (!email) {
    emailError.value = "";
    return;
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    emailError.value = "请输入有效的邮箱地址";
    return;
  }
  // 检查是否为教育邮箱（可选）
  if (!email.endsWith(".edu") && !email.includes("edu")) {
    emailError.value = "建议使用教育邮箱（.edu）";
    return;
  }
  emailError.value = "";
};

const validatePhone = () => {
  const phone = registerForm.value.phone;
  if (!phone) {
    phoneError.value = "";
    return;
  }
  if (!/^1[3-9]\d{9}$/.test(phone)) {
    phoneError.value = "请输入有效的11位手机号";
    return;
  }
  phoneError.value = "";
};

const validatePassword = () => {
  const password = registerForm.value.password;
  if (!password) {
    passwordError.value = "";
    return;
  }
  if (password.length !== 8) {
    passwordError.value =
      password.length > 8 ? "密码超出8位，请删除多余字符" : "密码必须是8位";
    return;
  }
  const hasDigit = /\d/.test(password);
  const hasAlpha = /[a-zA-Z]/.test(password);
  if (!hasDigit || !hasAlpha) {
    passwordError.value = "密码必须包含数字和字母";
    return;
  }
  passwordError.value = "";
};

const validateNewPassword = () => {
  const password = changePasswordForm.value.newPassword;
  if (!password) {
    newPasswordError.value = "";
    return;
  }
  if (password.length !== 8) {
    newPasswordError.value =
      password.length > 8 ? "密码超出8位，请删除多余字符" : "密码必须是8位";
    return;
  }
  const hasDigit = /\d/.test(password);
  const hasAlpha = /[a-zA-Z]/.test(password);
  if (!hasDigit || !hasAlpha) {
    newPasswordError.value = "密码必须包含数字和字母";
    return;
  }
  newPasswordError.value = "";
};

// 认证方法
const handleLogin = async () => {
  loginError.value = "";
  try {
    const response = await axios.post(`${API_BASE}/login`, {
      email: loginForm.value.email,
      password: loginForm.value.password,
    });

    currentUser.value = response.data;
    isLoggedIn.value = true;
    localStorage.setItem("currentUser", JSON.stringify(response.data));
  } catch (error) {
    if (error.response?.status === 404) {
      loginError.value = "邮箱不存在，请先注册";
    } else if (error.response?.status === 401) {
      loginError.value = "密码错误";
    } else {
      loginError.value = "登录失败，请稍后重试";
    }
  }
};

const handleRegister = async () => {
  try {
    const response = await axios.post(`${API_BASE}/users`, registerForm.value);
    currentUser.value = response.data;
    isLoggedIn.value = true;
    localStorage.setItem("currentUser", JSON.stringify(response.data));
    alert(
      `✅ 注册成功！\n\n` +
        `欢迎，${response.data.username}！\n` +
        `您的邮箱：${response.data.email}\n` +
        `初始余额：¥${response.data.balance}\n\n` +
        `💡 提示：请牢记您的8位密码`
    );
  } catch (error) {
    alert("❌ 注册失败: " + (error.response?.data?.error || error.message));
  }
};

const handleLogout = () => {
  if (confirm("确定要退出登录吗？")) {
    isLoggedIn.value = false;
    currentUser.value = null;
    localStorage.removeItem("currentUser");
  }
};

const handleChangePassword = async () => {
  if (!currentUser.value) {
    alert("❌ 请先登录");
    return;
  }

  if (!currentUser.value.can_change_password) {
    alert("❌ 每月只能修改一次密码，请稍后再试");
    return;
  }

  if (
    changePasswordForm.value.newPassword !==
    changePasswordForm.value.confirmPassword
  ) {
    alert("❌ 两次输入的密码不一致");
    return;
  }

  try {
    const response = await axios.put(
      `${API_BASE}/users/${currentUser.value.id}/change-password`,
      {
        old_password: changePasswordForm.value.oldPassword,
        new_password: changePasswordForm.value.newPassword,
      }
    );

    alert("✅ 密码修改成功！下次登录请使用新密码");

    // 更新用户信息
    currentUser.value = response.data.user;
    localStorage.setItem("currentUser", JSON.stringify(response.data.user));

    // 关闭模态框并重置表单
    showChangePasswordModal.value = false;
    changePasswordForm.value = {
      oldPassword: "",
      newPassword: "",
      confirmPassword: "",
    };
    newPasswordError.value = "";
  } catch (error) {
    const errorMsg = error.response?.data?.error || error.message;
    alert("❌ 修改失败: " + errorMsg);
  }
};

const startEditInfo = () => {
  editingInfo.value = true;
  editInfoForm.value = {
    phone: currentUser.value?.phone || "",
    student_id: currentUser.value?.student_id || "",
  };
};

const cancelEditInfo = () => {
  editingInfo.value = false;
  editInfoForm.value = {
    phone: "",
    student_id: "",
  };
};

const saveUserInfo = async () => {
  if (!currentUser.value) {
    alert("❌ 请先登录");
    return;
  }

  // 验证手机号
  if (
    editInfoForm.value.phone &&
    !/^1[3-9]\d{9}$/.test(editInfoForm.value.phone)
  ) {
    alert("❌ 请输入有效的11位手机号");
    return;
  }

  try {
    const response = await axios.put(
      `${API_BASE}/users/${currentUser.value.id}`,
      {
        phone: editInfoForm.value.phone || null,
        student_id: editInfoForm.value.student_id || null,
      }
    );

    alert("✅ 信息更新成功！");

    // 更新用户信息
    currentUser.value = response.data;
    localStorage.setItem("currentUser", JSON.stringify(response.data));

    // 退出编辑模式
    editingInfo.value = false;
  } catch (error) {
    const errorMsg = error.response?.data?.error || error.message;
    alert("❌ 更新失败: " + errorMsg);
  }
};

// 方法
const switchTab = (tabId) => {
  activeTab.value = tabId;
  if (tabId === "home") fetchProducts();
  else if (tabId === "myProducts") fetchProducts();
  else if (tabId === "myFavorites") fetchFavorites();
  else if (tabId === "myOrders") fetchOrders();
  else if (tabId === "stats") fetchStats();
};

const fetchUsers = async () => {
  try {
    const response = await axios.get(`${API_BASE}/users`);
    users.value = response.data;
  } catch (error) {
    console.error("获取用户列表失败:", error);
  }
};

const fetchProducts = async () => {
  try {
    const params = {
      search: searchQuery.value,
      category: filterCategory.value,
      sort: sortBy.value,
    };

    // 我的发布页面：显示所有自己的商品
    if (activeTab.value === "myProducts" && currentUser.value) {
      params.seller_id = currentUser.value.id;
      delete params.status;
    } else {
      // 商品市场：不过滤状态，显示所有商品
      delete params.status;
    }

    const response = await axios.get(`${API_BASE}/products`, { params });
    let productList = response.data;

    // 商品市场：优先按状态排序（在售>已下单>已售），然后按用户选择的排序
    if (activeTab.value === "home") {
      productList = productList.sort((a, b) => {
        // 第一优先级：状态排序
        const statusOrder = {
          available: 0, // 在售 - 最前面
          ordered: 1, // 已下单 - 中间
          sold: 2, // 已售出 - 最后面
        };
        const statusA =
          statusOrder[a.status] !== undefined ? statusOrder[a.status] : 3;
        const statusB =
          statusOrder[b.status] !== undefined ? statusOrder[b.status] : 3;

        // 如果状态不同，按状态排序
        if (statusA !== statusB) {
          return statusA - statusB;
        }

        // 如果状态相同，按用户选择的排序方式
        if (sortBy.value === "price_asc") {
          return a.price - b.price;
        } else if (sortBy.value === "price_desc") {
          return b.price - a.price;
        } else if (sortBy.value === "views") {
          return b.views - a.views;
        } else {
          // newest
          return new Date(b.created_at) - new Date(a.created_at);
        }
      });
    }

    products.value = productList;
  } catch (error) {
    console.error("获取商品列表失败:", error);
  }
};

const viewProduct = async (product) => {
  try {
    const response = await axios.get(`${API_BASE}/products/${product.id}`);
    selectedProduct.value = response.data;

    // 获取商品评价
    const reviewsResponse = await axios.get(
      `${API_BASE}/products/${product.id}/reviews`
    );
    productReviews.value = reviewsResponse.data;

    showDetailModal.value = true;
  } catch (error) {
    alert("❌ 获取商品详情失败");
  }
};

const editProduct = (product) => {
  editingProduct.value = product;
  productForm.value = {
    title: product.title,
    description: product.description,
    price: product.price,
    original_price: product.original_price,
    category: product.category,
    status: product.status,
    image_url: product.image_url,
    location: product.location,
    seller_id: product.seller_id,
  };
  showPublishModal.value = true;
};

const submitProduct = async () => {
  if (!currentUser.value) {
    alert("❌ 请先登录");
    return;
  }

  try {
    productForm.value.seller_id = currentUser.value.id;

    if (editingProduct.value) {
      await axios.put(
        `${API_BASE}/products/${editingProduct.value.id}`,
        productForm.value
      );
      alert("✅ 商品更新成功！");
    } else {
      await axios.post(`${API_BASE}/products`, productForm.value);
      alert("✅ 商品发布成功！");
    }

    closePublishModal();
    await fetchProducts();
  } catch (error) {
    console.error("操作失败:", error);
    const errorMsg = error.response?.data?.error || error.message;
    if (errorMsg.includes("foreign key") || errorMsg.includes("seller_id")) {
      alert("❌ 用户信息已过期，请重新登录");
      handleLogout();
    } else {
      alert("❌ 操作失败: " + errorMsg);
    }
  }
};

const deleteProduct = async (id) => {
  if (!confirm("确定要删除这个商品吗？")) return;
  try {
    await axios.delete(`${API_BASE}/products/${id}`);
    await fetchProducts();
    alert("✅ 删除成功！");
  } catch (error) {
    alert("❌ 删除失败: " + error.message);
  }
};

const closePublishModal = () => {
  showPublishModal.value = false;
  editingProduct.value = null;
  productForm.value = {
    title: "",
    description: "",
    price: 0,
    original_price: null,
    category: "",
    status: "available",
    image_url: "",
    location: "",
    seller_id: null,
  };
};

const contactSeller = (product) => {
  if (!currentUser.value) {
    alert("❌ 请先登录");
    return;
  }
  if (product.seller_id === currentUser.value.id) {
    alert("ℹ️ 这是您自己发布的商品");
    return;
  }
  alert(
    `💬 联系卖家: ${product.seller?.username}\n📱 ${
      product.seller?.phone || "未提供联系方式"
    }`
  );
};

const purchaseProduct = async (product) => {
  if (!currentUser.value) {
    alert("❌ 请先登录");
    return;
  }

  if (product.seller_id === currentUser.value.id) {
    alert("❌ 不能购买自己的商品");
    return;
  }

  if (product.status !== "available") {
    alert("❌ 该商品不可购买");
    return;
  }

  // 确认购买
  const confirmed = confirm(
    `确认购买商品？\n\n` +
      `商品：${product.title}\n` +
      `价格：¥${product.price}\n` +
      `卖家：${product.seller?.username}\n\n` +
      `您的当前余额：¥${currentUser.value.balance}\n` +
      `购买后余额：¥${(currentUser.value.balance - product.price).toFixed(
        2
      )}\n\n` +
      `点击确定后将创建订单并预定商品`
  );

  if (!confirmed) return;

  try {
    // 创建订单
    const response = await axios.post(`${API_BASE}/orders`, {
      product_id: product.id,
      buyer_id: currentUser.value.id,
    });

    alert(
      `✅ 订单创建成功！\n\n` +
        `订单号：${response.data.id}\n` +
        `商品已预定，请联系卖家完成交易\n\n` +
        `💡 提示：在"我的订单"中可以查看订单详情`
    );

    // 关闭详情模态框
    showDetailModal.value = false;

    // 刷新商品列表和用户信息
    await fetchProducts();

    // 更新当前用户信息
    const userResponse = await axios.get(
      `${API_BASE}/users/${currentUser.value.id}`
    );
    currentUser.value = userResponse.data;
    localStorage.setItem("currentUser", JSON.stringify(userResponse.data));
  } catch (error) {
    console.error("购买失败:", error);
    const errorMsg = error.response?.data?.error || error.message;
    alert("❌ 购买失败: " + errorMsg);
  }
};

const fetchStats = async () => {
  try {
    const response = await axios.get(`${API_BASE}/stats`);
    stats.value = response.data;
  } catch (error) {
    console.error("获取统计数据失败:", error);
  }
};

const fetchOrders = async () => {
  if (!currentUser.value) return;
  try {
    const response = await axios.get(`${API_BASE}/orders`, {
      params: { user_id: currentUser.value.id },
    });
    orders.value = response.data;
  } catch (error) {
    console.error("获取订单列表失败:", error);
  }
};

const completeOrder = async (orderId) => {
  if (!confirm("确认完成此订单？交易完成后将自动扣款")) return;

  try {
    await axios.put(`${API_BASE}/orders/${orderId}/complete`);
    alert("✅ 订单已完成！款项已转账");
    await fetchOrders();
    await fetchProducts();

    // 更新用户余额
    const userResponse = await axios.get(
      `${API_BASE}/users/${currentUser.value.id}`
    );
    currentUser.value = userResponse.data;
    localStorage.setItem("currentUser", JSON.stringify(userResponse.data));
  } catch (error) {
    alert("❌ 操作失败: " + (error.response?.data?.error || error.message));
  }
};

const cancelOrder = async (orderId) => {
  if (!confirm("确认取消此订单？")) return;

  try {
    await axios.put(`${API_BASE}/orders/${orderId}/cancel`);
    alert("✅ 订单已取消");
    await fetchOrders();
    await fetchProducts();
  } catch (error) {
    alert("❌ 操作失败: " + (error.response?.data?.error || error.message));
  }
};

// 收藏相关方法
const fetchFavorites = async () => {
  if (!currentUser.value) return;
  try {
    const response = await axios.get(`${API_BASE}/favorites`, {
      params: { user_id: currentUser.value.id },
    });
    favorites.value = response.data;
  } catch (error) {
    console.error("获取收藏列表失败:", error);
  }
};

const toggleFavorite = async (product) => {
  if (!currentUser.value) {
    alert("❌ 请先登录");
    return;
  }

  if (product.seller_id === currentUser.value.id) {
    alert("❌ 不能收藏自己的商品");
    return;
  }

  try {
    // 检查是否已收藏
    const checkResponse = await axios.get(`${API_BASE}/favorites/check`, {
      params: {
        user_id: currentUser.value.id,
        product_id: product.id,
      },
    });

    if (checkResponse.data.is_favorited) {
      // 取消收藏
      await axios.delete(
        `${API_BASE}/favorites/${checkResponse.data.favorite_id}`
      );
      alert("💔 已取消收藏");
    } else {
      // 添加收藏
      await axios.post(`${API_BASE}/favorites`, {
        user_id: currentUser.value.id,
        product_id: product.id,
      });
      alert("❤️ 收藏成功");
    }

    // 刷新收藏列表
    await fetchFavorites();
  } catch (error) {
    const errorMsg = error.response?.data?.error || error.message;
    alert("❌ 操作失败: " + errorMsg);
  }
};

const isFavorited = (productId) => {
  return favorites.value.some((fav) => fav.product_id === productId);
};

// 评价相关方法
const openReviewDialog = (order) => {
  reviewingOrder.value = order;
  reviewForm.value = {
    rating: 5,
    comment: "",
  };
  showReviewModal.value = true;
};

const submitReview = async () => {
  if (!reviewingOrder.value) return;

  try {
    await axios.post(`${API_BASE}/reviews`, {
      product_id: reviewingOrder.value.product_id,
      order_id: reviewingOrder.value.id,
      reviewer_id: currentUser.value.id,
      rating: reviewForm.value.rating,
      comment: reviewForm.value.comment,
    });

    alert("✅ 评价成功！");
    showReviewModal.value = false;
    reviewingOrder.value = null;
    await fetchOrders();
  } catch (error) {
    alert("❌ 评价失败: " + (error.response?.data?.error || error.message));
  }
};

const getOrderStatusText = (status) => {
  const map = {
    pending: "待完成",
    paid: "已支付",
    completed: "已完成",
    cancelled: "已取消",
  };
  return map[status] || status;
};

const getStatusText = (status) => {
  const map = {
    available: "在售",
    reserved: "已预订",
    sold: "已售出",
  };
  return map[status] || status;
};

const getCategoryText = (category) => {
  const map = {
    books: "📚 教材书籍",
    electronics: "💻 电子产品",
    daily: "🏠 生活用品",
    sports: "⚽ 运动器材",
    clothing: "👕 服装配饰",
    other: "📦 其他",
  };
  return map[category] || category;
};

const formatDate = (dateString) => {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleString("zh-CN");
};

// 初始化
onMounted(async () => {
  await fetchUsers();

  // 检查本地存储的登录状态
  const savedUser = localStorage.getItem("currentUser");
  if (savedUser) {
    try {
      const user = JSON.parse(savedUser);
      // 验证用户是否仍然存在于数据库中
      const response = await axios.get(`${API_BASE}/users/${user.id}`);
      if (response.data) {
        currentUser.value = response.data;
        isLoggedIn.value = true;
      } else {
        // 用户不存在，清除本地存储
        localStorage.removeItem("currentUser");
      }
    } catch (error) {
      // 用户不存在或请求失败，清除本地存储
      console.log("用户验证失败，清除登录状态");
      localStorage.removeItem("currentUser");
    }
  }

  await fetchProducts();
  await fetchStats();
  if (currentUser.value) {
    await fetchFavorites();
  }
});
</script>
