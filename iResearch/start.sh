#!/bin/bash

# 行业概念研究系统启动脚本

echo "=== 行业概念研究系统启动脚本 ==="
echo ""

# 检查Python和Node.js是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python 3.10+"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "错误: 未找到Node.js，请先安装Node.js 16+"
    exit 1
fi

# 检查MySQL是否运行
if ! command -v mysql &> /dev/null; then
    echo "警告: 未找到MySQL客户端，请确保MySQL服务正在运行"
fi

echo "1. 检查后端依赖..."
cd backend
if [ ! -f "requirements.txt" ]; then
    echo "错误: 未找到requirements.txt文件"
    exit 1
fi

echo "安装Python依赖..."
pip3 install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "警告: 未找到.env文件，请复制env.example并配置数据库连接"
    echo "cp env.example .env"
    echo "然后编辑.env文件设置数据库连接信息"
fi

echo ""
echo "2. 检查前端依赖..."
cd ../frontend
if [ ! -f "package.json" ]; then
    echo "错误: 未找到package.json文件"
    exit 1
fi

echo "安装Node.js依赖..."
npm install

echo ""
echo "3. 启动服务..."
echo ""

# 启动后端
echo "启动后端服务 (端口5000)..."
cd ../backend
python3 app.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "启动前端服务 (端口5173)..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=== 服务启动完成 ==="
echo "后端服务: http://localhost:5000"
echo "前端服务: http://localhost:5173"
echo ""
echo "默认管理员账户:"
echo "用户名: admin"
echo "密码: admin123"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
