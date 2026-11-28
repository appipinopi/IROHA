# 辞書データのライセンス

この配布物は、ソースごとのライセンス・再利用条件を保持し、全データに単一のライセンスを一律適用しません。JMdict/JMnedict由来部分、選定Wiktionary由来部分、JSTシソーラス由来部分はCC BY-SA 4.0、国立国語研究所の3データ部分はCC BY 4.0、日本語WordNet・NAIST-JDIC・IPADIC由来部分はそれぞれの個別条件で配布します。IPADIC由来部分にはNAISTの許諾・免責およびICOT由来の追加条件が適用されます。日本郵便の郵便番号データとNDLの典拠データには別個のSPDXライセンス名を付与せず、各提供元の公式再利用条件・表示条件を別々に保持します。

- CC BY-SA 4.0 概要: https://creativecommons.org/licenses/by-sa/4.0/
- CC BY-SA 4.0 法的条文: https://creativecommons.org/licenses/by-sa/4.0/legalcode
- EDRDGライセンス説明: https://www.edrdg.org/edrdg/licence.html

コンポーネントごとの原データ・ライセンス・帰属ファイルの一覧は [`LICENSE-INDEX.md`](LICENSE-INDEX.md) を参照してください。公式全文は `licenses/CC-BY-SA-4.0-LEGALCODE.txt`、`licenses/LICENSE-CC-BY-4.0.txt`、`licenses/CC0-1.0-LEGALCODE.txt`、`licenses/GFDL-1.3.txt` に同梱しています。JSTに必要な原典クレジットは `licenses/LICENSE-JST-THESAURUS.txt` にも記載しています。

この配布物には別途、日本語WordNet v2.1由来の表記・読み・品詞データも含みます。WordNet部分は `licenses/LICENSE-WORDNET.txt` の許諾・著作権表示・免責条件を保持しています。日本語WordNetのライセンスは商用を含む任意目的の利用・複製・改変・再配布を認める許諾です。
WordNet由来の各追加行と元XML内のLexicalEntry ID・表記・品詞・読み・生成種別は `WORDNET-ATTRIBUTION.tsv` に対応づけています。辞書TSV自体に出典タグは追加していません。

## 出典表示

> This IROHA dictionary contains adapted data from JMdict and JMnedict, copyright the Electronic Dictionary Research and Development Group (EDRDG), and is licensed under CC BY-SA 4.0. It also incorporates Japanese WordNet v2.1 lemma, reading and part-of-speech data, with its separate license notice preserved in the distribution. IROHA adds generated inflectional and auxiliary-combination forms and IROHA-local categories and costs. EDRDG does not endorse this project.

日本語表示:

> 本IROHA辞書は、Electronic Dictionary Research and Development Group（EDRDG）著作権のJMdictおよびJMnedictを加工したデータを含み、CC BY-SA 4.0で公開します。また、日本語WordNet v2.1の表記・読み・品詞データを含み、そのライセンス表示は配布物に保持しています。IROHA版では規則に基づく活用形・補助動詞結合形の生成とIROHA独自の品詞ID・コスト付与を行っています。EDRDGによる推奨・承認を示すものではありません。

JMdict/JMnedictの出典とライセンス条件は `NOTICE.txt` を、日本語WordNetの著作権表示・免責は `licenses/LICENSE-WORDNET.txt` を参照してください。再配布時は各ライセンス文書と出典表示を保持してください。この説明は法的助言ではなく、各ライセンス本文に代わるものではありません。


## Wiktionary由来データ

この配布物には、英語版Wiktionaryの日本語エントリーから選んだ名詞に加え、動詞・形容詞・名前等の表記・読み・品詞を含みます。収録行数は 98,976 行です。元ページの編集者への帰属は、各表記の出典URLを列挙した `WIKTIONARY-ATTRIBUTION.tsv` に記録しています。利用したのは表記・明示されたかな転写・品詞のみで、語義・例文は辞書行へ複製していません。

Wiktionaryの本文はCC BY-SA 4.0とGFDLの条件で提供されており、この配布物では選定した項目をCC BY-SA 4.0の条件に従って扱います。元データのスナップショット `source/ja-extract.jsonl.gz` と出典ページ情報を同梱しています。Wiktionaryの著作権・帰属説明: https://en.wiktionary.org/wiki/Wiktionary:Copyrights。抽出元: https://kaikki.org/dictionary/rawdata.html。日本語データの説明: https://kaikki.org/dictionary/Japanese/index.html。全項目の人手校正は行っていません。


## Wiktionaryの広い品詞・語形サブセット

この拡張では、同梱Kaikkiスナップショットの日本語エントリーから、品詞が明確で、語義があり、明示されたかな読みが少なくとも一つある語を選びました。読みが複数明示されている項目は、その各読みを個別候補として残しています。収録行は 73,217 行です。語義や例文は辞書行に複製していません。項目別の出典ページURLは `WIKTIONARY-ATTRIBUTION-EXPANDED.tsv` に記録しています。

「する」動詞の活用と一補助動詞までの結合はIROHAのローカル規則で生成しました。形容詞・形容動詞の派生形は、Wiktionaryの該当項目に活用形として記載されたものだけを追加し、読み側は明示された読みから規則的な語尾対応で作っています。全語の人手校正は行っていません。英語版Wiktionaryの本文・データのライセンス条件を維持し、選定データはCC BY-SA 4.0で配布します。詳細: [Wiktionary著作権説明](https://en.wiktionary.org/wiki/Wiktionary:Copyrights)、[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)、[Kaikki raw data](https://kaikki.org/dictionary/rawdata.html)。


## NAIST-JDIC由来データ

この配布物にはNAIST-JDIC 0.6.3.b-20111013由来の表記・読み・品詞およびIROHA側で生成した語形が 635,960 行含まれます。動詞・形容詞の非基本形語幹は単独候補として採用せず、規則が明確な現代活用型から語形を生成しました。NAIST-JDICの著作権表示とBSD-3-Clause全文を `licenses/LICENSE-NAIST-JDIC.txt` に保持しています。ソースアーカイブ `source/naist-jdic_0.6.3.b-20111013.orig.tar.gz` とDebian公式著作権記録（https://metadata.ftp-master.debian.org/changelogs//main/m/mecab-naist-jdic/mecab-naist-jdic_0.6.3.b-20111013-11_copyright）を参照してください。BSD条件はソース/バイナリ配布および改変を許可し、著作権表示・条項・免責の保持、NAIST等を製品の推奨に使わないことを求めます。

取り込んだのはNAIST-JDIC CSVの表層形・明示かな読み・選定品詞/基本形活用型のみです。動詞・形容詞の非基本形語幹を単独候補として登録せず、原辞書の接続ID・cost・発音も移植していません。同じアーカイブに含まれるUniDic由来データも使っていません。行別ソース行番号は `NAIST-ATTRIBUTION.tsv` にあります。ライセンス本文を優先してください。これは法的助言ではありません。


## Wikidata日本語Lexeme由来データ

Wikidata Lexeme namespace の日本語語彙から、明示された `ja` 表記と `ja-hira` 読み、および確認済みの品詞カテゴリだけを取り込みました。未然形・連用形・仮定形・促音便などの非単独語幹は除外し、無タグの語形は活用品詞で見出し語と読みが一致する場合だけ許可、文法タグ付きは確認済みの終止形・連体形・命令形だけを許可しています。今回新たに追加した行は 3,287 行です。Wikidataの構造化データはCC0 1.0で提供されています。辞書行ごとのWikidata Lexeme IDは `WIKIDATA-ATTRIBUTION.tsv` に保持し、再現用の日本語Lexemeスナップショットと公式データダンプの識別情報を同梱します。

- 出典: https://dumps.wikimedia.org/wikidatawiki/entities/latest-lexemes.json.gz
- Lexemeデータ説明: https://www.wikidata.org/wiki/Wikidata:Lexicographical_data
- CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/

Wikidata由来行はCC0の条件に従って再利用できます。CC BY-SA 4.0で公開する統合辞書全体には、既存JMdict/JMnedict由来データの条件が別途適用されます。


## Wiktionaryの追加POS選定

従来の名詞サブセットに加え、単一の明示読み・語義・品詞対応が確認できる動詞、形容詞、名前等を追加しました。動詞の表記は明示されたcanonical形を使用し、サ変動詞以外の活用読みは推測していません。各追加行の元ページURLはWIKTIONARY-ATTRIBUTION.tsvに記録しています。ライセンスと帰属の説明は[https://en.wiktionary.org/wiki/Wiktionary:Copyrights](https://en.wiktionary.org/wiki/Wiktionary:Copyrights)および[https://creativecommons.org/licenses/by-sa/4.0/](https://creativecommons.org/licenses/by-sa/4.0/)を参照してください。


## 国立国語研究所 教育基本語彙DB 2009B由来データ

この配布物には、National Institute for Japanese Language and Linguistics（NINJAL）公開の *Database of Basic Vocabulary in Education (Version 2009B)* を選定・加工した辞書行が 6,429 行含まれます。出典は[公式配布ページ](https://mmsrv.ninjal.ac.jp/brfvep/)、[CSV原本](https://mmsrv.ninjal.ac.jp/brfvep/kyoikukihongoi_2009B.csv)、[国立国語研究所報告127（2009年）](https://doi.org/10.15084/00001288)です。NINJAL公式ページは同DBを **Creative Commons Attribution 4.0 International（CC BY 4.0）** の下で提供すると明記しています。CC BY 4.0の法的条文は `licenses/LICENSE-CC-BY-4.0.txt` に保持しています。

この部分については、提供者・データベース名・版・出典・CC BY 4.0表示を保持し、変更を明示しています。具体的な変更は、明示かな見出しの正規化、注記付きまたは複数の表記欄を推測で分割せずかな表記へ置き換える選択、IROHA独自POS ID・コストの割当、明確な現代活用区分に限った活用形・サ変複合形の生成です。元CSVは `source/ninjal_kyoikukihongoi_2009B.csv`、変更後各行と元CSV行番号は `NINJAL-ATTRIBUTION.tsv` にあります。NINJALは本プロジェクトを推奨・承認していません。

NINJAL由来部分をCC BY-SA 4.0の条件で一律に再ライセンスしたとは主張しません。配布物はコンポーネント別のライセンス条件を保持しています。無料配布でもCC BY 4.0の帰属条件は適用されます。これは法的助言ではなく、ライセンス本文を優先してください。


## 国立国語研究所 日本語教育基本語彙データベース由来

この配布物には、NINJALが公開する *Database of Basic Vocabulary in Japanese Language Education*（報告書127付属、6種対照CSV）から選定・加工した辞書行が 1,283 行含まれます。出典: [公式ページ](https://mmsrv.ninjal.ac.jp/brfvep/)、[CSV原本](https://mmsrv.ninjal.ac.jp/brfvep/rokusyutaisyo.csv)、[報告書127](https://doi.org/10.15084/00001288)。NINJAL公式ページはこのデータベースをCreative Commons Attribution 4.0 International（CC BY 4.0）の下で提供すると明記しています。ライセンス条文は `licenses/LICENSE-CC-BY-4.0.txt` に同梱しています。

提供者・データベース名・報告書・CC BY 4.0表示を保持し、変更を明示します。利用したのは見出し・表記・品詞のみです。出典別マーク、語種、語彙配当、分類番号や原コストは候補選定・辞書行に使っていません。読みの正規化、保守的な表記選択、IROHA独自のPOS ID・コスト付与、明確な現代活用・サ変形の生成を行いました。元CSVは `source/ninjal_rokushutaisho_2009.csv`、各追加行と元CSV行番号は `NINJAL-JP-EDU-ATTRIBUTION.tsv` にあります。NINJALは本プロジェクトを推奨・承認していません。この構成要素をCC BY-SA 4.0へ一律に再ライセンスしたとは主張しません。

## JSTシソーラス2015年版由来データ

この配布物には、NBDCが公開した「科学技術用語形態素解析辞書」から選定・加工した表記・読み・品詞データとIROHA規則で生成したサ変語形が204,641行含まれます。公式READMEはJSTシソーラス2015年版の見出し語・同義語を元にしたMeCab用データと説明し、CC BY-SA 4.0を明記します。原アーカイブは `source/jst-thesaurus/mecab_thesaurus.zip`、出典説明スナップショットは `source/jst-thesaurus/NBDC-README.html` です。

配布時に保持する必須クレジット: “科学技術用語形態素解析辞書 © バイオサイエンスデータベースセンター licensed under CC表示-継承4.0 国際”。同じ表示と原典条件を `licenses/LICENSE-JST-THESAURUS.txt` に記載し、CC BY-SA 4.0法的条文は `licenses/CC-BY-SA-4.0-LEGALCODE.txt` に保持しています。利用したのは選定表記・明示読み・選定POSなどです。原接続ID・原cost・出典タグは辞書行へ移さず、出典情報は `JST-ATTRIBUTION.tsv` に分離しています。JST/NBDCは本プロジェクトを推奨・承認していません。

NBDCの上流READMEは、同辞書項目がIPA辞書に基づくとも説明しています。この由来を記録し再配布時に参照できるよう、IPADICの上流 `COPYING` 全文を `licenses/LICENSE-IPADIC.txt` に保持しています。NBDCのCC BY-SA 4.0表示・条件は `licenses/LICENSE-JST-THESAURUS.txt` に、IPADIC由来の直接選定分とその許諾文書は `LICENSE-INDEX.md` の別項目に記載しています。

## NINJAL「現代雑誌200万字言語調査」由来データ

この配布物には、国立国語研究所（NINJAL）の公開版ver.1.0（2006-08-11）から選定した表記・近似読み・品詞データ2,124行が含まれます。公式配布ページとZIP内の「著作権及び使用条件（2023年12月28日）」はデータ著作権をNINJALに帰属させ、CC BY 4.0で提供すると明記しています。元データは1994年発行月刊誌70誌の調査成果で、アーカイブは `source/ninjal-magazines/Zasshi200.zip`、抽出CSVは `source/ninjal-magazines/goihyo_50_ver.1.0.csv` です。

選定表記は元の実表記一覧に完全一致し2回以上観測されるものに限り、観測一覧・頻度・雑誌数・元行番号を `NINJAL-MAGAZINES-ATTRIBUTION.tsv` に保存しています。NINJALが読みを近似とするため、読みの誤りが残る可能性があり、全件の人手校正もしていません。変更は候補選定、読み・表記の保守的な選択、IROHA独自POS ID・costの付与です。活用形は生成していません。CC BY 4.0部分をCC BY-SA 4.0へ一律に再ライセンスしたとは主張せず、NINJALによる推奨・承認も示しません。


## IPADIC由来データ

この配布物には、MeCab公式配布元のIPA辞書 IPADIC 2.7.0-20070801 から選定・加工した表記、読み、品詞、規則的な語形が 10,743 行含まれます。原アーカイブ `source/mecab-ipadic-2.7.0-20070801.tar.gz` のSHA-256は `b62f527d881c504576baed9c6ef6561554658b175ce6ae0096a60307e49e3523` です。CSV 26ファイル、計 392,126 レコードを読みました。行別の出典ファイル・行番号は `IPADIC-ATTRIBUTION.tsv` に記録しています。

IPADICの全体条件はNAISTの著作権許諾とICOT Free Software由来の追加条件を含み、Debianのcopyright記録では `BSD-3-Clause-with-ICOT-term` とされています。原本の `COPYING`（3,795 bytes、SHA-256 `fca02d9adb601d101eccdf3131119abfff2d9c825ef5c759d7a89ebbaa972099`）全文を `licenses/LICENSE-IPADIC.txt` として保持し、アーカイブ内にも原版を同梱しています。必須のNAIST著作権表示、免責、ICOT `NO WARRANTY` 全文を削除せず保持してください。配布上の表示・出典・条件は [`LICENSE-INDEX.md`](LICENSE-INDEX.md) と `NOTICE.txt` を参照してください。

利用したのはCSVの表層形、明示かな読み、選定POS、活用型・形・原形のみです。既存辞書に同じ表記で別読みしかない原行、固有名詞品詞、ラテン文字表記を除外しました。さらに派生語形を含む候補も既存辞書の同表記・別読みに衝突する場合は除外し、五段・サ行の短縮使役受身形は文法資料に従って生成しません。異読フィルターは正当な別読みも除外し得ます。IPADIC接続ID、原コスト、発音、MeCabランタイムは使用していません。辞書行には出典タグを入れず、IROHA独自のPOS ID・コストを割り当てています。UniDic・Mozc由来データは使用していません。

## 日本郵便「住所の郵便番号」データ

日本郵便の[公式説明・利用条件](https://www.post.japanpost.jp/service/search/zipcode/download/utf-readme.html)は「郵便番号データに限っては日本郵便株式会社は著作権を主張しません。自由に配布していただいて結構です。」と記載しています。本配布物ではこの文言を郵便番号データに限る再配布条件として保持し、CC0等の別ライセンスを付与したとは主張しません。出典表示・原データは `licenses/NOTICE-JAPAN-POST.txt`、`source/japanpost/README.md`、`source/japanpost/utf_ken_all.zip` にあります。行別の対応は `JAPAN-POST-ATTRIBUTION.tsv` です。この条件は他のソースには適用しません。

## Web NDL Authorities（NDLSH・NDLGFT）

NDLの[公式Terms of Use](https://id.ndl.go.jp/information/use_en/)はWeb NDL Authoritiesの再利用を営利・非営利のいずれにも事前申請なしで認め、公開時にNDLから取得したデータであることを表示するよう求めます。NDLデータに個人情報が含まれ得る旨の公式注意も保持しています。本配布では、公式説明にある主題標目・ジャンル/形式用語の対象範囲を用い、個人名・企業名を対象とする別の典拠ファイルは取得・追加していません。

この条件には別個のSPDXライセンス名を付与しません。必須表示は `NOTICE-NDL.txt`、原データと利用条件の保存版は `source/ndl/`、NDL IDと元見出し・読み・出典欄・行位置は `NDL-ATTRIBUTION.tsv` にあります。各出典の条件と帰属資料の対応は [`LICENSE-INDEX.md`](LICENSE-INDEX.md) を参照してください。
