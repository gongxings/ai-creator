# 全埋点数据采集系统部署指南

## 概述

本系统实现完整的用户行为追踪：
- **页面访问**：PV/UV/跳出率/停留时长/滚动深度
- **用户事件**：点击、滚动等行为自动采集
- **数据流程**：前端 SDK → Redis 缓存 → FastAPI 后台线程定时同步 → MySQL

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

## 3. 启动 FastAPI 应用（包含后台任务）

启动 FastAPI 应用时，会自动启动后台数据同步任务（每60秒执行一次）：

```bash
cd backend
python run.py
```

后台任务会自动：
1. 每60秒从 Redis 读取缓存的埋点数据
2. 批量写入 MySQL 数据库
3. 记录日志到控制台

无需额外启动 Celery Worker 或 Beat！

---

## 4. 手动触发数据同步

如需手动触发同步（例如调试），可运行：

```bash
# 同步埋点数据
python scripts/sync_tracker.py

# 强制同步所有数据（忽略批次限制）
python scripts/sync_tracker.py --force

# 同步数据并同时执行每日统计汇总
python scripts/sync_tracker.py --aggregate
```

---

## 5. 验证功能

### 5.1 检查路由

访问 http://localhost:8001/docs，确认以下接口存在：

- `POST /api/v1/traffic/batch` - 批量埋点上报
- `GET /api/v1/traffic/stats` - 缓存统计（管理员）
- `GET /api/v1/traffic/overview` - 流量概览（管理员）
- `GET /api/v1/traffic/daily` - 每日统计（管理员）
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

### 5.4 查看后台任务日志

FastAPI 启动日志中会显示：

```
[Tracker] Background task started
[Tracker] Synced: 15 page views, 42 events
```

---

## 6. 管理员页面功能

### 流量统计仪表盘

- **今日 PV/UV**：实时统计
- **平均停留时长**：用户平均页面停留时间
- **跳出率**：单页访问比例
- **每日统计**：30/90天趋势图（柱状图 + 折线图）

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
3. 如果 Redis 不可用，系统会自动降级直接写入数据库（性能较差）

### Q2: 数据没有写入 MySQL

**现象**：访问页面后，PV 没增加

**解决**：
1. 检查 FastAPI 日志中是否有 `[Tracker] Synced` 输出
2. 打开浏览器控制台检查网络请求：`/api/v1/traffic/batch` 是否成功
3. 检查 `page_views` 表中是否有数据
4. 手动运行 `python scripts/sync_tracker.py` 测试同步

### Q3: 后台任务没有启动

**现象**：启动 FastAPI 后，没有看到 `[Tracker] Background task started`

**解决**：
1. 检查 `app/main.py` 是否导入了 `start_tracker_background`
2. 检查是否有报错（如 Redis 连接失败不会阻止后台启动）
3. 查看线程列表：后台任务会在名为 `TrackerBackgroundTask` 的线程中运行

---

## 9. 性能优化建议

1. **Redis 持久化**：配置 RDB 或 AOF，避免重启丢失数据
2. **调整同步频率**：修改 `background_tracker.py` 中的 `sync_interval` 参数
3. **批量大小**：根据需要调整 `batch_size`（默认1000条/批次）
4. **降级策略**：Redis 故障时自动切换为直接写库（已实现）

---

## 10. 架构对比

| 特性 | 原方案（Celery） | 现方案（后台线程） |
|------|----------------|-------------------|
| 依赖 | 需要 Celery + Redis Broker | 仅需 Redis 作为缓存 |
| 启动复杂度 | 需要启动3个进程（app + worker + beat） | 只需启动 FastAPI 一个进程 |
| 资源占用 | 较高（多个 Python 进程） | 较低（仅后台线程） |
| 定时精度 | 高（Beat 精确调度） | 中（异步循环，可能有秒级偏差） |
| 功能 | 完整任务队列、重试、监控 | 基础定时同步 |
| 适用场景 | 大规模分布式任务 | 轻量级定时同步 |

---

## 11. 文件清单

| 文件 | 说明 |
|------|------|
| `backend/app/models/traffic.py` | 数据模型（PageView, UserEvent, DailyStats） |
| `backend/app/services/tracker_service.py` | Redis 缓存服务 |
| `backend/app/api/v1/traffic.py` | 流量统计 API（含批量上报） |
| `backend/app/tasks/background_tracker.py` | 后台同步任务（替代 Celery） |
| `backend/scripts/add_tracking_tables.py` | 数据库迁移脚本 |
| `backend/scripts/sync_tracker.py` | 手动同步脚本 |
| `frontend/src/utils/tracker.ts` | 前端埋点 SDK |
| `frontend/src/api/traffic.ts` | 前端流量 API |
| `frontend/src/router/index.ts` | 埋点集成（afterEach 守卫） |
| `frontend/src/views/admin/TrafficStats.vue` | 管理员统计页面 |
| `README.md` | 项目说明文档 |

---

## 12. 下一步扩展

- [ ] 添加用户路径分析（漏斗模型）
- [ ] 实时大屏展示（WebSocket 推送）
- [ ] 用户分群画像（基于行为标签）
- [ ] A/B 测试支持

---

## 联系

如有问题，请提交 Issue 或查看项目文档。
