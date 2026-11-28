# IROHA 日本語IME辞書

IROHAは、Mozc・UniDic由来の語彙やMozcへの実行時依存を使わない、日本語IME向けの独立した辞書です。2026-11-28-r2版には **7,084,033行** を収録しています。

## 最新版をダウンロード

- [Releaseページ v2026-11-28-r2](https://github.com/appipinopi/IROHA/releases/tag/v2026-11-28-r2)
- [辞書・SQLite・元データを含む一式ZIPをダウンロード](https://github.com/appipinopi/IROHA/releases/download/v2026-11-28-r2/IROHA-dictionary-2026-11-28-r2-verified-7084033.zip)
- [ZIP内のREADMEを単独で読む](https://github.com/appipinopi/IROHA/releases/download/v2026-11-28-r2/README.md)

TSVシャード18個（全7,084,033行）は、[GitHubの `tsv/` ディレクトリ](https://github.com/appipinopi/IROHA/tree/main/tsv)にも個別ファイルとして公開しています（Release ZIP内の同名ファイルと同一です）。SQLiteはRelease ZIPに収録されています。

Release ZIPには、TSV・SQLiteのほか、元データ、出典別の帰属表、ライセンス資料、生成コード、再生成手順をまとめています。各データの採用条件と利用条件はZIP内README、`LICENSE-DATA.md`、`LICENSE-INDEX.md`、NOTICE類で確認できます。

## 辞書の形式

TSVはUTF-8、ヘッダーなし、タブ区切りの5列です。

```text
reading<TAB>left_id<TAB>right_id<TAB>cost<TAB>surface
```

`left_id`・`right_id` はIROHA独自の品詞クラスID、`cost` はIROHA独自の候補順位ヒューリスティックです。Mozc用の接続IDやコストとは互換ではありません。出典情報は辞書の各行に埋め込まず、別の帰属表で管理しています。

## 出典とライセンス

配布物は無料です。データ全体に単一のライセンスを一律適用しているわけではなく、各出典の利用条件と表示を個別に保っています。日本郵便とNDLには公式の再利用・出典表示条件を適用し、独立したSPDXライセンス名を付与していません。再配布時はZIP内のライセンス資料と帰属表示を維持してください。第三者による再利用条件も、各出典の条件に従います。

新規追加語彙の行別出典対応表: [日本郵便](JAPAN-POST-ATTRIBUTION.tsv) / [NDL](NDL-ATTRIBUTION.tsv)。原データと保存された公式条件は一式ZIPに含みます。

## 再生成について

このリポジトリには基礎辞書を作る `build_iroha.py` と元データ取得用の `fetch_sources.py` があります。2026-11-28-r2版の全7,084,033行を再生成する手順・拡張スクリプト・元データは、Release ZIP内READMEに記載・同梱しています。
