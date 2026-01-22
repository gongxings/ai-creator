#!/bin/bash

# AI创作者平台启动脚本

echo "🚀 启动AI创作者平台..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: 未安装Docker，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ 错误: 未安装Docker Compose，请先安装Docker Compose"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo "📝 创建.env配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑.env文件，配置必要的参数（如数据库密码、API密钥等）"
    echo "   配置完成后，请重新运行此脚本"
    exit 0
fi

# 构建并启动服务
echo "🔨 构建Docker镜像..."
docker-compose build

echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 初始化数据库
echo "🗄️  初始化数据库..."
docker-compose exec backend python scripts/init_db.py

echo ""
echo "✅ AI创作者平台启动成功！"
echo ""
echo "📝 访问地址："
echo "   前端: http://localhost"
echo "   后端API: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""
echo "📋 常用命令："
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo ""
