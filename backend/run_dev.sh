#!/bin/bash
# 后端开发环境启动脚本 (Linux/Mac)

echo "🚀 启动AI创作者平台后端（开发模式）..."
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未安装Python，请先安装Python 3.10+"
    exit 1
fi

# 检查是否在backend目录
if [ ! -f "app/main.py" ]; then
    echo "❌ 错误: 请在backend目录下运行此脚本"
    echo "   或使用: cd backend && ./run_dev.sh"
    exit 1
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 创建.env配置文件..."
        cp .env.example .env
        echo "⚠️  请编辑.env文件，配置必要的参数"
        echo "   配置完成后，请重新运行此脚本"
        exit 0
    else
        echo "❌ 错误: 未找到.env.example文件"
        exit 1
    fi
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建Python虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ 错误: 创建虚拟环境失败"
        exit 1
    fi
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📦 检查并安装依赖..."
pip install -r requirements.txt

# 启动应用
echo
echo "✅ 启动应用..."
echo
python run.py
