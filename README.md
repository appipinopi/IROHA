# IROHA 日本語IME辞書

IROHAは、Mozc・UniDic由来の語彙やMozcへの実行時依存を使わない、日本語IME向けの独立した辞書です。2026-11-28版には **7,054,954行** を収録しています。

## 最新版をダウンロード

- [Releaseページ v2026-11-28](https://github.com/appipinopi/IROHA/releases/tag/v2026-11-28)
- [辞書一式ZIP（約483 MB）をダウンロード](https://github.com/appipinopi/IROHA/releases/download/v2026-11-28/IROHA-dictionary-2026-11-28-local-verified-7054954.zip)
- [ZIP内のREADMEを単独で読む](https://github.com/appipinopi/IROHA/releases/download/v2026-11-28/README.md)

辞書のTSV・SQLiteはRelease ZIPに収録されています。GitHubのファイル一覧にTSVシャードが個別表示されないのは、ソースコードと配布データを分けているためです。ZIP内の `tsv/` にある16個のTSVファイルが辞書本体です。

Release ZIPには、TSV・SQLiteのほか、元データ、出典別の帰属表、ライセンス資料、生成コード、再生成手順をまとめています。各データの採用条件とライセンスはZIP内READMEおよび同梱文書を確認してください。

## 辞書の形式

TSVはUTF-8、ヘッダーなし、タブ区切りの5列です。

```text
reading<TAB>left_id<TAB>right_id<TAB>cost<TAB>surface
```

`left_id`・`right_id` はIROHA独自の品詞クラスID、`cost` はIROHA独自の候補順位ヒューリスティックです。Mozc用の接続IDやコストとは互換ではありません。出典情報は辞書の各行に埋め込まず、別の帰属表で管理しています。

## 出典とライセンス

配布物は無料です。データ全体に単一のライセンスを一律適用しているわけではなく、各出典の利用条件と表示を個別に保っています。再配布時はZIP内のライセンス資料と帰属表示を維持してください。第三者による商用利用の可否も、各データのライセンスに従います。

## 再生成について

このリポジトリには基礎辞書を作る `build_iroha.py` と元データ取得用の `fetch_sources.py` があります。2026-11-28版の全7,054,954行を再生成する手順・拡張スクリプト・元データは、Release ZIP内READMEに記載・同梱しています。
