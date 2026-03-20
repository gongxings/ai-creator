# 全埋点数据采集系统部署指南

## 概述

本系统实现完整的用户行为追踪：
- **页面访问**：PV/UV/跳出率/停留时长/滚动深度
- **用户事件**：点击、滚动等行为自动采集
- **数据流程**：前端 SDK → Redis 缓存 → Celery 定时同步 → MySQL

---

## 1. 数据库迁移

```bash
cd backend
python -m scripts.add_tracking_tables
```

该脚本会：
- 扩展 `page_views` 表：添加 `stay_duration`, `max_scroll_depth`, `is_bounce`, `screen_width`, `screen_height`, `updated_at`
- 创建 `user_events` 表
- 更新 `daily_stats` 表：添加统计字段

---

## 2. 启动 Redis

确保 Redis 服务正在运行：

```bash
# Windows（如果已安装）
redis-server

# 或使用 Docker
docker run -d -p 6379:6379 redis:alpine
```

修改 `backend/.env` 配置：

```env
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=  # 如有密码则填写
```

---

## 3. 启动 Celery Worker 和 Beat

在 `backend` 目录下执行：

```bash
# 启动 Worker（处理数据同步任务）
celery -A app.tasks.celery_app worker --loglevel=info

# 启动 Beat（定时任务调度器，另一个终端）
celery -A app.tasks.celery_app beat --loglevel=info
```

或使用脚本启动：

```bash
# 启动 worker
python -m celery -A app.tasks.celery_app worker --loglevel=info

# 启动 beat
python -m celery -A app.tasks.celery_app beat --loglevel=info
```

---

## 4. 重启后端服务

```bash
# 如果使用 uvicorn
python run.py

# 或使用 gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 5. 验证功能

### 5.1 检查路由

访问 http://localhost:8001/docs，确认以下接口存在：

- `POST /api/v1/traffic/batch` - 批量埋点上报
- `GET /api/v1/traffic/stats` - 缓存统计（管理员）
- `GET /api/v1/traffic/hot-pages` - 热门页面（管理员）
- `GET /api/v1/traffic/click-events` - 点击事件统计（管理员）

### 5.2 前端测试

1. 使用管理员账号登录
2. 访问 `/admin/traffic` 查看流量统计
3. 在流量统计页面点击"刷新"查看实时数据
4. 访问其他页面，观察 PV 是否增加

### 5.3 查看 Redis 缓存

```bash
redis-cli
> LLEN tracker:page_views
> LLEN tracker:user_events
```

如果数字在增长，说明埋点数据正在缓存。

### 5.4 查看 Celery 日志

Worker 会每分钟同步数据到 MySQL：

```
[Tracker] Synced: 15 page views, 0 updates, 42 events
```

---

## 6. 管理员页面功能

### 流量统计仪表盘

- **今日 PV/UV**：实时统计
- **平均停留时长**：用户平均页面停留时间
- **跳出率**：单页访问比例
- **每日统计**：30/90天趋势图（柱状图）

### 热门页面（Top 10）

- 页面路径
- 访问量（PV）
- 独立访客（UV）
- 平均停留时长

### 点击事件统计（Top 20）

- 事件名称（如 `button_el-button`）
- 目标元素（CSS 选择器）
- 所属页面
- 点击次数

---

## 7. 埋点配置说明

### 自动采集

- ✅ 所有页面访问
- ✅ 所有按钮点击（通过事件代理）
- ✅ 滚动深度（页面滚动时）
- ✅ 停留时长（页面离开时计算）

### 手动标记（可选）

在关键元素上添加 `data-track-id` 或 `data-track-name` 属性：

```vue
<el-button data-track-id="submit_order" @click="submit">提交订单</el-button>
```

上报的事件名称将使用 `submit_order`，便于精确追踪转化点。

---

## 8. 常见问题

### Q1: Redis 连接失败

**现象**：日志显示 `Redis connection failed`

**解决**：
1. 检查 Redis 是否启动：`redis-cli ping`
2. 检查 `REDIS_URL` 配置是否正确
3. 如果 Redis 不可用，系统会降级直接写入数据库（性能较差）

### Q2: Celery 任务不执行

**现象**：数据只进 Redis，不入 MySQL

**解决**：
1. 确认 Worker 和 Beat 都在运行
2. 查看 Worker 日志是否有错误
3. 手动触发同步任务测试：
   ```python
   from app.tasks.traffic_tasks import sync_tracking_data
   sync_tracking_data()
   ```

### Q3: 页面没有统计

**现象**：访问页面后，PV 没增加

**解决**：
1. 打开浏览器控制台检查网络请求：`/api/v1/traffic/batch` 是否成功
2. 检查 `sessionStorage` 是否有 `tracking_session_id`
3. 确认前端 tracker 已初始化：`console.log('[Tracker]')`

---

## 9. 性能优化建议

1. **Redis 持久化**：配置 RDB 或 AOF，避免重启丢失数据
2. **监控队列长度**：如果 `tracker:*` 队列持续增长，考虑增加 Worker 数量
3. **数据归档**：定期将 `page_views` 表中历史数据迁移到分析库
4. **降级策略**：Redis 故障时自动切换为直接写库（已实现）

---

## 10. 下一步扩展

- [ ] 添加用户路径分析（漏斗模型）
- [ ] 实时大屏展示（WebSocket 推送）
- [ ] 用户分群画像（基于行为标签）
- [ ] A/B 测试支持

---

## 文件清单

| 文件 | 说明 |
|------|------|
| `backend/app/models/traffic.py` | 数据模型（PageView, UserEvent, DailyStats） |
| `backend/app/services/tracker_service.py` | Redis 缓存服务 |
| `backend/app/api/v1/traffic.py` | 流量统计 API（含批量上报） |
| `backend/app/tasks/celery_app.py` | Celery 应用配置 |
| `backend/app/tasks/traffic_tasks.py` | 定时同步和聚合任务 |
| `backend/scripts/add_tracking_tables.py` | 数据库迁移脚本 |
| `frontend/src/utils/tracker.ts` | 前端埋点 SDK |
| `frontend/src/api/traffic.ts` | 前端流量 API |
| `frontend/src/router/index.ts` | 埋点集成（afterEach 守卫） |
| `frontend/src/views/admin/TrafficStats.vue` | 管理员统计页面 |

---

## 联系

如有问题，请提交 Issue 或查看项目文档。
