# IROHA — UniDic 日本語IME辞書

現代書き言葉UniDic 2025.12（元データ版）を元に作成した、日本語IME向けの語彙辞書です。Mozcには依存しません。基礎辞書は **456,209件**で、各レコードは「表記・ひらがな読み・品詞・コスト」の4項目です。

このリポジトリの公開時期は **2026年11月**です。UniDic元データの版（2025.12）と、リポジトリの公開時期（2026年11月）は別の情報です。Releaseタグ `v2025-12`、ディレクトリ名や配布ファイル名の `2025-12` は元データ版に対応する識別子です。

## ダウンロードと使い方

- UTF-8 TSV（ヘッダーなし、タブ区切り）: [`data/2025-12/tsv/`](data/2025-12/tsv/)
- SQLite版を含む完全な配布物: [最新のGitHub Release](https://github.com/appipinopi/IROHA/releases/latest) から `ime-dictionary-unidic-2025-12.zip` をダウンロード
- 配布ZIPの内部ファイル一覧・件数・生成情報: [`data/2025-12/manifest.json`](data/2025-12/manifest.json)

SQLiteのテーブルは `entries(surface, reading, pos, cost)` です。読みから検索する例:

```sql
SELECT surface, pos, cost
FROM entries
WHERE reading = 'とうきょう'
ORDER BY cost, surface;
```

TSVやSQLiteを単体で再配布する場合も、出典・ライセンス表示の [`NOTICE.txt`](NOTICE.txt) と [`LICENSE-BSD.txt`](LICENSE-BSD.txt) を一緒に配布してください。出典情報は個々の辞書行やSQLiteの列には入れず、別ファイルで管理しています。

## 追加語の提案

既存の基礎TSVは直接編集せず、[`contributions/additions.tsv`](contributions/additions.tsv) に「表記・ひらがな読み・品詞・整数コスト」の4列を1語1行で追加し、Pull Requestで提案してください。出典名・URL・適用ライセンス・再配布が許される根拠を [`contributions/SOURCES.txt.example`](contributions/SOURCES.txt.example) に沿って記録します。出典や権利条件を確認できない語は取り込みません。手順とローカル検証方法は [`CONTRIBUTING.md`](CONTRIBUTING.md) を参照してください。

## 収録内容と注意点

表記にはUniDicの基底表記を使い、活用形などの非基底形、句読記号・絵文字などを含むデータ、利用可能な読みのないデータを除外しています。ひらがな・カタカナだけの表記は表記自体から読みを作り、それ以外はUniDic由来の読み候補を使います。同一の表記・読み・品詞の重複はまとめ、最も低い元コストを残しています。単語や読みを自動生成して水増ししていません。

`cost` はUniDic/Mecab由来の値で、特定IMEの候補順位向けに調整したものではありません。実装先IMEで評価・調整してください。本辞書はUniDicの派生物であり、UniDicまたは国立国語研究所による推奨・承認を示すものではありません。

## 出典・ライセンス

出典は[現代書き言葉UniDic 2025.12のフル配布物](https://clrd.ninjal.ac.jp/unidic_archive/2512/unidic-cwj-202512_full.zip)です。元データのSHA-256、加工内容、権利表示は [`NOTICE.txt`](NOTICE.txt) を参照してください。

ライセンスの範囲を分けています。**辞書データは修正BSD**（条件は [`LICENSE-BSD.txt`](LICENSE-BSD.txt)）、**このリポジトリの生成・補助スクリプトはMIT**（[`LICENSE-MIT.txt`](LICENSE-MIT.txt)）です。辞書データを再配布する際は修正BSDの表示を保持してください。

## 再生成

Python 3.9以降・標準ライブラリのみで動作します。UniDicの公式フルZIP全体ではなく、必要なファイルだけを取得できます。

```bash
python3 scripts/fetch_unidic_source.py --output-dir build/unidic-source
python3 scripts/build_dictionary.py \
  --source-csv build/unidic-source/lex.csv \
  --output-dir build/2025-12
```

ビルドスクリプトは現時点でUniDic 2025.12用です。次の版に更新するときは、CSV列仕様・ライセンス・配布URLを確認し、新しい版のディレクトリとリリースを作成してください。

## ライセンスファイル

- [`LICENSE-BSD.txt`](LICENSE-BSD.txt): UniDic由来の辞書データ
- [`LICENSE-MIT.txt`](LICENSE-MIT.txt): 生成・補助スクリプト
