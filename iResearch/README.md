# 行业概念研究系统

一个基于 Flask + Vue3 的前后端分离的行业概念研究系统，支持多角色权限控制、概念管理、公司关联等功能。

## 功能特性

- **多角色权限控制**：支持管理员、编辑、浏览者三种角色
- **知识库管理**：三栏布局的概念浏览、搜索、编辑界面
- **公司管理**：公司信息管理和概念关联
- **分类体系**：支持多级分类和分类关系管理
- **数据导入导出**：支持JSON批量导入和CSV导出
- **用户管理**：完整的用户账户管理系统

## 技术栈

### 后端
- Python 3.10+
- Flask 2.3.3
- PyMySQL 1.1.0
- PyJWT 2.8.0
- MySQL 5.7+/8.0

### 前端
- Vue 3.3.4
- Vue Router 4.2.4
- Axios 1.5.0
- Bootstrap 5.3.0
- Vite 4.4.9

## 快速开始

### 1. 环境准备

确保已安装以下软件：
- Python 3.10+
- Node.js 16+
- MySQL 5.7+

### 2. 数据库配置

创建MySQL数据库：
```sql
CREATE DATABASE concept_research CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. 后端配置

进入后端目录：
```bash
cd backend
```

安装依赖：
```bash
pip install -r requirements.txt
```

配置环境变量（复制并修改）：
```bash
cp env.example .env
```

编辑 `.env` 文件：
```env
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASS=your_password
DB_NAME=concept_research

# 应用配置
SECRET_KEY=your-secret-key-change-in-production
FLASK_ENV=development

# 管理员账户
ADMIN_USER=admin
ADMIN_PASS=admin123

# 最近使用天数
RECENT_DAYS=7
```

启动后端服务：
```bash
python app.py
```

后端服务将在 `http://localhost:5000` 启动。

### 4. 前端配置

进入前端目录：
```bash
cd frontend
```

安装依赖：
```bash
npm install
```

启动开发服务器：
```bash
npm run dev
```

前端服务将在 `http://localhost:5173` 启动。

### 5. 生产部署

构建前端：
```bash
npm run build
```

构建后的文件会自动复制到 `backend/static` 目录。

启动生产环境：
```bash
cd backend
FLASK_ENV=production python app.py
```

## 默认账户

系统首次启动时会自动创建默认管理员账户：
- 用户名：admin
- 密码：admin123

**重要**：请在生产环境中立即修改默认密码！

## 角色权限

### 管理员 (admin)
- 拥有所有功能权限
- 可以管理用户账户
- 可以上传JSON数据
- 可以删除分类

### 编辑 (editor)
- 可以增删改概念、公司、分类
- 可以导出数据
- 不能管理用户账户
- 不能上传JSON数据

### 浏览者 (viewer)
- 只能查看和搜索数据
- 可以导出选中的公司数据
- 不能进行任何修改操作

## API文档

### 认证接口
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 用户管理
- `GET /api/users` - 获取用户列表（管理员）
- `POST /api/users` - 创建用户（管理员）
- `PUT /api/users/<id>` - 更新用户（管理员）
- `DELETE /api/users/<id>` - 删除用户（管理员）

### 概念管理
- `GET /api/concepts` - 查询概念列表
- `GET /api/concept/<id>` - 获取概念详情
- `POST /api/concept` - 新建概念（编辑+）
- `PUT /api/concept/<id>` - 更新概念（编辑+）
- `POST /api/concept/<id>/quick_update` - 快速更新概念（编辑+）
- `POST /api/concept/<id>/move` - 移动概念主分类（编辑+）
- `POST /api/concepts/bulk` - 批量操作概念（编辑+）
- `POST /api/concept/<id>/image` - 上传概念图片（编辑+）

### 公司管理
- `GET /api/companies` - 查询公司列表
- `GET /api/company/<id>` - 获取公司详情
- `POST /api/company` - 新建公司（编辑+）
- `PUT /api/company/<id>` - 更新公司（编辑+）
- `DELETE /api/company/<id>` - 删除公司（编辑+）
- `POST /api/companies/bulk` - 批量删除公司（编辑+）
- `POST /api/company/<id>/concepts` - 添加公司概念关联（编辑+）
- `DELETE /api/company/<id>/concepts/<concept_id>` - 移除公司概念关联（编辑+）

### 分类管理
- `GET /api/categories/flat` - 获取所有分类（平铺）
- `GET /api/categories/tree` - 获取分类树结构
- `POST /api/category` - 创建新分类（编辑+）
- `PUT /api/category/<id>` - 更新分类（编辑+）
- `DELETE /api/category/<id>` - 删除分类（管理员）
- `GET /api/category/<id>/concepts` - 获取分类关联概念列表（编辑+）
- `POST /api/category/<id>/concepts` - 添加概念到分类（编辑+）
- `DELETE /api/category/<cid>/concepts/<concept_id>` - 移除概念关联（编辑+）
- `GET /api/category/<id>/relations` - 获取分类关系列表（编辑+）
- `POST /api/category/<id>/relations` - 添加分类关系（编辑+）
- `DELETE /api/category_relation/<relation_id>` - 删除分类关系（编辑+）

### 数据导入
- `POST /api/upload` - 批量导入JSON数据（管理员）

## 数据库结构

### 主要表
- `user` - 用户表
- `company` - 公司表
- `concept` - 概念表
- `category` - 分类表
- `company_concept` - 公司概念关联表
- `category_concept` - 分类概念关联表
- `category_relation` - 分类关系表

详细表结构请参考 `backend/app.py` 中的 `ensure_schema()` 函数。

## 开发说明

### 后端开发
- 使用 Flask Blueprint 组织路由（当前版本在单个文件中）
- JWT 认证，24小时过期
- 支持 CORS（开发环境）
- 自动创建数据库表结构

### 前端开发
- Vue 3 Composition API
- Vue Router 路由守卫
- Axios 请求拦截器
- Bootstrap 5 样式框架

### 部署注意事项
1. 修改默认管理员密码
2. 设置强密码的 SECRET_KEY
3. 配置生产环境数据库
4. 关闭 CORS 或限制允许的域名
5. 使用 HTTPS 保护 JWT 传输

## 常见问题

### Q: 如何重置管理员密码？
A: 可以通过数据库直接修改，或删除用户表让系统重新创建默认账户。

### Q: 如何备份数据？
A: 直接备份 MySQL 数据库即可，所有数据都存储在数据库中。

### Q: 如何添加新的角色权限？
A: 修改后端权限检查逻辑和前端路由守卫，添加新的角色判断。

### Q: 如何自定义分类层级？
A: 通过分类管理界面可以创建多级分类，支持无限层级。

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request。
