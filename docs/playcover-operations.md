# PlayCover 首实例 Python 操作记录

记录日期：2026-10-27，Asia/Shanghai。本文记录已实际观察到的行为；尚未验证的部分单独注明。

## 当前结果

首实例为「梦幻西游」，bundle ID `com.netease.my`，登录服务器「三界乐园」。已验证 Python 启动、截图、登录、打开和关闭包裹。首轮测试位置为玉苑琼楼 `(111,34)`。Windows 真机和完整师门流程尚未验证，未执行购买或上交物品。

好友详情已核对「秋风知我意」，角色 ID `342281445`，当时队伍显示 `1/5`。16:28:51 的截图明确提示“你已申请加入秋风知我意的队伍，请耐心等候……”。**申请已发送，尚无成功加入队伍的核验证据。** 用户随后确认已经申请过，后续不得重复申请。16:37 尝试关闭好友面板，但操作后截图仍显示“我的好友”，因此不能记为已关闭；此后未再执行游戏操作。

## 唯一组队目标

后续只允许加入用户大号「秋风知我意」（ID `342281445`）的队伍。通过好友详情核对姓名和角色 ID 后才可申请；有同名、信息不全或不一致时停止。禁止其他玩家和随机匹配。申请发送后，等待批准并查看队伍成员、队长信息；申请提示不能作为成功入队的证据。

`team-policy.json` 保存该约束，`AGENTS.md` 规定后续执行必须遵守。目前通用坐标控制脚本不识别游戏姓名，也不会自动读取该策略；它不是已经完成身份校验的自动组队功能，执行者必须依据最新截图核验目标。尚未实现自动 OCR、完整好友导航或申请状态识别。

## 已验证的操作方法

操作由 Python 的 PyAutoGUI 输入与截图、Quartz 窗口查询、AppKit 前台校验执行，未通过 Computer Use 发送游戏输入。

1. 激活 bundle `com.netease.my`，截图确认首实例当前状态。
2. 登录页瞬时 `gui.click()` 未见响应；同位置 `mouseDown()` → 等待 `0.2` 秒 → `mouseUp()` 后进入游戏。打开和关闭包裹也成功。
3. 主场景左下“好友”进入好友面板，选择「秋风知我意」详情，核对 ID 后点击“申请入队”。
4. 保存申请提示；不重复发送申请。最后截图仍在好友面板，关闭面板未确认成功。下一步应只读核验是否已被接受。

`scripts/playcover_control.py` 提供快照、激活、点击、双击、快捷键与粘贴，默认 `--hold 0.2`，范围 `0.05–2` 秒，使用 `try/finally` 释放鼠标。输入命令应始终提供 `--expected com.netease.my`，防止输入到其他前台应用。`--expected` 仅检查应用身份，不校验好友身份。`paste` 会改变系统剪贴板，且输入文本会写入日志，不用于密码或验证码。

## 复现环境与命令

在 macOS 的项目根目录执行，先安装依赖（建议环境放在本机非云盘目录）：

```sh
python3 -m venv /tmp/mhxy-playcover
/tmp/mhxy-playcover/bin/python -m pip install -r requirements-playcover.txt
/tmp/mhxy-playcover/bin/python scripts/playcover_control.py activate com.netease.my --label current
/tmp/mhxy-playcover/bin/python scripts/playcover_control.py snapshot --label before-action
```

`activate` 要求该实例已运行。首实例安装目录为 `~/Library/Containers/io.playcover.PlayCover/Applications/com.netease.my.app`。若需启动，可使用 Python：

```python
from pathlib import Path
import subprocess
subprocess.run(['open', str(Path('~/Library/Containers/io.playcover.PlayCover/Applications/com.netease.my.app').expanduser())], check=True)
```

根据刚生成的截图决定当前逻辑坐标，再执行单次输入；以下 `X Y` 是占位符，不能原样运行：

```sh
/tmp/mhxy-playcover/bin/python scripts/playcover_control.py click X Y --expected com.netease.my --hold 0.2 --label after-action
```

截图会写入脚本当前固定的 `runs/20261027-first-login/`，文件名含时间，动作追加到 `actions.jsonl`。本机逻辑屏幕为 `1470×956`、原始截图 `2940×1912`；脚本将截图缩放为逻辑尺寸后保存，使输出像素与鼠标坐标一致。窗口移动、缩放或屏幕改变后必须重新截图定位，不能复用本次坐标。

本轮使用 `/tmp/mhxy-runtime-20261027/bin/python`。原项目 `.venv` 在导入 numpy/PyObjC 时读取模块文件极慢；独立临时环境可正常运行，临时目录可能被清理。辅助功能和屏幕录制权限检查均为 True，单次截图约半秒。先前长延迟主要来自依赖导入、逐步截图判断和协调等待，不是点击本身耗时。持续按压在本轮有效，不能据此断言每个 UI 都必须采用相同时间。

## 操作证据

提交的图片只保留游戏窗口：

- [目标姓名、ID 与队伍人数](evidence/qiufeng-profile.png)
- [已发送申请的明确提示](evidence/qiufeng-application.png)
- [申请后状态（好友面板仍打开）](evidence/after-application.png)

原始完整屏幕截图与 JSONL 仍保留在本地 `runs/20261027-first-login/`，未上传桌面全屏信息：`162557-qiufeng-menu.png`、`162850-qiufeng-join-request.png`、`163722-after-join-request.png`、`actions.jsonl`。此前首轮详细试运行记录位于本地 `runs/20261027-first-instance-trial/README.md`。

## 提交范围与后续

本次归档控制辅助脚本、依赖说明、操作记录、窗口证据和组队约束。原工作区已有的跨平台后端、师门及其他未提交改动未纳入本次提交。后续可将已验证步骤合并为 Python 状态流程，仅在状态变化时截图；必须先实现目标身份校验和申请去重，再考虑自动组队。

## 归档校验

控制脚本 `py_compile` 通过；策略 JSON 可解析且姓名、ID 与截图一致。现有本地工作区的 `python -m unittest discover -s tests -v` 共 9 项最终全部通过（首次运行 1 项导入超时，重试通过，耗时 23.55 秒）。这套测试包含本次未提交的跨平台改动，不代表本提交实现或验证了自动组队。
