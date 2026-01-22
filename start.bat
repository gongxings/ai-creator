@echo off
chcp 65001 >nul
REM AI创作者平台启动脚本 (Windows)

echo 🚀 启动AI创作者平台...
echo.

REM 检查Docker是否安装
docker --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未安装Docker，请先安装Docker Desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未安装Docker Compose，请先安装Docker Desktop
    pause
    exit /b 1
)

REM 检查.env文件
if not exist .env (
    echo 📝 创建.env配置文件...
    copy .env.example .env
    echo ⚠️  请编辑.env文件，配置必要的参数（如数据库密码、API密钥等）
    echo    配置完成后，请重新运行此脚本
    pause
    exit /b 0
)

REM 构建并启动服务
echo 🔨 构建Docker镜像...
docker-compose build

echo 🚀 启动服务...
docker-compose up -d

REM 等待服务启动
echo ⏳ 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo 📊 检查服务状态...
docker-compose ps

REM 初始化数据库
echo 🗄️  初始化数据库...
docker-compose exec backend python scripts/init_db.py

echo.
echo ✅ AI创作者平台启动成功！
echo.
echo 📝 访问地址：
echo    前端: http://localhost
echo    后端API: http://localhost:8000
echo    API文档: http://localhost:8000/docs
echo.
echo 📋 常用命令：
echo    查看日志: docker-compose logs -f
echo    停止服务: docker-compose down
echo    重启服务: docker-compose restart
echo.
pause
