# TINY KNIGHT / 迷你骑士

一个用 [Pyxel](https://github.com/kitao/pyxel) 制作的俯视角（上帝视角）小游戏。
你扮演一名迷你骑士，在石质废墟竞技场里迎战一波又一波的怪物，尽可能活得久、拿更高的分。

- 分辨率 256 × 224，3 倍缩放，60 FPS
- 640 × 480 的可滚动竞技场，摄像机平滑跟随
- 所有像素画、字体和音效都在代码里生成，不依赖任何外部素材
- 程序生成的无尽波次，最高分保存在本地

## 运行

需要 Python 3.9 或更高版本。

```bash
pip3 install -r requirements.txt
python3 main.py
```

如果系统提示找不到 `pyxel`，可以改用：

```bash
python3 -m pip install --user pyxel
```

游戏窗口会以 3 倍大小打开。首次运行会在同目录创建 `highscore.txt` 记录最高分。

如果不想安装 Python，也可以直接打开已经生成好的网页版 `dist/TinyKnight.html`（见下文“打包与分享”）。

## 操作

| 按键 | 功能 |
| --- | --- |
| `WASD` / 方向键 | 移动 |
| `空格` / `Z` / `J` | 挥剑 |
| `Shift` / `X` / `K` | 冲刺（短暂无敌） |
| `P` | 暂停 / 继续 |
| `Esc` | 退出游戏 |

> 游戏内文字使用英文，是因为 Pyxel 内置的是英文字体；标题和波次横幅另用了代码生成的 3×5 点阵字体。

## 玩法

- **无尽波次**：清光当前波的所有敌人后，会获得 `25 × 波数` 的奖励分，然后自动进入下一波。
- **三种敌人**：
  - 绿色史莱姆：行动慢，会一跳一跳地靠近你。
  - 紫色蝙蝠：速度快、飞行轨迹飘忽。
  - 骷髅弓箭手：保持距离并射箭；越到后面的波次血量越高。
- **回血**：每两个波次清场时会恢复 1 点生命；击败敌人也有概率掉落红心。
- **冲刺**：冲刺期间完全无敌，可以穿过敌人和箭矢，适合用来脱离包围。
- **受击**：受伤后有短暂无敌时间，同时会被击退；屏幕会轻微震动并出现打击顿帧。
- **最高分**：游戏结束时会自动保存。源码运行时写入游戏目录的 `highscore.txt`；`.pyxapp` / EXE 打包版写入系统用户数据目录（Windows 为 `%APPDATA%\TinyKnight\`，macOS 为 `~/Library/Application Support/TinyKnight/`）。网页版受浏览器沙箱限制，最高分只在当前页面内有效，刷新后会清零。

小技巧：被围住时不要硬拼，朝敌人少的方向冲刺；弓箭手放箭前会有一条瞄准线，看到线就横向移动。

## 生成与打包说明

源码只有两个 Python 文件：`main.py` 和 `art.py`。游戏中的像素画、字体、音效和地面都在运行时由代码生成，因此**没有额外的素材构建步骤**。这里的“生成”指把源码打包成可分享的 `.pyxapp`、网页 HTML 或可执行文件。

### 前置条件

- Python 3.9 或更高版本
- 源码运行需要 Pyxel：

  ```bash
  python3 -m pip install -r requirements.txt
  ```

- 只有打包 EXE / 原生可执行文件时才需要 PyInstaller：

  ```bash
  python3 -m pip install pyinstaller
  ```

本文命令在 Pyxel 2.8.10 上验证；`requirements.txt` 将 Pyxel 限定在 2.x。

打包流程如下：

```text
main.py + art.py
      │  pyxel package
      ▼
TinyKnight.pyxapp
      ├── pyxel play ......  直接运行
      ├── pyxel app2html ... 生成网页版
      └── pyxel app2exe .... 生成当前平台可执行文件（需 PyInstaller）
```

### 快捷命令（Makefile）

macOS / Linux 下可以直接使用 Makefile，避免手敲多步命令：

```bash
make            # 查看所有命令
make run        # 从源码运行
make dist       # 生成 dist/TinyKnight.pyxapp 和 dist/TinyKnight.html
make app        # 只生成 .pyxapp
make web        # 只生成网页版
make play       # 运行已打包的 .pyxapp
make serve      # 在 http://localhost:8000 预览网页版
make exe        # 生成当前系统的可执行文件（需 PyInstaller）
make clean      # 清理临时文件
make distclean  # 连 dist/ 一起清理
```

`make exe` 生成的是当前平台的可执行文件，不能借此在 macOS 上生成 Windows 的 `.exe`。Windows 上建议直接运行 `build_windows.bat`（系统默认不带 GNU Make）。

### 1. 生成 .pyxapp

macOS / Linux：

```bash
rm -rf build/TinyKnight
mkdir -p build/TinyKnight dist
cp main.py art.py build/TinyKnight/
python3 -m pyxel package build/TinyKnight build/TinyKnight/main.py
mv TinyKnight.pyxapp dist/
rm -rf build
```

Windows（在项目根目录执行）：

```bat
if exist build\TinyKnight rmdir /S /Q build\TinyKnight
mkdir build\TinyKnight
copy /Y main.py build\TinyKnight\
copy /Y art.py build\TinyKnight\
python -m pyxel package build\TinyKnight build\TinyKnight\main.py
if not exist dist mkdir dist
move /Y TinyKnight.pyxapp dist\
rmdir /S /Q build
```

产物：`dist/TinyKnight.pyxapp`。

`pyxel package` 会读取 `main.py` 顶部的 `# title:`、`# desc:`、`# version:` 注释，把它们写进应用信息；修改这些注释即可改变打包后的标题和说明。

运行方式（需要已安装 Pyxel）：

```bash
python3 -m pyxel play dist/TinyKnight.pyxapp
```

### 2. 生成网页版 HTML

从 `.pyxapp` 生成：

```bash
python3 -m pyxel app2html dist/TinyKnight.pyxapp
mv TinyKnight.html dist/
```

Windows 下把 `python3` 换成 `python`，最后一行换成 `move /Y TinyKnight.html dist\`。

产物：`dist/TinyKnight.html`，单文件，游戏代码和素材以 base64 内嵌。Pyxel Web 运行时（Pyodide）不内嵌，而是从 CDN 加载，所以**首次打开需要联网**，加载会停留一段时间并显示点击提示，点一下画面才开始。

推荐用本地服务器打开，避免浏览器对本地文件的限制：

```bash
python3 -m http.server 8000 --directory dist
```

然后访问 <http://localhost:8000/TinyKnight.html>。直接双击 HTML 通常也可以。

浏览器不能写本地文件，因此网页版最高分只在当前页面内有效，刷新后会清零；其余玩法与桌面版一致。

### 3. 生成 Windows EXE

PyInstaller 无法跨平台编译，所以 Windows 的 `.exe` 必须在 Windows 上生成。项目附带了 `build_windows.bat`，它会自动完成打包、生成 EXE 和整理 `dist` 目录。

在 Windows 上执行：

```bat
pip install pyxel pyinstaller
build_windows.bat
```

产物：

```text
dist\TinyKnight\TinyKnight.exe   ← 可执行文件
dist\TinyKnight\...              ← 依赖文件和 pyxapp
```

PyInstaller 使用“文件夹”模式，**分发时请把整个 `dist\TinyKnight` 文件夹压缩发送**，只复制 exe 无法运行。

等价的命令行步骤：

```bat
if exist build\TinyKnight rmdir /S /Q build\TinyKnight
mkdir build\TinyKnight
copy /Y main.py build\TinyKnight\
copy /Y art.py build\TinyKnight\
python -m pyxel package build\TinyKnight build\TinyKnight\main.py
python -m pyxel app2exe TinyKnight.pyxapp
if not exist dist mkdir dist
move /Y TinyKnight.pyxapp dist\
if exist dist\TinyKnight rmdir /S /Q dist\TinyKnight
move /Y TinyKnight dist\
```

如果提示 `Pyinstaller is not found. Please install it.`，说明 PyInstaller 未安装或不在当前 Python 环境中，重新执行 `python -m pip install pyinstaller` 即可。`app2exe` 会清除项目根目录下的 `build` 临时目录，这是正常现象。

### 4. 生成 macOS / Linux 可执行文件

在目标系统上安装 PyInstaller 后，执行与 Windows 相同的流程：

```bash
python3 -m pyxel app2exe dist/TinyKnight.pyxapp
```

得到的是适合当前系统和 CPU 架构的可执行文件（macOS 通常是一个 `.app` 或可执行文件夹），不是 Windows 的 `.exe`。PyInstaller 只能生成当前平台的文件，Apple Silicon 和 Intel 也需要分别打包；要发布 Windows 版仍然要在 Windows 上构建。

### 5. 用 GitHub Actions 打多平台包

`.github/workflows/package.yml` 会在 GitHub 托管的三台机器上分别打包，不需要本机安装对应系统：

| 产物 | 平台 |
| --- | --- |
| `TinyKnight-windows-x64.zip` | Windows x64，解压后运行整个 `TinyKnight` 文件夹里的 `TinyKnight.exe` |
| `TinyKnight-linux-x64.zip` | Linux x64，解压后运行 `TinyKnight/TinyKnight` |
| `TinyKnight-macos-arm64.zip` | macOS Apple Silicon，解压后打开 `TinyKnight.app` |
| `TinyKnight.pyxapp` / `TinyKnight.html` | 与系统无关，可直接分享 |

推送版本标签后会自动构建，并把上面的文件挂到对应的 GitHub Release：

```bash
git tag v1.0.0
git push origin v1.0.0
```

不想发 Release 时，也可以在仓库的 Actions 页面手动运行「多平台打包」，完成后从该次运行的 Artifacts 下载。GitHub 免费托管机器没有 Intel 版 macOS，所以这里不生成 Intel Mac 包。macOS 包未签名，首次打开若被系统拦截，在访达里右键应用并选择“打开”。

### 6. 重新生成与清理

- 修改 `main.py` 或 `art.py` 后，必须重新执行 `pyxel package`，再重新生成 HTML / EXE；直接改 `dist` 里的文件不会生效。用 Makefile 时执行 `make -B dist` 可强制全部重建。
- `build/` 只是打包时的临时目录，可以随时删除；`make clean` 会清理它、Python 缓存和 PyInstaller 的临时文件。
- `dist/` 中的产物也可以删除后重新生成；`make distclean` 会连同 `dist/` 一起删除。
- `.gitignore` 忽略缓存、`build/`、PyInstaller 临时产物和 `highscore.txt`，但保留 `dist/TinyKnight.html` 与 `dist/TinyKnight.pyxapp` 这两个可直接分享的小文件。
- 打包版如果把最高分写到了用户数据目录，卸载游戏时不会自动删除；需要的话手动清理：
  - Windows：`%APPDATA%\TinyKnight\highscore.txt`
  - macOS：`~/Library/Application Support/TinyKnight/highscore.txt`
  - Linux：`~/.local/share/TinyKnight/highscore.txt`

## 项目结构

```text
test-game/
├── main.py             # 游戏循环、玩家/敌人逻辑、波次、HUD、状态机、音效
├── art.py              # 调色板、精灵图、点阵字体、地面与场景装饰的生成
├── README.md           # 本文件
├── requirements.txt    # 依赖
├── Makefile            # 一键构建：run / app / web / dist / exe / clean
├── build_windows.bat   # 在 Windows 上一键打包 EXE
├── .github/workflows/package.yml  # GitHub Actions：Windows / Linux / macOS 打包
├── .gitignore          # 忽略缓存、临时构建和本地存档
├── dist/
│   ├── TinyKnight.html   # 已生成的网页版
│   └── TinyKnight.pyxapp # 已生成的 Pyxel 应用包
└── highscore.txt       # 源码运行后自动生成
```

### 主要文件说明

- `main.py`
  - 常量区：移动速度、攻击范围/冷却、冲刺参数、无敌帧、敌人属性等。
  - `Game`：状态机（标题 / 游戏 / 暂停 / 结束）、波次编排、摄像机、粒子与屏幕震动、音频。
  - `Player` / `Enemy` / `Arrow` / `HeartPickup`：各自的更新与绘制。
- `art.py`
  - `PALETTE`：自定义的 16 色调色板，偏暖、自然。
  - 精灵图使用字符串逐像素定义，启动时写入 `pyxel.Image`。
  - `Art._build_floor()` 在启动时把整个 640 × 480 的地面（草地、泥土十字路、石质广场、围墙）预渲染到一张图里。
  - `draw_font()`：用于大标题和波次横幅的 3 × 5 点阵字体。

## 调整与扩展

想改难度或手感，直接修改 `main.py` 顶部的常量即可，例如：

```python
PLAYER_SPEED = 1.55   # 玩家移动速度
PLAYER_MAX_HP = 5     # 最大生命
ATTACK_RADIUS = 30    # 挥剑判定半径
DASH_CD = 46          # 冲刺冷却（帧）
IFRAMES_HURT = 72     # 受伤后的无敌帧
```

- 波次构成在 `Game.build_spawners()`：
  - 史莱姆数量 `min(3 + wave, 12)`
  - 第 2 波起加入蝙蝠
  - 第 3 波起加入弓箭手
- 敌人属性在 `ENEMY_INFO`。
- 地面和装饰在 `art.py`；`ARENA_W` / `ARENA_H` 同时影响逻辑与生成，改动后建议重新检查出生点和围墙。
- 调色板必须保持 16 个颜色（Pyxel 的索引是 0–15）。

## 素材与许可

- 游戏中的全部图像、字体与音效均由代码实时生成，没有使用任何第三方美术或音频文件，可自由使用、修改和再发布。
- 游戏引擎 Pyxel 采用 MIT 许可证，详见其项目主页。

祝你玩得开心，活得比上一局更久。
