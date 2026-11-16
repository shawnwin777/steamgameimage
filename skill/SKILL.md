# SGS Steam Auto Video Skill

## Trigger
When the user pastes a Steam Store /app/<ID>/ URL, extract the numeric app ID.

## Workflow
1. Call createSteamVideo with app_id.
2. Save request_id returned by the API.
3. Call checkSteamVideo with both app_id and request_id to check completion.
4. Share the MP4 link ONLY after the API confirms status=ready.

## Video requirements
- 9:16, 720×1280, 10-second MP4
- Upper section: 4 verified original Steam gameplay screenshots with timed transitions
- Lower section: SGS cyberpunk cyan #00E5BC and purple #946BFF game info
- Show name, original price, current price, discount, sale end, full-language Steam user review summary, Traditional Chinese status
- Natural Taiwan Mandarin narration when speech service is available; if not, label output as silent
- Never fabricate original screenshots, Steam prices, discounts, reviews, languages, or deadlines
- If fewer than 4 usable screenshots are obtained, report failure and do not publish
- Steam media availability is not itself a license to republish commercially

## Important
This repository contains the back-end worker, not a directly installed ChatGPT skill. An API gateway and Custom GPT Action must be configured once.
