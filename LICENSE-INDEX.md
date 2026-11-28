# IROHA 辞書データ・ライセンス索引

この配布物は複数の独立したデータソースを含み、**全データに単一のライセンスを一律適用していません**。コンポーネントごとの条件と出典表示を以下で確認してください。各ライセンス本文は `licenses/` に同梱しています。配布・改変・再利用時はライセンス本文と各ソースの表示条件が優先されます。

| コンポーネント | データのライセンス | 同梱するライセンス全文・表示 | 原データ・帰属記録 |
| --- | --- | --- | --- |
| JMdict / JMnedictおよび選定Wiktionaryデータ | CC BY-SA 4.0 | [`licenses/CC-BY-SA-4.0-LEGALCODE.txt`](licenses/CC-BY-SA-4.0-LEGALCODE.txt) | EDRDG表示は `NOTICE.txt`、Wiktionary項目ページは `WIKTIONARY-ATTRIBUTION.tsv` と `WIKTIONARY-ATTRIBUTION-EXPANDED.tsv` |
| Wiktionary上流テキストの別ライセンス | GFDL 1.3（上流の選択肢） | [`licenses/GFDL-1.3.txt`](licenses/GFDL-1.3.txt) | [Wiktionary著作権・ライセンス説明](https://en.wiktionary.org/wiki/Wiktionary:Copyrights)。この配布物の選定データはCC BY-SA 4.0で扱い、GFDLとの二重ライセンスを一律に主張しません |
| 国立国語研究所 教育基本語彙DB 2009B | CC BY 4.0 | [`licenses/LICENSE-CC-BY-4.0.txt`](licenses/LICENSE-CC-BY-4.0.txt) | `source/ninjal_kyoikukihongoi_2009B.csv`、`NINJAL-ATTRIBUTION.tsv` |
| 国立国語研究所 日本語教育基本語彙DB（6種対照） | CC BY 4.0 | [`licenses/LICENSE-CC-BY-4.0.txt`](licenses/LICENSE-CC-BY-4.0.txt) | `source/ninjal_rokushutaisho_2009.csv`、`NINJAL-JP-EDU-ATTRIBUTION.tsv` |
| JSTシソーラス2015年版から選定した見出し語・同義語とIROHA生成形 | CC BY-SA 4.0 | [`licenses/CC-BY-SA-4.0-LEGALCODE.txt`](licenses/CC-BY-SA-4.0-LEGALCODE.txt)、必須クレジットは [`licenses/LICENSE-JST-THESAURUS.txt`](licenses/LICENSE-JST-THESAURUS.txt)。NBDC READMEはIPA辞書に基づくと説明し、その由来文書としてIPADICの上流COPYING全文も `licenses/LICENSE-IPADIC.txt` に保持 | `source/jst-thesaurus/mecab_thesaurus.zip`、`source/jst-thesaurus/NBDC-README.html`、`JST-ATTRIBUTION.tsv` |
| 国立国語研究所「現代雑誌200万字言語調査」選定語彙 | CC BY 4.0 | [`licenses/LICENSE-CC-BY-4.0.txt`](licenses/LICENSE-CC-BY-4.0.txt)、元アーカイブ内notice `licenses/LICENSE-NINJAL-MAG200.txt` | `source/ninjal-magazines/Zasshi200.zip`、抽出CSV、`NINJAL-MAGAZINES-ATTRIBUTION.tsv` |
| Wikidata日本語Lexeme | CC0 1.0 | [`licenses/CC0-1.0-LEGALCODE.txt`](licenses/CC0-1.0-LEGALCODE.txt)、補足表示 `licenses/LICENSE-WIKIDATA-CC0.txt` | `source/wikidata-japanese-lexemes.jsonl.gz`、`WIKIDATA-ATTRIBUTION.tsv` |
| 日本語WordNet v2.1 | 同梱のWordNet個別許諾・表示 | `licenses/LICENSE-WORDNET.txt`（著作権表示・許諾・免責） | `source/wnja-2.1.xml`、`WORDNET-ATTRIBUTION.tsv`、`NOTICE.txt` |
| NAIST-JDIC 0.6.3.b-20111013 | BSD 3-Clause | `licenses/LICENSE-NAIST-JDIC.txt`（著作権表示・条項・免責） | `source/naist-jdic_0.6.3.b-20111013.orig.tar.gz`、`NAIST-ATTRIBUTION.tsv` |
| MeCab IPA Dictionary (IPADIC) 2.7.0-20070801 selected data | NAIST permission + ICOT additional terms (BSD-3-Clause-with-ICOT-term) | [`licenses/LICENSE-IPADIC.txt`](licenses/LICENSE-IPADIC.txt) (full upstream COPYING) | `source/mecab-ipadic-2.7.0-20070801.tar.gz`, `IPADIC-ATTRIBUTION.tsv`; [official source](https://sourceforge.net/projects/mecab/files/mecab-ipadic/2.7.0-20070801/mecab-ipadic-2.7.0-20070801.tar.gz/download), [Debian copyright record](https://metadata.ftp-master.debian.org/changelogs/main/m/mecab-ipadic/mecab-ipadic_2.7.0-20070801%2Bmain-3_copyright) |
| 日本郵便「住所の郵便番号」データ | 日本郵便は郵便番号データの著作権を主張せず自由配布可と明記。独立したSPDXライセンスは主張しない | `licenses/NOTICE-JAPAN-POST.txt`、`source/japanpost/README.md`（公式条件保存版と原ZIPを同梱） | `source/japanpost/utf_ken_all.zip`、`JAPAN-POST-ATTRIBUTION.tsv`、[公式利用条件](https://www.post.japanpost.jp/service/search/zipcode/download/utf-readme.html) |
| Web NDL Authorities（NDLSH / NDLGFT） | 公式Terms of Useは営利・非営利の再利用を認め、公開時の出典表示を要求。別個のSPDXライセンスは主張しない | `NOTICE-NDL.txt`、`source/ndl/README.md`、`source/ndl/use_en.html` | `source/ndl/ndlsh-tsv.zip`、`source/ndl/ndlgft-tsv.zip`、`NDL-ATTRIBUTION.tsv`、[公式利用条件](https://id.ndl.go.jp/information/use_en/) |
| IROHAの生成コード | MIT | `LICENSE-MIT.txt` | プロジェクトコード |

## 公式ライセンス本文の出典・固定値

- CC BY-SA 4.0: [公式legalcode](https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt)。同梱ファイルSHA-256: `28a9529c7d0bb4dc51f4bf5c116a3d16ef247a052f7591466768ddf563fd1cf5`。
- CC BY 4.0: [公式legalcode](https://creativecommons.org/licenses/by/4.0/legalcode.txt)。同梱ファイルSHA-256: `9ba9550ad48438d0836ddab3da480b3b69ffa0aac7b7878b5a0039e7ab429411`。
- CC0 1.0: [公式legalcode](https://creativecommons.org/publicdomain/zero/1.0/legalcode.txt)。同梱ファイルSHA-256: `a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499`。
- GFDL 1.3: [GNU公式本文](https://www.gnu.org/licenses/fdl-1.3.txt)。同梱ファイルSHA-256: `110535522396708cea37c72a802c5e7e81391139f5f7985631c93ef242b206a4`。

## 国立国語研究所データの帰属表示

2009Bと6種対照の両データ部分は、それぞれの原CSV、公式ページ、報告書情報および変更説明を保持し、CC BY 4.0条件を適用します。IROHAでの変更は、明示かな読みの正規化、保守的な表記選択、IROHA独自品詞ID・コスト、選定した規則活用形の生成です。6種対照CSVの各リスト由来マーカーや分類・出典列は辞書行に取り込んでいません。国立国語研究所（NINJAL）が本プロジェクトを推奨・承認していることを示しません。CC BY 4.0の部分をCC BY-SA 4.0へ一律に再ライセンスしたとは主張しません。

`LICENSE-DATA.md` はデータごとの追加説明、`NOTICE.txt` は配布時に保持すべきソース表示、`SHA256SUMS.txt` は配布ファイルの整合性確認に使えます。これは法的助言ではありません。

## JSTシソーラスの必須表示

NBDC公式READMEは、科学技術用語形態素解析辞書のクレジットを次のとおり指定し、CC BY-SA 4.0の下での提供と翻案物への継承条件を明記しています。再配布時にはこの表示とライセンス本文を保持してください。

> 科学技術用語形態素解析辞書 © バイオサイエンスデータベースセンター licensed under CC表示-継承4.0 国際

元READMEスナップショットと詳細は `source/jst-thesaurus/NBDC-README.html`、原アーカイブの版・ダウンロード説明は [NBDCデータベース説明](https://dbarchive.biosciencedbc.jp/en/mecab/desc.html) を参照してください。辞書行にはソースタグやMeCabの接続ID・costを含めず、IROHA独自POS ID・costを用いています。

## NINJAL現代雑誌語彙表の帰属

国立国語研究所の[公式配布ページ](https://mmsrv.ninjal.ac.jp/mag200/)は公開版ver.1.0（2006-08-11）をCC BY 4.0で提供すると明記し、同梱の `licenses/LICENSE-NINJAL-MAG200.txt` にも原著作権・使用条件を保持しています。変更は、掲載語彙表からの選定、観測表記が2回以上ある候補への限定、読み・表記の保守的選択、IROHA独自POS ID・costの付与です。読みは原資料でも近似値とされるため、精度に関する注意をREADMEおよび `NINJAL-MAGAZINES-ATTRIBUTION.tsv` に残しています。NINJALの推奨・承認を示しません。


IPADICの上流COPYING本文のSHA-256は `fca02d9adb601d101eccdf3131119abfff2d9c825ef5c759d7a89ebbaa972099` です。NAISTの許諾・免責とICOT由来の追加免責を一体で保持します。
