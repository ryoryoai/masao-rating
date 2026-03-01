# Skill Frame Template — 新規スキル作成テンプレート

masao の品質基準を構造的に満たすスキルの雛形。

---

## フロントマター

```yaml
---
name: <skill-name>
description: >
  <1-2文でスキルの目的を記述>.
  Triggers: <日本語トリガー1>, <日本語トリガー2>, <日本語トリガー3>,
  <英語トリガー1>, <英語トリガー2>, <英語トリガー3>,
  <バリエーション1>, <バリエーション2>, <バリエーション3>, <バリエーション4>.
  Do NOT load for: <除外ケース1>(use <別スキル>), <除外ケース2>(use <別スキル>).
allowed-tools: [<必要最小限のツールリスト>]
metadata:
  skillport:
    category: <skill-name>
    tags: [<tag1>, <tag2>, <tag3>, <tag4>]
    alwaysApply: false
---
```

### トリガー設計チェックリスト

- [ ] 10個以上のトリガーキーワードを設定
- [ ] 日本語トリガーを含む（漢字・ひらがな両方）
- [ ] 英語トリガーを含む
- [ ] 否定トリガー（Do NOT load for）を設定
- [ ] 競合するスキル名を否定トリガーで明示

---

## 本文テンプレート（200行以内）

```markdown
# <Skill Title>

<1-2文の概要説明>

---

## モード / コマンド

| モード | コマンド | 用途 |
|--------|----------|------|
| ... | ... | ... |

---

## 使い方

### 基本手順

1. <ステップ1>
2. <ステップ2>
3. <ステップ3>

### コマンド例

\```bash
<具体的なコマンド>
\```

---

## ⚠️ ガードレール

### 禁止事項

| 禁止 | 理由 |
|------|------|
| <禁止事項1> | <なぜダメか> |
| <禁止事項2> | <なぜダメか> |

### 安全な運用

- <安全に使うためのポイント1>
- <安全に使うためのポイント2>

---

## エラーハンドリング

| 症状 | 原因 | 対処 |
|------|------|------|
| <エラー1> | <原因1> | <対処1> |
| <エラー2> | <原因2> | <対処2> |

---

## リソース

| ファイル | 内容 |
|----------|------|
| `scripts/<script>.py` | <スクリプトの説明> |
| `references/<ref>.md` | <参照ファイルの説明> |
```

---

## ディレクトリ構成テンプレート

```
<skill-name>/
├── SKILL.md                    # メイン定義 (< 200行)
├── scripts/                    # 実行可能スクリプト (必要な場合)
│   └── <script>.py
├── references/                 # 参照ドキュメント (1階層のみ)
│   ├── <topic1>.md
│   └── <topic2>.md
└── agents/
    └── openai.yaml             # UI メタデータ
```

---

## agents/openai.yaml テンプレート

```yaml
interface:
  display_name: "<User-Facing Name>"
  short_description: "<25-64文字の簡潔な説明>"
```

---

## リリース前セルフチェックリスト

### 必須チェック

- [ ] `python3 ~/.claude/skills/.system/skill-creator/scripts/quick_validate.py <path>` がパス
- [ ] SKILL.md が 200行以内
- [ ] トリガーが 10個以上（日英バイリンガル）
- [ ] 否定トリガーが設定済み
- [ ] allowed-tools が最小権限で設定済み
- [ ] metadata.skillport が完備（category, tags, alwaysApply）

### 品質チェック

- [ ] ガードレールセクションがある
- [ ] エラーハンドリングセクションがある
- [ ] references/ が 1階層構成
- [ ] SKILL.md 内の参照リンクが全て実在するファイルを指す
- [ ] TODO / FIXME / HACK が残っていない
- [ ] 時間依存情報（「最新」「現在」「今年」）がない

### 最終確認

- [ ] `python3 ~/.claude/skills/masao/scripts/masao_check.py <path>` で A 以上
- [ ] 他の既存スキルとトリガーが重複していない
