# LLM Provider Monitor

多 LLM Provider 余额监控与模型查询桌面工具。

![app-screenshot](./screenshot.png)

---

## 功能

- **余额监控** — 同时展示 Kimi、DeepSeek、SiliconFlow 三个平台的余额信息
- **模型查询** — 查看每个平台可用的模型列表，支持搜索过滤，点击模型名自动复制到剪贴板
- **自动刷新** — 余额按用户设定的周期自动轮询；模型列表每 5 分钟后台静默刷新
- **手动刷新** — 一键刷新余额 + 模型缓存

## 界面

**主窗口 560×340，固定尺寸不可缩放：**

```
┌─ LLM Provider Monitor ────── [⚙] [⟳] ─┐
│                                          │
│ Kimi              [📋 查看模型]          │
│ ──────────────────────────────────────── │
│ ¥48.71  可用余额 ¥48.71  现金 ¥48.71 ... │
│                                          │
│ DeepSeek           [📋 查看模型]          │
│ ──────────────────────────────────────── │
│ ¥45.35  总余额 ¥45.35  充值 ¥45.35 ...   │
│                                          │
│ SiliconFlow        [📋 查看模型]          │
│ ──────────────────────────────────────── │
│ ¥45.83  总余额 ¥45.83  充值 ¥45.83 ...   │
├──────────────────────────────────────────┤
│     上次刷新 12:30:45    自动刷新 60s     │
└──────────────────────────────────────────┘
```

- 主窗口：工具栏（标题 + 设置/刷新按钮）→ 卡片区（3 个 Provider）× 状态栏
- 设置弹窗：API Key 配置（支持 👁 明文/密文切换）+ 刷新周期 + 自动刷新开关
- 模型弹窗：搜索输入框（带 ✕ 一键清除）+ 滚动模型列表（点击复制）

## 支持的 Provider

| Provider | Base URL | 余额接口 | 模型接口 |
|---|---|---|---|
| Kimi | `api.moonshot.cn` | `GET /v1/users/me/balance` | `GET /v1/models` |
| DeepSeek | `api.deepseek.com` | `GET /user/balance` | `GET /models` |
| SiliconFlow | `api.siliconflow.cn` | `GET /v1/user/info` | `GET /v1/models` |

## 配置

配置文件自动生成，位置：

| 系统 | 路径 |
|---|---|
| Windows | `%APPDATA%\LLMProviderMon\config.json` |
| Linux | `~/.config/LLMProviderMon/config.json` |

通过界面 ⚙ **设置** 按钮配置：

- **API Key** — 三个 Provider 各自的密钥
- **刷新周期** — 余额自动拉取的间隔（秒）
- **自动刷新** — 启用/关闭定时轮询

## 项目结构

```
provider/
├── main.py                   # 入口
├── requirements.txt          # 依赖清单
├── config/
│   └── manager.py            # 配置读写
├── providers/
│   ├── __init__.py            # 工厂函数
│   ├── base.py                # 抽象基类
│   ├── kimi.py                # Kimi
│   ├── deepseek.py            # DeepSeek
│   └── siliconflow.py         # SiliconFlow
└── ui/
    ├── app.py                 # 主窗口
    ├── provider_card.py       # Provider 卡片
    ├── model_dialog.py        # 模型列表弹窗
    └── settings_dialog.py     # 设置弹窗
```

## 开发运行

```bash
pip install -r requirements.txt
python main.py
```

---

## 编译为独立可执行文件

### Windows (生成 .exe)

在 Windows 上安装 Python 后执行：

```powershell
pip install pyinstaller customtkinter requests
cd provider
pyinstaller --onedir --windowed --collect-all customtkinter --name "LLMProviderMon" main.py
```

也可直接运行项目中的 `build.bat`。

生成文件在 `dist\LLMProviderMon\LLMProviderMon.exe`，双击运行。

**单文件版（启动略慢）：**

```powershell
pyinstaller --onefile --windowed --collect-all customtkinter --name "LLMProviderMon" main.py
```

生成 `dist\LLMProviderMon.exe`。

### Linux

```bash
pip install pyinstaller
cd provider
./build.sh
```

生成文件在 `dist/LLMProviderMon/LLMProviderMon`。

### CLI 参数说明

| 参数 | 说明 |
|---|---|
| `--onedir` | 目录模式，生成文件夹，启动快 |
| `--onefile` | 单文件模式，启动时自解压稍慢 |
| `--windowed` | GUI 模式，不弹控制台窗口 |
| `--collect-all customtkinter` | 包含 customtkinter 全部资源（必须） |
| `--name "LLMProviderMon"` | 输出文件名 |
