#!/usr/bin/env python3
"""Build a five-column Japanese full-form IME lexicon from JMdict and JMnedict.

This builder does not read or import UniDic, Mozc, or their connection IDs/costs.
Output TSV columns are: reading, left_id, right_id, cost, surface.
The IDs are IROHA-local POS class IDs; they are not Mozc-compatible IDs.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import sqlite3
import sys
import unicodedata
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

TARGET_ROWS = 6_000_000
SHARD_ROWS = 1_000_000
BATCH_ROWS = 5_000
AUXILIARIES = [
    ("いる", "いる", "ichidan"),
    ("おく", "おく", "godan_ku"),
    ("しまう", "しまう", "godan_u"),
    ("みる", "みる", "ichidan"),
    ("いく", "いく", "iku"),
    ("くる", "くる", "kuru"),
    ("ある", "ある", "aru"),
    ("くれる", "くれる", "ichidan"),
    ("もらう", "もらう", "godan_u"),
    ("あげる", "あげる", "ichidan"),
    ("くださる", "くださる", "godan_ru_aru"),
    ("いただく", "いただく", "godan_ku"),
]
# IROHA-local category IDs; left_id and right_id both identify the row's class.
# These IDs are intentionally independent of any third-party IME dictionary.
POS_IDS = {
    "noun": 1, "verbal_noun": 2, "pronoun": 3, "adjective_i": 4,
    "adjective_na": 5, "adverb": 6, "adverb_to": 7, "verb": 8,
    "aux_verb": 9, "particle": 10, "conjunction": 11,
    "interjection": 12, "prefix": 13, "suffix": 14, "counter": 15,
    "expression": 16, "other": 17, "proper_noun": 18,
}
ID_LABELS = {v: k for k, v in POS_IDS.items()}

# For godan verbs, each ending gives its a/i/e/o-row and te/ta allomorphs.
GODAN = {
    "う": ("わ", "い", "え", "お", "って", "った"),
    "く": ("か", "き", "け", "こ", "いて", "いた"),
    "ぐ": ("が", "ぎ", "げ", "ご", "いで", "いだ"),
    "す": ("さ", "し", "せ", "そ", "して", "した"),
    "つ": ("た", "ち", "て", "と", "って", "った"),
    "ぬ": ("な", "に", "ね", "の", "んで", "んだ"),
    "ぶ": ("ば", "び", "べ", "ぼ", "んで", "んだ"),
    "む": ("ま", "み", "め", "も", "んで", "んだ"),
    "る": ("ら", "り", "れ", "ろ", "って", "った"),
}
KATA_ENDINGS = {"う":"ウ", "く":"ク", "ぐ":"グ", "す":"ス", "つ":"ツ", "ぬ":"ヌ", "ぶ":"ブ", "む":"ム", "る":"ル"}
AUX_FORM_NAMES = {
    "plain": 0, "past": 1, "negative": 2, "negative_past": 3,
    "te": 4, "polite": 5, "polite_past": 6, "polite_negative": 7,
    "polite_negative_past": 8, "conditional": 9, "tara": 10,
    "volitional": 11, "potential": 12, "imperative": 13,
    "negative_te": 14, "desiderative": 15,
    "polite_special": 5, "polite_past_special": 6,
    "polite_negative_special": 7, "polite_negative_past_special": 8,
    "imperative_special": 13,
}


def to_hiragana(text: str) -> str:
    out=[]
    for c in unicodedata.normalize("NFKC", text.strip()):
        cp=ord(c)
        if 0x30A1 <= cp <= 0x30F6:
            out.append(chr(cp-0x60))
        elif c == "ヷ": out.append("わ\u3099")
        elif c == "ヸ": out.append("ゐ\u3099")
        elif c == "ヹ": out.append("ゑ\u3099")
        elif c == "ヺ": out.append("を\u3099")
        else: out.append(c)
    return unicodedata.normalize("NFC", "".join(out))


def clean_surface(s: str) -> str | None:
    s=unicodedata.normalize("NFC", s.strip())
    if not s or any(ch.isspace() or unicodedata.category(ch) in {"Cc", "Cf", "Cs"} for ch in s):
        return None
    # Avoid punctuation-only terms; retain normal Japanese word-internal marks.
    if not any(unicodedata.category(ch)[0] in "LNM" for ch in s):
        return None
    if any(unicodedata.category(ch)[0] == "P" and ch not in "・＝-‐‑–—ー々〆ヶゝゞヽヾ" for ch in s):
        return None
    return s


def clean_reading(s: str) -> str | None:
    s=to_hiragana(s)
    if not s or any(ch.isspace() or unicodedata.category(ch) in {"Cc", "Cf", "Cs"} for ch in s):
        return None
    if not any("\u3041" <= ch <= "\u3096" for ch in s):
        return None
    if any(unicodedata.category(ch)[0] == "P" and ch not in "・ーゝゞヽヾ" for ch in s):
        return None
    return s


def source_priority(tags: set[str], infos: set[str]) -> int:
    """Coarse ordering only; JMdict priority tags, never imported costs."""
    tags={t.lower() for t in tags}
    if any(t in tags for t in ("news1", "ichi1", "spec1", "gai1")): rank=0
    elif any(t in tags for t in ("news2", "ichi2", "spec2", "gai2")): rank=1
    else:
        nfs=[]
        for t in tags:
            m=re.fullmatch(r"nf(\d{2})",t)
            if m: nfs.append(int(m.group(1)))
        if nfs:
            n=min(nfs)
            rank=1 if n<=12 else 2 if n<=24 else 3 if n<=36 else 4
        else: rank=5
    if any("rarely used kanji" in x.lower() for x in infos): rank=min(7,rank+1)
    return rank


def verb_type_from_pos(pos: set[str], surface: str, reading: str) -> str | None:
    joined=" | ".join(sorted(pos))
    low=joined.lower()
    if "ichidan verb - zuru" in low: return "zuru"
    if "ichidan verb" in low: return "ichidan"
    if "kuru verb" in low: return "kuru"
    if "godan verb - iku/yuku" in low: return "iku"
    if "godan verb - -aru special class" in low: return "godan_ru_aru"
    if "godan verb with 'ru' ending (irregular verb)" in low:
        return "aru" if reading.endswith("ある") else "godan_ru"
    if "godan verb with 'u' ending" in low:
        if "special class" in low: return "godan_u_special"
        return "godan_u"
    for kana,kind in (("ku","godan_ku"),("gu","godan_gu"),("su","godan_su"),("tsu","godan_tsu"),("nu","godan_nu"),("bu","godan_bu"),("mu","godan_mu"),("ru","godan_ru")):
        if f"godan verb with '{kana}' ending" in low: return kind
    if "suru verb" in low: return "suru"
    if "verb unspecified" in low: return None
    if "auxiliary verb" in low:
        if reading.endswith("する"): return "suru"
        if reading.endswith("くる"): return "kuru"
        if reading and reading[-1] in GODAN: return "godan_"+{"う":"u","く":"ku","ぐ":"gu","す":"su","つ":"tsu","ぬ":"nu","ぶ":"bu","む":"mu","る":"ru"}[reading[-1]]
        if reading.endswith("る"): return "ichidan"
    return None


def is_suru_noun(pos: set[str]) -> bool:
    return "noun or participle which takes the aux. verb suru" in pos


def classes_for_pos(pos: set[str]) -> set[int]:
    out=set()
    joined=" | ".join(pos).lower()
    if any("adjective (keiyoushi)" in p for p in pos): out.add(POS_IDS["adjective_i"])
    if any("adjectival nouns" in p or "'taru' adjective" in p for p in pos): out.add(POS_IDS["adjective_na"])
    if any("adverb taking the 'to' particle" in p for p in pos): out.add(POS_IDS["adverb_to"])
    elif any("adverb" in p for p in pos): out.add(POS_IDS["adverb"])
    if any("pronoun" in p for p in pos): out.add(POS_IDS["pronoun"])
    if any("particle" in p for p in pos): out.add(POS_IDS["particle"])
    if any("conjunction" in p for p in pos): out.add(POS_IDS["conjunction"])
    if any("interjection" in p for p in pos): out.add(POS_IDS["interjection"])
    if any("prefix" in p for p in pos): out.add(POS_IDS["prefix"])
    if any("suffix" in p for p in pos): out.add(POS_IDS["suffix"])
    if any("counter" in p for p in pos): out.add(POS_IDS["counter"])
    if any("expression" in p for p in pos): out.add(POS_IDS["expression"])
    if is_suru_noun(pos): out.add(POS_IDS["verbal_noun"])
    if any("noun" in p for p in pos) and not is_suru_noun(pos): out.add(POS_IDS["noun"])
    if any("verb" in p for p in pos): out.add(POS_IDS["verb"])
    if "auxiliary verb" in pos: out.add(POS_IDS["aux_verb"])
    return out or {POS_IDS["other"]}


def endings_for_class(kind: str) -> tuple[str, str] | None:
    roman_to_kana={"u":"う","ku":"く","gu":"ぐ","su":"す","tsu":"つ","nu":"ぬ","bu":"ぶ","mu":"む","ru":"る"}
    m=re.fullmatch(r"godan_(u|ku|gu|su|tsu|nu|bu|mu|ru)(?:_special)?",kind)
    if m: return ("godan",roman_to_kana[m.group(1)])
    if kind=="godan_ru_aru": return ("godan","ru_ある")
    if kind=="iku": return ("godan","く")
    return None


def conjugations(surface: str, reading: str, kind: str) -> list[tuple[str,str,str,int]]:
    """Return full forms (surface, reading, form-name, form-priority)."""
    out=[]
    def put(ss,rr,name,rank):
        ss=clean_surface(ss); rr=clean_reading(rr)
        if ss and rr: out.append((ss,rr,name,rank))
    # Zuru verbs are irregular in the written stem (e.g. 演ずる -> 演じない).
    # Keep their source headwords, but do not emit guessed forms here.
    if kind=="zuru": return out
    # Each pair below uses an independently specified surface suffix and reading suffix.
    if kind in {"ichidan","zuru"}:
        ending="る" if kind=="ichidan" else "る"
        if not surface.endswith(ending) or not reading.endswith(ending): return out
        sroot=surface[:-1]; rroot=reading[:-1]
        forms=[
            ("ない","ない","negative",2),("なかった","なかった","negative_past",3),
            ("なくて","なくて","negative_te",14),("ないで","ないで","negative_de",15),
            ("ます","ます","polite",5),("ました","ました","polite_past",6),
            ("ません","ません","polite_negative",7),("ませんでした","ませんでした","polite_negative_past",8),
            ("て","て","te",4),("た","た","past",1),
            ("れば","れば","conditional",9),("たら","たら","tara",10),
            ("よう","よう","volitional",11),("ろ","ろ","imperative",13),
            ("よ","よ","imperative_alt",13),("られる","られる","potential",12),
            ("られない","られない","potential_negative",16),("られた","られた","potential_past",17),
            ("られます","られます","potential_polite",18),("られれば","られれば","potential_conditional",19),
            ("られる","られる","passive",20),("させる","させる","causative",21),
            ("させられる","させられる","causative_passive",22),("させられない","させられない","causative_passive_negative",23),
            ("たい","たい","desiderative",24),("たくない","たくない","desiderative_negative",25),
            ("たかった","たかった","desiderative_past",26),("たくなかった","たくなかった","desiderative_negative_past",27),
        ]
        for a,b,n,r in forms: put(sroot+a,rroot+b,n,r)
        if kind=="zuru":
            # Zuru verbs follow the ichidan surface pattern, but their standard te/past forms are じて/じた.
            # The generic ichidan forms are retained where valid; source entries are typically archaic/rare.
            pass
    elif kind=="suru":
        if not surface.endswith("する") or not reading.endswith("する"): return out
        sr=surface[:-2]; rr=reading[:-2]
        forms=[
            ("しない","しない","negative",2),("しなかった","しなかった","negative_past",3),
            ("しなくて","しなくて","negative_te",14),("しないで","しないで","negative_de",15),
            ("します","します","polite",5),("しました","しました","polite_past",6),
            ("しません","しません","polite_negative",7),("しませんでした","しませんでした","polite_negative_past",8),
            ("して","して","te",4),("した","した","past",1),
            ("すれば","すれば","conditional",9),("したら","したら","tara",10),
            ("しよう","しよう","volitional",11),("しろ","しろ","imperative",13),
            ("せよ","せよ","imperative_alt",13),("できる","できる","potential",12),
            ("できない","できない","potential_negative",16),("できた","できた","potential_past",17),
            ("される","される","passive",20),("されない","されない","passive_negative",21),
            ("させる","させる","causative",22),("させられる","させられる","causative_passive",23),
            ("させられない","させられない","causative_passive_negative",24),
            ("したい","したい","desiderative",25),("したくない","したくない","desiderative_negative",26),
            ("したかった","したかった","desiderative_past",27),
        ]
        for a,b,n,r in forms: put(sr+a,rr+b,n,r)
    elif kind=="kuru":
        if not reading.endswith("くる"): return out
        rroot=reading[:-2]; sroot=surface[:-2] if surface.endswith("くる") else (surface[:-1] if surface.endswith("る") else None)
        if sroot is None: return out
        kana_surface=surface.endswith("くる")
        forms=[
            ("ない","こない","negative",2),("なかった","こなかった","negative_past",3),
            ("なくて","こなくて","negative_te",14),("ないで","こないで","negative_de",15),
            ("ます","きます","polite",5),("ました","きました","polite_past",6),
            ("ません","きません","polite_negative",7),("ませんでした","きませんでした","polite_negative_past",8),
            ("て","きて","te",4),("た","きた","past",1),
            ("れば","くれば","conditional",9),("たら","きたら","tara",10),
            ("よう","こよう","volitional",11),("い","こい","imperative",13),
            ("られる","こられる","potential",12),("られない","こられない","potential_negative",16),
            ("られた","こられた","potential_past",17),("られます","こられます","potential_polite",18),
            ("られる","こられる","passive",20),("させる","こさせる","causative",21),
            ("させられる","こさせられる","causative_passive",22),("させられない","こさせられない","causative_passive_negative",23),
            ("たい","きたい","desiderative",24),("たくない","きたくない","desiderative_negative",25),
            ("たかった","きたかった","desiderative_past",26),
        ]
        for ss,rr,n,r in forms:
            put(sroot+(rr if kana_surface else ss),rroot+rr,n,r)
    elif kind=="aru":
        if not surface.endswith("ある") or not reading.endswith("ある"): return out
        prefix_s=surface[:-2]; prefix_r=reading[:-2]
        aroot_s=surface[:-1]; aroot_r=reading[:-1]
        forms=[
            (prefix_s+"ない",prefix_r+"ない","negative",2),(prefix_s+"なかった",prefix_r+"なかった","negative_past",3),
            (prefix_s+"なくて",prefix_r+"なくて","negative_te",14),(prefix_s+"ないで",prefix_r+"ないで","negative_de",15),
            (prefix_s+"あります",prefix_r+"あります","polite",5),(prefix_s+"ありました",prefix_r+"ありました","polite_past",6),
            (prefix_s+"ありません",prefix_r+"ありません","polite_negative",7),(prefix_s+"ありませんでした",prefix_r+"ありませんでした","polite_negative_past",8),
            (aroot_s+"って",aroot_r+"って","te",4),(aroot_s+"った",aroot_r+"った","past",1),
            (prefix_s+"あれば",prefix_r+"あれば","conditional",9),(prefix_s+"あったら",prefix_r+"あったら","tara",10),
            (prefix_s+"あろう",prefix_r+"あろう","volitional",11),(prefix_s+"あれ",prefix_r+"あれ","imperative",13),
        ]
        for ss,rr,n,r in forms: put(ss,rr,n,r)
    else:
        ec=endings_for_class(kind)
        if not ec: return out
        _,ending=ec
        # Adapt only spellings whose final kana corresponds to the dictionary reading.
        if ending=="ru_ある": ending="る"
        e=ending[-1] if ending in GODAN else None
        if not e or not reading.endswith(e): return out
        se=KATA_ENDINGS[e]
        if surface.endswith(e): sroot=surface[:-1]; surf_end=e
        elif surface.endswith(se): sroot=surface[:-1]; surf_end=se
        else: return out
        rroot=reading[:-1]
        a,i,e_row,o,te,ta=GODAN[e]
        if kind=="iku": te,ta="って","った"
        if surf_end==se:
            conv=lambda kana: chr(ord(kana)+0x60) if "ぁ" <= kana <= "ゖ" else kana
            a,i,e_row,o,te,ta=("ア" if x=="あ" else "イ" if x=="い" else "エ" if x=="え" else "オ" if x=="お" else x.translate(str.maketrans("かきくけこがぎぐげごさしすせそたちつてとならにぬねのばびぶべぼまみむめもらりるれろ", "カキクケコガギグゲゴサシスセソタチツテトナラニヌネノバビブベボマミムメモラリルレロ")) for x in (a,i,e_row,o,te,ta))
        endings=[
            (a+"ない",a+"ない","negative",2),(a+"なかった",a+"なかった","negative_past",3),
            (a+"なくて",a+"なくて","negative_te",14),(a+"ないで",a+"ないで","negative_de",15),
            (i+"ます",i+"ます","polite",5),(i+"ました",i+"ました","polite_past",6),
            (i+"ません",i+"ません","polite_negative",7),(i+"ませんでした",i+"ませんでした","polite_negative_past",8),
            (te,te,"te",4),(ta,ta,"past",1),(e_row+"ば",e_row+"ば","conditional",9),
            (ta+"ら",ta+"ら","tara",10),(o+"う",o+"う","volitional",11),(e_row,"え" if e=="う" and False else e_row,"imperative",13),
            (e_row+"る",e_row+"る","potential",12),(e_row+"ない",e_row+"ない","potential_negative",16),
            (e_row+"た",e_row+"た","potential_past",17),(a+"れる",a+"れる","passive",20),
            (a+"れない",a+"れない","passive_negative",21),(a+"せる",a+"せる","causative",22),
            (a+"せられる",a+"せられる","causative_passive",23),(a+"される",a+"される","causative_passive_short",24),
            (i+"たい",i+"たい","desiderative",25),(i+"たくない",i+"たくない","desiderative_negative",26),
            (i+"たかった",i+"たかった","desiderative_past",27),(i+"たくなかった",i+"たくなかった","desiderative_negative_past",28),
            (i+"がる",i+"がる","desiderative_garu",29),
        ]
        for ss,rr,n,r in endings:
            if kind=="godan_ru_aru" and n in {"polite","polite_past","polite_negative","polite_negative_past"}:
                continue
            if n=="imperative":
                # Godan imperative is the e-row (e.g. 書け), already represented by e_row.
                put(sroot+ss,rroot+rr,n,r)
            else: put(sroot+ss,rroot+rr,n,r)
        if kind=="godan_ru_aru":
            # Honorific -aru verbs use -います/ください, not the regular -ります.
            for ss,rr,name,rank in [
                ("います","います","polite_special",5),
                ("いました","いました","polite_past_special",6),
                ("いません","いません","polite_negative_special",7),
                ("いませんでした","いませんでした","polite_negative_past_special",8),
                ("い","い","imperative_special",13),
            ]:
                put(sroot+ss,rroot+rr,name,rank)
        if kind=="godan_u_special":
            # 問う/請う retain their established -います forms.
            put(sroot+"います",rroot+"います","polite_special",5)
        if kind=="iku":
            # Standard Iku/Yuku te and past forms are いって/いった.
            put(sroot+"って",rroot+"って","te_special",4)
            put(sroot+"った",rroot+"った","past_special",1)
    # Keep one best-ranked variant per surface/reading pair.
    best={}
    for ss,rr,name,rank in out:
        key=(ss,rr)
        if key not in best or rank<best[key][3]: best[key]=(ss,rr,name,rank)
    return list(best.values())


def base_te_form(surface: str, reading: str, kind: str) -> tuple[str,str] | None:
    for ss,rr,name,rank in conjugations(surface,reading,kind):
        if name in ("te","te_special"):
            return ss,rr
    return None


def get_entry_data(e):
    poss={x.text or "" for s in e.findall("sense") for x in s.findall("pos")}
    k_items=[]
    for k in e.findall("k_ele"):
        keb=clean_surface(k.findtext("keb") or "")
        if keb:
            k_items.append((keb,{x.text or "" for x in k.findall("ke_pri")},{x.text or "" for x in k.findall("ke_inf")}))
    r_items=[]
    for r in e.findall("r_ele"):
        reb=clean_reading(r.findtext("reb") or "")
        if reb:
            r_items.append((reb,{x.text or "" for x in r.findall("re_pri")},{x.text or "" for x in r.findall("re_inf")},{x.text or "" for x in r.findall("re_restr")},r.find("re_nokanji") is not None))
    pairs=[]
    if not k_items:
        for r,rtags,rinfo,restr,nokanji in r_items:
            pairs.append((r,r,source_priority(rtags,rinfo),rinfo))
    else:
        for r,rtags,rinfo,restr,nokanji in r_items:
            if nokanji:
                pairs.append((r,r,source_priority(rtags,rinfo),rinfo))
            for k,ktags,kinfo in k_items:
                if restr and k not in restr: continue
                pairs.append((k,r,source_priority(rtags|ktags,rinfo|kinfo),rinfo|kinfo))
    # A duplicate pair in one entry keeps the best source-priority rank.
    best={}
    for s,r,rank,info in pairs:
        key=(s,r)
        if key not in best or rank<best[key][2]: best[key]=(s,r,rank,info)
    return poss,list(best.values())


def cost_for(freq: int, tier: int, penalty: int=0) -> int:
    # Lower cost ranks candidates earlier; values are original IROHA heuristics, not imported.
    return min(32767, 1100 + freq*650 + tier*17 + penalty)


def rank_for(kind_order: int, freq: int, form_order: int) -> int:
    # Keep all canonical lexical pairs first; then regular inflections; then auxiliary compounds.
    return kind_order*10_000_000 + freq*10_000 + form_order


def init_db(db: Path):
    if db.exists(): db.unlink()
    con=sqlite3.connect(db)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=NORMAL")
    con.execute("PRAGMA temp_store=FILE")
    con.execute("PRAGMA cache_size=-200000")
    con.execute("""CREATE TABLE candidates(
        reading TEXT NOT NULL, surface TEXT NOT NULL,
        left_id INTEGER NOT NULL, right_id INTEGER NOT NULL,
        cost INTEGER NOT NULL, rank INTEGER NOT NULL, kind TEXT NOT NULL,
        PRIMARY KEY(reading,surface,left_id,right_id)
    ) WITHOUT ROWID""")
    con.execute("CREATE INDEX idx_candidate_order ON candidates(rank,cost,reading,surface,left_id,right_id)")
    return con


def insert_batch(con, batch):
    if not batch: return
    con.executemany("""INSERT INTO candidates(reading,surface,left_id,right_id,cost,rank,kind)
        VALUES(?,?,?,?,?,?,?) ON CONFLICT(reading,surface,left_id,right_id) DO UPDATE SET
        cost=MIN(candidates.cost,excluded.cost), rank=MIN(candidates.rank,excluded.rank),
        kind=CASE WHEN excluded.rank<candidates.rank THEN excluded.kind ELSE candidates.kind END""",batch)
    batch.clear()


def build_candidates(source: Path, con, stats: Counter, include_double: bool=False):
    batch=[]
    with gzip.open(source,"rb") as src:
        for _,entry in ET.iterparse(src,events=("end",)):
            if entry.tag!="entry": continue
            pos,pairs=get_entry_data(entry)
            vt=verb_type_from_pos(pos,"",pairs[0][1] if pairs else "")
            classes=classes_for_pos(pos)
            for surface,reading,freq,infos in pairs:
                if not surface or not reading: continue
                # All source headwords, including already lexicalized compounds.
                for cls in classes:
                    cat_name=ID_LABELS.get(cls,"other")
                    batch.append((reading,surface,cls,cls,cost_for(freq,0),rank_for(0,freq,0),"lexical"))
                    stats["lexical_pairs"]+=1
                    if len(batch)>=BATCH_ROWS: insert_batch(con,batch)
                # Regular full forms from explicitly inflecting JMdict classes only.
                local_type=verb_type_from_pos(pos,surface,reading)
                if local_type:
                    forms=conjugations(surface,reading,local_type)
                    base_id=POS_IDS["verb"]
                    for ss,rr,name,form_rank in forms:
                        batch.append((rr,ss,base_id,base_id,cost_for(freq,2,30),rank_for(1,freq,form_rank),"inflection"))
                        stats["inflection_candidates"]+=1
                        if name in ("te","te_special"): te=(ss,rr)
                    te=base_te_form(surface,reading,local_type)
                    if te:
                        for ai,(aux_s,aux_r,aux_t) in enumerate(AUXILIARIES):
                            if aux_s=="ある" and not any("transitive verb" in p for p in pos):
                                continue
                            aux_forms=[(aux_s,aux_r,"plain",0)]+conjugations(aux_s,aux_r,aux_t)
                            for ass,arr,aname,arank in aux_forms:
                                # Include common conjugated auxiliary forms; avoid combining every rare imperative.
                                if aname not in AUX_FORM_NAMES: continue
                                form_order=100+ai*40+AUX_FORM_NAMES[aname]
                                batch.append((te[1]+arr,te[0]+ass,POS_IDS["aux_verb"],POS_IDS["aux_verb"],
                                              cost_for(freq,5,80+ai*5),rank_for(2,freq,form_order),"auxiliary_compound"))
                                stats["aux_compound_candidates"]+=1
                                if len(batch)>=BATCH_ROWS: insert_batch(con,batch)
                        # More elaborate but still rule-based multi-auxiliary compounds are a fallback tier.
                        if include_double:
                            for ai,(aux_s,aux_r,aux_t) in enumerate(AUXILIARIES):
                                ate=base_te_form(aux_s,aux_r,aux_t)
                                if not ate: continue
                                for bi,(aux2_s,aux2_r,aux2_t) in enumerate(AUXILIARIES):
                                    if bi not in (0,1,2,5,7,10,11): continue
                                    for ass,arr,aname,arank in conjugations(aux2_s,aux2_r,aux2_t):
                                        if aname not in ("plain","past","negative","polite","polite_past","polite_negative","te","conditional","tara"): continue
                                        form_order=1000+ai*100+bi*10+AUX_FORM_NAMES.get(aname,0)
                                        batch.append((te[1]+ate[1]+arr,te[0]+ate[0]+ass,
                                                      POS_IDS["aux_verb"],POS_IDS["aux_verb"],
                                                      cost_for(freq,9,160+ai*5+bi),rank_for(3,freq,form_order),"double_aux_compound"))
                                        stats["double_aux_candidates"]+=1
                                        if len(batch)>=BATCH_ROWS: insert_batch(con,batch)
                # Productive N+する compound verbs from the explicit JMdict verbal-noun label.
                if is_suru_noun(pos):
                    if not surface.endswith("する") and not reading.endswith("する"):
                        cs=surface+"する"; cr=reading+"する"
                    else:
                        cs,cr=surface,reading
                    cs=clean_surface(cs); cr=clean_reading(cr)
                    if cs and cr:
                        batch.append((cr,cs,POS_IDS["verb"],POS_IDS["verb"],cost_for(freq,2,40),rank_for(1,freq,0),"suru_compound"))
                        stats["suru_compound_candidates"]+=1
                        for ss,rr,name,form_rank in conjugations(cs,cr,"suru"):
                            batch.append((rr,ss,POS_IDS["verb"],POS_IDS["verb"],cost_for(freq,3,50),rank_for(1,freq,form_rank),"inflection"))
                            stats["inflection_candidates"]+=1
                        te=base_te_form(cs,cr,"suru")
                        if te:
                            for ai,(aux_s,aux_r,aux_t) in enumerate(AUXILIARIES):
                                if aux_s=="ある" and not any("transitive verb" in p for p in pos):
                                    continue
                                aux_forms=[(aux_s,aux_r,"plain",0)]+conjugations(aux_s,aux_r,aux_t)
                                for ass,arr,aname,arank in aux_forms:
                                    if aname not in AUX_FORM_NAMES: continue
                                    form_order=100+ai*40+AUX_FORM_NAMES[aname]
                                    batch.append((te[1]+arr,te[0]+ass,POS_IDS["aux_verb"],POS_IDS["aux_verb"],
                                                  cost_for(freq,6,90+ai*5),rank_for(2,freq,form_order),"auxiliary_compound"))
                                    stats["aux_compound_candidates"]+=1
                                    if len(batch)>=BATCH_ROWS: insert_batch(con,batch)
            entry.clear()
            stats["source_entries"]+=1
            if stats["source_entries"]%50000==0:
                insert_batch(con,batch); con.commit()
                print(f"parsed {stats['source_entries']:,} JMdict entries",flush=True)
    insert_batch(con,batch); con.commit()


def build_name_candidates(source: Path, con, stats: Counter):
    """Add JMnedict proper-name entries; no inflection or guessed readings."""
    batch=[]
    with gzip.open(source,"rb") as src:
        for _,entry in ET.iterparse(src,events=("end",)):
            if entry.tag!="entry": continue
            k_items=[]
            for k in entry.findall("k_ele"):
                keb=clean_surface(k.findtext("keb") or "")
                if keb: k_items.append((keb,{x.text or "" for x in k.findall("ke_inf")}))
            r_items=[]
            for r in entry.findall("r_ele"):
                reb=clean_reading(r.findtext("reb") or "")
                if reb:
                    r_items.append((reb,{x.text or "" for x in r.findall("re_restr")},r.find("re_nokanji") is not None))
            pairs=set()
            if not k_items:
                pairs.update((r,r) for r,restr,nokanji in r_items)
            else:
                for r,restr,nokanji in r_items:
                    if nokanji: pairs.add((r,r))
                    for k,infos in k_items:
                        if not restr or k in restr: pairs.add((k,r))
            for surface,reading in pairs:
                batch.append((reading,surface,POS_IDS["proper_noun"],POS_IDS["proper_noun"],
                              cost_for(5,1,120),rank_for(0,5,100),"proper_name"))
                stats["proper_name_candidates"]+=1
                if len(batch)>=BATCH_ROWS: insert_batch(con,batch)
            entry.clear()
            stats["name_source_entries"]+=1
            if stats["name_source_entries"]%100000==0:
                insert_batch(con,batch); con.commit()
                print(f"parsed {stats['name_source_entries']:,} JMnedict entries",flush=True)
    insert_batch(con,batch); con.commit()


def write_outputs(con, outdir: Path, target: int, stats: Counter, sources: list[tuple[str,Path,str,str]]):
    total=con.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
    if total<target:
        raise RuntimeError(f"Only {total:,} unique valid candidates; target is {target:,}. More approved source vocabulary or additional reviewed generation rules are needed.")
    outdir.mkdir(parents=True,exist_ok=True)
    shards=[]
    cur=con.execute("SELECT reading,left_id,right_id,cost,surface,kind FROM candidates ORDER BY rank,cost,reading,surface,left_id,right_id LIMIT ?",(target,))
    outdb=outdir/"dictionary.sqlite3"
    if outdb.exists(): outdb.unlink()
    db=sqlite3.connect(outdb)
    db.execute("PRAGMA journal_mode=OFF")
    db.execute("PRAGMA synchronous=OFF")
    db.execute("PRAGMA temp_store=FILE")
    db.execute("CREATE TABLE entries(reading TEXT NOT NULL,left_id INTEGER NOT NULL,right_id INTEGER NOT NULL,cost INTEGER NOT NULL,surface TEXT NOT NULL,PRIMARY KEY(reading,surface,left_id,right_id)) WITHOUT ROWID")
    db.execute("CREATE INDEX idx_reading_cost ON entries(reading,cost,surface)")
    db.execute("CREATE INDEX idx_surface ON entries(surface)")
    tsvdir=outdir/"tsv"; tsvdir.mkdir(exist_ok=True)
    lines=0; shard_no=0; shard_rows=0; fh=None; shard_path=None
    dbbatch=[]
    kind_counts=Counter()
    try:
        for reading,left_id,right_id,cost,surface,kind in cur:
            if fh is None or shard_rows>=SHARD_ROWS:
                if fh: fh.close()
                shard_no+=1; shard_rows=0
                shard_path=tsvdir/f"dictionary-{shard_no:03d}.tsv"
                fh=shard_path.open("w",encoding="utf-8",newline="\n")
                shards.append(shard_path.name)
            fh.write(f"{reading}\t{left_id}\t{right_id}\t{cost}\t{surface}\n")
            dbbatch.append((reading,left_id,right_id,cost,surface))
            kind_counts[kind]+=1
            lines+=1; shard_rows+=1
            if len(dbbatch)>=BATCH_ROWS:
                db.executemany("INSERT INTO entries VALUES(?,?,?,?,?)",dbbatch); db.commit(); dbbatch.clear()
            if lines%500000==0: print(f"wrote {lines:,}/{target:,} rows",flush=True)
    finally:
        if fh: fh.close()
    if dbbatch: db.executemany("INSERT INTO entries VALUES(?,?,?,?,?)",dbbatch); db.commit()
    db.execute("PRAGMA optimize"); db.commit(); db.close()
    stats["unique_candidates"]=total
    stats["output_rows"]=lines
    stats["selected_kind_counts"]=dict(kind_counts)
    stats["tsv_shards"]=shards
    stats["sources"]=[{
        "name":name,"file":path.name,"url":url,"last_modified_utc":modified,
        "file_bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
        "license":"CC BY-SA 4.0","license_url":"https://www.edrdg.org/edrdg/licence.html"
    } for name,path,url,modified in sources]
    stats["license_url"]="https://www.edrdg.org/edrdg/licence.html"
    stats["data_schema"]=["reading","left_id","right_id","cost","surface"]
    stats["id_policy"]="IROHA-local POS-class IDs; not compatible with Mozc IDs"
    stats["cost_policy"]="IROHA-local heuristic, lower values rank earlier; no source dictionary costs imported"
    stats["generated_utc"]=datetime.now(timezone.utc).isoformat()
    (outdir/"manifest.json").write_text(json.dumps(dict(stats),ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return lines


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,default=Path("source/JMdict.gz"))
    ap.add_argument("--names-source",type=Path,default=Path("source/JMnedict.xml.gz"))
    ap.add_argument("--out",type=Path,default=Path("release"))
    ap.add_argument("--work-db",type=Path,default=Path("candidates.sqlite3"))
    ap.add_argument("--target",type=int,default=TARGET_ROWS)
    ap.add_argument("--include-double-aux",action="store_true")
    args=ap.parse_args()
    if not args.source.is_file(): ap.error(f"JMdict source not found: {args.source}")
    if not args.names_source.is_file(): ap.error(f"JMnedict source not found: {args.names_source}")
    stats=Counter()
    con=init_db(args.work_db)
    try:
        build_candidates(args.source,con,stats,args.include_double_aux)
        build_name_candidates(args.names_source,con,stats)
        total=con.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
        print(f"unique candidates: {total:,}")
        if total<args.target and not args.include_double_aux:
            print("candidate count below target; rerun with --include-double-aux after review",file=sys.stderr)
            raise SystemExit(2)
        write_outputs(con,args.out,args.target,stats,[
            ("JMdict",args.source,"https://www.edrdg.org/pub/Nihongo/JMdict.gz","2026-11-27T03:30:28Z"),
            ("JMnedict",args.names_source,"https://www.edrdg.org/pub/Nihongo/JMnedict.xml.gz","2026-11-27T03:30:02Z"),
        ])
    finally:
        con.close()

if __name__=="__main__": main()
