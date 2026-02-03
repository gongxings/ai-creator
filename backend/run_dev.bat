@echo off
chcp 65001 >nul
REM 后端开发环境启动脚本 (Windows)

echo 🚀 启动AI创作者平台后端（开发模式）...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未安装Python，请先安装Python 3.10+
    pause
    exit /b 1
)

REM 检查是否在backend目录
if not exist "app\main.py" (
    echo ❌ 错误: 请在backend目录下运行此脚本
    echo    或使用: cd backend ^&^& run_dev.bat
    pause
    exit /b 1
)

REM 检查.env文件
if not exist ".env" (
    if exist ".env.example" (
        echo 📝 创建.env配置文件...
        copy .env.example .env
        echo ⚠️  请编辑.env文件，配置必要的参数
        echo    配置完成后，请重新运行此脚本
        pause
        exit /b 0
    ) else (
        echo ❌ 错误: 未找到.env.example文件
        pause
        exit /b 1
    )
)

REM 检查虚拟环境
if not exist "venv" (
    echo 📦 创建Python虚拟环境...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 错误: 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo 🔧 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 📦 检查并安装依赖...
pip install -r requirements.txt

REM 启动应用
echo.
echo ✅ 启动应用...
echo.
python run.py

pause
