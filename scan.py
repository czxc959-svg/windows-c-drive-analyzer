"""
================================================================================
  C 盘磁盘空间扫描分析工具 | C Drive Disk Space Analyzer
  版本: 1.0
  位置: D:\CDriveScan\scan.py
--------------------------------------------------------------------------------
  安全声明 (SAFETY NOTICE):
      本脚本对 C 盘执行完全只读操作。
      - 不会删除任何文件
      - 不会修改任何文件
      - 不会向 C 盘写入任何内容
      所有分析报告均保存在 D:\CDriveScan\reports\ 文件夹中。
      是否清理 C 盘，由用户自行决定。
================================================================================
"""

import os
import sys
import time
import datetime
import traceback
from collections import defaultdict
import webbrowser

# 强制使用 UTF-8 输出，防止中文路径乱码
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# ── 常量配置 ──────────────────────────────────────────────────────────────────
SCAN_ROOT    = "C:\\"
REPORT_DIR   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
TOP_N_FILES  = 50
TOP_N_FOLDERS= 30
MIN_FILE_SIZE= 1 * 1024 * 1024   # 1 MB
PROGRESS_EVERY = 5000

# ── 文件类型分类 ───────────────────────────────────────────────────────────────
FILE_CATEGORIES = {
    "视频":        {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".rmvb", ".ts"},
    "音频":        {".mp3", ".flac", ".wav", ".aac", ".ogg", ".m4a", ".wma"},
    "图片":        {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".ico"},
    "文档":        {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv"},
    "压缩包":      {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"},
    "磁盘镜像":    {".iso", ".img", ".vhd", ".vmdk", ".vdi"},
    "安装程序":    {".exe", ".msi", ".msix", ".appx"},
    "系统文件":    {".dll", ".sys", ".drv", ".cab", ".inf", ".dat"},
    "代码/项目":   {".py", ".js", ".ts", ".java", ".cpp", ".c", ".cs", ".go", ".json", ".xml"},
    "数据库":      {".db", ".sqlite", ".mdf", ".ldf", ".accdb"},
    "缓存/临时":   {".tmp", ".temp", ".cache", ".log", ".dmp", ".etl"},
}

def get_category(ext):
    ext = ext.lower()
    for cat, exts in FILE_CATEGORIES.items():
        if ext in exts:
            return cat
    return "其他"

def format_size(bytes_val):
    if bytes_val >= 1024**3:
        return f"{bytes_val / 1024**3:8.2f} GB"
    elif bytes_val >= 1024**2:
        return f"{bytes_val / 1024**2:8.2f} MB"
    elif bytes_val >= 1024:
        return f"{bytes_val / 1024:8.2f} KB"
    else:
        return f"{bytes_val:8d}  B"

def format_size_short(bytes_val):
    if bytes_val >= 1024**3:
        return f"{bytes_val / 1024**3:.2f} GB"
    elif bytes_val >= 1024**2:
        return f"{bytes_val / 1024**2:.2f} MB"
    else:
        return f"{bytes_val / 1024:.2f} KB"

def guess_app_name(filepath):
    """从文件路径推断所属应用程序名称"""
    parts = filepath.replace('/', '\\').split('\\')
    path_lower = filepath.lower()

    app_dirs = {'program files', 'program files (x86)', 'programdata'}
    appdata_subdirs = {'local', 'roaming', 'locallow'}
    skip_names = {'common files', 'microsoft shared', 'packages'}

    for i, part in enumerate(parts):
        pl = part.lower()
        if pl in app_dirs and i + 1 < len(parts):
            candidate = parts[i + 1]
            if candidate.lower() in skip_names and i + 2 < len(parts):
                return parts[i + 2]
            return candidate
        if pl == 'appdata' and i + 2 < len(parts):
            if parts[i + 1].lower() in appdata_subdirs:
                candidate = parts[i + 2]
                if candidate.lower() in skip_names and i + 3 < len(parts):
                    return parts[i + 3]
                return candidate

    if '\\windows\\' in path_lower or path_lower.startswith('c:\\windows'):
        return "Windows 系统"
    if '\\downloads\\' in path_lower:
        return "用户下载"
    if '\\desktop\\' in path_lower:
        return "用户桌面"
    if '\\documents\\' in path_lower:
        return "用户文档"

    return "未知"


# ─────────────────────────────────────────────────────────────────────────────
#  核心扫描函数（只读！）
# ─────────────────────────────────────────────────────────────────────────────
def scan_drive(root_path):
    folder_sizes   = defaultdict(int)
    all_files      = []
    category_sizes = defaultdict(int)
    error_paths    = []
    file_count     = 0
    total_size     = 0
    start_time     = time.time()

    print("\n" + "="*70)
    print(f"  开始扫描: {root_path}")
    print(f"  时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print("  [只读模式] 本脚本不会对 C 盘做任何修改或删除操作")
    print("="*70)
    print("  扫描进行中，请稍候...\n")

    for dirpath, dirnames, filenames in os.walk(root_path, topdown=True, followlinks=False):
        try:
            if os.path.islink(dirpath):
                dirnames.clear()
                continue
        except Exception:
            pass

        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                if os.path.islink(filepath):
                    continue
                stat = os.stat(filepath, follow_symlinks=False)
                size = stat.st_size
                ext  = os.path.splitext(filename)[1]
                cat  = get_category(ext)

                # 累计每一级父目录的大小
                cur = dirpath
                while True:
                    folder_sizes[cur] += size
                    parent = os.path.dirname(cur)
                    if parent == cur:
                        break
                    cur = parent

                if size >= MIN_FILE_SIZE:
                    all_files.append((filepath, size, ext))

                category_sizes[cat] += size
                total_size += size
                file_count += 1

                if file_count % PROGRESS_EVERY == 0:
                    elapsed = time.time() - start_time
                    short_path = dirpath[:65] + "..." if len(dirpath) > 65 else dirpath
                    print(f"  [{file_count:,} 个文件] [{elapsed:.0f}s] {short_path}")

            except PermissionError:
                error_paths.append(filepath)
            except FileNotFoundError:
                pass
            except Exception as e:
                error_paths.append(f"{filepath} ({type(e).__name__})")

    elapsed = time.time() - start_time
    print(f"\n  扫描完成！共 {file_count:,} 个文件，耗时 {elapsed:.1f} 秒。\n")
    return folder_sizes, all_files, category_sizes, error_paths, total_size, file_count


# ─────────────────────────────────────────────────────────────────────────────
#  报告生成
# ─────────────────────────────────────────────────────────────────────────────
def generate_report(folder_sizes, all_files, category_sizes,
                    error_paths, total_size, file_count, scan_root):
    os.makedirs(REPORT_DIR, exist_ok=True)
    ts          = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORT_DIR, f"report_{ts}.txt")

    lines = []
    def w(line=""):
        lines.append(line)
        print(line)

    w("=" * 80)
    w("   C 盘磁盘空间扫描分析报告")
    w(f"   扫描时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    w(f"   扫描路径: {scan_root}")
    w("=" * 80)

    # 1. 总览
    w()
    w("【1】总体概览")
    w("-" * 80)
    w(f"  总文件数    : {file_count:,} 个")
    w(f"  总占用空间  : {format_size_short(total_size)}")
    w(f"  访问受限路径: {len(error_paths):,} 个（系统保护目录，已跳过）")

    # 2. 文件类型分布
    w()
    w("【2】文件类型占用分布（按大小排序）")
    w("-" * 80)
    for cat, sz in sorted(category_sizes.items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(sz / total_size * 40) if total_size > 0 else ""
        pct = sz / total_size * 100 if total_size > 0 else 0
        w(f"  {cat:<12} {format_size(sz)}  {bar:<40} {pct:5.1f}%")

    # 3. 最大文件夹
    w()
    w(f"【3】占用空间最大的 {TOP_N_FOLDERS} 个文件夹")
    w("-" * 80)
    w(f"  {'排名':<4} {'大小':>10}  {'路径'}")
    w(f"  {'-'*4} {'-'*10}  {'-'*60}")
    sorted_folders = sorted(
        [(p, s) for p, s in folder_sizes.items() if p != scan_root and s > 0],
        key=lambda x: x[1], reverse=True
    )[:TOP_N_FOLDERS]
    for i, (path, sz) in enumerate(sorted_folders, 1):
        w(f"  {i:<4} {format_size(sz)}  {path}")

    # 4. 最大文件
    w()
    w("【4】占用空间最大的 100 个文件（按应用分组）")
    w("-" * 80)
    top_files = sorted(all_files, key=lambda x: x[1], reverse=True)
    
    filtered_top = []
    for path, sz, ext in top_files:
        app = guess_app_name(path)
        if app != "Windows 系统":
            filtered_top.append((path, sz, ext, app))
            
    filtered_top = filtered_top[:100]
    
    app_groups_rpt = defaultdict(list)
    for path, sz, ext, app in filtered_top:
        app_groups_rpt[app].append((path, sz, ext))
        
    sorted_groups = sorted(app_groups_rpt.items(), key=lambda x: sum(s for _,s,_ in x[1]), reverse=True)
    rank = 1
    for app, files in sorted_groups:
        group_total = sum(s for _,s,_ in files)
        w(f"  \u250c\u2500 {app}\uff08\u5171 {format_size_short(group_total)}\uff0c{len(files)} \u4e2a\u6587\u4ef6\uff09")
        for path, sz, ext in files:
            w(f"  \u2502  {rank:<3} {format_size(sz)}  {get_category(ext):<8}  {path}")
            rank += 1
        w("  \u2514" + "\u2500" * 75)
        w()
    w()
    w("【5】可清理区域提示（仅供参考，是否清理请您自行决定）")
    w("-" * 80)
    suggestions = [
        ("临时文件",     r"C:\Users", "AppData\\Local\\Temp",
         "Windows 临时文件，通常可安全清理。按 Win+R 输入 %temp% 打开后全选删除。"),
        ("NVIDIA着色器", r"C:\Users", "AppData\\LocalLow\\NVIDIA\\PerDriverVersion\\DXCache",
         "显卡缓存，删除后游戏启动时会自动重新生成，不影响正常使用。"),
        ("Chrome 缓存",  r"C:\Users", "AppData\\Local\\Google\\Chrome",
         "建议在 Chrome 浏览器内按 Ctrl+Shift+Del 清理，不要直接删除文件夹。"),
        ("WPS 缓存",     r"C:\Users", "AppData\\Roaming\\kingsoft",
         "WPS Office 的插件和缓存文件，可通过 WPS 软件内设置清理。"),
        ("Windows更新",  r"C:\Windows", "SoftwareDistribution\\Download",
         "旧版更新包，可通过「磁盘清理」中的「Windows 更新清理」安全删除。"),
        ("回收站",       r"C:\$Recycle.Bin", "",
         "直接右键桌面回收站 -> 清空回收站 即可。"),
        ("💡 快速打开隐藏路径 (如 AppData)", "", "",
         "由于 AppData 等系统目录默认隐藏，最快的方法是：选中报告中的路径前半部分（如 C:\\Users\\用户名\\AppData\\...），\n"
         "    右键复制，然后打开任意文件夹，将路径【粘贴到顶部的地址栏】按回车即可直达！"),
    ]
    for name, base, sub, tip in suggestions:
        full_path = os.path.join(base, sub) if sub else base
        sz = folder_sizes.get(full_path)
        sz_str = format_size_short(sz) if sz else "（路径含用户名，请手动核查）"
        w(f"  ► {name}")
        w(f"    参考路径: {full_path}")
        w(f"    参考大小: {sz_str}")
        w(f"    建议    : {tip}")
        w()

    # 6. 受限路径
    if error_paths:
        w(f"【6】无权访问的路径（共 {len(error_paths):,} 个，已跳过）")
        w("-" * 80)
        for p in error_paths[:30]:
            w(f"  ⚠  {p}")
        if len(error_paths) > 30:
            w(f"  ... 另有 {len(error_paths)-30} 个（见完整报告文件）")
        w()

    w("=" * 80)
    w("  重要提示：本报告仅供参考，脚本未对 C 盘做任何修改。")
    w("  清理前请仔细确认文件用途，避免误删重要文件。")
    w(f"  完整报告已保存至: {report_path}")
    w("=" * 80)

    # 报告写入 D 盘（不写 C 盘）
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return report_path

def generate_html_report(folder_sizes, all_files, category_sizes,
                         error_paths, total_size, file_count, scan_root):
    """生成 HTML 格式的可视化分析报告"""
    import html as html_mod
    os.makedirs(REPORT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    html_path = os.path.join(REPORT_DIR, f"report_{ts}.html")
    now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    top_files = sorted(all_files, key=lambda x: x[1], reverse=True)
    app_groups = defaultdict(list)
    for path, sz, ext in top_files:
        app = guess_app_name(path)
        app_groups[app].append((path, sz, ext))
    sorted_app_groups = sorted(app_groups.items(), key=lambda x: sum(s for _,s,_ in x[1]), reverse=True)

    sorted_folders = sorted(
        [(p, s) for p, s in folder_sizes.items() if p != scan_root and s > 0],
        key=lambda x: x[1], reverse=True
    )[:TOP_N_FOLDERS]

    sorted_cats = sorted(category_sizes.items(), key=lambda x: x[1], reverse=True)

    cat_colors = {
        "视频": "#e74c3c", "音频": "#e67e22", "图片": "#f1c40f",
        "文档": "#2ecc71", "压缩包": "#3498db", "磁盘镜像": "#9b59b6",
        "安装程序": "#e91e63", "系统文件": "#607d8b", "代码/项目": "#00bcd4",
        "数据库": "#8bc34a", "缓存/临时": "#ff9800", "其他": "#95a5a6",
    }

    cat_rows = ""
    for cat, sz in sorted_cats:
        pct = sz / total_size * 100 if total_size > 0 else 0
        color = cat_colors.get(cat, "#95a5a6")
        cat_rows += '<tr>'
        cat_rows += '<td><span class="badge" style="background:' + color + '">' + html_mod.escape(cat) + '</span></td>'
        cat_rows += '<td>' + format_size_short(sz) + '</td>'
        cat_rows += '<td style="width:50%"><div class="bar-bg"><div class="bar-fill" style="width:' + f"{pct:.1f}" + '%;background:' + color + '"></div></div></td>'
        cat_rows += '<td class="num">' + f"{pct:.1f}" + '%</td>'
        cat_rows += '</tr>\n'

    folder_rows = ""
    for i, (path, sz) in enumerate(sorted_folders, 1):
        pct = sz / total_size * 100 if total_size > 0 else 0
        folder_rows += '<tr>'
        folder_rows += '<td class="num">' + str(i) + '</td>'
        folder_rows += '<td class="num">' + format_size_short(sz) + '</td>'
        folder_rows += '<td class="path">' + html_mod.escape(path) + '</td>'
        folder_rows += '<td class="num">' + f"{pct:.1f}" + '%</td>'
        folder_rows += '</tr>\n'

    app_sections = ""
    for app, files in sorted_app_groups:
        group_total = sum(s for _,s,_ in files)
        file_rows = ""
        
        display_files = []
        hidden_files = []
        for path, sz, ext in files:
            cat = get_category(ext)
            if app == "Windows 系统":
                hidden_files.append((path, sz, ext, cat))
            else:
                display_files.append((path, sz, ext, cat))
                
        visible_files = display_files[:20]
        extra_files = display_files[20:]
        
        for path, sz, ext, cat in visible_files:
            color = cat_colors.get(cat, "#95a5a6")
            file_rows += '<tr>'
            file_rows += '<td class="num">' + format_size_short(sz) + '</td>'
            file_rows += '<td><span class="badge sm" style="background:' + color + '">' + html_mod.escape(cat) + '</span></td>'
            file_rows += '<td class="path">' + html_mod.escape(path) + '</td>'
            file_rows += '</tr>\n'
            
        merged_count = len(extra_files) + len(hidden_files)
        if merged_count > 0:
            merged_sz = sum(s for _,s,_,_ in extra_files) + sum(s for _,s,_,_ in hidden_files)
            file_rows += '<tr>'
            file_rows += '<td class="num">' + format_size_short(merged_sz) + '</td>'
            file_rows += '<td><span class="badge sm" style="background:#555">合并折叠</span></td>'
            file_rows += '<td class="path" style="color:#888; font-style:italic">📦 还有 ' + str(merged_count) + ' 个较小文件或系统底层文件...</td>'
            file_rows += '</tr>\n'

        app_sections += '<details><summary>'
        app_sections += '<span class="app-name">' + html_mod.escape(app) + '</span>'
        app_sections += '<span class="app-meta">' + format_size_short(group_total) + ' &middot; ' + str(len(files)) + ' 个文件</span>'
        app_sections += '</summary>'
        app_sections += '<table class="file-table"><thead><tr><th>大小</th><th>类型</th><th>文件路径</th></tr></thead>'
        app_sections += '<tbody>' + file_rows + '</tbody></table></details>\n'

    css = """*{margin:0;padding:0;box-sizing:border-box}
body{background:linear-gradient(135deg,#0f0c29,#1a1a2e,#16213e);color:#e0e0e0;font-family:'Segoe UI',system-ui,sans-serif;min-height:100vh;padding:20px}
.container{max-width:1100px;margin:0 auto}
h1{text-align:center;font-size:2em;margin:30px 0 5px;background:linear-gradient(90deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:700}
.subtitle{text-align:center;color:#888;margin-bottom:30px;font-size:0.95em}
.card{background:rgba(255,255,255,0.05);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:28px;margin:20px 0;transition:transform 0.2s}
.card:hover{transform:translateY(-2px);border-color:rgba(255,255,255,0.15)}
.card h2{font-size:1.3em;margin-bottom:18px;color:#fff;display:flex;align-items:center;gap:10px}
.card h2 .icon{font-size:1.4em}
.overview{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px}
.stat{background:rgba(255,255,255,0.04);border-radius:12px;padding:20px;text-align:center}
.stat .val{font-size:2em;font-weight:700;background:linear-gradient(135deg,#667eea,#764ba2);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.stat .label{color:#999;font-size:0.85em;margin-top:6px}
table{width:100%;border-collapse:collapse;font-size:0.9em}
th{text-align:left;padding:10px 12px;border-bottom:2px solid rgba(255,255,255,0.1);color:#999;font-weight:600;font-size:0.85em;text-transform:uppercase;letter-spacing:0.5px}
td{padding:8px 12px;border-bottom:1px solid rgba(255,255,255,0.04)}
tr:hover td{background:rgba(255,255,255,0.03)}
.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
.path{font-family:'Cascadia Code','Consolas',monospace;font-size:0.85em;color:#b0b0b0;word-break:break-all}
.badge{display:inline-block;padding:3px 10px;border-radius:20px;font-size:0.8em;color:#fff;font-weight:500}
.badge.sm{padding:2px 8px;font-size:0.75em}
.bar-bg{background:rgba(255,255,255,0.08);border-radius:6px;height:22px;overflow:hidden}
.bar-fill{height:100%;border-radius:6px;transition:width 1s ease}
details{background:rgba(255,255,255,0.03);border-radius:12px;margin:10px 0;border:1px solid rgba(255,255,255,0.05);overflow:hidden}
details[open]{border-color:rgba(102,126,234,0.3)}
summary{padding:14px 18px;cursor:pointer;display:flex;align-items:center;gap:12px;font-weight:500;transition:background 0.2s}
summary:hover{background:rgba(255,255,255,0.05)}
summary::marker{color:#667eea}
.app-name{font-size:1.05em;color:#fff}
.app-meta{color:#888;font-size:0.85em;margin-left:auto}
.file-table{margin:0}.file-table th{padding:8px 18px}.file-table td{padding:6px 18px}
.safety{background:rgba(46,204,113,0.08);border:1px solid rgba(46,204,113,0.2);border-radius:12px;padding:20px;margin:20px 0;text-align:center;color:#2ecc71}
.footer{text-align:center;color:#666;font-size:0.85em;padding:30px 0}"""

    js = """document.addEventListener('DOMContentLoaded',function(){document.querySelectorAll('.bar-fill').forEach(function(b){var w=b.style.width;b.style.width='0';requestAnimationFrame(function(){b.style.width=w})})});"""

    html_out = '<!DOCTYPE html>\n<html lang="zh-CN"><head><meta charset="UTF-8">\n'
    html_out += '<meta name="viewport" content="width=device-width,initial-scale=1.0">\n'
    html_out += '<title>C盘空间分析报告 - ' + now_str + '</title>\n'
    html_out += '<style>' + css + '</style></head><body><div class="container">\n'
    html_out += '<h1>C 盘磁盘空间扫描分析报告</h1>\n'
    html_out += '<p class="subtitle">扫描时间：' + now_str + '&emsp;&middot;&emsp;扫描路径：' + html_mod.escape(scan_root) + '</p>\n'

    html_out += '<div class="card"><h2><span class="icon">&#x1F4CA;</span> 总体概览</h2><div class="overview">'
    html_out += '<div class="stat"><div class="val">' + f"{file_count:,}" + '</div><div class="label">文件总数</div></div>'
    html_out += '<div class="stat"><div class="val">' + format_size_short(total_size) + '</div><div class="label">总占用空间</div></div>'
    html_out += '<div class="stat"><div class="val">' + f"{len(error_paths):,}" + '</div><div class="label">受限路径（已跳过）</div></div>'
    html_out += '</div></div>\n'

    html_out += '<div class="card"><h2><span class="icon">&#x1F4C1;</span> 文件类型占用分布</h2>'
    html_out += '<table><thead><tr><th>类型</th><th>大小</th><th>占比</th><th></th></tr></thead>'
    html_out += '<tbody>' + cat_rows + '</tbody></table></div>\n'

    html_out += '<div class="card"><h2><span class="icon">&#x1F4C2;</span> 占用最大的 ' + str(TOP_N_FOLDERS) + ' 个文件夹</h2>'
    html_out += '<table><thead><tr><th>#</th><th>大小</th><th>路径</th><th>占比</th></tr></thead>'
    html_out += '<tbody>' + folder_rows + '</tbody></table></div>\n'

    html_out += '<div class="card"><h2><span class="icon">&#x1F50D;</span> 所有文件（>= 1 MB） — 按应用分组</h2>'
    html_out += '<p style="color:#888;font-size:0.9em;margin-bottom:8px">点击应用名称可以展开/折叠文件列表</p>'
    html_out += '<div style="background:rgba(102,126,234,0.1);border-left:4px solid #667eea;padding:12px 16px;border-radius:0 8px 8px 0;margin-bottom:20px;font-size:0.9em;color:#d0d0d0;line-height:1.6;">'
    html_out += '<strong>💡 小贴士：如何快速找到 AppData 等隐藏文件夹？</strong><br>'
    html_out += '最快的方法是：鼠标选中文件路径的前半部分（例如 <code>C:\\Users\\用户名\\AppData\\Roaming\\...</code>），<strong>右键复制</strong>，然后打开任意文件夹，将路径<strong>粘贴到顶部的地址栏</strong>中并按回车键，即可瞬间直达目标文件夹！'
    html_out += '</div>'
    html_out += app_sections + '</div>\n'

    html_out += '<div class="safety">&#x1F512; 本工具严格只读，未对 C 盘做任何修改。扫描报告仅供参考，清理前请仔细确认文件用途。</div>\n'
    html_out += '<div class="footer">C Drive Disk Space Analyzer &middot; ' + now_str + '</div>\n'
    html_out += '</div><script>' + js + '</script></body></html>'

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_out)

    return html_path




# ─────────────────────────────────────────────────────────────────────────────
#  主程序
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print(__doc__)
    print("  按 Enter 开始扫描，或按 Ctrl+C 退出...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n  已取消。")
        return

    try:
        folder_sizes, all_files, category_sizes, error_paths, total_size, file_count = \
            scan_drive(SCAN_ROOT)
        generate_report(
            folder_sizes, all_files, category_sizes,
            error_paths, total_size, file_count, SCAN_ROOT
        )

        html_path = generate_html_report(
            folder_sizes, all_files, category_sizes,
            error_paths, total_size, file_count, SCAN_ROOT
        )
        print(f"\n  HTML \u53ef\u89c6\u5316\u62a5\u544a\u5df2\u4fdd\u5b58\u81f3: {html_path}")
        print("  提示：请前往 reports 文件夹查看生成的分析报告。")
    except KeyboardInterrupt:
        print("\n\n  扫描被用户中断。")
    except Exception as e:
        print(f"\n  发生错误: {e}")
        traceback.print_exc()

    print("\n  按 Enter 退出...")
    try:
        input()
    except Exception:
        pass

if __name__ == "__main__":
    main()
