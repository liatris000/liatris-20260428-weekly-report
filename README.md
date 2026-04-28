# md_to_report.py — Markdown → PDF対応HTML週次レポート変換ツール

MarkdownファイルをPDF保存・ダークモード対応の美しいHTMLレポートに変換するPythonスクリプトです。

**依存ライブラリ: ゼロ（Python標準ライブラリのみ）**

## デモ

[サンプルレポートを見る](https://liatris000.github.io/liatris-20260428-weekly-report/)

## 使い方

```bash
# 基本
python md_to_report.py report.md

# 出力ファイル名指定
python md_to_report.py report.md -o output.html

# ライトテーマ
python md_to_report.py report.md --theme light
```

## 対応Markdown記法

| 記法 | 対応 |
|------|------|
| 見出し (h1〜h3) | ✅ |
| 太字・斜体 | ✅ |
| 箇条書き・番号付きリスト | ✅ |
| タスクリスト `- [x]` | ✅ |
| コードブロック | ✅ |
| テーブル | ✅ |
| 引用 | ✅ |
| インラインコード | ✅ |
| リンク | ✅ |

## 機能

- 🎨 ダーク / ライトテーマ切替（ボタン1クリック）
- 🖨️ PDF保存ボタン（ブラウザの印刷 → PDFとして保存）
- 📋 自動目次生成
- 📱 レスポンシブ対応
- 🚀 外部依存ゼロ（Python 3.6+）

## 生成例

```
$ python md_to_report.py weekly_report.md
変換完了: weekly_report.html (8,386 bytes)
```

---

[Zenn記事はこちら](https://zenn.dev/liatris)
