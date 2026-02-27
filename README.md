# 全屏桌面时钟（Windows）

一款 Windows 桌面时钟应用，支持全屏显示、正倒计时、文字样式自定义，以及仿磨砂玻璃功能栏。

## 功能特性

- 实时时钟显示（`HH:MM:SS`）
- `正计时（Count Up）` 与 `倒计时（Count Down）`
- 手动设置显示时间（`HH:MM:SS`）
- 自定义展示文字
- 样式面板：
  - 时间字号滑块 + 数字输入
  - 文字字号滑块 + 数字输入
  - RGB 颜色滑块 + 数字输入
- 背景自定义：
  - 可选择背景图或纯色背景
  - 背景缩放滑块（`20%` ~ `300%`）+ 数字输入
- 底部仿磨砂玻璃风格功能栏
- 模式显示集成在功能栏内
- 功能栏隐藏/显示：
  - 点击 `隐藏栏` 隐藏
  - 隐藏后保留一个箭头按钮用于恢复
- 支持切换全屏
- 支持打包单文件 `.exe`

## 项目文件

- `clock_app.py`：主程序源码
- `CHANGELOG.md`：版本记录
- `scripts/build_client.ps1`：打包脚本（客户端输出到 Downloads）

## 运行环境

- Python 3.12+
- Pillow（用于更完整的图片格式支持与高质量缩放）

安装依赖：

```powershell
py -3 -m pip install pillow
```

## 源码运行

```powershell
py -3 clock_app.py
```

## 打包 EXE

推荐（输出到 `Downloads`，且不在仓库保留构建垃圾）：

```powershell
.\scripts\build_client.ps1 -Version V0.8
```

## 快捷键

- `H`：帮助
- `B`：选择背景图片
- `C`：选择背景颜色
- `T`：编辑自定义文字
- `F`：打开样式面板
- `M`：切换模式
- `R`：重置计时
- `S`：暂停/继续计时
- `Esc`：退出全屏
- `Q`：退出程序

---

# Desktop Clock (Windows)

A Windows desktop clock app with fullscreen display, timing modes, customizable text styles, and a frosted-glass control bar.

## Features

- Real-time clock display (`HH:MM:SS`)
- `Count Up` and `Count Down` modes
- Set current displayed time manually (`HH:MM:SS`)
- Custom text content
- Text style panel:
  - Time font size slider + numeric input
  - Text font size slider + numeric input
  - RGB color sliders + numeric inputs
- Background customization:
  - Select image or solid color background
  - Background scale slider (`20%` to `300%`) + numeric input
- Bottom frosted-glass style toolbar
- Mode display integrated directly in toolbar
- Toolbar hide/show:
  - Click `隐藏栏` to hide
  - Keep only one arrow button to restore toolbar
- Fullscreen toggle
- Packaged single-file `.exe` support

## Project Files

- `clock_app.py`: main app source code
- `CHANGELOG.md`: version history
- `scripts/build_client.ps1`: build script (outputs client to Downloads)

## Requirements

- Python 3.12+
- Pillow (for robust image support and scaling)

Install dependencies:

```powershell
py -3 -m pip install pillow
```

## Run from Source

```powershell
py -3 clock_app.py
```

## Build EXE

Recommended (outputs to `Downloads` and keeps repo clean):

```powershell
.\scripts\build_client.ps1 -Version V0.8
```

## Shortcuts

- `H`: Help
- `B`: Select background image
- `C`: Select background color
- `T`: Edit custom text
- `F`: Open style panel
- `M`: Switch mode
- `R`: Reset timer
- `S`: Pause/Resume timer
- `Esc`: Exit fullscreen
- `Q`: Quit app
