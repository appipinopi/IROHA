# IROHA 日本語IME辞書 — 2026-11-27版

Mozc・UniDicを使わない環境向けの独立した日本語IME辞書です。辞書、元データ、生成スクリプト、出典・ライセンス資料を一つの配布アーカイブにまとめ、利用者が元ファイルを複数サイトから個別に探して取得しなくても済む形で無料公開します。

## この版の収録数

**TSV 6ファイル × 1,000,000行 = 合計6,000,000行**です。生成された10,470,706件の一意候補から、優先順位上位の6,000,000件を収録しています。6百万は基礎見出し語の数ではなく、見出し語・固有名詞・活用形・結合形を合わせたレコード数です。

| レコード種別 | 収録数 |
| --- | ---: |
| 基礎語彙 | 396,540 |
| 固有名詞 | 744,140 |
| 「名詞＋する」形 | 19,481 |
| 活用形 | 1,160,705 |
| 補助動詞との結合形 | 3,679,134 |
| **合計** | **6,000,000** |

結合形はJMdictの品詞・活用情報に基づき、テ形＋補助動詞の規則で生成しています。機械生成した語形がすべて自然・一般的とは限りません。未収録候補は4,470,706件です。件数・出典ハッシュ・生成時刻・選定方針は `manifest.json` を確認してください。

## ファイル形式

TSVはUTF-8、ヘッダーなし、タブ区切りです。列順:

```text
reading<TAB>left_id<TAB>right_id<TAB>cost<TAB>surface
```

`left_id` / `right_id` はIROHA独自の品詞クラスID、`cost` もIROHA独自の候補順位ヒューリスティックです。Mozcの語彙・接続ID・コストは使用しておらず、Mozc用のドロップイン辞書ではありません。SQLite版のテーブルは `entries(reading, left_id, right_id, cost, surface)` です。

## 一括ダウンロードと再生成

配布アーカイブは[GitHub Releases](https://github.com/appipinopi/IROHA/releases/latest)から無料で取得できます。TSV・SQLite・JMdict/JMnedict元データ・生成コード・ライセンス資料を一つにまとめており、この配布物だけで辞書を使い、再生成できます。

同梱元データから再生成する場合:

```bash
python3 build_iroha.py --source source/JMdict.gz --names-source source/JMnedict.xml.gz \
  --out release --work-db buildtmp/candidates.sqlite3 --target 6000000
```

元データを公式サイトからまとめて再取得する場合:

```bash
python3 fetch_sources.py
```

配布物各ファイルのSHA-256は `SHA256SUMS.txt` を参照してください。

## ライセンス

辞書データはJMdict・JMnedictを加工・拡張したもので、**CC BY-SA 4.0**で公開します。出典表示と条件は `NOTICE.txt`、`LICENSE-DATA.md`、`licenses/CC-BY-SA-4.0.txt` を参照してください。生成コードはデータと別に `LICENSE-MIT.txt` に従います。

IROHAプロジェクトは無料で配布します。ただしCC BY-SA 4.0は、表示・継承条件を守る第三者の改変・再配布や商用利用も認めます。第三者による販売まで禁止するライセンスではありません。元データの著作権はEDRDG等の各権利者に帰属し、EDRDGによる本プロジェクトの推奨・承認を示すものではありません。
