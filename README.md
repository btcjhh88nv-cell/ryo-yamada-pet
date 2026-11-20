# 山田凉桌面伙伴

Q 版山田凉，自制的《孤独摇滚！》桌面伙伴。待机时低头弹白色贝斯，抬头眨一下单眼。鼠标悬停时，她会比心踏步，最后害羞地摸摸头。

| 待机 | 悬停 |
| --- | --- |
| ![弹贝斯](previews/idle.gif) | ![比心踏步再摸头](previews/hover.gif) |

## 安装到 ChatGPT 桌面端

将 `pet.json` 和 `spritesheet.png` 一起放进本地 Codex 数据目录的 `pets/ryo-yamada/`。Windows 上的默认目录是 `%USERPROFILE%\.codex\pets\ryo-yamada\`。如果设置过 `CODEX_HOME`，用该目录下的 `pets`。然后打开 **设置 → 智能伙伴（Pets）**，刷新列表，选择「山田凉」。

也可以在仓库根目录用 Python 3 运行以下命令，安装脚本会先校验素材。

```powershell
python -m pip install -r requirements.txt
python tools/pet.py install
```

如果同名目录中已有不同版本，脚本会提示目录冲突，便于先备份已有素材。

## 素材和工具

- `pet.json` 是本地安装配置，指向 v2 的 `spritesheet.png`。
- `spritesheet.png` 为 1536 × 2288 像素的透明 PNG，按 192 × 208 像素分格，包含 9 组动作和 16 个视线方向。
- `tools/pet.py` 可校验安装包，或根据精灵图重新绘制 GIF。桌面端的实际触发条件和播放策略由客户端控制。

```powershell
python tools/pet.py validate
python tools/pet.py preview
```

角色来自《孤独摇滚！》，贝斯外观参考动画里的白色 Precision Bass。[动画官方角色页](https://bocchi.rocks/omnibus/character/ryo.html)
