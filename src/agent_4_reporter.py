import os
import json
import requests
import shutil

def send_telegram_message(message):
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("Telegram bot configuration is missing. Skipping Telegram notification.")
        return False
        
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        print("Successfully sent unified Telegram report.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Telegram message: {e}")
        return False

def main():
    print("Starting Agent 4: Unified Reporter")
    report_path = "workspace/report.json"
    
    if os.path.exists(report_path):
        with open(report_path, 'r') as f:
            try:
                report = json.load(f)
            except json.JSONDecodeError:
                report = {}
    else:
        report = {}
        
    # Default values in case keys are missing
    video_name = report.get('video_name', 'N/A')
    download_status = report.get('download_status', 'Failed / Unknown')
    editing_status = report.get('editing_status', 'N/A')
    upload_status = report.get('upload_status', 'N/A')
    seo_title = report.get('seo_title', 'N/A')
    description = report.get('description', 'N/A')
    fb_url = report.get('facebook_url', 'N/A')
    
    # Determine YouTube Status
    yt_url = report.get('youtube_url', 'N/A')
    yt_status = "Success" if "youtube.com" in yt_url or "youtu.be" in yt_url else "Failed / N/A"
    
    # GitHub Action Variables
    repo = os.environ.get('GITHUB_REPOSITORY', 'Vikram-Bosak/Facebook-Viral-Chinese-Reels')
    run_id = os.environ.get('GITHUB_RUN_ID', 'UNKNOWN')
    repo_url = f"https://github.com/{repo}"
    run_url = f"{repo_url}/actions/runs/{run_id}"
    
    emoji_status = "✅" if upload_status == "成功" or upload_status == "Success" else "❌"
    
    yt_status_cn = "成功" if yt_status == "Success" else "失败"
    message = (
        f"{emoji_status} <b>📤 管道运行完成</b>\n\n"
        f"🎬 <b>视频名称:</b>\n{video_name}\n\n"
        f"📥 <b>下载状态:</b> {download_status}\n"
        f"✂️ <b>编辑状态:</b> {editing_status}\n"
        f"📤 <b>Facebook 上传状态:</b> {upload_status}\n"
        f"📤 <b>YouTube 上传状态:</b> {yt_status_cn}\n\n"
        f"🏷️ <b>SEO 标题:</b>\n{seo_title}\n\n"
        f"📝 <b>描述:</b>\n{description}\n\n"
        f"🔗 <b>Facebook Reel 链接:</b>\n{fb_url}\n\n"
        f"▶️ <b>YouTube 视频链接:</b>\n{yt_url}\n\n"
        f"📦 <b>GitHub 仓库:</b>\n{repo_url}\n\n"
        f"📄 <b>工作流运行:</b>\n{run_url}"
    )
    
    if "No new video" in download_status or "无新视频" in download_status:
        print("没有新视频可处理。跳过 Telegram 通知以避免打扰。")
    else:
        send_telegram_message(message)
    
    # Cleanup workspace completely
    if os.path.exists("workspace"):
        shutil.rmtree("workspace")
        print("Cleaned up workspace directory.")

if __name__ == "__main__":
    main()
