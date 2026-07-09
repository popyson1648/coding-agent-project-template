# Coding Agent Project Template

[English](README.md) | **日本語**

[![CI](https://img.shields.io/github/actions/workflow/status/popyson1648/coding-agent-project-template/ci.yml?branch=main&label=CI)](https://github.com/popyson1648/coding-agent-project-template/actions/workflows/ci.yml)
[![Latest Release](https://img.shields.io/github/v/release/popyson1648/coding-agent-project-template?label=release)](https://github.com/popyson1648/coding-agent-project-template/releases)
[![License](https://img.shields.io/github/license/popyson1648/coding-agent-project-template?label=license)](LICENSE)

コーディングエージェント(Claude Code、Gemini CLI、Codex など)と一緒に作業するためのプロジェクトハーネスです。
共通のエージェントルール、プラン・決定ログ、プロジェクトドキュメントの雛形、pre-commit と CI に組み込まれた
単一の検証エントリポイントを提供します。

このテンプレートを導入した後は、この README を自分のプロジェクト用の README に置き換えてください。

## 目次

- [含まれるもの](#含まれるもの)
- [新規プロジェクトを始める](#新規プロジェクトを始める)
- [既存プロジェクトに導入する](#既存プロジェクトに導入する)
- [テンプレートを最新版に更新する](#テンプレートを最新版に更新する)
- [必要環境](#必要環境)
- [ライセンス](#ライセンス)

## 含まれるもの

- `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`: エージェントが読み込むリポジトリルール。内容は同一に保たれます。
- `.plans/`: タスクごとの Markdown プラン(`.plans/TEMPLATE.md`)。
- `.decisions/`: 決定ごとの Markdown レコード(`.decisions/TEMPLATE.md`)。
- `.project/`: 現在のプロジェクトドキュメント(conventions, structure, build, testing, release)。
- `.template/`: `.project/` 配下のファイルおよび設定ファイルの雛形。
- `scripts/verify.py`: `.project/verification.toml` で定義された検証フェーズを実行します。
- `.pre-commit-config.yaml`、`.github/workflows/ci.yml`、`.github/dependabot.yml`: ローカル検証、
  CI 検証、GitHub Actions の更新確認を行います。
- `.gitignore`: Python、OS、エディタ由来の最低限の無視設定。プロジェクトの言語やツールに合わせて
  追記してください。

## 新規プロジェクトを始める

1. GitHub で **Use this template** をクリックしてリポジトリを作成する。
2. `.template/` の雛形をもとに `.project/` のドキュメントを記入する。
3. 実際のツールを導入したフェーズから `.project/verification.toml` で有効化する。
4. ローカルフックをインストールする: `pre-commit install`。

## 既存プロジェクトに導入する

GitHub の "Use this template" は新規リポジトリしか作成できないため、既存プロジェクトへの導入はファイルコピーになります。

1. Git 履歴なしでテンプレートをダウンロードする(同等の方法であれば何でも構いません。
   下の `npx giget` 例を使う場合は Node.js/npm が必要です):

   ```bash
   npx giget@latest gh:popyson1648/coding-agent-project-template .tmp/agent-template
   ```

2. プロジェクトのルートから、まだ存在しないものだけをコピーする(`-n` は既存ファイルを上書きしません。
   最近の GNU cp はこのオプションに移植性の警告を出し、同等の `--update=none` を案内します):

   ```bash
   cp -Rn .tmp/agent-template/.plans .tmp/agent-template/.decisions \
          .tmp/agent-template/.project .tmp/agent-template/.template .
   cp -n .tmp/agent-template/AGENTS.md .tmp/agent-template/CLAUDE.md \
         .tmp/agent-template/GEMINI.md .tmp/agent-template/.pre-commit-config.yaml .
   mkdir -p scripts .github/workflows
   cp -n .tmp/agent-template/scripts/verify.py scripts/
   cp -n .tmp/agent-template/.github/workflows/ci.yml .github/workflows/
   cp -n .tmp/agent-template/.github/dependabot.yml .github/
   ```

3. すでに存在していたものは手作業で整合させる: 既存の `AGENTS.md`/`CLAUDE.md`/`GEMINI.md` にテンプレートの
   ルールを統合し(3ファイルの内容は同一に保つ)、既存の pre-commit と CI 設定に検証ステップを統合して、
   どちらも `python3 scripts/verify.py` を実行するようにする。
4. `.template/` をもとに `.project/` のドキュメントを記入し、`.project/verification.toml` に実際のコマンドを
   設定する(フェーズは最初は無効なので、有効化するまで CI は green のままです)。
5. 検証して後片付けする:

   ```bash
   python3 scripts/verify.py
   pre-commit install
   rm -rf .tmp/agent-template
   ```

## テンプレートを最新版に更新する

テンプレートに変更が公開されるたびに `.template-version`(source commit・公開日時・リリースタグ)が
更新され、日付付きの [GitHub Release](https://github.com/popyson1648/coding-agent-project-template/releases)
が自動生成ノート付きで作成されます。人が読める版数は上部のバッジまたは Releases ページで、
機械可読な版数は `.template-version` で確認できます。どちらも手で編集しないでください。

### 推奨: テンプレートを remote に追加してマージする

新規作成("Use this template")・ファイルコピーどちらの導入方法でも機能します。

```bash
git remote add template https://github.com/popyson1648/coding-agent-project-template.git
git fetch template
git merge template/main --allow-unrelated-histories   # 初回のみ
```

2回目以降は通常の3-way マージです:

```bash
git fetch template && git merge template/main
```

- git がマージベースを記録するため、ローカルのカスタマイズは保持され、衝突は両側が同じ行を変更した
  箇所にのみ発生します。解消したら `python3 scripts/verify.py` を実行し、commit してください。
- テンプレートのマージを squash しないでください。squash するとマージベースが失われ、以後の同期が
  毎回最初から衝突するようになります。

### 代替: remote を追加せずに差分だけ適用する

`.template-version` があれば、テンプレートの旧→新の差分だけを適用できます:

```bash
git clone https://github.com/popyson1648/coding-agent-project-template .tmp/template
BASE=$(git -C .tmp/template log --format=%H \
  --grep "$(sed -n 's/^source-commit: //p' .template-version)")
git -C .tmp/template diff "$BASE"..HEAD | git apply --reject
rm -rf .tmp/template
```

`.rej` ファイルは手作業で解消し(この差分は `.template-version` も更新します)、
`python3 scripts/verify.py` を実行してから commit してください。可能な限りマージ経路を優先してください。
本物の3-way マージのほうが単純なパッチ適用より多くのケースを解決できます。

`.template-version` が存在する前に導入したプロジェクトはマージ経路を使ってください。初回の
`--allow-unrelated-histories` 同期がマージベースを確立します。

定期的な自動更新 PR が欲しい場合は、サードパーティの
[actions-template-sync](https://github.com/AndreasAugustin/actions-template-sync) アクションを参照してください
(プロジェクトごとに独自のトークン設定が必要です)。

## 必要環境

- Python 3.11 以上(`scripts/verify.py` 用)
- [pre-commit](https://pre-commit.com/)(ローカルフック用)
- 上記の `npx giget` 導入コマンドを使う場合のみ Node.js/npm

## ライセンス

このテンプレートは [Mozilla Public License 2.0](LICENSE) の下でライセンスされています。
