"""
PDF Test Report Generator v2 — HTML → PDF via Playwright / Chromium
Renders a full-fidelity HTML report matching the reference design:
  - DM Sans + JetBrains Mono fonts
  - Gradient header, grand-totals bar, metric cards with color stripes
  - Status badges, bar charts per module, failed-case cards

Falls back to fpdf2 plain-text if Playwright is unavailable.
"""
import math
import html as _html_lib
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import List, Dict


# ──────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ──────────────────────────────────────────────────────────────────────────────

def _has_chinese(s: str) -> bool:
    return any('\u4e00' <= c <= '\u9fff' for c in (s or ''))


def _get_en_name(case: dict) -> str:
    en = case.get("display_name_en") or case.get("docstring_summary_en", "")
    if en and not _has_chinese(en):
        return en
    raw = case.get("test_func_name", "Unknown")
    pretty = str(raw).replace("test_", "").replace("_", " ").strip()
    return pretty[:1].upper() + pretty[1:] if pretty else "Unknown"


def _esc(text: str) -> str:
    """HTML-escape a plain-text string."""
    return _html_lib.escape(str(text or ""))


def _pct(numerator: int, total: int, decimals: int = 1) -> float:
    if total == 0:
        return 0.0
    return round(numerator / total * 100, decimals)


# ── Transaction API patterns（TPS 专用，每次命中 = 一笔交易事务）──────────────
_TXN_PATHS = (
    "/money-movements/ach/credit",
    "/money-movements/ach/debit",
    "/money-movements/ach/reversal",
    "/money-movements/wire/payment",
    "/money-movements/international-wire/payment",
    "/money-movements/wire/request-payment",
    "/money-movements/instant-pay/payment",
    "/money-movements/instant-pay/request-payment",
    "/money-movements/instant-pay/return-payment",
    "/money-movements/account-transfer",
    "/money-movements/internal-pay/transfer",
    "/money-movements/checks/deposit",
    "/money-movements/checks/scan",
)


def _is_txn_api(api_path: str) -> bool:
    p = (api_path or "").lower()
    return any(pat in p for pat in _TXN_PATHS)


# ──────────────────────────────────────────────────────────────────────────────
# Build HTML sections
# ──────────────────────────────────────────────────────────────────────────────

def _build_module_rows(module_stats: dict, total: int) -> str:
    rows = []
    for module in sorted(module_stats):
        st = module_stats[module]
        m_total = st["passed"] + st["failed"] + st["skipped"]
        rate = _pct(st["passed"], m_total)
        rate_badge = (
            f'<span class="badge badge-passed">{rate}%</span>'
            if rate >= 80
            else f'<span class="badge badge-failed">{rate}%</span>'
        )
        failed_cell = (
            f'<span style="color:#b91c1c;font-weight:700">{st["failed"]}</span>'
            if st["failed"] > 0
            else str(st["failed"])
        )
        row_cls = "row-failed" if st["failed"] > 0 else ""
        rows.append(f"""
          <tr class="{row_cls}">
            <td><div class="stripe-tag" style="--stripe:{'#dc2626' if st['failed'] > 0 else '#16a34a'}">{_esc(module)}</div></td>
            <td class="center">{st['passed']}</td>
            <td class="center">{failed_cell}</td>
            <td class="center">{st['skipped']}</td>
            <td class="center">{m_total}</td>
            <td class="center">{rate_badge}</td>
          </tr>""")
    return "\n".join(rows)


def _build_case_rows(results: List[dict]) -> str:
    rows = []
    for idx, case in enumerate(results, 1):
        status = case.get("status", "unknown")
        name = _get_en_name(case)
        module = case.get("module", "")
        dur = float(case.get("duration") or 0)
        row_cls = f"row-{status}" if status in ("passed", "failed", "skipped") else ""
        badge_cls = f"badge-{status}" if status in ("passed", "failed", "skipped") else ""
        rows.append(f"""
          <tr class="{row_cls}">
            <td class="center" style="color:#aaa;font-family:'JetBrains Mono',monospace;font-size:11px">{idx}</td>
            <td style="max-width:360px;word-break:break-word">{_esc(name)}</td>
            <td style="color:#555;font-size:11px">{_esc(module)}</td>
            <td><span class="badge {badge_cls}">{_esc(status.upper())}</span></td>
            <td class="center" style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#888">{dur:.2f}s</td>
          </tr>""")
    return "\n".join(rows)


def _strip_chinese_from_analysis(text: str) -> str:
    """
    Remove Chinese UI labels from failure_reason/failure_analysis and keep
    the meaningful parts (API business errors, assertion messages, etc.).
    Common patterns:
      - 'API 业务层返回错误 code=599，错误信息：「...」' -> '→ API business error code=599: ...'
      - '测试场景X:' prefixes
      - Module/Chinese labels
    """
    import re
    if not text:
        return text
    # Convert common Chinese error patterns to English
    text = re.sub(r'API\s*业务层返回错误\s*', 'API business error ', text)
    text = re.sub(r'错误信息：?[「""]?', 'error message: "', text)
    text = re.sub(r'[」""]', '"', text)
    text = re.sub(r'，', ', ', text)
    text = re.sub(r'：', ': ', text)
    # Strip remaining Chinese chars (labels, etc.)
    text = re.sub(r'[\u4e00-\u9fff]+', '', text)
    # Clean up extra whitespace
    text = re.sub(r'\s{2,}', ' ', text).strip()
    return text


def _build_failed_section(failed_cases: List[dict]) -> str:
    if not failed_cases:
        return ""
    cards = []
    for i, case in enumerate(failed_cases, 1):
        name = _get_en_name(case)
        module = case.get("module", "")
        api = case.get("api_path", "") or ""
        analysis = case.get("failure_analysis", "") or case.get("failure_reason", "") or ""
        # Translate Chinese content and trim
        analysis = _strip_chinese_from_analysis(analysis)
        if len(analysis) > 400:
            analysis = analysis[:397] + "..."
        analysis_block = (
            f'<div class="failed-card-analysis">→ {_esc(analysis)}</div>'
            if analysis else ""
        )
        api_block = f"  API: {_esc(api)}" if api else ""
        cards.append(f"""
          <div class="failed-card">
            <div class="failed-card-title">{i}. {_esc(name)}</div>
            <div class="failed-card-meta">Module: {_esc(module)}{api_block}</div>
            {analysis_block}
          </div>""")
    return f"""
      <div class="page-break"></div>
      <div class="section-wrap">
        <div class="section-title">Failed Cases Detail ({len(failed_cases)} cases)</div>
        {''.join(cards)}
      </div>"""


# ──────────────────────────────────────────────────────────────────────────────
# Main generator
# ──────────────────────────────────────────────────────────────────────────────

def generate_pdf_summary(
    results: List[Dict],
    output_path: str,
    env: str = "DEV",
    core: str = "actc",
) -> bool:
    """
    Render a full-fidelity PDF report via Playwright (Chromium headless).
    Returns True on success.
    """
    # ── Statistics ───────────────────────────────────────────────────
    total   = len(results)
    passed  = sum(1 for r in results if r.get("status") == "passed")
    failed  = sum(1 for r in results if r.get("status") == "failed")
    skipped = sum(1 for r in results if r.get("status") == "skipped")
    pass_rate = _pct(passed, total)

    durations = [float(r.get("duration") or 0) for r in results]
    # Wall time：优先 start_epoch（与 HTML 一致）；旧数据回退解析 start_time 字符串
    epoch_list = []
    max_epoch_item = None
    max_epoch = None
    for r in results:
        ep = r.get("start_epoch")
        if ep is not None and isinstance(ep, (int, float)) and float(ep) > 0:
            fv = float(ep)
            epoch_list.append(fv)
            if max_epoch is None or fv > max_epoch:
                max_epoch = fv
                max_epoch_item = r
            continue
        t = r.get("start_time", "")
        if t:
            try:
                dt = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
                epoch_list.append(dt.timestamp())
                fts = dt.timestamp()
                if max_epoch is None or fts > max_epoch:
                    max_epoch = fts
                    max_epoch_item = r
            except Exception:
                pass

    wall_time = 0.0
    if epoch_list:
        wall_time = max(epoch_list) - min(epoch_list)
        if max_epoch_item:
            wall_time += float(max_epoch_item.get("duration") or 0)

    avg_dur  = sum(durations) / len(durations) if durations else 0
    sorted_d = sorted(durations)
    p95_idx  = max(0, math.ceil(len(sorted_d) * 0.95) - 1)
    p95_dur  = sorted_d[p95_idx] if sorted_d else 0

    # ── QPS = total / wall_time（每秒完成多少个接口调用）────────────────
    qps = round(total / wall_time, 2) if wall_time > 0 else 0

    # ── TPS = 交易接口数 / 交易接口总耗时（每秒完成多少笔交易事务）──────
    txn_results   = [r for r in results if _is_txn_api(r.get("api_path", ""))]
    txn_count     = len(txn_results)
    txn_dur_sum   = sum(float(r.get("duration") or 0) for r in txn_results)
    tps           = round(txn_count / txn_dur_sum, 2) if txn_dur_sum > 0 else 0

    module_stats: Dict[str, Dict] = defaultdict(
        lambda: {"passed": 0, "failed": 0, "skipped": 0})
    for r in results:
        m = r.get("module", "Unknown")
        s = r.get("status", "unknown")
        if s in ("passed", "failed", "skipped"):
            module_stats[m][s] += 1

    failed_cases  = [r for r in results if r.get("status") == "failed"]
    report_time   = datetime.now().strftime("%Y-%m-%d %H:%M")
    passed_pct    = _pct(passed,  total)
    failed_pct    = _pct(failed,  total)
    skipped_pct   = _pct(skipped, total)

    # ── Load template ────────────────────────────────────────────────
    tpl_path = Path(__file__).parent.parent / "assets" / "pdf_report_template.html"
    template  = tpl_path.read_text(encoding="utf-8")

    # ── Render dynamic sections ──────────────────────────────────────
    module_rows  = _build_module_rows(module_stats, total)
    case_rows    = _build_case_rows(results)
    failed_sec   = _build_failed_section(failed_cases)

    # ── Replace placeholders ─────────────────────────────────────────
    html_content = (
        template
        .replace("{{ENV}}",          _esc(env.upper()))
        .replace("{{CORE}}",         _esc(core))
        .replace("{{REPORT_TIME}}",  _esc(report_time))
        .replace("{{TOTAL}}",        str(total))
        .replace("{{PASSED}}",       str(passed))
        .replace("{{FAILED}}",       str(failed))
        .replace("{{SKIPPED}}",      str(skipped))
        .replace("{{PASS_RATE}}",    str(pass_rate))
        .replace("{{PASSED_PCT}}",   str(passed_pct))
        .replace("{{FAILED_PCT}}",   str(failed_pct))
        .replace("{{SKIPPED_PCT}}",  str(skipped_pct))
        .replace("{{WALL_TIME}}",    f"{wall_time:.2f}")
        .replace("{{AVG_DUR}}",      f"{avg_dur:.2f}")
        .replace("{{P95_DUR}}",      f"{p95_dur:.2f}")
        .replace("{{QPS}}",          str(qps))
        .replace("{{TPS}}",          str(tps))
        .replace("{{TXN_COUNT}}",    str(txn_count))
        .replace("{{MODULE_COUNT}}", str(len(module_stats)))
        .replace("{{MODULE_ROWS}}",  module_rows)
        .replace("{{CASE_ROWS}}",    case_rows)
        .replace("{{FAILED_SECTION}}", failed_sec)
    )

    # ── Write temp HTML ──────────────────────────────────────────────
    out_path  = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_html  = out_path.with_suffix(".tmp.html")
    tmp_html.write_text(html_content, encoding="utf-8")

    # ── Render HTML → PDF via Playwright ────────────────────────────
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page    = browser.new_page()
            page.goto(f"file://{tmp_html.resolve()}", wait_until="networkidle", timeout=30000)
            page.pdf(
                path=str(out_path),
                format="A4",
                print_background=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
            )
            browser.close()
        tmp_html.unlink(missing_ok=True)
        return True

    except Exception as e:
        # ── Fallback: keep HTML, skip PDF if Playwright fails ────────
        tmp_html.rename(out_path.with_suffix(".html"))
        raise RuntimeError(
            f"Playwright PDF render failed: {e}\n"
            f"HTML saved to: {out_path.with_suffix('.html')}"
        ) from e


# ──────────────────────────────────────────────────────────────────────────────
# CLI entry point for manual preview
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import json, re, sys

    script_dir = Path(__file__).parent.parent
    html_path  = script_dir / "reports" / "final_report.html"
    if not html_path.exists():
        print("❌ final_report.html not found. Run tests first.")
        sys.exit(1)

    content = html_path.read_text(encoding="utf-8")
    m = re.search(r"const testData = (\[.*?\]);", content, re.DOTALL)
    if not m:
        print("❌ Cannot extract testData from final_report.html")
        sys.exit(1)

    results = json.loads(m.group(1).replace("<\\/", "</"))
    out     = script_dir / "reports" / "test_pdf_preview.pdf"
    print(f"Rendering {len(results)} cases → {out}")
    ok = generate_pdf_summary(results, str(out))
    print(f"{'✓ Done' if ok else '✗ Failed'}  →  {out}")
