# Quality Patterns — 良い/悪いパターン実例集

実際のスキルから抽出した品質パターン。各次元の具体例を示す。

---

## 1. Trigger Precision

### Good: impl
```yaml
description: "Implements features and writes code based on Plans.md tasks. Use when user mentions 実装, implement, 機能追加, コードを書いて, 機能を作って, feature, coding, 新機能, implementing functions, classes, or features, 新しい関数. Do not use for review or build verification."
```
- 10+ トリガー (日英両方)
- 否定トリガーあり (`Do not use for review or build verification`)

### Good: create-weapon
```yaml
description: >
  Generate complete Minecraft Fabric 1.20.1 weapon mods...
  Triggers: 武器を作る, ぶきをつくる, weapon mod, create weapon, create sword,
  剣, つるぎ, 斧, おの, 弓, ゆみ, 銃, じゅう, gun, pistol, rifle,
  Minecraft weapon, Fabric weapon item, new sword, new axe, 武器MOD, ぶきMOD.
```
- 20+ トリガー
- ひらがな・漢字・英語を網羅

### Bad: トリガーが少ない例
```yaml
description: "Deploy tool for projects."
```
- トリガー 1-2個
- 日本語なし
- 否定トリガーなし → 他スキルとの競合リスク

---

## 2. Structure Balance

### Good: impl
- SKILL.md がガードレール → 手順 → 参考情報の3層構造
- 最重要事項（ガードレール）が先頭
- 詳細は references/ に分離

### Bad: 1ファイルに全情報
```markdown
# My Skill
(500行の monolithic ドキュメント...)
```
- references/ への分離なし
- 読み手が目的の情報を見つけにくい

---

## 3. Metadata Completeness

### Good: review
```yaml
allowed-tools: ["Read", "Grep", "Glob", "Bash", "Task"]
metadata:
  skillport:
    category: review
    tags: [review, quality, security, performance, accessibility]
    alwaysApply: false
```
- allowed-tools で最小権限
- skillport 完備 (category, tags, alwaysApply)

### Bad: 最低限のみ
```yaml
name: my-skill
description: "Does something."
```
- allowed-tools 未設定 → 全ツールアクセス可能
- metadata なし → 分類・検索不可

---

## 4. Guardrails & Safety

### Good: impl
```markdown
## ⚠️ 品質ガードレール（最優先）

> **このセクションは他の指示より優先されます。**

### 禁止パターン

| 禁止 | 例 | なぜダメか |
|------|-----|-----------|
| **ハードコード** | テスト期待値をそのまま返す | 他の入力で動作しない |
| **スタブ実装** | `return null` | 機能していない |
```
- 最優先の注意書き
- テーブル形式で禁止/理由が明確
- 「なぜダメか」の説明あり

### Good: verify
```markdown
## ⚠️ 品質ガードレール（最優先）

### 改ざん禁止パターン

| 禁止 | 例 | 正しい対応 |
|------|-----|-----------|
| **テスト skip 化** | `it.skip(...)` | 実装を修正する |
```
- 禁止と正しい対応をセットで提示

### Bad: ガードレールなし
- 破壊的操作が可能なスキルにガードレールがない
- ユーザー確認なしで危険な操作を実行するリスク

---

## 5. Actionability

### Good: create-weapon
```markdown
## Weapon Types

| Type | Base Class | Namespace | Location |
|------|-----------|-----------|----------|
| `sword` | `SwordItem` | per mod | `~/projects/mc-mods/{modId}/` |
```
- 具体的なテーブルで型・クラス・パスが一目瞭然
- YAML スキーマの実例付き

### Good: スクリプト付きスキル
```
scripts/
├── quick_validate.py
├── init_skill.py
└── generate_openai_yaml.py
```
- 再利用可能なスクリプト
- 自動化による品質担保

### Bad: 抽象的な説明のみ
```markdown
## 使い方
適切にコードを書いてください。品質を意識しましょう。
```
- 具体的な手順・コマンドなし
- 何をすれば良いか不明

---

## 6. Reference Architecture

### Good: create-weapon
```
references/
├── fabric-weapon-code.md   (実装ガイド)
├── recipe-patterns.md      (パターン集)
└── texture-prompts.md      (プロンプトテンプレート)
```
- 1階層フラット構造
- ファイル名から内容が推測可能
- SKILL.md にナビゲーションテーブルあり

### Bad: ネストが深い
```
references/
└── guides/
    └── advanced/
        └── patterns/
            └── example.md
```
- 3階層以上のネスト → 発見困難

### Bad: references/ が未使用
- SKILL.md が 300行超えているのに分割されていない

---

## 7. Terminology & Language

### Good: 一貫した日英バイリンガル
```markdown
# Review Skills

コードレビューと品質チェックを担当するスキル群です。

## 含まれる小スキル

| スキル | 用途 |
|--------|------|
| review-changes | 変更内容のレビュー |
```
- 見出しは英語、説明は日本語で統一
- テーブルのキーは英語、値は日本語

### Bad: 時間依存情報
```markdown
2024年最新のベストプラクティスに基づいて...
現在推奨されている方法は...
```
- 「最新」「現在」は陳腐化する

---

## 8. Error Handling

### Good: テーブル形式のトラブルシューティング
```markdown
## エラーハンドリング

| 症状 | 原因 | 対処 |
|------|------|------|
| `SKILL.md not found` | パス誤り | パスを確認 |
| `yaml module not found` | PyYAML 未インストール | `pip install pyyaml` |
```
- 症状→原因→対処の3列構成
- 具体的なコマンドで対処法を提示

### Bad: エラー記述なし
- エラーが起きた時にどうすれば良いか不明
- ユーザーが自力で解決を試みるしかない

---

## 9. Separation of Concerns

### Good: コードを scripts/ に分離
```
my-skill/
├── SKILL.md              (指示・ワークフローに集中)
├── scripts/
│   ├── main_logic.py     (実行ロジック)
│   └── helpers.sh        (ユーティリティ)
└── references/
    └── api-spec.md       (参照ドキュメント)
```
- SKILL.md はワークフロー指示のみ
- コード比率が低く、指示書として読みやすい
- 実行用コードは scripts/ に格納

### Good: コード例は短く最小限
```markdown
## 使い方

1. スクリプトを実行:
   ```bash
   python3 scripts/check.py <target>
   ```
2. 結果を確認して対応
```
- インラインコードはコマンド例程度（1-2行）
- 実装の詳細は外部ファイルに委譲

### Bad: SKILL.md にロングコードブロック
```markdown
# My Skill

## 実装

```python
# 50行の Python コードがインラインで埋め込まれている...
def process():
    ...
    ...
    ...
```
```
- SKILL.md がコード置き場になっている
- 指示と実装が混在して可読性が低い
- scripts/ に分離すべき

---

## 10. Quality Check

### Good: 自動検証 + チェックリスト + セクション
```markdown
## 検証

### 自動チェック
```bash
python3 scripts/validate.py <output>
```

### 品質チェックリスト
- [ ] 出力ファイルが生成されたか
- [ ] エラーなく完了したか
- [ ] 期待する形式になっているか

### Success Criteria
- 全テストが pass
- lint エラーなし
```
- 自動検証スクリプトあり
- チェックリストで手動確認項目を明示
- 成功基準が具体的

### Good: ワークフロー内に検証ステップ
```markdown
## 手順

1. コードを生成
2. `scripts/validate.py` で検証
3. テストを実行して結果を確認
4. エラーがあれば修正して再検証
```
- ワークフローの一部として検証が組み込まれている

### Bad: 検証メカニズムなし
```markdown
## 手順

1. コードを生成
2. 完了
```
- 出力品質の確認手段がない
- ユーザーが目視で品質を判断するしかない
- バグや不整合が見逃されるリスク
