# 🇨🇳 AI 中国视频自动发布系统

全自动化的云端短视频发布系统，通过 GitHub Actions 自动将中国风格短视频从 Google Drive 上传至 Facebook Reels 和 YouTube Shorts。

系统 24/7 自动运行，抓取视频、生成 AI SEO 标题和描述、自动上传，并通过 Telegram 发送成功/失败报告。

## ✨ 功能特性

- **Google Drive 集成**：自动扫描指定文件夹获取新视频。
- **AI SEO 优化**：使用 OpenAI 根据视频文件名生成热门标题、描述和中文标签。
- **多平台上传**：同时上传至 Facebook Reels 和 YouTube Shorts。
- **中国受众时段优化**：发布时间针对中国用户高峰时段优化：
  - 🌅 早通勤：7:00 - 9:00 (CST)
  - 🍜 午休：12:00 - 13:00 (CST)
  - 🌙 晚间黄金：19:00 - 22:00 (CST)
- **Telegram 报告**：上传成功或失败时即时推送通知（中文标签）。
- **重复防护与数据库同步**：使用 SQLite 跟踪已上传文件，支持 GitHub Actions 临时运行器。
- **GitHub Actions 自动调度**：每 4 小时自动运行。

## 🛠️ 安装指南

### 1. 前置条件

你需要以下服务的账号/密钥：
- **Facebook 公共主页**：用于上传 Reels。
- **Facebook 开发者应用**：获取 Graph API 访问令牌。
- **Google Cloud 控制台**：创建服务账号以访问 Google Drive。
- **Telegram 机器人**：发送通知。
- **OpenAI API 密钥**：生成 SEO 内容。

### 2. 环境变量 & GitHub Secrets

将 `.env.example` 复制为 `.env` 用于本地测试。
在 GitHub Actions 中，将以下变量添加为 **Repository Secrets**：

| 变量 | 说明 |
|---|---|
| `FB_ACCESS_TOKEN` | Facebook 公共主页访问令牌（需要 `pages_manage_posts`、`pages_read_engagement`） |
| `FB_PAGE_ID` | 你的 Facebook 公共主页 ID |
| `TELEGRAM_BOT_TOKEN` | BotFather 生成的令牌 |
| `TELEGRAM_CHAT_ID` | 你的 Chat ID（机器人发送消息的位置） |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | Google 服务账号密钥的完整 JSON 字符串 |
| `GOOGLE_DRIVE_FOLDER_ID` | Google Drive 中父文件夹的 ID（从 URL 获取） |
| `OPENAI_API_KEY` | 你的 OpenAI API 密钥 |
| `CHINESE_CONTENT_SOURCE` | 中国内容来源（weibo/douyin/bilibili/kuaishou） |
| `SEO_LANGUAGE` | SEO 语言偏好（默认 zh-CN） |
| `INCLUDE_CHINESE_SUBTITLES` | 是否包含中文字幕（true/false） |

### 3. Google Drive 设置

1. 在 Google Drive 中创建主文件夹（例如 `Facebook-Chinese-Reels`），从 URL 获取其 ID。这就是你的 `GOOGLE_DRIVE_FOLDER_ID`。
2. 将此文件夹共享给你的 Google 服务账号邮箱，给予 **编辑者** 权限。
3. 脚本会自动在主文件夹内创建 `Pending`、`Uploaded` 和 `Failed` 子文件夹。
4. 将 `.mp4` 视频放入 `Pending` 文件夹。

### 4. 本地运行

1. 创建虚拟环境：`python -m venv venv`
2. 激活环境：`venv\Scripts\activate`（Windows）或 `source venv/bin/activate`（Mac/Linux）
3. 安装依赖：`pip install -r requirements.txt`
4. 确保系统已安装 FFmpeg。
5. 在 `.env` 中设置变量。本地运行时，将 `GOOGLE_APPLICATION_CREDENTIALS` 设置为下载的 `service-account.json` 文件路径。
6. 运行脚本：`python src/scheduler.py`

### 5. 通过 GitHub Actions 运行

将代码推送到 GitHub 并设置好 Repository Secrets 后，`.github/workflows/upload.yml` 中定义的工作流将每 4 小时自动运行。你也可以从 "Actions" 选项卡手动触发。

### 6. 日志与监控

代理将活动日志记录到控制台（stdout）和本地日志文件：
- 日志位置：`logs/agent.log`
- 每条日志包含时间戳和日志级别（`INFO`、`WARNING`、`ERROR`），用于跟踪代理操作和 API 交互。

## 📁 项目结构

```
Facebook-Viral-Chinese-Reels/
├── src/
│   ├── scheduler.py              # 调度器 - 基于中国时区的发布计划
│   ├── youtube_uploader.py       # YouTube Shorts 上传器
│   ├── agent_3_uploader.py       # Facebook/YouTube 上传代理
│   ├── agent_4_reporter.py       # Telegram 报告代理（中文标签）
│   ├── facebook_uploader.py      # Facebook Graph API 上传
│   ├── drive_reader.py           # Google Drive 文件读取
│   ├── queue_manager.py          # 上传队列管理
│   └── logger.py                 # 日志配置
├── .env.example                  # 环境变量模板
├── requirements.txt              # Python 依赖
└── README.md                     # 本文件
```
