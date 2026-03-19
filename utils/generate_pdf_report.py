"""
PDF Test Report Generator
Generates a professional PDF report from test_results data.
All content is in English.

Structure:
  Page 1: Cover - Banner metrics (6 indicators) + Donut chart + Progress bar
  Page 2: Module Statistics table
  Page 3+: All Test Cases (passed/failed/skipped)
  Last: Failed Cases with analysis
"""
import math
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict

# macOS system font (supports CJK)
_FONT_PATHS = [
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/System/Library/Fonts/STHeiti Light.ttc",
]


def _load_font(pdf):
    import os
    for path in _FONT_PATHS:
        if os.path.exists(path):
            pdf.add_font("CJK", fname=path)
            return "CJK"
    return "Helvetica"


def _draw_donut(pdf, cx, cy, r, passed, failed, skipped, total):
    """
    Draw a simple donut/pie chart using small arc segments.
    Uses filled triangles to approximate a pie chart.
    """
    import math as _m

    if total == 0:
        pdf.set_fill_color(200, 200, 200)
        # full circle fallback
        pdf.ellipse(cx - r, cy - r, r * 2, r * 2, "F")
        return

    slices = [
        (passed, (82, 196, 26)),
        (failed, (245, 34, 45)),
        (skipped, (250, 173, 20)),
    ]

    angle = -90.0  # start from top
    ri = r * 0.45  # inner radius (donut hole)

    for count, color in slices:
        if count == 0:
            continue
        sweep = 360.0 * count / total
        steps = max(8, int(sweep / 3))
        a_start = _m.radians(angle)
        a_end = _m.radians(angle + sweep)

        pdf.set_fill_color(*color)

        # Draw outer arc segments as small polygons
        da = (a_end - a_start) / steps
        for s in range(steps):
            a1 = a_start + s * da
            a2 = a_start + (s + 1) * da
            # outer points
            x1o = cx + r * _m.cos(a1)
            y1o = cy + r * _m.sin(a1)
            x2o = cx + r * _m.cos(a2)
            y2o = cy + r * _m.sin(a2)
            # inner points
            x1i = cx + ri * _m.cos(a1)
            y1i = cy + ri * _m.sin(a1)
            x2i = cx + ri * _m.cos(a2)
            y2i = cy + ri * _m.sin(a2)

            # Draw quadrilateral as two triangles using polygon approximation
            # fpdf2 does not have polygon; draw a filled rectangle-like shape
            # Use line + fill hack: draw outer triangle
            pdf.set_draw_color(*color)
            pdf.set_line_width(0.01)
            # approximate with two triangles
            pdf.polygon([(x1i, y1i), (x1o, y1o), (x2o, y2o), (x2i, y2i)], style="F")

        angle += sweep

    # White donut hole
    pdf.set_fill_color(255, 255, 255)
    pdf.ellipse(cx - ri, cy - ri, ri * 2, ri * 2, "F")


def generate_pdf_summary(
    results: List[Dict],
    output_path: str,
    env: str = "DEV",
    core: str = "actc"
) -> bool:
    try:
        from fpdf import FPDF
        from fpdf.enums import XPos, YPos
    except ImportError:
        raise ImportError("Please install fpdf2: pip install fpdf2")

    # ── Statistics ───────────────────────────────────────────────────
    total = len(results)
    passed = sum(1 for r in results if r.get("status") == "passed")
    failed = sum(1 for r in results if r.get("status") == "failed")
    skipped = sum(1 for r in results if r.get("status") == "skipped")
    pass_rate = round(passed / total * 100, 1) if total > 0 else 0

    # Wall time
    durations = [float(r.get("duration") or 0) for r in results]
    start_times, max_t_item = [], None
    for r in results:
        t = r.get("start_time", "")
        if t:
            try:
                dt = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                start_times.append(dt)
                if max_t_item is None or dt > datetime.strptime(
                        max_t_item.get("start_time", "1970-01-01 00:00:00"),
                        "%Y-%m-%d %H:%M:%S"):
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

    # Module stats
    module_stats: Dict[str, Dict] = defaultdict(
        lambda: {"passed": 0, "failed": 0, "skipped": 0})
    for r in results:
        m = r.get("module", "Unknown")
        s = r.get("status", "unknown")
        if s in ("passed", "failed", "skipped"):
            module_stats[m][s] += 1

    failed_cases = [r for r in results if r.get("status") == "failed"]
    report_time = datetime.now().strftime("%Y-%m-%d %H:%M")

    # ── Init PDF ─────────────────────────────────────────────────────
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    F = _load_font(pdf)

    def setfont(sz):
        pdf.set_font(F, size=sz)

    # ════════════════════════════════════════════════════════════════
    # PAGE 1: Cover
    # ════════════════════════════════════════════════════════════════
    pdf.add_page()

    # Top banner
    pdf.set_fill_color(22, 40, 120)
    pdf.rect(0, 0, 210, 42, "F")
    setfont(20)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(0, 9)
    pdf.cell(210, 12, "API Automation Test Report",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    setfont(10)
    pdf.set_xy(0, 26)
    pdf.cell(210, 8,
             f"Env: {env.upper()}   |   Core: {core}   |   Generated: {report_time}",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── 6 Banner-style metric cards (2 rows × 3 cols) ──────────────
    banner_metrics = [
        ("Wall Time",  f"{wall_time:.2f}s",   (22, 40, 120)),
        ("Avg Duration", f"{avg_dur:.2f}s",   (47, 84, 235)),
        ("Min Duration", f"{min_dur:.2f}s",   (82, 196, 26)),
        ("Max Duration", f"{max_dur:.2f}s",   (245, 34, 45)),
        ("P95 Duration", f"{p95_dur:.2f}s",   (114, 46, 209)),
        ("TPS (cases/s)", f"{tps}",           (19, 194, 194)),
    ]

    card_start_y = 50
    card_w = 61
    card_h = 22
    card_gap = 2.5
    card_start_x = 11

    for idx, (label, value, color) in enumerate(banner_metrics):
        row = idx // 3
        col = idx % 3
        x = card_start_x + col * (card_w + card_gap)
        y = card_start_y + row * (card_h + card_gap)

        # Card background (light tint of color)
        r_bg = min(255, color[0] + 210)
        g_bg = min(255, color[1] + 210)
        b_bg = min(255, color[2] + 210)
        pdf.set_fill_color(r_bg, g_bg, b_bg)
        pdf.rect(x, y, card_w, card_h, "F")

        # Left color stripe
        pdf.set_fill_color(*color)
        pdf.rect(x, y, 3, card_h, "F")

        # Value (large)
        setfont(14)
        pdf.set_text_color(*color)
        pdf.set_xy(x + 5, y + 2)
        pdf.cell(card_w - 7, 10, value, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        # Label (small)
        setfont(8)
        pdf.set_text_color(80, 80, 80)
        pdf.set_xy(x + 5, y + 13)
        pdf.cell(card_w - 7, 6, label, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── Donut chart (right side) + Legend (center-left area) ────────
    chart_y_start = card_start_y + 2 * (card_h + card_gap) + 10
    chart_cx = 168    # center x of donut - moved right to avoid overlap
    chart_cy = chart_y_start + 30
    chart_r = 25

    _draw_donut(pdf, chart_cx, chart_cy, chart_r, passed, failed, skipped, total)

    # Center text inside donut
    setfont(11)
    pdf.set_text_color(40, 40, 40)
    pdf.set_xy(chart_cx - 15, chart_cy - 6)
    pdf.cell(30, 6, f"{pass_rate}%", align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    setfont(7)
    pdf.set_text_color(100, 100, 100)
    pdf.set_xy(chart_cx - 15, chart_cy + 1)
    pdf.cell(30, 5, "Pass Rate", align="C",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Stats panel (left of chart) - narrowed to avoid overlapping donut
    panel_x = 11
    panel_y = chart_y_start
    panel_w = 118   # reduced from 130 to give chart room (chart left edge at 143)
    panel_h = 62

    pdf.set_fill_color(248, 249, 252)
    pdf.set_draw_color(220, 225, 240)
    pdf.rect(panel_x, panel_y, panel_w, panel_h, "FD")

    # Title
    setfont(9)
    pdf.set_text_color(22, 40, 120)
    pdf.set_xy(panel_x + 4, panel_y + 3)
    pdf.cell(panel_w - 8, 7, "Execution Summary",
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # Divider
    pdf.set_draw_color(200, 210, 240)
    pdf.line(panel_x + 4, panel_y + 11, panel_x + panel_w - 4, panel_y + 11)

    # 2-col stat grid inside panel
    stats_items = [
        ("Total Cases", str(total),    (22, 40, 120)),
        ("Passed",      str(passed),   (82, 196, 26)),
        ("Failed",      str(failed),   (245, 34, 45) if failed > 0 else (82, 196, 26)),
        ("Skipped",     str(skipped),  (250, 173, 20)),
        ("Pass Rate",   f"{pass_rate}%",
         (82, 196, 26) if pass_rate >= 80 else (245, 34, 45)),
        ("Fail Rate",   f"{round(failed/total*100,1) if total else 0}%",
         (245, 34, 45) if failed > 0 else (82, 196, 26)),
    ]
    grid_x = panel_x + 4
    grid_y = panel_y + 14
    col_w2 = (panel_w - 8) / 2
    for i, (lbl, val, color) in enumerate(stats_items):
        col = i % 2
        row = i // 2
        sx = grid_x + col * col_w2
        sy = grid_y + row * 14

        # small color dot
        pdf.set_fill_color(*color)
        pdf.rect(sx, sy + 2, 2.5, 2.5, "F")

        setfont(8)
        pdf.set_text_color(80, 80, 80)
        pdf.set_xy(sx + 5, sy)
        pdf.cell(col_w2 - 5, 5, lbl, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        setfont(11)
        pdf.set_text_color(*color)
        pdf.set_xy(sx + 5, sy + 5)
        pdf.cell(col_w2 - 5, 7, val, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ── Progress bar ─────────────────────────────────────────────────
    bar_y = chart_cy + chart_r + 10
    bar_x = 11
    bar_w = 188
    bar_h = 7

    pdf.set_fill_color(225, 225, 225)
    pdf.rect(bar_x, bar_y, bar_w, bar_h, "F")
    if total > 0:
        x = bar_x
        for count, color in [(passed, (82, 196, 26)),
                              (failed, (245, 34, 45)),
                              (skipped, (250, 173, 20))]:
            if count > 0:
                w = bar_w * count / total
                pdf.set_fill_color(*color)
                pdf.rect(x, bar_y, w, bar_h, "F")
                x += w

    setfont(7)
    pdf.set_text_color(80, 80, 80)
    pdf.set_xy(bar_x, bar_y + 8)
    fail_rate = round(failed / total * 100, 1) if total else 0
    skip_rate = round(skipped / total * 100, 1) if total else 0
    pdf.cell(bar_w, 5,
             f"■ Passed {pass_rate}%   ■ Failed {fail_rate}%   ■ Skipped {skip_rate}%",
             align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    # ════════════════════════════════════════════════════════════════
    # PAGE 2: Module Statistics
    # ════════════════════════════════════════════════════════════════
    pdf.add_page()
    _sec_title(pdf, F, "Test Results by Module")

    col_w = [83, 22, 22, 22, 22, 17]
    hdrs = ["Module", "Passed", "Failed", "Skipped", "Total", "Rate"]
    _tbl_hdr(pdf, F, hdrs, col_w)

    for module, stats in sorted(module_stats.items()):
        m_total = stats["passed"] + stats["failed"] + stats["skipped"]
        m_rate = f"{round(stats['passed']/m_total*100)}%" if m_total > 0 else "-"

        pdf.set_fill_color(255, 255, 255)
        if stats["failed"] > 0:
            pdf.set_fill_color(255, 244, 244)
        elif stats["skipped"] > m_total * 0.3:
            pdf.set_fill_color(255, 251, 235)
        else:
            pdf.set_fill_color(248, 252, 248)

        row = [
            module[:40] if len(module) > 40 else module,
            str(stats["passed"]), str(stats["failed"]),
            str(stats["skipped"]), str(m_total), m_rate,
        ]
        setfont(9)
        for j, (cell_txt, cw) in enumerate(zip(row, col_w)):
            align = "L" if j == 0 else "C"
            if j == 2 and stats["failed"] > 0:
                pdf.set_text_color(200, 0, 0)
            elif j == 5 and cell_txt != "-":
                rv = int(cell_txt.rstrip("%"))
                pdf.set_text_color(0, 150, 0) if rv >= 80 else pdf.set_text_color(200, 0, 0)
            else:
                pdf.set_text_color(0, 0, 0)
            pdf.cell(cw, 7, cell_txt, border=1, align=align, fill=True,
                     new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.ln(7)

    # ════════════════════════════════════════════════════════════════
    # PAGE 3+: All Test Cases
    # ════════════════════════════════════════════════════════════════
    pdf.add_page()
    _sec_title(pdf, F, f"All Test Cases  ({total} total)")

    case_col_w = [8, 70, 50, 25, 15, 20]
    case_hdrs = ["#", "Test Case", "Module", "API Path", "Status", "Duration"]
    _tbl_hdr(pdf, F, case_hdrs, case_col_w)

    STATUS_COLORS = {
        "passed": (82, 196, 26),
        "failed": (245, 34, 45),
        "skipped": (250, 173, 20),
    }
    STATUS_BG = {
        "passed": (240, 255, 240),
        "failed": (255, 240, 240),
        "skipped": (255, 251, 230),
    }

    for idx, case in enumerate(results, 1):
        status = case.get("status", "unknown")
        name = (case.get("docstring_summary_en")
                or case.get("test_func_name", ""))
        module = case.get("module", "")
        api = case.get("api_path", "") or ""
        dur = float(case.get("duration") or 0)

        # Auto page break check
        if pdf.get_y() > 272:
            pdf.add_page()
            _sec_title(pdf, F, "All Test Cases (continued)")
            _tbl_hdr(pdf, F, case_hdrs, case_col_w)

        bg = STATUS_BG.get(status, (255, 255, 255))
        fg = STATUS_COLORS.get(status, (100, 100, 100))

        pdf.set_fill_color(*bg)
        row_data = [
            (str(idx),                                   case_col_w[0], "C", (100, 100, 100)),
            (name[:36] if len(name) > 36 else name,     case_col_w[1], "L", (0, 0, 0)),
            (module[:25] if len(module) > 25 else module, case_col_w[2], "L", (60, 60, 60)),
            (api[-22:] if len(api) > 22 else api,       case_col_w[3], "L", (80, 80, 180)),
            (status.upper()[:4],                        case_col_w[4], "C", fg),
            (f"{dur:.2f}s",                             case_col_w[5], "C", (100, 100, 100)),
        ]
        setfont(7)
        for cell_txt, cw, align, color in row_data:
            pdf.set_text_color(*color)
            pdf.cell(cw, 6, cell_txt, border=1, align=align, fill=True,
                     new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.ln(6)

    # ════════════════════════════════════════════════════════════════
    # Last section: Failed Cases with analysis
    # ════════════════════════════════════════════════════════════════
    if failed_cases:
        pdf.add_page()
        _sec_title(pdf, F, f"Failed Cases Detail  ({len(failed_cases)} cases)")

        for i, case in enumerate(failed_cases, 1):
            name = (case.get("docstring_summary_en")
                    or case.get("test_func_name", "Unknown"))
            module = case.get("module", "")
            api = case.get("api_path", "") or ""
            analysis = case.get("failure_analysis", "") or ""

            if pdf.get_y() > 265:
                pdf.add_page()
                _sec_title(pdf, F, "Failed Cases Detail (continued)")

            # Case title
            setfont(9)
            pdf.set_text_color(180, 0, 0)
            line = f"{i}. {name}"
            if len(line) > 92:
                line = line[:89] + "..."
            pdf.cell(0, 6, line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            # Module + API
            setfont(8)
            pdf.set_text_color(100, 100, 100)
            info = f"   Module: {module}"
            if api:
                info += f"   API: {api}"
            pdf.cell(0, 5, info, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            # Analysis
            if analysis:
                setfont(8)
                pdf.set_text_color(140, 70, 0)
                a_line = f"   → {analysis}"
                if len(a_line) > 102:
                    a_line = a_line[:99] + "..."
                pdf.cell(0, 5, a_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

            pdf.ln(1)

    # ════════════════════════════════════════════════════════════════
    # Footer on every page
    # ════════════════════════════════════════════════════════════════
    total_pages = pdf.page
    for p in range(1, total_pages + 1):
        pdf.page = p
        pdf.set_xy(0, 289)
        setfont(7)
        pdf.set_text_color(160, 160, 160)
        pdf.cell(0, 5,
                 f"Page {p} / {total_pages}   |   Generated: {report_time}   |   Confidential",
                 align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    pdf.output(output_path)
    return True


def _sec_title(pdf, font, title: str):
    from fpdf.enums import XPos, YPos
    pdf.set_fill_color(22, 40, 120)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font(font, size=10)
    pdf.cell(0, 8, f"  {title}", fill=True,
             new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(2)
    pdf.set_text_color(0, 0, 0)


def _tbl_hdr(pdf, font, headers, col_widths):
    from fpdf.enums import XPos, YPos
    pdf.set_fill_color(210, 220, 255)
    pdf.set_font(font, size=8)
    pdf.set_text_color(22, 40, 120)
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
        print("❌ final_report.html not found, please run tests first")
        sys.exit(1)
    content = html_path.read_text(encoding="utf-8")
    m = re.search(r"const testData = (\[.*?\]);", content, re.DOTALL)
    if not m:
        print("❌ Cannot extract testData from HTML")
        sys.exit(1)
    results = json.loads(m.group(1).replace("<\\/", "</"))
    out = script_dir / "reports" / "test_pdf_preview.pdf"
    ok = generate_pdf_summary(results, str(out))
    print(f"{'✓' if ok else '✗'} PDF: {out}")
