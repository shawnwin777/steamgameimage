# SGS Steam Auto Video

這是一個以 Steam App ID 取得真實遊戲截圖、Steam 遊戲資料並合成 SGS 10 秒賽博龐克短影音的原型專案。

## 快速入口
- 自動製片工作流程：`.github/workflows/create-video.yml`
- 影片合成：`src/create_video.py`
- GPT API 代理：`worker/index.js`（必須另行部署與設定密鑰）
- GPT Actions schema：`gpt/openapi.yaml`
- Skill 規格：`skill/SKILL.md`

## 使用說明
本專案預設使用 GitHub Actions 的 `workflow_dispatch`，需傳入 `app_id` 與 UUID 格式 `request_id`。工作流程會嘗試取得至少四張真實官方截圖，任何不足都會失敗，不使用 AI 假畫面。

**重要：** 上傳程式碼不等於完成完整 Skill。正式的「貼網址自動生成影片」還需要部署 Cloudflare Worker 並與自訂 GPT Actions 連接，確認 GitHub Actions 能在網路環境中成功下載 Steam 截圖與執行製片。影片素材重新發布須確認使用權利。
