# Game 35 Progress

Team: 马来风光 (id=156). Snapshot pulled 2026-09-01 via `gzctf_client.py challenges`.
Already solved (by teammate kjie, before this tracking started): id 276, id 278.

Update this table as challenges get solved. Paste results/output from the
scripts here (or just tell Claude the flag + which challenge) and it'll be
filled in and committed with a write-up.

| id  | title | category | score | status | flag |
|-----|-------|----------|-------|--------|------|
| 276 | 东西很好，就是有点毛病 | Misc | 125 | solved (teammate) | |
| 278 | 头等机密 | Misc | 525 | solved (teammate) | |
| 277 | 飞机大战 | Misc | 525 | not started | |
| 271 | 神秘符号的召唤 | Crypto | 661 | not started | |
| 272 | Ping！第一关：畅通无阻 | Web | 661 | not started | |
| 284 | Ping！第二关：路障初现 | Web | 2495 | not started | |
| 285 | Ping！第三关：此路不通 | Web | 2495 | not started | |
| 286 | Ping！第四关：神秘符号失踪案 | Web | 2717 | not started | |
| 287 | Ping！第五关：迷失的输出 | Web | 2722 | not started | |
| 288 | Ping！第六关：终极绕道大赛 | Web | 2717 | not started | |
| 270 | 神秘验证码生成器 | Web | 1000 | not started | |
| 273 | 现在你不是管理员 | Web | 1000 | not started | |
| 274 | VIP商城 | Web | 3000 | not started | |
| 275 | 隐私之眼 | Web | 1000 | not started | |
| 280 | 固执的登录守卫 | Web | 3000 | not started | |
| 281 | ERP迷宫：隐藏的路径 | Web | 2728 | not started | |
| 282 | 自由的沙盒 | Web | 2728 | not started | |
| 283 | 什么？过了今天就要在等一年！ | Web | 3000 | not started | |
| 289 | 折扣猎手 | Web | 3000 | not started | |
| 302 | 新系统上线 | Web | 1000 | not started | |
| 305 | 爬虫协议可曾听说过？ | Web | 864 | not started | |
| 307 | 国庆放假，我想到处看看 | Web | 864 | not started | |
| 309 | KK快递用户中心 | Web | 752 | not started | |
| 291 | 快递大逃亡 | Reverse | 2722 | not started | |
| 279 | 分析幽灵的脚步 | Forensics | 2000 | not started | |
| 295 | 被删除的webshell | Forensics | 2728 | not started | |
| 292 | 听说你要参加编程马拉松？ | PPC | 2495 | not started | |
| 311 | 在线文件管理 | PPC | 1000 | not started | |
| 312 | 我要开个小卖部 | PPC | 1000 | not started | |

Status values: `not started`, `in progress`, `solved`, `blocked`.

## Suggested order

Start with the **Ping! series** (272, 284, 285, 286, 287, 288) — same
challenge type end to end, and `scripts/ping_bypass.py` is built for
exactly this. Then move to id 270 (神秘验证码生成器).
