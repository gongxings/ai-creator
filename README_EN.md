# AI Creator Platform

[中文](README.md) | English

A powerful AI content creation platform with AI writing, image generation, video generation, PPT generation tools, and one-click multi-platform publishing.

![Login Page](assert/login.png)

## ✨ Features

- **14 Professional Writing Tools**: WeChat articles, Xiaohongshu notes, official documents, papers, marketing copy, etc.
- **Image Generation**: Text-to-image, image variants, AI editing
- **Video Generation**: Text-to-video, image-to-video, AI dubbing
- **PPT Generation**: Theme generation, outline generation, online editing
- **One-Click Publishing**: WeChat, Xiaohongshu, Douyin, Kuaishou, Toutiao
- **Multi-Model Support**: OpenAI, Claude, Qwen, Ernie Bot, Zhipu AI
- **Credits & Membership System**: Flexible billing options

## 🚀 Quick Start

### Requirements

- Python 3.13+
- Node.js 22+
- MySQL 8.0+
- Redis 6.0+

### Local Development

```bash
# Clone the repository
git clone https://github.com/gongxings/ai-creator.git
cd ai-creator

# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env  # Edit configuration
python -m uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Access: Frontend http://localhost:5173 | Backend http://localhost:8000/docs

### Docker Deployment

**Option 1: External Database (Recommended for Production)**

```bash
cp .env.example .env
# Edit .env, configure DATABASE_URL and REDIS_URL
docker-compose up -d --build
```

**Option 2: Full Deployment (with MySQL + Redis)**

```bash
cp .env.example .env
docker-compose -f docker-compose.full.yml up -d --build
```

The application automatically creates 22 database tables and initializes base data on startup.

## 🏗️ Tech Stack

| Backend | Frontend |
|---------|----------|
| FastAPI | Vue 3 + TypeScript |
| SQLAlchemy + MySQL | Element Plus |
| Redis | Pinia |
| JWT Auth | Vite |

## 📁 Project Structure

```
ai-creator/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── models/   # Database models
│   │   ├── schemas/  # Pydantic models
│   │   └── services/ # Business logic
│   └── requirements.txt
├── frontend/         # Vue frontend
│   ├── src/
│   │   ├── api/      # API interfaces
│   │   ├── views/    # Page components
│   │   └── store/    # State management
│   └── package.json
├── docker-compose.yml
└── docker-compose.full.yml
```

## ⚙️ Configuration

Core environment variables (`.env`):

```bash
# Database
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/ai_creator

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key

# AI API Keys
OPENAI_API_KEY=sk-xxx
ANTHROPIC_API_KEY=sk-ant-xxx
```

## 📚 Documentation

- [Features](docs/FEATURES.md)
- [API Reference](docs/API_REFERENCE.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Database Design](docs/DATABASE.md)

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

[MIT License](LICENSE)

---

⭐ If this project helps you, please give it a Star!
