# 更新・追加への参加方法

追加語はPull Requestで提案できます。基礎辞書のTSVや生成済みファイルを直接書き換えず、追加語TSVと出典・権利情報をセットで提出してください。ライセンスと再配布の根拠を確認できない語は取り込みません。

## 追加語の形式

`contributions/additions.tsv` に、次の4列をタブ区切りで1語1行に記入します。ヘッダーは付けません。

1. 表記
2. ひらがな読み
3. 品詞（例: `名詞/普通名詞/一般`）
4. 整数コスト

空行と `#` で始まるコメント行は無視されます。追加語の読みはひらがなで記入してください。既存辞書と同じ（表記・読み・品詞）のレコードや、候補ファイル内の重複はエラーになります。既存語のコストを変更する用途では使わず、別の変更提案として説明してください。

## 出典・権利情報

TSV行には出典名・権利表示を入れません。追加語の根拠と再配布条件は `contributions/SOURCES.txt` にまとめます。`contributions/SOURCES.txt.example` を雛形として使い、作者/提供元、出典URL、適用ライセンスと再配布の根拠を記載してください。このファイルは誤公開を防ぐためGitで通常は無視されます。提出する場合は内容を完成させたうえで、明示的に `git add -f contributions/SOURCES.txt` してPull Requestに含めてください。このファイルは統合後に `SUPPLEMENTAL-NOTICE.txt` として配布物へコピーされます。ライセンス本文の同梱が必要な場合は、その全文も `SOURCES.txt` の末尾に追記してください。

出典や権利条件が不明な語、再配布許諾が確認できないデータは追加しないでください。UniDicの修正BSDライセンスが別のデータソースにも当然適用されるわけではありません。第三者データを追加する場合は、そのデータ固有の出典・表示・ライセンスを必ず分けて記録します。

## ローカルでの統合・検証

リポジトリのルートで実行します。既存データは変更せず、出力先には新しいディレクトリを指定してください。

```bash
python3 scripts/merge_additions.py \
  --base-dir data/2025-12 \
  --additions-tsv contributions/additions.tsv \
  --source-notice contributions/SOURCES.txt \
  --output-dir build/2025-12-with-additions
```

出力には並べ替え済みTSV、SQLite、manifest、SHA-256一覧、UniDicのNOTICE/LICENSE、追加データ用の `SUPPLEMENTAL-NOTICE.txt` と入力TSVが入ります。補助スクリプトは重複を黙って統合せず、競合時に停止します。

## UniDicの新しい版

`build_dictionary.py` と `fetch_unidic_source.py` は現時点でUniDic 2025-12の配布URL・列仕様を前提にしています。新しい版を追加するときは、まず公式配布物の列仕様、ライセンス本文、出典URLを確認し、版ごとの `data/<version>/` と変更履歴を作ってください。生成されたTSV/SQLiteの件数・整合性・SHA-256を検証し、既存版を上書きせず新しいGitタグとRelease assetとして配布します。

リリースには辞書ZIP、含まれる全ファイルのチェックサム、変更内容、出典とライセンス表示を添付します。追加したデータに新しい権利表示がある場合は、それもZIP内の別ファイルに含めます。
