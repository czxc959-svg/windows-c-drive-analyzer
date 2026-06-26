# C盘磁盘空间扫描分析工具
# C Drive Disk Space Analyzer

> 一款纯 Python 编写的 C 盘空间分析脚本，**只读扫描，不修改任何文件**。
> A read-only Python script to analyze disk space usage on your C: drive. It never modifies any file.

---

## 📋 功能 Features

- 扫描 C 盘全部文件，统计各文件夹和文件类型的占用大小
- 列出占用最大的前 50 个文件、前 30 个文件夹
- 提供可清理区域建议（临时文件、浏览器缓存、系统更新包等）
- 扫描结果保存为 `reports/report_日期时间.txt`

---

## ⚙️ 环境要求 Requirements

- **操作系统**：Windows 10 / 11
- **Python**：3.9 或以上版本（[下载地址](https://www.python.org/downloads/)）
- **无需安装任何第三方库**，只用 Python 标准库

---

## 🚀 使用方法 Usage

### 方法一：双击运行（推荐）
直接**双击 `运行扫描.bat`** 即可启动。

### 方法二：命令行
```bash
python scan.py
```

---

## 📂 文件结构 File Structure

```
CDriveScan/
├── scan.py          # 主扫描脚本
├── 运行扫描.bat      # Windows 一键启动文件
├── README.md        # 说明文档
└── reports/         # 扫描报告保存目录（自动生成）
    └── report_YYYYMMDD_HHMMSS.txt
```

---

## 🔒 安全声明 Safety Notice

本工具**严格只读**，不会：
- ❌ 删除任何文件 / Never deletes any file.
- ❌ 修改任何文件 / Never modifies any file.
- ❌ 向 C 盘写入任何内容 / Never writes any content to the C: drive.

> ⚠️ **免责声明 / Disclaimer**
> 1. **仅供参考**：本工具提供的扫描报告和“可清理区域提示”仅供参考，不作为绝对的安全清理依据。
> 2. **人工核对**：工具本身**不会**自动帮你清理或删除任何文件。如果您决定释放空间，请务必在手动删除文件前仔细确认文件用途，避免误删重要数据或系统文件。
> 3. **免责条款**：因用户自行手动删除文件导致的系统故障或数据丢失，本工具及作者不承担任何责任。
> 
> *The reports and cleanup suggestions provided by this tool are for reference only. The tool does not perform deletions. Please double-check before deleting any files manually. The author is not responsible for any data loss.*

扫描报告保存在脚本所在目录的 `reports/` 子文件夹中。

---

## 📊 报告内容 Report Contents

1. **总体概览** — 文件总数、总占用空间
2. **文件类型分布** — 视频、音频、图片、文档等各类型占比
3. **最大文件夹 Top 30** — 按大小排序
4. **最大文件 Top 50** — 1MB 以上的文件
5. **可清理建议** — 临时文件、系统缓存等清理提示

---

## 📝 许可 License

MIT License — 自由使用、修改、分发。
