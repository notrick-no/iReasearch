@echo off
REM 行业概念研究系统启动脚本 (Windows)

echo === 行业概念研究系统启动脚本 ===
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

REM 检查Node.js是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Node.js，请先安装Node.js 16+
    pause
    exit /b 1
)

echo 1. 检查后端依赖...
cd backend
if not exist "requirements.txt" (
    echo 错误: 未找到requirements.txt文件
    pause
    exit /b 1
)

echo 安装Python依赖...
pip install -r requirements.txt

if not exist ".env" (
    echo 警告: 未找到.env文件，请复制env.example并配置数据库连接
    echo copy env.example .env
    echo 然后编辑.env文件设置数据库连接信息
)

echo.
echo 2. 检查前端依赖...
cd ..\frontend
if not exist "package.json" (
    echo 错误: 未找到package.json文件
    pause
    exit /b 1
)

echo 安装Node.js依赖...
npm install

echo.
echo 3. 启动服务...
echo.

REM 启动后端
echo 启动后端服务 (端口5000)...
cd ..\backend
start "后端服务" python app.py

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端
echo 启动前端服务 (端口5173)...
cd ..\frontend
start "前端服务" npm run dev

echo.
echo === 服务启动完成 ===
echo 后端服务: http://localhost:5000
echo 前端服务: http://localhost:5173
echo.
echo 默认管理员账户:
echo 用户名: admin
echo 密码: admin123
echo.
echo 按任意键退出...
pause >nul
