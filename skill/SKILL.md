# SGS Steam Auto Video Skill

## Purpose
When a user sends a Steam Store app URL, automatically produce a 10-second portrait (9:16) SGS cyberpunk game-introduction MP4 based on real Steam game screenshots and source-verified Steam metadata.

## Trigger
Recognize `https://store.steampowered.com/app/<APP_ID>/...` and extract the numeric app ID.

## Execution (requires connected GPT Action)
1. Call `createSteamVideo` with `app_id`.
2. Keep its returned `request_id`; do not substitute another or reuse a prior video's result.
3. Call `checkSteamVideo` with `app_id` and `request_id`.
4. Only provide the confirmed `mp4_url` when status is `ready`.
5. If the API is unavailable or a job fails, report the blocker truthfully; do not pretend the MP4 exists.

## Video production requirements
- 720×1280 or higher, portrait 9:16, exactly 10 seconds, MP4.
- Upper area: at least 4 **actual verified game screenshots** obtained from Steam; switch images throughout the clip.
- Lower area: static/animated SGS neon cyberpunk info cards, background #0B1018, cyan #00E5BC, purple #946BFF.
- Information: title, original price, current price, discount %, sale end date, overall Steam player review summary, Traditional Chinese language support.
- Free-to-play games: original/current price = 免費遊玩, discount = 無, end date = 不適用.
- Missing sale deadline or language verification: use 未提供 / 待確認, never invent them.
- Text and narration in Traditional Chinese, natural Taiwan Mandarin when TTS succeeds. If TTS fails, flag the final as silent and never imply narration exists.
- Never use AI-generated gameplay visuals, illustrative mockups or source-unverified material as authentic screenshots.
- Fewer than 4 usable source screenshots: stop generation; report insufficient assets.
- Source screenshots still require appropriate redistribution rights before commercial publishing.

## Technical architecture
- Renderer: `src/create_video.py` (Steam API + screenshot verification + FFmpeg).
- GitHub workflow: `.github/workflows/create-video.yml`.
- Gateway: `worker/index.js` and `worker/wrangler.toml`, requires Cloudflare Worker deployment.
- GPT API spec: `gpt/openapi.yaml` (replace placeholder server URL with real Worker host).
- GPT instructions: `gpt/instructions.md`.
- Source code: https://github.com/shawnwin777/steamgameimage

## Validation status (2026-11-16)
A real GitHub Actions test for Steam App ID 1096900 (RPG Maker MZ) succeeded and published an MP4:
https://github.com/shawnwin777/steamgameimage/releases/tag/sgs-rpg-maker-mz-first-test

**Not yet activated inside ChatGPT as a directly callable Skill.** Deploy the gateway, configure its secrets and install the Custom GPT Action. Until then, simply pasting an URL in an ordinary GPT chat will not reliably launch a new GitHub job.
