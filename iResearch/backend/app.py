#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行业概念研究系统 - Flask 后端主应用
提供 REST API 服务，支持多角色权限控制
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from functools import wraps

import pymysql
import jwt
from flask import Flask, request, jsonify, send_from_directory, abort
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 Flask 应用
app = Flask(__name__)

# 从环境变量读取配置
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
app.config['DB_PORT'] = int(os.getenv('DB_PORT', '3306'))
app.config['DB_USER'] = os.getenv('DB_USER', 'root')
app.config['DB_PASS'] = os.getenv('DB_PASS', '')
app.config['DB_NAME'] = os.getenv('DB_NAME', 'concept_research')
app.config['ADMIN_USER'] = os.getenv('ADMIN_USER', 'admin')
app.config['ADMIN_PASS'] = os.getenv('ADMIN_PASS', 'admin123')
app.config['RECENT_DAYS'] = int(os.getenv('RECENT_DAYS', '7'))

# 开发环境启用 CORS
if os.getenv('FLASK_ENV') == 'development':
    CORS(app, origins="http://localhost:5173", supports_credentials=True)

# 确保上传目录存在
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 全局变量存储数据库连接
db_connection = None

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host=app.config['DB_HOST'],
            port=app.config['DB_PORT'],
            user=app.config['DB_USER'],
            password=app.config['DB_PASS'],
            database=app.config['DB_NAME'],
            charset='utf8mb4',
            autocommit=False
        )
        return connection
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise

def ensure_schema():
    """创建/更新数据库表结构"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 创建公司表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                domain VARCHAR(255),
                website VARCHAR(512),
                address VARCHAR(255),
                team_info TEXT,
                funding_info TEXT,
                field VARCHAR(255),
                product TEXT,
                problem TEXT,
                method TEXT,
                difference TEXT,
                tech_core TEXT,
                biz_model TEXT,
                partners TEXT,
                clients TEXT,
                notes TEXT,
                source_link VARCHAR(512),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_company_name (name)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # 创建分类表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS category (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(128) UNIQUE NOT NULL,
                parent_id BIGINT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES category(id) ON DELETE SET NULL,
                INDEX idx_category_parent (parent_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # 创建概念表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS concept (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                term VARCHAR(128) UNIQUE NOT NULL,
                plain_def TEXT,
                mechanism TEXT,
                examples TEXT,
                image_path VARCHAR(512),
                last_used TIMESTAMP NULL,
                category_id BIGINT NULL,
                FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL,
                INDEX idx_concept_term (term),
                INDEX idx_concept_cat (category_id, last_used)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # 创建公司概念关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS company_concept (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                company_id BIGINT NOT NULL,
                concept_id BIGINT NOT NULL,
                UNIQUE(company_id, concept_id),
                FOREIGN KEY (company_id) REFERENCES company(id) ON DELETE CASCADE,
                FOREIGN KEY (concept_id) REFERENCES concept(id) ON DELETE CASCADE,
                INDEX idx_cc_company (company_id),
                INDEX idx_cc_concept (concept_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # 创建分类概念关联表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS category_concept (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                category_id BIGINT NOT NULL,
                concept_id BIGINT NOT NULL,
                UNIQUE(category_id, concept_id),
                FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE CASCADE,
                FOREIGN KEY (concept_id) REFERENCES concept(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # 创建分类关系表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS category_relation (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                subject_id BIGINT NOT NULL,
                predicate ENUM('broader','narrower','related') NOT NULL,
                object_id BIGINT NOT NULL,
                UNIQUE(subject_id, predicate, object_id),
                FOREIGN KEY (subject_id) REFERENCES category(id) ON DELETE CASCADE,
                FOREIGN KEY (object_id) REFERENCES category(id) ON DELETE CASCADE,
                INDEX idx_cr_subject (subject_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # 创建用户表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('admin','editor','viewer') NOT NULL DEFAULT 'viewer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_user_username (username),
                INDEX idx_user_email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        # 创建全文索引（若不存在）
        try:
            cursor.execute(
                """
                SELECT COUNT(1) 
                FROM information_schema.statistics
                WHERE table_schema = %s 
                  AND table_name = 'concept' 
                  AND index_name = 'ft_concept_term_plain'
                """,
                (app.config['DB_NAME'],)
            )
            exists = cursor.fetchone()[0]
            if not exists:
                cursor.execute(
                    """
                    CREATE FULLTEXT INDEX ft_concept_term_plain 
                    ON concept(term, plain_def, mechanism, examples)
                    """
                )
                logger.info("全文索引创建成功")
            else:
                logger.info("全文索引已存在，跳过创建")
        except Exception as e:
            logger.warning(f"检查/创建全文索引时出错（可能不支持FULLTEXT）: {e}")
        
        conn.commit()
        logger.info("数据库表结构创建/更新完成")
        
        # 检查是否需要创建默认管理员
        cursor.execute("SELECT COUNT(*) FROM user")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            admin_password_hash = generate_password_hash(app.config['ADMIN_PASS'])
            cursor.execute("""
                INSERT INTO user (username, email, password_hash, role) 
                VALUES (%s, %s, %s, 'admin')
            """, (app.config['ADMIN_USER'], 'admin@example.com', admin_password_hash))
            conn.commit()
            logger.info(f"默认管理员账户已创建: {app.config['ADMIN_USER']} / {app.config['ADMIN_PASS']}")
            logger.warning("请在生产环境中修改默认密码！")
        
    except Exception as e:
        conn.rollback()
        logger.error(f"数据库初始化失败: {e}")
        raise
    finally:
        cursor.close()

def generate_token(user):
    """生成 JWT token"""
    payload = {
        'user_id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """验证 JWT token"""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def auth_required(required_role=None):
    """权限验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 检查 Authorization 头
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return jsonify({'error': '缺少认证令牌'}), 401
            
            token = auth_header.split(' ')[1]
            payload = verify_token(token)
            
            if not payload:
                return jsonify({'error': '无效或过期的令牌'}), 401
            
            # 检查角色权限
            if required_role and payload['role'] != required_role:
                if required_role == 'admin' and payload['role'] not in ['admin']:
                    return jsonify({'error': '需要管理员权限'}), 403
                elif required_role == 'editor' and payload['role'] not in ['admin', 'editor']:
                    return jsonify({'error': '需要编辑权限'}), 403
            
            # 将用户信息添加到请求上下文
            request.current_user = payload
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# 身份认证相关路由
@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            token = generate_token(user)
            return jsonify({
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'role': user['role']
                }
            })
        else:
            return jsonify({'error': '用户名或密码不正确'}), 401
    
    except Exception as e:
        logger.error(f"登录错误: {e}")
        return jsonify({'error': '登录失败'}), 500
    finally:
        cursor.close()

@app.route('/api/auth/me', methods=['GET'])
@auth_required()
def get_current_user():
    """获取当前用户信息"""
    return jsonify({
        'id': request.current_user['user_id'],
        'username': request.current_user['username'],
        'role': request.current_user['role']
    })

# 用户管理路由
@app.route('/api/users', methods=['GET'])
@auth_required('admin')
def get_users():
    """获取用户列表"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute("SELECT id, username, email, role, created_at FROM user ORDER BY created_at DESC")
        users = cursor.fetchall()
        
        # 格式化日期
        for user in users:
            if user['created_at']:
                user['created_at'] = user['created_at'].strftime('%Y-%m-%d')
        
        return jsonify({'items': users})
    
    except Exception as e:
        logger.error(f"获取用户列表错误: {e}")
        return jsonify({'error': '获取用户列表失败'}), 500
    finally:
        cursor.close()

@app.route('/api/users', methods=['POST'])
@auth_required('admin')
def create_user():
    """创建新用户"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'viewer')
    
    if not username or not password:
        return jsonify({'error': '用户名和密码不能为空'}), 400
    
    if role not in ['admin', 'editor', 'viewer']:
        return jsonify({'error': '无效的角色'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        password_hash = generate_password_hash(password)
        cursor.execute("""
            INSERT INTO user (username, email, password_hash, role) 
            VALUES (%s, %s, %s, %s)
        """, (username, email, password_hash, role))
        
        user_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({'id': user_id}), 201
    
    except pymysql.IntegrityError as e:
        if 'username' in str(e):
            return jsonify({'error': '用户名已存在'}), 400
        elif 'email' in str(e):
            return jsonify({'error': '邮箱已存在'}), 400
        else:
            return jsonify({'error': '用户创建失败'}), 400
    except Exception as e:
        logger.error(f"创建用户错误: {e}")
        return jsonify({'error': '创建用户失败'}), 500
    finally:
        cursor.close()

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@auth_required('admin')
def update_user(user_id):
    """更新用户信息"""
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if 'password' in data:
            password_hash = generate_password_hash(data['password'])
            updates.append("password_hash = %s")
            params.append(password_hash)
        
        if 'role' in data:
            if data['role'] not in ['admin', 'editor', 'viewer']:
                return jsonify({'error': '无效的角色'}), 400
            updates.append("role = %s")
            params.append(data['role'])
        
        if not updates:
            return jsonify({'error': '没有要更新的字段'}), 400
        
        params.append(user_id)
        sql = f"UPDATE user SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(sql, params)
        
        if cursor.rowcount == 0:
            return jsonify({'error': '用户不存在'}), 404
        
        conn.commit()
        return jsonify({'ok': True})
    
    except Exception as e:
        logger.error(f"更新用户错误: {e}")
        return jsonify({'error': '更新用户失败'}), 500
    finally:
        cursor.close()

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@auth_required('admin')
def delete_user(user_id):
    """删除用户"""
    # 防止删除自己
    if user_id == request.current_user['user_id']:
        return jsonify({'error': '不能删除自己'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("DELETE FROM user WHERE id = %s", (user_id,))
        
        if cursor.rowcount == 0:
            return jsonify({'error': '用户不存在'}), 404
        
        conn.commit()
        return jsonify({'ok': True})
    
    except Exception as e:
        logger.error(f"删除用户错误: {e}")
        return jsonify({'error': '删除用户失败'}), 500
    finally:
        cursor.close()

# 分类相关路由
@app.route('/api/categories/flat', methods=['GET'])
@auth_required()
def get_categories_flat():
    """获取所有分类（平铺）"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute("SELECT id, name, parent_id FROM category ORDER BY name")
        categories = cursor.fetchall()
        return jsonify({'items': categories})
    
    except Exception as e:
        logger.error(f"获取分类列表错误: {e}")
        return jsonify({'error': '获取分类列表失败'}), 500
    finally:
        cursor.close()

@app.route('/api/categories/tree', methods=['GET'])
@auth_required()
def get_categories_tree():
    """获取分类树结构"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取所有分类
        cursor.execute("SELECT id, name, parent_id FROM category ORDER BY name")
        categories = cursor.fetchall()
        
        # 构建分类树
        category_dict = {cat['id']: cat for cat in categories}
        root_categories = []
        
        for cat in categories:
            cat['children'] = []
            if cat['parent_id'] is None:
                root_categories.append(cat)
            else:
                parent = category_dict.get(cat['parent_id'])
                if parent:
                    parent['children'].append(cat)
        
        # 计算每个分类的主分类概念数
        for cat in categories:
            cursor.execute("SELECT COUNT(*) AS cnt FROM concept WHERE category_id = %s", (cat['id'],))
            cat['count_main'] = cursor.fetchone()['cnt']
        
        # 计算统计信息
        cursor.execute("SELECT COUNT(*) AS cnt FROM concept")
        count_all = cursor.fetchone()['cnt']
        
        cursor.execute("SELECT COUNT(*) AS cnt FROM concept WHERE category_id IS NULL")
        count_uncat = cursor.fetchone()['cnt']
        
        recent_days = int(app.config['RECENT_DAYS'])
        cursor.execute(f"SELECT COUNT(*) AS cnt FROM concept WHERE last_used >= NOW() - INTERVAL {recent_days} DAY")
        count_recent = cursor.fetchone()['cnt']
        
        return jsonify({
            'tree': root_categories,
            'count_all': count_all,
            'count_uncat': count_uncat,
            'count_recent': count_recent
        })
    
    except Exception as e:
        logger.error(f"获取分类树错误: {e}")
        return jsonify({'error': '获取分类树失败'}), 500
    finally:
        cursor.close()

@app.route('/api/category', methods=['POST'])
@auth_required('editor')
def create_category():
    """创建新分类"""
    data = request.get_json()
    name = data.get('name')
    parent_id = data.get('parent_id')
    
    if not name:
        return jsonify({'error': '分类名称不能为空'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("INSERT INTO category (name, parent_id) VALUES (%s, %s)", (name, parent_id))
        category_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({'id': category_id, 'name': name, 'parent_id': parent_id}), 201
    
    except pymysql.IntegrityError:
        return jsonify({'error': '分类名称已存在'}), 400
    except Exception as e:
        logger.error(f"创建分类错误: {e}")
        return jsonify({'error': '创建分类失败'}), 500
    finally:
        cursor.close()

@app.route('/api/category/<int:category_id>', methods=['GET'])
@auth_required('editor')
def get_category(category_id):
    """获取分类详情"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        cursor.execute("SELECT * FROM category WHERE id = %s", (category_id,))
        category = cursor.fetchone()
        
        if not category:
            return jsonify({'error': '分类不存在'}), 404
        
        return jsonify(category)
    
    except Exception as e:
        logger.error(f"获取分类详情错误: {e}")
        return jsonify({'error': '获取分类详情失败'}), 500
    finally:
        cursor.close()

@app.route('/api/category/<int:category_id>', methods=['PUT'])
@auth_required('editor')
def update_category(category_id):
    """更新分类"""
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if 'name' in data:
            updates.append("name = %s")
            params.append(data['name'])
        
        if 'parent_id' in data:
            updates.append("parent_id = %s")
            params.append(data['parent_id'])
        
        if not updates:
            return jsonify({'error': '没有要更新的字段'}), 400
        
        params.append(category_id)
        sql = f"UPDATE category SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(sql, params)
        
        if cursor.rowcount == 0:
            return jsonify({'error': '分类不存在'}), 404
        
        conn.commit()
        return jsonify({'ok': True})
    
    except pymysql.IntegrityError:
        return jsonify({'error': '分类名称已存在'}), 400
    except Exception as e:
        logger.error(f"更新分类错误: {e}")
        return jsonify({'error': '更新分类失败'}), 500
    finally:
        cursor.close()

@app.route('/api/category/<int:category_id>', methods=['DELETE'])
@auth_required('admin')
def delete_category(category_id):
    """删除分类"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查是否有关联的概念
        cursor.execute("SELECT COUNT(*) FROM concept WHERE category_id = %s", (category_id,))
        main_concepts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM category_concept WHERE category_id = %s", (category_id,))
        extra_concepts = cursor.fetchone()[0]
        
        if main_concepts > 0 or extra_concepts > 0:
            return jsonify({'error': '分类下还有概念，无法删除'}), 400
        
        cursor.execute("DELETE FROM category WHERE id = %s", (category_id,))
        
        if cursor.rowcount == 0:
            return jsonify({'error': '分类不存在'}), 404
        
        conn.commit()
        return jsonify({'ok': True})
    
    except Exception as e:
        logger.error(f"删除分类错误: {e}")
        return jsonify({'error': '删除分类失败'}), 500
    finally:
        cursor.close()

# 概念相关路由
@app.route('/api/concepts', methods=['GET'])
@auth_required()
def get_concepts():
    """查询概念列表"""
    # 获取查询参数
    q = request.args.get('q', '')
    cat_id = request.args.get('cat_id')
    sort = request.args.get('sort', 'term')
    page = int(request.args.get('page', 1))
    page_size = min(int(request.args.get('page_size', 50)), 200)
    use_ft = request.args.get('use_ft', '0') == '1'
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 构建查询条件
        where_conditions = []
        params = []
        
        # 关键词搜索
        if q:
            if use_ft:
                # 全文搜索
                words = q.split()
                ft_query = ' '.join([f'+{word}*' for word in words])
                where_conditions.append(f"MATCH(term, plain_def, mechanism, examples) AGAINST (%s IN BOOLEAN MODE)")
                params.append(ft_query)
            else:
                # LIKE 搜索
                search_term = f"%{q}%"
                where_conditions.append("(term LIKE %s OR plain_def LIKE %s OR mechanism LIKE %s OR examples LIKE %s)")
                params.extend([search_term, search_term, search_term, search_term])
        
        # 分类筛选
        if cat_id:
            if cat_id == '-1':  # 未分类
                where_conditions.append("category_id IS NULL")
            elif cat_id == '-2':  # 最近使用
                recent_days = int(app.config['RECENT_DAYS'])
                where_conditions.append(f"last_used >= NOW() - INTERVAL {recent_days} DAY")
            else:
                # 具体分类（包括主分类和附加分类）
                where_conditions.append("""
                    (category_id = %s OR id IN (
                        SELECT concept_id FROM category_concept WHERE category_id = %s
                    ))
                """)
                params.extend([cat_id, cat_id])
        
        # 构建 WHERE 子句
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # 排序
        order_clause = ""
        if sort == 'last_used':
            order_clause = "ORDER BY (last_used IS NULL) ASC, last_used DESC, term ASC"
        else:
            order_clause = "ORDER BY term ASC"
        
        # 分页
        offset = (page - 1) * page_size
        
        # 查询数据
        sql = f"""
            SELECT c.id, c.term, c.plain_def, c.mechanism, c.examples, 
                   c.category_id, cat.name as category, c.last_used
            FROM concept c
            LEFT JOIN category cat ON c.category_id = cat.id
            {where_clause}
            {order_clause}
            LIMIT %s OFFSET %s
        """
        
        params.extend([page_size, offset])
        cursor.execute(sql, params)
        concepts = cursor.fetchall()
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) AS cnt FROM concept c {where_clause}"
        cursor.execute(count_sql, params[:-2])  # 去掉 LIMIT 和 OFFSET 参数
        total = cursor.fetchone()['cnt']
        
        # 格式化日期
        for concept in concepts:
            if concept['last_used']:
                concept['last_used'] = concept['last_used'].strftime('%Y-%m-%d')
            else:
                concept['last_used'] = None
        
        return jsonify({
            'items': concepts,
            'total': total,
            'page': page,
            'page_size': page_size
        })
    
    except Exception as e:
        logger.error(f"查询概念列表错误: {e}")
        return jsonify({'error': '查询概念列表失败'}), 500
    finally:
        cursor.close()

@app.route('/api/concept/<int:concept_id>', methods=['GET'])
@auth_required()
def get_concept(concept_id):
    """获取单个概念详情"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取概念基本信息
        cursor.execute("""
            SELECT c.*, cat.name as category
            FROM concept c
            LEFT JOIN category cat ON c.category_id = cat.id
            WHERE c.id = %s
        """, (concept_id,))
        concept = cursor.fetchone()
        
        if not concept:
            return jsonify({'error': '概念不存在'}), 404
        
        # 获取附加分类
        cursor.execute("""
            SELECT cat.id, cat.name
            FROM category_concept cc
            JOIN category cat ON cc.category_id = cat.id
            WHERE cc.concept_id = %s
        """, (concept_id,))
        extra_categories = cursor.fetchall()
        
        # 格式化日期
        if concept['last_used']:
            concept['last_used'] = concept['last_used'].strftime('%Y-%m-%d')
        
        concept['extra_categories'] = extra_categories
        
        return jsonify(concept)
    
    except Exception as e:
        logger.error(f"获取概念详情错误: {e}")
        return jsonify({'error': '获取概念详情失败'}), 500
    finally:
        cursor.close()

@app.route('/api/concept', methods=['POST'])
@auth_required('editor')
def create_concept():
    """新建概念"""
    data = request.get_json()
    term = data.get('term')
    plain_def = data.get('plain_def', '')
    mechanism = data.get('mechanism', '')
    examples = data.get('examples', '')
    category_id = data.get('category_id')
    
    if not term:
        return jsonify({'error': '概念术语不能为空'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO concept (term, plain_def, mechanism, examples, category_id) 
            VALUES (%s, %s, %s, %s, %s)
        """, (term, plain_def, mechanism, examples, category_id))
        
        concept_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({'id': concept_id}), 201
    
    except pymysql.IntegrityError:
        return jsonify({'error': '概念术语已存在'}), 400
    except Exception as e:
        logger.error(f"创建概念错误: {e}")
        return jsonify({'error': '创建概念失败'}), 500
    finally:
        cursor.close()

@app.route('/api/concept/<int:concept_id>', methods=['PUT'])
@auth_required('editor')
def update_concept(concept_id):
    """更新概念"""
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        if 'term' in data:
            updates.append("term = %s")
            params.append(data['term'])
        
        if 'plain_def' in data:
            updates.append("plain_def = %s")
            params.append(data['plain_def'])
        
        if 'mechanism' in data:
            updates.append("mechanism = %s")
            params.append(data['mechanism'])
        
        if 'examples' in data:
            updates.append("examples = %s")
            params.append(data['examples'])
        
        if 'category_id' in data:
            updates.append("category_id = %s")
            params.append(data['category_id'])
        
        if 'last_used' in data and data['last_used']:
            updates.append("last_used = NOW()")
        
        if not updates:
            return jsonify({'error': '没有要更新的字段'}), 400
        
        params.append(concept_id)
        sql = f"UPDATE concept SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(sql, params)
        
        if cursor.rowcount == 0:
            return jsonify({'error': '概念不存在'}), 404
        
        # 处理附加分类
        if 'extra_categories' in data:
            # 删除现有附加分类
            cursor.execute("DELETE FROM category_concept WHERE concept_id = %s", (concept_id,))
            
            # 添加新的附加分类
            for cat_id in data['extra_categories']:
                cursor.execute("""
                    INSERT INTO category_concept (category_id, concept_id) 
                    VALUES (%s, %s)
                """, (cat_id, concept_id))
        
        conn.commit()
        return jsonify({'ok': True})
    
    except pymysql.IntegrityError:
        return jsonify({'error': '概念术语已存在'}), 400
    except Exception as e:
        logger.error(f"更新概念错误: {e}")
        return jsonify({'error': '更新概念失败'}), 500
    finally:
        cursor.close()

@app.route('/api/concept/<int:concept_id>/quick_update', methods=['POST'])
@auth_required('editor')
def quick_update_concept(concept_id):
    """快速更新概念"""
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if data.get('last_used') and len(data) == 1:
            # 仅更新 last_used
            cursor.execute("UPDATE concept SET last_used = NOW() WHERE id = %s", (concept_id,))
        else:
            # 更新其他字段
            updates = []
            params = []
            
            for field in ['term', 'plain_def', 'mechanism', 'examples', 'category_id']:
                if field in data:
                    updates.append(f"{field} = %s")
                    params.append(data[field])
            
            if updates:
                params.append(concept_id)
                sql = f"UPDATE concept SET {', '.join(updates)} WHERE id = %s"
                cursor.execute(sql, params)
        
        if cursor.rowcount == 0:
            return jsonify({'error': '概念不存在'}), 404
        
        conn.commit()
        return jsonify({'ok': True})
    
    except Exception as e:
        logger.error(f"快速更新概念错误: {e}")
        return jsonify({'error': '快速更新概念失败'}), 500
    finally:
        cursor.close()

@app.route('/api/concept/<int:concept_id>/move', methods=['POST'])
@auth_required('editor')
def move_concept(concept_id):
    """移动概念主分类"""
    data = request.get_json()
    category_id = data.get('category_id')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("UPDATE concept SET category_id = %s WHERE id = %s", (category_id, concept_id))
        
        if cursor.rowcount == 0:
            return jsonify({'error': '概念不存在'}), 404
        
        conn.commit()
        return jsonify({'ok': True})
    
    except Exception as e:
        logger.error(f"移动概念错误: {e}")
        return jsonify({'error': '移动概念失败'}), 500
    finally:
        cursor.close()

@app.route('/api/concepts/bulk', methods=['POST'])
@auth_required('editor')
def bulk_concepts():
    """批量操作概念"""
    data = request.get_json()
    concept_ids = data.get('ids', [])
    operation = data.get('op')
    payload = data.get('payload', {})
    
    if not concept_ids:
        return jsonify({'error': '请选择要操作的概念'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if operation == 'move':
            category_id = payload.get('category_id')
            cursor.execute("""
                UPDATE concept SET category_id = %s 
                WHERE id IN ({})
            """.format(','.join(['%s'] * len(concept_ids))), 
            [category_id] + concept_ids)
            
            conn.commit()
            return jsonify({'ok': True})
        
        elif operation == 'delete':
            # 删除关联
            cursor.execute("""
                DELETE FROM company_concept 
                WHERE concept_id IN ({})
            """.format(','.join(['%s'] * len(concept_ids))), concept_ids)
            
            cursor.execute("""
                DELETE FROM category_concept 
                WHERE concept_id IN ({})
            """.format(','.join(['%s'] * len(concept_ids))), concept_ids)
            
            # 删除概念
            cursor.execute("""
                DELETE FROM concept 
                WHERE id IN ({})
            """.format(','.join(['%s'] * len(concept_ids))), concept_ids)
            
            deleted_count = cursor.rowcount
            conn.commit()
            return jsonify({'ok': True, 'deleted': deleted_count})
        
        else:
            return jsonify({'error': '不支持的操作'}), 400
    
    except Exception as e:
        logger.error(f"批量操作概念错误: {e}")
        return jsonify({'error': '批量操作失败'}), 500
    finally:
        cursor.close()

@app.route('/api/concept/<int:concept_id>/image', methods=['POST'])
@auth_required('editor')
def upload_concept_image(concept_id):
    """上传概念图片"""
    if 'image' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    # 检查文件类型
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if not ('.' in file.filename and 
            file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({'error': '只支持 PNG, JPG, JPEG, GIF 格式'}), 400
    
    # 生成安全文件名
    filename = secure_filename(file.filename)
    filename = f"{concept_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        file.save(filepath)
        
        # 更新数据库
        conn = get_db_connection()
        cursor = conn.cursor()
        relative_path = f"uploads/{filename}"
        cursor.execute("UPDATE concept SET image_path = %s WHERE id = %s", (relative_path, concept_id))
        conn.commit()
        
        return jsonify({'ok': True, 'image_path': relative_path})
    
    except Exception as e:
        logger.error(f"上传图片错误: {e}")
        return jsonify({'error': '上传图片失败'}), 500

# 公司相关路由
@app.route('/api/companies', methods=['GET'])
@auth_required()
def get_companies():
    """查询公司列表"""
    q = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    page_size = min(int(request.args.get('page_size', 50)), 200)
    
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        where_conditions = []
        params = []
        
        if q:
            where_conditions.append("(name LIKE %s OR field LIKE %s)")
            search_term = f"%{q}%"
            params.extend([search_term, search_term])
        
        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)
        
        offset = (page - 1) * page_size
        
        sql = f"""
            SELECT id, name, field, created_at
            FROM company
            {where_clause}
            ORDER BY name ASC
            LIMIT %s OFFSET %s
        """
        
        params.extend([page_size, offset])
        cursor.execute(sql, params)
        companies = cursor.fetchall()
        
        # 查询总数
        count_sql = f"SELECT COUNT(*) FROM company {where_clause}"
        cursor.execute(count_sql, params[:-2])
        total = cursor.fetchone()['COUNT(*)']
        
        # 格式化日期
        for company in companies:
            if company['created_at']:
                company['created_at'] = company['created_at'].strftime('%Y-%m-%d')
        
        return jsonify({
            'items': companies,
            'total': total,
            'page': page,
            'page_size': page_size
        })
    
    except Exception as e:
        logger.error(f"查询公司列表错误: {e}")
        return jsonify({'error': '查询公司列表失败'}), 500
    finally:
        cursor.close()

@app.route('/api/company/<int:company_id>', methods=['GET'])
@auth_required()
def get_company(company_id):
    """获取公司详情"""
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    try:
        # 获取公司基本信息
        cursor.execute("SELECT * FROM company WHERE id = %s", (company_id,))
        company = cursor.fetchone()
        
        if not company:
            return jsonify({'error': '公司不存在'}), 404
        
        # 获取关联概念
        cursor.execute("""
            SELECT c.id, c.term, c.plain_def
            FROM concept c
            JOIN company_concept cc ON c.id = cc.concept_id
            WHERE cc.company_id = %s
            ORDER BY c.term
        """, (company_id,))
        concepts = cursor.fetchall()
        
        company['concepts'] = concepts
        
        # 格式化日期
        if company['created_at']:
            company['created_at'] = company['created_at'].strftime('%Y-%m-%d')
        
        return jsonify(company)
    
    except Exception as e:
        logger.error(f"获取公司详情错误: {e}")
        return jsonify({'error': '获取公司详情失败'}), 500
    finally:
        cursor.close()

@app.route('/api/company', methods=['POST'])
@auth_required('editor')
def create_company():
    """新建公司"""
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO company (name, domain, website, address, team_info, funding_info, 
                               field, product, problem, method, difference, tech_core, 
                               biz_model, partners, clients, notes, source_link) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get('name'), data.get('domain'), data.get('website'), data.get('address'),
            data.get('team_info'), data.get('funding_info'), data.get('field'), data.get('product'),
            data.get('problem'), data.get('method'), data.get('difference'), data.get('tech_core'),
            data.get('biz_model'), data.get('partners'), data.get('clients'), data.get('notes'),
            data.get('source_link')
        ))
        
        company_id = cursor.lastrowid
        conn.commit()
        
        return jsonify({'id': company_id}), 201
    
    except pymysql.IntegrityError:
        return jsonify({'error': '公司名称已存在'}), 400
    except Exception as e:
        logger.error(f"创建公司错误: {e}")
        return jsonify({'error': '创建公司失败'}), 500
    finally:
        cursor.close()

@app.route('/api/company/<int:company_id>', methods=['PUT'])
@auth_required('editor')
def update_company(company_id):
    print("update_company() 被调用, company_id =", company_id)

    """更新公司"""
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        updates = []
        params = []
        
        fields = ['name', 'domain', 'website', 'address', 'team_info', 'funding_info',
                 'field', 'product', 'problem', 'method', 'difference', 'tech_core',
                 'biz_model', 'partners', 'clients', 'notes', 'source_link']
        
        for field in fields:
            if field in data:
                updates.append(f"{field} = %s")
                params.append(data[field])
        
        if not updates:
            return jsonify({'error': '没有要更新的字段'}), 400
        
        params.append(company_id)
        sql = f"UPDATE company SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(sql, params)
        
        if cursor.rowcount == 0:
            return jsonify({'error': '公司不存在'}), 404
        
        conn.commit()
        return jsonify({'ok': True})
    
    except pymysql.IntegrityError:
        return jsonify({'error': '公司名称已存在'}), 400
    except Exception as e:
        logger.error(f"更新公司错误: {e}")
        return jsonify({'error': '更新公司失败'}), 500
    finally:
        cursor.close()

@app.route('/api/company/<int:company_id>', methods=['DELETE'])
@auth_required('editor')
def delete_company(company_id):
    """删除公司"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 删除关联
        cursor.execute("DELETE FROM company_concept WHERE company_id = %s", (company_id,))
        
        # 删除公司
        cursor.execute("DELETE FROM company WHERE id = %s", (company_id,))
        
        if cursor.rowcount == 0:
            return jsonify({'error': '公司不存在'}), 404
        
        conn.commit()
        return jsonify({'ok': True})
    
    except Exception as e:
        logger.error(f"删除公司错误: {e}")
        return jsonify({'error': '删除公司失败'}), 500
    finally:
        cursor.close()

@app.route('/api/companies/bulk', methods=['POST'])
@auth_required('editor')
def bulk_companies():
    """批量删除公司"""
    data = request.get_json()
    company_ids = data.get('ids', [])
    operation = data.get('op')
    
    if not company_ids:
        return jsonify({'error': '请选择要操作的公司'}), 400
    
    if operation != 'delete':
        return jsonify({'error': '不支持的操作'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 删除关联
        cursor.execute("""
            DELETE FROM company_concept 
            WHERE company_id IN ({})
        """.format(','.join(['%s'] * len(company_ids))), company_ids)
        
        # 删除公司
        cursor.execute("""
            DELETE FROM company 
            WHERE id IN ({})
        """.format(','.join(['%s'] * len(company_ids))), company_ids)
        
        deleted_count = cursor.rowcount
        conn.commit()
        return jsonify({'ok': True, 'deleted': deleted_count})
    
    except Exception as e:
        logger.error(f"批量删除公司错误: {e}")
        return jsonify({'error': '批量删除失败'}), 500
    finally:
        cursor.close()

@app.route('/api/company/<int:company_id>/concepts', methods=['POST'])
@auth_required('editor')
def add_company_concept(company_id):
    """添加公司概念关联"""
    data = request.get_json()
    term = data.get('term')
    
    if not term:
        return jsonify({'error': '概念术语不能为空'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 查找或创建概念
        cursor.execute("SELECT id FROM concept WHERE term = %s", (term,))
        concept = cursor.fetchone()
        
        if not concept:
            # 创建新概念
            cursor.execute("INSERT INTO concept (term) VALUES (%s)", (term,))
            concept_id = cursor.lastrowid
        else:
            concept_id = concept[0]
        
        # 建立关联
        cursor.execute("""
            INSERT INTO company_concept (company_id, concept_id) 
            VALUES (%s, %s)
        """, (company_id, concept_id))
        
        conn.commit()
        return jsonify({'ok': True, 'concept_id': concept_id})
    
    except pymysql.IntegrityError:
        return jsonify({'error': '关联已存在'}), 400
    except Exception as e:
        logger.error(f"添加公司概念关联错误: {e}")
        return jsonify({'error': '添加关联失败'}), 500
    finally:
        cursor.close()

@app.route('/api/company/<int:company_id>/concepts/<int:concept_id>', methods=['DELETE'])
@auth_required('editor')
def remove_company_concept(company_id, concept_id):
    """移除公司概念关联"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            DELETE FROM company_concept 
            WHERE company_id = %s AND concept_id = %s
        """, (company_id, concept_id))
        
        if cursor.rowcount == 0:
            return jsonify({'error': '关联不存在'}), 404
        
        conn.commit()
        return jsonify({'ok': True})
    
    except Exception as e:
        logger.error(f"移除公司概念关联错误: {e}")
        return jsonify({'error': '移除关联失败'}), 500
    finally:
        cursor.close()

# 上传JSON路由
@app.route('/api/upload', methods=['POST'])
@auth_required('admin')
def upload_json():
    """批量导入JSON数据"""
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400
    
    if not file.filename.endswith('.json'):
        return jsonify({'error': '只支持JSON格式文件'}), 400
    
    try:
        import json
        # 读取文件内容并解析JSON
        file_content = file.read().decode('utf-8')
        data = json.loads(file_content)
        
        if not isinstance(data, list):
            return jsonify({'error': 'JSON格式错误，应为数组'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            companies_added = 0
            concepts_added = 0
            errors = []
            
            for i, company_data in enumerate(data):
                try:
                    # 创建或更新公司
                    company_name = company_data.get('company_name')
                    if not company_name:
                        errors.append(f"第{i+1}条记录缺少公司名称")
                        continue
                    
                    cursor.execute("SELECT id FROM company WHERE name = %s", (company_name,))
                    existing_company = cursor.fetchone()
                    
                    if existing_company:
                        company_id = existing_company[0]
                    else:
                        cursor.execute("""
                            INSERT INTO company (name, website, address, team_info, funding_info,
                                               product, biz_model, partners, clients, field, 
                                               notes, source_link) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            company_name,
                            company_data.get('website'),
                            company_data.get('address'),
                            company_data.get('team_info'),
                            company_data.get('funding_info'),
                            company_data.get('product_service'),
                            company_data.get('biz_model'),
                            company_data.get('partners'),
                            company_data.get('clients'),
                            company_data.get('field'),
                            company_data.get('detail'),
                            company_data.get('source')
                        ))
                        company_id = cursor.lastrowid
                        companies_added += 1
                    
                    # 处理概念
                    explain = company_data.get('explain', {})
                    if isinstance(explain, dict):
                        for term, definition in explain.items():
                            if not term:
                                continue
                            
                            # 查找或创建概念
                            cursor.execute("SELECT id FROM concept WHERE term = %s", (term,))
                            concept = cursor.fetchone()
                            
                            if not concept:
                                cursor.execute("""
                                    INSERT INTO concept (term, plain_def) VALUES (%s, %s)
                                """, (term, definition or ''))
                                concept_id = cursor.lastrowid
                                concepts_added += 1
                            else:
                                concept_id = concept[0]
                            
                            # 建立关联
                            try:
                                cursor.execute("""
                                    INSERT INTO company_concept (company_id, concept_id) 
                                    VALUES (%s, %s)
                                """, (company_id, concept_id))
                            except pymysql.IntegrityError:
                                pass  # 关联已存在，忽略
                
                except Exception as e:
                    errors.append(f"第{i+1}条记录处理失败: {str(e)}")
            
            conn.commit()
            
            return jsonify({
                'ok': True,
                'companies_added': companies_added,
                'concepts_added': concepts_added,
                'errors': errors
            })
        
        finally:
            cursor.close()
            conn.close()
    
    except json.JSONDecodeError:
        return jsonify({'error': 'JSON格式错误'}), 400
    except Exception as e:
        logger.error(f"上传JSON错误: {e}")
        return jsonify({'error': '上传处理失败'}), 500

# 静态文件服务
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传文件访问"""
    return send_from_directory(UPLOAD_FOLDER, filename)

# SPA 路由支持
@app.route('/<path:path>')
def catch_all(path):
    """捕获所有未匹配的路由，返回前端入口"""
    if path.startswith('api/'):
        abort(404)
    return send_from_directory('static', 'index.html')

@app.route('/')
def index():
    """首页"""
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    # 初始化数据库
    ensure_schema()
    
    # 启动应用
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
