"""
PDF 管理层摘要报告生成器
从 test_results 数据生成一份简洁专业的 PDF 报告，用于提交给老板/管理层查阅。

内容：
  1. 封面：标题、环境、日期、4 个关键指标大卡片
  2. 执行摘要：通过/失败/跳过 + 耗时指标（P95、TPS 等）
  3. 按模块统计：每模块通过/失败/跳过数量
  4. 失败用例清单：失败用例名 + 简要分析
"""
import math
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Optional

# macOS 系统黑体字体（支持中英文）
_FONT_PATH = "/System/Library/Fonts/STHeiti Medium.ttc"
_FONT_FALLBACK = "/System/Library/Fonts/STHeiti Light.ttc"


def _load_font(pdf):
    """加载中文字体，返回字体名称"""
    import os
    for path in [_FONT_PATH, _FONT_FALLBACK]:
        if os.path.exists(path):
            pdf.add_font("CJK", fname=path)
            return "CJK"
    # 降级：用 Helvetica（不支持中文，中文会丢失但不报错）
    return "Helvetica"


def generate_pdf_summary(
    results: List[Dict],
    output_path: str,
    env: str = "DEV",
    core: str = "actc"
) -> bool:
    """
    根据 test_results 数据生成 PDF 摘要报告。

    Args:
        results: conftest.py 中 sorted_results 数据
        output_path: 输出 PDF 文件路径
        env: 测试环境名称
        core: core 名称
    Returns:
        bool: 是否生成成功
    """
    try:
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
    except ImportError:
        raise ImportError("请先安装 fpdf2：pip install fpdf2")

    # ── 数据统计 ─────────────────────────────────────────────────────
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "passed")
    failed = sum(1 for r in results if r.get("status") == "failed")
    skipped = sum(1 for r in results if r.get("status") == "skipped")
    pass_rate = round(passed / total * 100, 1) if total > 0 else 0

    # Wall time（真实挂钟耗时）
    durations = [float(r.get("duration") or 0) for r in results]
    start_times = []
    max_t_item = None
    for r in results:
        t = r.get("start_time", "")
        if t:
            try:
                dt = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                start_times.append(dt)
                if max_t_item is None or dt > datetime.strptime(max_t_item.get("start_time","1970-01-01 00:00:00"), "%Y-%m-%d %H:%M:%S"):
                    max_t_item = r
            except Exception:
                pass

    wall_time = 0.0
    if start_times:
        wall_time = (max(start_times) - min(start_times)).total_seconds()
        if max_t_item:
            wall_time += float(max_t_item.get("duration") or 0)

    avg_dur = sum(durations) / len(durations) if durations else 0
    sorted_durs = sorted(durations)
    p95_idx = max(0, math.ceil(len(sorted_durs) * 0.95) - 1)
    p95_dur = sorted_durs[p95_idx] if sorted_durs else 0
    min_dur = min(durations) if durations else 0
    max_dur = max(durations) if durations else 0
    tps = round(total / wall_time, 2) if wall_time > 0 else 0

    # 按模块统计
    module_stats: Dict[str, Dict] = defaultdict(lambda: {"passed": 0, "failed": 0, "skipped": 0})
    for r in results:
        m = r.get("module", "Unknown")
        s = r.get("status", "unknown")
        if s in ("passed", "failed", "skipped"):
            module_stats[m][s] += 1

    # 失败用例
    failed_cases = [r for r in results if r.get("status") == "failed"]

    report_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    report_date = datetime.now().strftime("%Y-%m-%d")

    # ── 初始化 PDF ───────────────────────────────────────────────────
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    font = _load_font(pdf)

    # TTC 字体只有 regular，Bold/Italic 降级用 Helvetica
    def S(size): pdf.set_font(font, size=size)
    def SB(size): pdf.set_font(font, size=size)   # bold 用 regular 替代
    def SI(size): pdf.set_font(font, size=size)   # italic 用 regular 替代

    def colored_cell(w, h, txt, r, g, b, fill=False, border=0, align="L"):
        pdf.set_text_color(r, g, b)
        pdf.cell(w, h, txt, border=border, align=align, fill=fill,
                 new_x=XPos.RIGHT, new_y=YPos.TOP)

    def new_line(h=5):
        pdf.ln(h)

    # ════════════════════════════════════════════════════════════════
    # 封面页
    # ════════════════════════════════════════════════════════════════
    pdf.add_page()

    # 顶部深蓝色横幅
    pdf.set_fill_color(30, 55, 153)
    pdf.rect(0, 0, 210, 50, "F")

    # 主标题
    SB(20)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(0, 12)
    pdf.cell(210, 12, "API Automation Test Report", align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # 副标题
    S(11)
    pdf.set_xy(0, 28)
    pdf.cell(210, 8,
             f"Env: {env.upper()}   Core: {core}   Date: {report_time}",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── 4 个关键指标卡片 ──────────────────────────────────────────
    card_y = 60
    cards = [
        ("Total Cases",  f"{total}",        (47, 84, 235),   (235, 240, 255)),
        ("Pass Rate",    f"{pass_rate}%",
         (82, 196, 26) if pass_rate >= 80 else (245, 34, 45),
         (240, 255, 240) if pass_rate >= 80 else (255, 240, 240)),
        ("Failed",       f"{failed}",
         (245, 34, 45) if failed > 0 else (82, 196, 26),
         (255, 240, 240) if failed > 0 else (240, 255, 240)),
        ("Wall Time",    f"{wall_time:.1f}s", (114, 46, 209), (245, 240, 255)),
    ]
    cw = 44
    cx = 11
    for i, (label, value, fg, bg) in enumerate(cards):
        x = cx + i * (cw + 3)
        pdf.set_fill_color(*bg)
        pdf.rect(x, card_y, cw, 32, "F")
        pdf.set_fill_color(*fg)
        pdf.rect(x, card_y, 3, 32, "F")
        # 数值
        SB(20)
        pdf.set_text_color(*fg)
        pdf.set_xy(x + 5, card_y + 4)
        pdf.cell(cw - 7, 14, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        # 标签
        S(9)
        pdf.set_text_color(80, 80, 80)
        pdf.set_xy(x + 5, card_y + 20)
        pdf.cell(cw - 7, 7, label, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── 次级指标行 ────────────────────────────────────────────────
    pdf.set_fill_color(245, 247, 255)
    pdf.set_draw_color(200, 210, 255)
    pdf.set_xy(11, card_y + 40)
    S(9)
    pdf.set_text_color(60, 60, 60)
    metrics_txt = (
        f"  Passed: {passed}  |  Failed: {failed}  |  Skipped: {skipped}  |  "
        f"Avg: {avg_dur:.2f}s  |  P95: {p95_dur:.2f}s  |  "
        f"Min: {min_dur:.2f}s  |  Max: {max_dur:.2f}s  |  TPS: {tps}"
    )
    pdf.cell(188, 9, metrics_txt, border=1, fill=True,
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── 通过/失败进度条 ───────────────────────────────────────────
    bar_y = card_y + 58
    bar_x = 11
    bar_w = 188
    bar_h = 8
    pdf.set_fill_color(220, 220, 220)
    pdf.rect(bar_x, bar_y, bar_w, bar_h, "F")
    if total > 0:
        pass_w = bar_w * passed / total
        fail_w = bar_w * failed / total
        skip_w = bar_w * skipped / total
        x = bar_x
        if pass_w > 0:
            pdf.set_fill_color(82, 196, 26)
            pdf.rect(x, bar_y, pass_w, bar_h, "F")
            x += pass_w
        if fail_w > 0:
            pdf.set_fill_color(245, 34, 45)
            pdf.rect(x, bar_y, fail_w, bar_h, "F")
            x += fail_w
        if skip_w > 0:
            pdf.set_fill_color(250, 173, 20)
            pdf.rect(x, bar_y, skip_w, bar_h, "F")

    # 进度条标签
    S(8)
    pdf.set_text_color(80, 80, 80)
    pdf.set_xy(bar_x, bar_y + 10)
    pdf.cell(188, 6,
             f"■ Passed {pass_rate}%   ■ Failed {round(failed/total*100,1) if total else 0}%   ■ Skipped {round(skipped/total*100,1) if total else 0}%",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ════════════════════════════════════════════════════════════════
    # 第二页：模块统计
    # ════════════════════════════════════════════════════════════════
    pdf.add_page()
    _sec_title(pdf, font, "Test Results by Module")

    col_w = [85, 22, 22, 22, 22, 15]
    hdrs = ["Module", "Passed", "Failed", "Skipped", "Total", "Rate"]
    _tbl_hdr(pdf, font, hdrs, col_w)

    for module, stats in sorted(module_stats.items()):
        m_total = stats["passed"] + stats["failed"] + stats["skipped"]
        m_rate = f"{round(stats['passed']/m_total*100)}%" if m_total > 0 else "-"

        if stats["failed"] > 0:
            pdf.set_fill_color(255, 244, 244)
        elif stats["skipped"] > m_total * 0.3:
            pdf.set_fill_color(255, 251, 235)
        else:
            pdf.set_fill_color(248, 252, 248)

        row = [
            module[:42] if len(module) > 42 else module,
            str(stats["passed"]),
            str(stats["failed"]),
            str(stats["skipped"]),
            str(m_total),
            m_rate,
        ]
        S(9)
        pdf.set_text_color(0, 0, 0)
        for j, (cell_txt, cw) in enumerate(zip(row, col_w)):
            align = "L" if j == 0 else "C"
            # 失败数用红色
            if j == 2 and int(cell_txt) > 0:
                pdf.set_text_color(200, 0, 0)
            elif j == 5:
                rate_val = int(cell_txt.rstrip("%")) if cell_txt != "-" else 100
                pdf.set_text_color(0, 150, 0) if rate_val >= 80 else pdf.set_text_color(200, 0, 0)
            else:
                pdf.set_text_color(0, 0, 0)
            pdf.cell(cw, 7, cell_txt, border=1, align=align, fill=True,
                     new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.ln(7)

    # ════════════════════════════════════════════════════════════════
    # 第三页：失败用例清单（如有）
    # ════════════════════════════════════════════════════════════════
    if failed_cases:
        pdf.add_page()
        _sec_title(pdf, font, f"Failed Test Cases  ({len(failed_cases)} total)")

        for i, case in enumerate(failed_cases, 1):
            # 优先用英文名
            name = (case.get("docstring_summary_en")
                    or case.get("test_func_name", "Unknown"))
            module = case.get("module", "")
            api = case.get("api_path", "") or ""
            analysis = case.get("failure_analysis", "") or ""

            # 检查分页余量
            if pdf.get_y() > 265:
                pdf.add_page()
                _sec_title(pdf, font, f"Failed Test Cases (continued)")

            # 用例序号 + 名称
            SB(9)
            pdf.set_text_color(180, 0, 0)
            line = f"{i}. {name}"
            if len(line) > 90:
                line = line[:87] + "..."
            pdf.cell(0, 6, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            # 模块 + API
            S(8)
            pdf.set_text_color(100, 100, 100)
            info = f"   Module: {module}"
            if api:
                info += f"  |  API: {api}"
            pdf.cell(0, 5, info, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            # 分析
            if analysis:
                SI(8)
                pdf.set_text_color(140, 70, 0)
                a_line = f"   → {analysis}"
                if len(a_line) > 100:
                    a_line = a_line[:97] + "..."
                pdf.cell(0, 5, a_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.ln(1)

    # ════════════════════════════════════════════════════════════════
    # 页脚（每页）
    # ════════════════════════════════════════════════════════════════
    total_pages = pdf.page  # pdf.pages 是 dict，pdf.page 是当前页码（即总页数）
    for p in range(1, total_pages + 1):
        pdf.page = p
        pdf.set_xy(0, 288)
        S(7)
        pdf.set_text_color(160, 160, 160)
        pdf.cell(0, 5,
                 f"Page {p} / {total_pages}   |   Generated: {report_time}   |   Confidential",
                 align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── 保存 ─────────────────────────────────────────────────────────
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    pdf.output(output_path)
    return True


def _sec_title(pdf, font, title: str):
    from fpdf.enums import XPos, YPos
    pdf.set_fill_color(30, 55, 153)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(font, size=11)
    pdf.cell(0, 9, f"  {title}", fill=True,
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    pdf.set_text_color(0, 0, 0)


def _tbl_hdr(pdf, font, headers, col_widths):
    from fpdf.enums import XPos, YPos
    pdf.set_fill_color(220, 228, 255)
    pdf.set_font(font, size=9)
    pdf.set_text_color(30, 55, 153)
    for h, w in zip(headers, col_widths):
        align = "L" if headers.index(h) == 0 else "C"
        pdf.cell(w, 7, h, border=1, align=align, fill=True,
                 new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.ln(7)
    pdf.set_text_color(0, 0, 0)


if __name__ == "__main__":
    import json, re, sys
    script_dir = Path(__file__).parent.parent
    html_path = script_dir / "reports" / "final_report.html"
    if not html_path.exists():
        print("❌ final_report.html 不存在，请先运行测试")
        sys.exit(1)

    content = html_path.read_text(encoding="utf-8")
    m = re.search(r"const testData = (\[.*?\]);", content, re.DOTALL)
    if not m:
        print("❌ 无法从 HTML 中提取 testData")
        sys.exit(1)

    raw_json = m.group(1).replace("<\\/", "</")
    results = json.loads(raw_json)
    out = script_dir / "reports" / "summary_report_test.pdf"
    ok = generate_pdf_summary(results, str(out))
    print(f"{'✓' if ok else '✗'} PDF 生成: {out}")
