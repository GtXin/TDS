"""Build the unified four-mode atlas with comparison and individual views."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODES = (
    "bi-strong_xd-strong",
    "bi-strong_xd-weak",
    "bi-weak_xd-strong",
    "bi-weak_xd-weak",
)


def main() -> None:
    """Write a reproducible atlas entry point linking every saved window."""
    body = """<!doctype html><html lang="zh"><meta charset="utf-8">
<title>XD030-E 四组合完整图集</title>
<style>body{font:16px/1.6 system-ui;max-width:1500px;margin:32px auto;padding:0 20px;color:#172033}img{width:100%;height:auto;border:1px solid #ddd}a{color:#245ec7}section{margin:36px 0}nav{padding:16px;background:#f3f5f8}small{color:#596579}</style>
<h1>XD030-E 四组合完整图集</h1>
<p>全量3027分型，同一快照全局求解。优先查看四组紧凑纵向比较，再打开单组交互图精读。每页四组使用共同价格范围与对齐时间轴；窗口不重算算法。</p>
<p><small>本次为试验口径结果。相邻段绑定已检查；局部包含/破坏口径仍未证明覆盖全部原文复杂情况。</small></p><nav>独立图集："""
    body += " · ".join(
        f'<a href="{mode}/index.html">{mode.replace("_", " / ")}</a>' for mode in MODES
    )
    body += "</nav><p>快速跳转："
    pages = [("overview", "全量总览")] + [
        (f"detail-{i:03d}", f"FX{(i - 1) * 500}–{min(i * 500 - 1, 3026)}")
        for i in range(1, 8)
    ]
    body += (
        " · ".join(f'<a href="#{stem}">{label}</a>' for stem, label in pages) + "</p>"
    )
    for stem, label in pages:
        picture = "../comparison/compact-" + stem + ".png"
        body += f'<section id="{stem}"><h2>{label}：四组合比较</h2><a href="{picture}"><img loading="lazy" src="{picture}" alt="{label}四组合紧凑纵向比较"></a><p>单组交互图：'
        body += " · ".join(
            f'<a href="{mode}/{stem}.html">{mode.replace("_", " / ")}</a>'
            for mode in MODES
        )
        body += f'</p><p><a href="{picture}">打开完整比较PNG</a></p></section>'
    (ROOT / "index.html").write_text(body + "</html>")


if __name__ == "__main__":
    main()
