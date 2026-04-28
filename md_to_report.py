#!/usr/bin/env python3
"""
md_to_report.py - MarkdownファイルをPDF対応HTML週次レポートに変換する

使い方:
  python md_to_report.py report.md
  python md_to_report.py report.md -o output.html
  python md_to_report.py report.md --theme light
"""

import sys
import re
import argparse
from pathlib import Path
from datetime import datetime

CSS_DARK = """
    :root {
      --bg: #0d1117; --surface: #161b22; --surface2: #21262d;
      --text: #e6edf3; --muted: #8b949e; --accent: #58a6ff;
      --accent2: #f78166; --border: #30363d; --code-bg: #1f2428;
      --success: #3fb950; --warning: #d29922;
    }
"""

CSS_LIGHT = """
    :root {
      --bg: #f6f8fa; --surface: #ffffff; --surface2: #f0f3f6;
      --text: #1f2328; --muted: #57606a; --accent: #0969da;
      --accent2: #cf222e; --border: #d1d9e0; --code-bg: #eff1f3;
      --success: #1a7f37; --warning: #9a6700;
    }
"""

CSS_COMMON = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Hiragino Sans', 'Yu Gothic', sans-serif;
      background: var(--bg); color: var(--text);
      line-height: 1.8; font-size: 16px;
    }
    .container { max-width: 860px; margin: 0 auto; padding: 40px 24px; }
    .header {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 12px; padding: 32px 40px; margin-bottom: 32px;
      border-left: 4px solid var(--accent);
    }
    .header h1 { font-size: 28px; color: var(--accent); margin-bottom: 8px; }
    .header .meta { color: var(--muted); font-size: 14px; }
    .toc {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 8px; padding: 24px; margin-bottom: 32px;
    }
    .toc h2 { font-size: 16px; color: var(--muted); margin-bottom: 12px;
               text-transform: uppercase; letter-spacing: 0.05em; }
    .toc ul { list-style: none; padding-left: 0; }
    .toc li { padding: 3px 0; }
    .toc a { color: var(--accent); text-decoration: none; font-size: 15px; }
    .toc a:hover { text-decoration: underline; }
    .toc li.h3 { padding-left: 16px; font-size: 14px; }
    section {
      background: var(--surface); border: 1px solid var(--border);
      border-radius: 8px; padding: 28px 32px; margin-bottom: 20px;
    }
    h2 { font-size: 20px; color: var(--text); padding-bottom: 8px;
         border-bottom: 1px solid var(--border); margin-bottom: 16px; }
    h3 { font-size: 16px; color: var(--accent); margin: 20px 0 10px; }
    p { margin-bottom: 12px; }
    ul, ol { padding-left: 24px; margin-bottom: 12px; }
    li { margin-bottom: 4px; }
    li.task { list-style: none; margin-left: -24px; padding-left: 0; }
    li.task input { margin-right: 8px; }
    code {
      background: var(--code-bg); color: var(--accent2);
      padding: 2px 6px; border-radius: 4px; font-size: 0.9em;
      font-family: 'SF Mono', Consolas, monospace;
    }
    pre {
      background: var(--code-bg); border: 1px solid var(--border);
      border-radius: 6px; padding: 16px; overflow-x: auto;
      margin-bottom: 12px;
    }
    pre code { background: none; padding: 0; color: var(--text); }
    table {
      width: 100%; border-collapse: collapse; margin-bottom: 12px;
      font-size: 15px;
    }
    th, td { padding: 10px 14px; border: 1px solid var(--border); text-align: left; }
    th { background: var(--surface2); color: var(--muted);
         text-transform: uppercase; font-size: 12px; letter-spacing: 0.05em; }
    blockquote {
      border-left: 3px solid var(--accent); padding-left: 16px;
      color: var(--muted); margin: 12px 0;
    }
    .badge-done { color: var(--success); font-weight: bold; }
    .badge-wip  { color: var(--warning); font-weight: bold; }
    .actions {
      position: fixed; bottom: 24px; right: 24px;
      display: flex; gap: 10px; flex-direction: column;
    }
    .btn {
      padding: 12px 20px; border-radius: 8px; border: none;
      cursor: pointer; font-size: 14px; font-weight: 600;
      display: flex; align-items: center; gap: 6px; box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .btn-print { background: var(--accent); color: white; }
    .btn-theme { background: var(--surface); color: var(--text);
                 border: 1px solid var(--border); }
    .footer { text-align: center; padding: 24px; color: var(--muted); font-size: 13px; }
    @media print {
      .actions { display: none; }
      body { background: white; color: #333; }
      section { box-shadow: none; border: 1px solid #ddd; break-inside: avoid; }
      a { color: #333; }
    }
"""

JS_TOGGLE = """
function toggleTheme() {
  const html = document.documentElement;
  const next = html.dataset.theme === 'dark' ? 'light' : 'dark';
  html.dataset.theme = next;
  const root = document.querySelector(':root');
  if (next === 'light') {
    root.style.setProperty('--bg', '#f6f8fa');
    root.style.setProperty('--surface', '#ffffff');
    root.style.setProperty('--surface2', '#f0f3f6');
    root.style.setProperty('--text', '#1f2328');
    root.style.setProperty('--muted', '#57606a');
    root.style.setProperty('--accent', '#0969da');
    root.style.setProperty('--accent2', '#cf222e');
    root.style.setProperty('--border', '#d1d9e0');
    root.style.setProperty('--code-bg', '#eff1f3');
  } else {
    root.style.setProperty('--bg', '#0d1117');
    root.style.setProperty('--surface', '#161b22');
    root.style.setProperty('--surface2', '#21262d');
    root.style.setProperty('--text', '#e6edf3');
    root.style.setProperty('--muted', '#8b949e');
    root.style.setProperty('--accent', '#58a6ff');
    root.style.setProperty('--accent2', '#f78166');
    root.style.setProperty('--border', '#30363d');
    root.style.setProperty('--code-bg', '#1f2428');
  }
}
"""


def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text.lower())
    return re.sub(r'[-\s]+', '-', text).strip('-')


def parse_markdown(md):
    """簡易Markdownパーサー（stdlib のみ）"""
    lines = md.split('\n')
    html_parts = []
    toc = []
    in_code = False
    code_lang = ''
    code_lines = []
    in_table = False
    table_rows = []
    in_section = False
    list_stack = []

    def close_section():
        nonlocal in_section
        if in_section:
            html_parts.append('</section>')
            in_section = False

    def close_list():
        while list_stack:
            tag = list_stack.pop()
            html_parts.append(f'</{tag}>')

    def render_table():
        nonlocal in_table, table_rows
        if not table_rows:
            return
        h = '<table>'
        for i, row in enumerate(table_rows):
            if i == 1 and all(c in '-| :' for c in row):
                continue
            cells = [c.strip() for c in row.strip('|').split('|')]
            tag = 'th' if i == 0 else 'td'
            h += '<tr>' + ''.join(f'<{tag}>{escape(c)}</{tag}>' for c in cells) + '</tr>'
        h += '</table>'
        html_parts.append(h)
        table_rows.clear()
        in_table = False

    def escape(s):
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    def inline(text):
        text = escape(text)
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
        text = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', text)
        text = re.sub(r'~~(.+?)~~', r'<del>\1</del>', text)
        text = text.replace('✅', '<span class="badge-done">✅</span>')
        text = text.replace('🔄', '<span class="badge-wip">🔄</span>')
        return text

    for line in lines:
        # コードブロック
        if line.startswith('```'):
            close_list()
            if in_code:
                code_content = escape('\n'.join(code_lines))
                lang_attr = f' data-lang="{code_lang}"' if code_lang else ''
                html_parts.append(f'<pre{lang_attr}><code>{code_content}</code></pre>')
                code_lines.clear()
                code_lang = ''
                in_code = False
            else:
                in_code = True
                code_lang = line[3:].strip()
            continue

        if in_code:
            code_lines.append(line)
            continue

        # テーブル
        if '|' in line:
            in_table = True
            table_rows.append(line)
            continue
        elif in_table:
            render_table()

        # 見出し
        m = re.match(r'^(#{1,3})\s+(.*)', line)
        if m:
            close_list()
            level = len(m.group(1))
            text = m.group(2)
            sid = slugify(text)
            if level == 2:
                close_section()
                html_parts.append(f'<section id="{sid}">')
                html_parts.append(f'<h2>{inline(text)}</h2>')
                toc.append((2, text, sid))
                in_section = True
            elif level == 3:
                html_parts.append(f'<h3 id="{sid}">{inline(text)}</h3>')
                toc.append((3, text, sid))
            else:
                close_section()
                html_parts.append(f'<h1 style="font-size:32px;margin-bottom:24px">{inline(text)}</h1>')
            continue

        # タスクリスト
        m_task = re.match(r'^(\s*)[*\-]\s+\[([xX ])\]\s+(.*)', line)
        if m_task:
            close_list()
            checked = 'checked' if m_task.group(2).lower() == 'x' else ''
            html_parts.append(
                f'<ul><li class="task">'
                f'<input type="checkbox" {checked} disabled>{inline(m_task.group(3))}'
                f'</li></ul>'
            )
            continue

        # 箇条書き
        m_ul = re.match(r'^(\s*)[*\-]\s+(.*)', line)
        m_ol = re.match(r'^(\s*)\d+\.\s+(.*)', line)

        if m_ul:
            content = m_ul.group(2)
            if not list_stack or list_stack[-1] != 'ul':
                while list_stack:
                    html_parts.append(f'</{list_stack.pop()}>')
                html_parts.append('<ul>')
                list_stack.append('ul')
            html_parts.append(f'<li>{inline(content)}</li>')
            continue
        elif m_ol:
            content = m_ol.group(2)
            if not list_stack or list_stack[-1] != 'ol':
                while list_stack:
                    html_parts.append(f'</{list_stack.pop()}>')
                html_parts.append('<ol>')
                list_stack.append('ol')
            html_parts.append(f'<li>{inline(content)}</li>')
            continue
        else:
            close_list()

        # 引用
        if line.startswith('>'):
            html_parts.append(f'<blockquote>{inline(line[1:].strip())}</blockquote>')
            continue

        # 水平線
        if re.match(r'^[-*_]{3,}$', line.strip()):
            html_parts.append('<hr style="border:none;border-top:1px solid var(--border);margin:16px 0">')
            continue

        # 空行
        if not line.strip():
            continue

        # 段落
        html_parts.append(f'<p>{inline(line)}</p>')

    close_list()
    if in_table:
        render_table()
    close_section()

    return '\n'.join(html_parts), toc


def build_toc(toc):
    if not toc:
        return ''
    items = []
    for level, text, sid in toc:
        if level == 1:
            continue
        cls_attr = ' class="h3"' if level == 3 else ''
        items.append(f'<li{cls_attr}><a href="#{sid}">{text}</a></li>')
    return (
        '<div class="toc"><h2>目次</h2><ul>'
        + ''.join(items)
        + '</ul></div>'
    )


def build_html(title, generated_at, css_vars, toc_html, body_html):
    return (
        '<!DOCTYPE html>\n'
        '<html lang="ja">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        f'<title>{title}</title>\n'
        '<style>\n'
        + css_vars
        + CSS_COMMON
        + '</style>\n'
        '</head>\n'
        '<body>\n'
        '<div class="container">\n'
        '  <div class="header">\n'
        f'    <h1>{title}</h1>\n'
        f'    <div class="meta">Generated: {generated_at} &nbsp;|&nbsp; md_to_report.py</div>\n'
        '  </div>\n'
        + toc_html + '\n'
        + body_html + '\n'
        + '</div>\n'
        '<div class="actions">\n'
        '  <button class="btn btn-print" onclick="window.print()">&#128424;&#65039; PDF&#20445;&#23384;</button>\n'
        '  <button class="btn btn-theme" onclick="toggleTheme()">&#127763; &#12486;&#12540;&#12510;&#20999;&#26367;</button>\n'
        '</div>\n'
        '<div class="footer">Generated by md_to_report.py</div>\n'
        '<script>\n'
        + JS_TOGGLE
        + '</script>\n'
        '</body>\n'
        '</html>'
    )


def convert(md_path, out_path, theme='dark'):
    md = Path(md_path).read_text(encoding='utf-8')
    title_m = re.search(r'^#\s+(.+)', md, re.MULTILINE)
    title = title_m.group(1) if title_m else Path(md_path).stem
    body_html, toc = parse_markdown(md)
    toc_html = build_toc(toc)
    css_vars = CSS_DARK if theme == 'dark' else CSS_LIGHT
    generated_at = datetime.now().strftime('%Y-%m-%d %H:%M')
    html = build_html(title, generated_at, css_vars, toc_html, body_html)
    Path(out_path).write_text(html, encoding='utf-8')
    size = len(html)
    print(f'変換完了: {out_path} ({size:,} bytes)')


def main():
    parser = argparse.ArgumentParser(description='Markdown -> PDF対応HTML変換ツール')
    parser.add_argument('input', help='入力Markdownファイル')
    parser.add_argument('-o', '--output', help='出力HTMLファイル (省略時: 入力名.html)')
    parser.add_argument('--theme', choices=['dark', 'light'], default='dark')
    args = parser.parse_args()
    out = args.output or Path(args.input).with_suffix('.html')
    convert(args.input, out, theme=args.theme)


if __name__ == '__main__':
    main()
