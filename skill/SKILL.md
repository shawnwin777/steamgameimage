# SGS Steam Auto Video Skill

## 觸發詞
使用者輸入「SGS製片」或「SGS Skill」並貼上 Steam 商店網址，例如：
`SGS製片 https://store.steampowered.com/app/230410/Warframe/`

在已連接 GitHub 的 ChatGPT 對話中，主動執行這套流程；不要只說明步驟。

## 真正可用的 GitHub 呼叫流程（已驗證）
1. 從 `store.steampowered.com/app/<APP_ID>/` 擷取純數字 App ID，確認域名與格式。
2. 透過 GitHub 連接工具，在儲存庫 `shawnwin777/steamgameimage` 建立新 Issue，**標題嚴格等於** `SGS VIDEO <APP_ID>`。body 寫明 Steam 原始網址及當次任務。
3. GitHub Workflow `.github/workflows/chat-trigger.yml` 收到 Issue `opened` 事件即執行。工作流程限制 Issue 建立者必須是儲存庫擁有者。
4. 記下剛建立 Issue 的 **issue_number**。檢查該次 GitHub Actions 執行狀態；在完成前，不宣稱已產生影片。
5. 工作成功後，取得 GitHub Release tag `sgs-issue-<issue_number>`，核對其 assets 確有 `SGS_10sec.mp4`，回覆該筆 MP4 的實際 `browser_download_url`。
6. 若失敗或 Release 缺檔，報告明確失敗階段與 GitHub Actions URL；不可拿舊影片充作新片。

### 可直接使用的工具介面
- `mcp__GitHub__create_issue`：
  `{repository_full_name:"shawnwin777/steamgameimage",title:"SGS VIDEO 230410",body:"Steam: https://store.steampowered.com/app/230410/Warframe/"}`
- 讀取 GitHub Actions 執行紀錄：`mcp__GitHub__fetch` 可讀 `https://api.github.com/repos/shawnwin777/steamgameimage/actions/runs`
- 取得成功影片 Release：`mcp__GitHub__fetch`，讀取 `https://api.github.com/repos/shawnwin777/steamgameimage/releases/tags/sgs-issue-<issue_number>`

## 影片素材優先順序
- 優先嘗試 Steam appdetails.movies 中的官方 MP4 預告片（不是保證實機遊玩畫面）。需檢查網址來源、成功下載、ffprobe 驗證後才當作動態影片。
- 若無可用的官方 MP4，回退到至少四張已下載驗證的 Steam 官方截圖。
- GitHub Release 的 source_manifest.json 有 media_mode、trailer.status、trailer.candidates 供追蹤。不可聲稱截圖輪播是遊戲實機動態錄影。
- 2026-11-16 Warframe 第二次重測：Steam API 回傳 0 個 MP4 候選，因此產生的是官方截圖輪播的 MP4，而非動態影片剪輯。

## 影片規格
- 9:16、720×1280、10秒 MP4
- 上半部至少四張經過實際下載及解碼驗證的 Steam 官方截圖
- 下半部 SGS 賽博龐克 #0B1018 深色底、#00E5BC 霓虹青綠、#946BFF 紫色
- 遊戲名稱、原價、現價、折扣、截止日期、全語言 Steam 玩家總評、繁體中文狀態
- 台灣華語 TTS（若語音生成失敗，須註明無聲）
- 絕不可用 AI 生成假畫面冒充官方遊戲截圖；不可猜測價格、折扣或語言狀態
- Steam 公開素材不代表擁有商業重製權；公開發布前應確認素材授權

## 關鍵限制
此 `SKILL.md` 已存於 GitHub，但**不代表已被安裝成 ChatGPT 帳號內建的全域 Skill**。在本對話的 GitHub 連線有效時，可以直接按此流程呼叫 GitHub 製片。若新對話沒有取得 GitHub 連接或此 Skill 的指示，則不能承諾會自動呼叫。若需跨新對話自動偵測，必須正式配置 GPT Builder Action 或能安裝技能的執行環境。

## 已驗證實例（2026-11-16）
- RPG Maker MZ (1096900) GitHub Actions 成功：https://github.com/shawnwin777/steamgameimage/releases/tag/sgs-rpg-maker-mz-first-test
- Warframe (230410) 經 ChatGPT GitHub Issue 啟動成功：https://github.com/shawnwin777/steamgameimage/releases/tag/sgs-issue-1
