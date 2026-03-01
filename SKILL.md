---
name: masao
user_invocable: true
invocation_hint: "/masao check <skill> or /masao frame"
description: >
  Skill quality checker and creation frame. Audits existing skills against
  8-dimension quality criteria and provides a template for creating high-quality skills.
  Triggers: masao, スキル品質, skill quality, スキルチェック, skill check,
  品質診断, quality audit, スキル診断, skill frame, スキルフレーム,
  テンプレート作成, skill template.
  Do NOT load for: スキルインストール(use skill-installer),
  新規スキル作成の実行(use skill-creator), スキル検索(use find-skills).
allowed-tools: ["Read", "Grep", "Glob", "Bash"]
metadata:
  skillport:
    category: masao
    tags: [quality, audit, skill-check, template, frame]
    alwaysApply: false
---

# Masao — Skill Quality Checker & Frame

スキルの品質を8次元で診断し、高品質スキルを作るためのフレームを提供する。

---

## モード

| モード | コマンド | 用途 |
|--------|----------|------|
| **check** | `masao check <skill>` | 既存スキルの品質診断 |
| **frame** | `masao frame` | 新規スキル用テンプレート生成 |

---

## Check モード

### 単一スキル診断

1. 自動チェックスクリプトを実行:
   ```bash
   python3 ~/.claude/skills/masao/scripts/masao_check.py ~/.claude/skills/<skill-name>
   ```
2. JSON結果を読み取り、`null` の次元はAIが SKILL.md を読んで手動判定
3. レポートを生成（下記フォーマット）

### バッチ診断（全スキル一括）

```bash
python3 ~/.claude/skills/masao/scripts/masao_check.py --all
```

全スキルのサマリーテーブルを生成し、グレード順にソートして出力。

### 8次元スコアリング概要

| # | 次元 | 重み | 主な評価観点 |
|---|------|------|-------------|
| 1 | Trigger Precision | 1.5x | トリガー数(10+)、否定トリガー、バイリンガル |
| 2 | Structure Balance | 1.0x | SKILL.md行数(< 200)、progressive disclosure |
| 3 | Metadata Completeness | 1.0x | allowed-tools, tags, category, alwaysApply |
| 4 | Guardrails & Safety | 1.5x | 禁止パターン、承認ワークフロー |
| 5 | Actionability | 1.0x | デフォルト推奨、具体例、実行可能スクリプト |
| 6 | Reference Architecture | 1.0x | 1階層参照、ナビゲーション |
| 7 | Terminology & Language | 0.5x | 用語一貫性、時間依存情報なし |
| 8 | Error Handling | 1.0x | トラブルシューティング、フォールバック |

詳細基準: `references/scoring-rubric.md`

### レポート出力フォーマット

```markdown
## Masao Quality Report: <skill-name>

**Grade**: <grade> (<score>/<max>)
**Path**: ~/.claude/skills/<skill-name>

| # | Dimension           | Score | Weight | Weighted | Key Finding          |
|---|---------------------|-------|--------|----------|----------------------|
| 1 | Trigger Precision   | ?/3   | 1.5x   | ?        | ...                  |
| 2 | Structure Balance   | ?/3   | 1.0x   | ?        | ...                  |
| 3 | Metadata            | ?/3   | 1.0x   | ?        | ...                  |
| 4 | Guardrails & Safety | ?/3   | 1.5x   | ?        | ...                  |
| 5 | Actionability       | ?/3   | 1.0x   | ?        | ...                  |
| 6 | Reference Arch.     | ?/3   | 1.0x   | ?        | ...                  |
| 7 | Terminology         | ?/3   | 0.5x   | ?        | ...                  |
| 8 | Error Handling      | ?/3   | 1.0x   | ?        | ...                  |
| **Total**            |       |        | **?/24** |                      |

### Top 3 改善提案
1. ...
2. ...
3. ...
```

**グレード判定:**
- **S** (22-24): Excellent
- **A** (18-21): Good
- **B** (14-17): Acceptable
- **C** (10-13): Needs Work
- **D** (< 10): Poor

---

## Frame モード

`references/skill-frame-template.md` を読み込み、ユーザーの要件に合わせてカスタマイズ。

### 手順

1. ユーザーにスキル名・目的・対象ツールをヒアリング
2. テンプレートを基にフロントマター・本文・参照ファイル構成を生成
3. 生成後に check モードで自己診断し、A 以上を目指す

テンプレート: `references/skill-frame-template.md`

---

## ⚠️ ガードレール

### 禁止事項

| 禁止 | 理由 |
|------|------|
| 他スキルの SKILL.md を書き換える | masao は診断のみ。修正はユーザーが行う |
| スコアの水増し | null 次元は正直に「AI判断必要」と報告 |
| 既存スキルの削除・無効化 | read-only ツールのみ使用 |

### 安全な運用

- masao は **Read / Grep / Glob / Bash (read系)** のみ使用
- スキルの改修提案は出すが、実際の修正は別のワークフローで実施
- バッチモードでも各スキルの結果を正確に報告

---

## エラーハンドリング

| 症状 | 原因 | 対処 |
|------|------|------|
| `SKILL.md not found` | パス誤り or スキルが存在しない | パスを確認、`ls ~/.claude/skills/` で一覧 |
| `yaml module not found` | PyYAML 未インストール | `pip install pyyaml` |
| `quick_validate.py not found` | skill-creator 未インストール | 基本検証をスキップし他次元のみ評価 |
| スコアが全て null | スクリプト実行エラー | エラーログ確認、手動で全次元評価 |

---

## リソース

| ファイル | 内容 |
|----------|------|
| `scripts/masao_check.py` | 自動品質チェックスクリプト |
| `references/scoring-rubric.md` | 8次元スコアリング詳細基準 |
| `references/quality-patterns.md` | 良い/悪いパターン実例集 |
| `references/skill-frame-template.md` | 新規スキル作成テンプレート |
