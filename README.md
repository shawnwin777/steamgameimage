# SGS Steam Auto Video

讓 Steam 網址產生 10 秒 SGS 賽博龐克影片的雲端製片專案。

## 已完成
- GitHub Actions 工作流程：`.github/workflows/create-video.yml`
- 透過 Steam App ID 擷取官方原始截圖：`src/create_video.py`
- 至少 4 張可解碼的實際遊戲截圖才可出片
- Steam 台灣區價格、全語言玩家總評與繁體中文狀態（無法確證時顯示待確認）
- 720×1280、10 秒 MP4、霓虹青綠＋紫色資訊面板
- 台灣華語語音合成（服務失敗時輸出無聲影片並在 manifest 註明）
- GitHub Release 出片、供自訂 GPT 呼叫的 Worker 程式及 OpenAPI

## 目前還沒有完成的
工作流程已提交到 GitHub，但尚未在 GitHub Actions 實際成功執行。Cloudflare Worker 未部署，GPT Action 尚未連接；因此現在貼 Steam 網址並不會自動輸出 MP4。

## 第一步：測試 GitHub Actions
開啟 https://github.com/shawnwin777/steamgameimage/actions/workflows/create-video.yml
選擇 Run workflow，填入：
- `app_id`: `3564740`（燕雲十六聲）或 `1096900`（RPG Maker MZ）
- `request_id`: 任一新產生的 UUID，例如 `11111111-2222-4333-8444-555555555555` （每次不可重複）

執行成功後，GitHub Releases 應有 `SGS_10sec.mp4` 和 `source_manifest.json`。檢查內容與授權，再將它用於公開宣傳。

## 第二步：部署 GPT 呼叫 API（一次性設定）
雲端代理在 `worker/index.js`，Cloudflare 配置在 `worker/wrangler.toml`。
在 Cloudflare Workers 部署前，設定兩項機密：
- `API_KEY`：只有自訂 GPT Actions 知道的 API Bearer token
- `GH_TOKEN`：可執行這個儲存庫 Actions 工作流程並讀取 Releases 的最小權限 GitHub Token

`GH_OWNER`、`GH_REPO` 已在 wrangler.toml 設為 `shawnwin777`、`steamgameimage`。
**不要**把任何金鑰放入公開 GitHub 檔案或聊天。

## 第三步：建立 SGS 自訂 GPT
1. 建立自訂 GPT。
2. 把 `gpt/instructions.md` 放入 Instructions。
3. 在 Actions 匯入 `gpt/openapi.yaml`。
4. 把 servers.url 換成自己的 Cloudflare Worker HTTPS URL。
5. 在 GPT Actions 設定 Bearer API Key 認證（應和 Worker 的 API_KEY 相同）。
6. 測試 `createSteamVideo` 和 `checkSteamVideo` 兩個動作。

## 注意
Steam 的公開截圖不等於一定有商業重製與發布權。確認素材授權後再對外發布影片。GitHub Actions 的雲端下載能力亦需要實際測試，不能以本地測試替代。
