# 🙌 推荐一款网页游戏

这个仓库首先是玩家入口，而不是 WebGL 技术展示或搬运合集。欢迎真正打开过、觉得好玩的网页游戏，近作和老作都可以。

## 收录条件

- ✅ 有明确的原作者或官方在线游玩地址，现代桌面浏览器可以打开；不用上传 ROM、ISO 或破解包
- ✅ 玩法值得推荐，有简短中文介绍，标出单人 / 多人及是否必须登录
- ✅ 如果有 GitHub 原仓库，提供准确地址；没有源码也能收录
- ✅ 说清中文支持现状；未核验比猜测更好
- ✅ 如需截图，优先原作者提供的宣传素材并标注来源，不能直接搬运未知版权的图包
- ❌ 不收强制下载客户端才能玩的游戏、破解/灰产资源站、广告站伪装的游戏链接
- ❌ 不因有 GitHub Stars 就谎称玩家评价好，也不因为游戏老就排除经典
- ❌ 不能把代码许可证误当作商业 IP、音乐、美术、商标的转载授权

## 怎么添加

1. [提交「推荐游戏」Issue](https://github.com/bmdy6/awesome-browser-games-zh/issues/new/choose) 或直接提 PR。
2. 修改 data/games.json，选择一个现有的 category，添加唯一 id 和实际可玩 play_url。
3. source_status：open=代码有明确开源许可；unknown=代码公开但许可待核；unavailable=官方源码暂时不可访问；closed=未提供公开源码，不代表已法律认定闭源。
4. zh_status：yes=明确支持简体中文、partial=部分中文、unknown=未核查。不要猜。
5. checked_at 使用实际核查日期，只有完成真实对局测试才把 playtested 设为 true。
6. 若要加封面，cover_url 必须是能直接访问、来源可追溯的项目图片；不要上传商业素材到仓库。开源代码和素材遵循不同许可。
7. 运行 python3 scripts/generate_readme.py，随后运行 python3 -m unittest discover -s tests -v 和 node --check assets/app.js。

优先收录国内用户愿意点进去玩的作品：射击、坦克、战争策略、无双、建造、聚会小游戏。清单不是按 GitHub Stars 机械排序的榜单。
