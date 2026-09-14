#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, html, json, random, re, shutil, time, unicodedata
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, unquote, urlencode, urljoin, urlsplit
from urllib.request import Request, urlopen
from concurrent.futures import ThreadPoolExecutor, as_completed
from zipfile import ZipFile, ZIP_DEFLATED

BASE="https://trillian.mit.edu/~jc/music/abc/Finland/"
STAMP="20160429003629"
ROOT=Path(__file__).resolve().parent
WORK=ROOT/"work"
OUT=ROOT/"output"

P2="""AntinValssi_Dm.abc
Avokatrilli.abc
ByTheLight.abc
ElamaJuoksuhaudoissa.abc
EllinPolkka.abc
Emma.abc
HeilaniKotiin_G.abc
HeiliKarjalasta.abc
HiluHilu_D.abc
HintikanMatinJ.abc
HoputasP_Am.abc
Hoylakatrilli.abc
JosSaisKerranReissullansa_D.abc
Kaki_Am.abc
Kapusta.abc
KarjalanKunnailla_Gm.abc
KarjalanP.abc
KatselinTaivaanTahtia_Gm.abc
KaustisenPolkka.abc
Kazazok.abc
Kerenski.abc
Kerenski_Am,Dm.abc
KiikkuriKaakkuri.abc
Kikapu.abc
Kipera.abc
KoivistonPolska.abc
KoivistonPolska2.abc
KoivistonPolska3.abc
KotimaaniOmpiSuomi_C.abc
KukkuvaKello.abc
KulkurinValssi_D.abc
KuuliaisetKottilassa_A.abc
Lanssi.abc
Lantti.abc
Lantti_F.abc
Lintunen.abc
LukkariHeikinP.abc
MaailmanMatti.abc
Mannikossa_G.abc
MatalanTorpanBalladi_Em.abc
Piiripolkka.abc
Ransissi.abc
__RAVIT_1__
__RAVIT_2__
SakkijarvenP.abc
Sakkijarven_polkka_Am.abc
SappuSakkijarvelta.abc
Seni.abc
Shot_Norbotten.abc
Shottish_Norbotten.abc
SinisiaPunasiaRuusunkukkia_Dm.abc
SomeronMasurkka.abc
SuomisenVainonP.abc
TaivasOnSininenJaValkoinen_Am.abc
TaivasOnSininenJaValkoinen_Cm.abc
TalikkalanMarkkinoilla_Gm.abc
Tulipunaruusut.abc
TuonneTaakseMetsamaan_Am.abc
TuonneTaakseMetsamaan_Cm.abc
VaiennutViulu.abc""".splitlines()

P3="""Lantti_Bb.abc
MenuettFrOravais_Dm.abc
MoosesFeedi.abc
PappilanPellola.abc
__RYSSA_1__
__RYSSA_2__
SaastopankkiValssi.abc
Serberijanozka.abc
Sparbanksvalsen.abc
__SYRJALA_1__
__SYRJALA_2__
TalonpojanTanssi.abc
TammerkoskenSillalla.abc
ValssiKarjaalta.abc
ZorrosMarke_Am.abc""".splitlines()

MISSING="""20140609.abc
20140619.abc
AiKuinkaKauniiltaKuuluupi_Am.abc
Finlandia.abc
FinnFest2013.abc
Halla-ViinenJenkka.abc
IllanHiljaisuudessa.abc
IltaTahti.abc
Iltalaulu_C.abc
IsaJussinSottiisi.abc
JuuretSuomessa.abc
JuuretSuomessa_Am.abc
JuuretSuomessa_Dm.abc
Kaki_Gm.abc
KarperoPolka.abc
KaynAhonLaitaa_D.abc
KohtalonTango.abc
KonstanparempiV.abc
KoskisenSakarinValssi.abc
KulkurinValssi.abc
KulkurinValssi_G.abc
Kultainen_nuoruus.abc
KymmenenKymmenen.abc
LokakuunPolka.abc
ManchurianHillsWaltz.abc
March1.abc
Masurka1.abc
Masurka3.abc
Menuett1.abc
MenuettFrKarleby_F.abc
Metsakukkia.abc
MinunKultani_Em.abc
NiinSinulleLaulan_Am.abc
NiinSinulleLaulan_Dm.abc
PaaskysenValssi_Am.abc
PaimenPlikanV.abc
Pilkku_C,G.abc
Polka1.abc
Polka2.abc
Polka3.abc
Polka4.abc
Polka4_Am.abc
Polka5.abc
Polska1.abc
Rakovalkealla.abc
Ralli_Am.abc
Rev20130425.abc
Rev20130928.abc
Rev2013FF.abc
Rev20150725.abc
Rev20151206.abc
Rev2015FF.abc
Rev20160116.abc
SininenJaValkoinenT.abc
Song01.abc
Song02.abc
Song03.abc
Song04.abc
Song05.abc
Song06.abc
Song07.abc
Song08.abc
Song09.abc
Song1.abc
Song10.abc
Song11.abc
Song12.abc
Song13.abc
Song14.abc
Song15.abc
Song16.abc
Song17.abc
Song18.abc
Song19.abc
Song2.abc
Song20.abc
Song3.abc
Song4.abc
Song5.abc
Song6.abc
SukkulaP.abc
SuviValssi_Em.abc
TaallaPohjantahdenAlla.abc
Tango2.abc
Valiaikainen_Em.abc
Vals1.abc
Vals2.abc
Vals3.abc
Vals4.abc
Vals5.abc
Vals6.abc
Vals7.abc
Vals8.abc
ViitalanAarnenSottiisi.abc
YoSaaristossa.abc
Yolintu.abc
_.abc
_1.abc
_2.abc
_3.abc
f.abc
m.abc
page.abc
sep.abc
shottish_Dm.abc
x3.abc
x4.abc
x6.abc""".splitlines()
TARGETS=P2+P3+MISSING
assert (len(P2),len(P3),len(MISSING),len(TARGETS),len(set(TARGETS)))==(60,15,108,183,183)
ALIASES={"HintikanMatinJ.abc":"Hintikan_Matin_jenkka-Dm-16-2.abc"}
SPECIAL={
 "__RAVIT_1__":("RavitKa",0,"RavitKapyla_variant_1.abc"),
 "__RAVIT_2__":("RavitKa",1,"RavitKapyla_variant_2.abc"),
 "__RYSSA_1__":("Ryssa",0,"Ryssa_variant_1.abc"),
 "__RYSSA_2__":("Ryssa",1,"Ryssa_variant_2.abc"),
 "__SYRJALA_1__":("Syrja",0,"Syrjalan_Kaapoon_polska_variant_1.abc"),
 "__SYRJALA_2__":("Syrja",1,"Syrjalan_Kaapoon_polska_variant_2.abc")}

class Links(HTMLParser):
 def __init__(self): super().__init__(); self.items=[]
 def handle_starttag(self,tag,attrs):
  if tag.lower()=="a":
   h=dict(attrs).get("href")
   if h: self.items.append(h)

def fetch(url,tries=6):
 errs=[]
 for i in range(tries):
  try:
   q=Request(url,headers={"User-Agent":"Mozilla/5.0 Finland-ABC-Recovery/1.0","Accept":"text/plain,text/vnd.abc,*/*"})
   with urlopen(q,timeout=45) as r:
    b=r.read()
    if b: return b,r.geturl()
    raise ValueError("empty response")
  except Exception as e:
   errs.append(str(e)); time.sleep(min(12,1.6**i)+random.random())
 raise RuntimeError(" | ".join(errs)[-2500:])

def textof(b):
 for enc in ("utf-8-sig","cp1252","latin-1"):
  try: return b.decode(enc).replace("\r\n","\n").replace("\r","\n")
  except UnicodeDecodeError: pass
 return b.decode("utf-8","replace").replace("\r\n","\n").replace("\r","\n")

def abc_ok(s):
 if re.search(r"<(?:!doctype|html|body)\b",s[:1200],re.I): return False
 return bool(re.search(r"(?m)^\s*T\s*:",s) and re.search(r"(?m)^\s*K\s*:",s))

def archive_urls(original):
 out=[f"https://web.archive.org/web/{STAMP}id_/{original}"]
 cdx="https://web.archive.org/cdx/search/cdx?"+urlencode({"url":original,"output":"json","filter":"statuscode:200","fl":"timestamp,original,digest","collapse":"digest","limit":"15"})
 try:
  b,_=fetch(cdx,3)
  rows=json.loads(b.decode())
  for row in reversed(rows[1:]):
   out.append(f"https://web.archive.org/web/{row[0]}id_/{row[1]}")
 except Exception: pass
 return list(dict.fromkeys(out))

def recover(item):
 live=urljoin(BASE,item["href"])
 trials=[("live",live),("live-http",live.replace("https://","http://",1))]
 original=urljoin(BASE.replace("https://","http://"),item["href"])
 trials += [("wayback",u) for u in archive_urls(original)]
 errors=[]
 for kind,url in trials:
  try:
   b,final=fetch(url,4 if kind=="live" else 2); s=textof(b)
   if abc_ok(s):
    item.update(status="recovered",kind=kind,url=final,text=s.rstrip()+"\n",size=len(b),error="")
    return item
   errors.append(kind+":not ABC")
  except Exception as e: errors.append(kind+":"+str(e))
 item.update(status="unresolved",kind="",url=live,text="",size=0,error=" || ".join(errors)[-3500:])
 return item

def de_moj(s):
 s=html.unescape(s).strip()
 for enc in ("latin-1","cp1252"):
  if not any(x in s for x in ("Ã","Â","Ì","â€")): break
  try:
   q=s.encode(enc).decode("utf-8")
   if sum(s.count(x) for x in ("Ã","Â","Ì","â€"))>sum(q.count(x) for x in ("Ã","Â","Ì","â€")): s=q
  except Exception: pass
 return re.sub(r"\s+"," ",s).strip(" ._-")

def fields(rec,tag):
 return [de_moj(m.group(1)) for m in re.finditer(rf"(?mi)^\s*{re.escape(tag)}\s*:\s*(.*?)\s*$",rec) if de_moj(m.group(1))]

def split_records(s):
 starts=list(re.finditer(r"(?m)^\s*X\s*:\s*.*$",s))
 if starts:
  out=[]
  for i,m in enumerate(starts):
   end=starts[i+1].start() if i+1<len(starts) else len(s)
   rec=s[m.start():end].strip()
   if re.search(r"(?m)^\s*K\s*:",rec): out.append(rec+"\n")
  return out
 if re.search(r"(?m)^\s*T\s*:",s) and re.search(r"(?m)^\s*K\s*:",s): return ["X:1\n"+s.strip()+"\n"]
 return []

def fingerprint(rec):
 kept=[]
 for raw in rec.splitlines():
  line=raw.strip()
  if not line or line.startswith("%"): continue
  m=re.match(r"^([A-Za-z+]):",line)
  if m and m.group(1) in set("XTCOZFNSHWw"): continue
  kept.append(re.sub(r"\s+","",line))
 canon="\n".join(kept)
 return hashlib.sha256(canon.encode()).hexdigest()

def titleof(rec,source,n):
 ts=fields(rec,"T")
 generic={"","untitled","unknown","song","tune","waltz","valssi","vals","polka","polska","march","masurka","mazurka"}
 for t in ts:
  if t.casefold() not in generic and not re.fullmatch(r"(?:song|tune|vals|rev)\s*\d*",t,re.I): return t
 return ts[0] if ts else f"{Path(source).stem} tune {n}"

def onefield(rec,tag):
 x=fields(rec,tag)
 return x[0].split()[0] if x else ""

def safe(s):
 s=unicodedata.normalize("NFKD",de_moj(s))
 s="".join(c for c in s if not unicodedata.combining(c)).encode("ascii","ignore").decode()
 s=s.replace("&"," and "); s=re.sub(r"['’]","",s)
 return re.sub(r"_+","_",re.sub(r"[^A-Za-z0-9]+","_",s).strip("_"))[:110] or "Untitled"

def csvout(path,rows,names):
 with path.open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=names); w.writeheader(); w.writerows(rows)

def main():
 shutil.rmtree(WORK,ignore_errors=True); shutil.rmtree(OUT,ignore_errors=True)
 src=WORK/"source_files"; ind=WORK/"individual"; rep=WORK/"reports"
 for p in (src,ind,rep,OUT): p.mkdir(parents=True,exist_ok=True)
 raw,index_url=fetch(BASE); parser=Links(); parser.feed(textof(raw))
 links=[]
 for href in parser.items:
  path=urlsplit(href).path
  if "/" in path.strip("/"): continue
  name=unquote(path.rsplit("/",1)[-1])
  if name.lower().endswith(".abc"): links.append({"href":href,"basename":name})
 links=list({x["href"]:x for x in links}.values()); by={x["basename"]:x for x in links}
 resolved=[]; index_errors=[]
 for target in TARGETS:
  if target in SPECIAL:
   prefix,pos,sav=SPECIAL[target]
   opts=sorted([x for x in links if x["basename"].startswith(prefix)],key=lambda x:x["href"])
   if pos>=len(opts): index_errors.append(f"{target}: expected variant {pos+1}, found {len(opts)}"); continue
   item=dict(opts[pos]); item["save"]=sav
  else:
   wanted=ALIASES.get(target,target); item=by.get(wanted)
   if not item: item=next((x for x in links if x["basename"].casefold()==wanted.casefold()),None)
   if not item: index_errors.append(f"{target}: absent from live index"); continue
   item=dict(item); item["save"]=wanted
  item["target"]=target; resolved.append(item)
 results=[]
 with ThreadPoolExecutor(max_workers=4) as pool:
  fs={pool.submit(recover,x):x for x in resolved}
  for f in as_completed(fs):
   x=f.result(); results.append(x); print(x["status"],x["target"],x["kind"],flush=True)
 results.sort(key=lambda x:TARGETS.index(x["target"]))
 used=set()
 for x in results:
  if x["status"]!="recovered": continue
  name=safe(Path(x["save"]).stem)+".abc"; base=Path(name).stem; n=2
  while name.casefold() in used: name=f"{base}_source-{n}.abc"; n+=1
  used.add(name.casefold()); x["saved"]=name
  (src/name).write_text(x["text"],encoding="utf-8",newline="\n")
 source_rows=[]; records=[]
 for x in results:
  source_rows.append({"target":x["target"],"directory_filename":x["basename"],"saved_filename":x.get("saved",""),"status":x["status"],"source_kind":x["kind"],"source_url":x["url"],"bytes":x["size"],"error":x["error"]})
  if x["status"]=="recovered":
   for n,record in enumerate(split_records(x["text"]),1):
    records.append({"record":record,"source":x["saved"],"number":n,"fp":fingerprint(record)})
 groups={}
 for x in records: groups.setdefault(x["fp"],[]).append(x)
 unique=[]; dupes=[]
 for fp,group in groups.items():
  group.sort(key=lambda x:(len(fields(x["record"],"T"))+len(fields(x["record"],"C"))+len(fields(x["record"],"R")),len(x["record"])),reverse=True)
  keep=group[0]; keep["sources"]=sorted({x["source"] for x in group}); unique.append(keep)
  for gone in group[1:]:
   dupes.append({"fingerprint":fp,"removed_source":gone["source"],"removed_record":gone["number"],"kept_source":keep["source"],"kept_record":keep["number"],"title":titleof(keep["record"],keep["source"],keep["number"]),"key":onefield(keep["record"],"K")})
 unique.sort(key=lambda x:(titleof(x["record"],x["source"],x["number"]).casefold(),onefield(x["record"],"K"),x["fp"]))
 used=set(); titles=[]; merged=[]
 for num,x in enumerate(unique,1):
  title=titleof(x["record"],x["source"],x["number"]); key=onefield(x["record"],"K"); rhythm=onefield(x["record"],"R")
  stem=safe(title); name=stem+".abc"
  if name.casefold() in used and key: name=f"{stem}_K-{safe(key)}.abc"
  v=2
  while name.casefold() in used: name=f"{stem}_variant-{v}.abc"; v+=1
  used.add(name.casefold())
  lines=x["record"].strip().splitlines()
  at=next((i for i,z in enumerate(lines) if re.match(r"^\s*X\s*:",z)),0)
  if not re.match(r"^\s*X\s*:",lines[at]): lines.insert(0,f"X:{num}"); at=0
  else: lines[at]=f"X:{num}"
  lines.insert(at+1,"% Recovered source file(s): "+"; ".join(x["sources"]))
  clean="\n".join(lines).rstrip()+"\n"; (ind/name).write_text(clean,encoding="utf-8",newline="\n"); merged.append(clean)
  titles.append({"filename":name,"title":title,"key":key,"rhythm":rhythm,"source_files":"; ".join(x["sources"]),"notation_sha256":x["fp"]})
 (WORK/"Finland_Clean_Collection.abc").write_text("\n\n".join(z.rstrip() for z in merged)+"\n",encoding="utf-8",newline="\n")
 csvout(rep/"SOURCE_RECOVERY.csv",source_rows,["target","directory_filename","saved_filename","status","source_kind","source_url","bytes","error"])
 csvout(rep/"TITLE_INDEX.csv",titles,["filename","title","key","rhythm","source_files","notation_sha256"])
 csvout(rep/"DUPLICATES_REMOVED.csv",dupes,["fingerprint","removed_source","removed_record","kept_source","kept_record","title","key"])
 unresolved=index_errors+[f"{x['target']}: {x['error']}" for x in results if x["status"]!="recovered"]
 (rep/"UNRESOLVED.txt").write_text("\n".join(unresolved)+"\n" if unresolved else "None\n",encoding="utf-8")
 recovered=sum(x["status"]=="recovered" for x in results)
 report=f"""FINLAND ABC RECOVERY - CLEANED COLLECTION
Original target source files: 183
Resolved against live index: {len(resolved)}
Genuine source files recovered: {recovered}
Unresolved source files: {len(unresolved)}
Tune records extracted: {len(records)}
Exact musical duplicates removed: {len(dupes)}
Unique tune records packaged: {len(unique)}

RULES
No placeholder or fabricated ABC bodies were created.
Multi-tune files were split at X: boundaries.
Exact duplicate comparison ignores catalogue, provenance and lyric fields.
Keys, notation, chords, voices and parts remain in the comparison, so alternate
keys and genuinely different arrangements are preserved.
Every unique tune is named from its internal T: title; collisions get a key or
variant suffix. All unique records are merged into Finland_Clean_Collection.abc.
Recovered top-level bodies remain in source_files.
Directory index: {index_url}
"""
 (rep/"RECOVERY_REPORT.txt").write_text(report,encoding="utf-8")
 (WORK/"README.txt").write_text("""FINLAND ABC CLEANED COLLECTION
Finland_Clean_Collection.abc - all unique tunes merged
individual/ - one real-title file per unique tune
source_files/ - recovered original top-level source bodies
reports/ - recovery audit, title index, duplicates and unresolved list
""",encoding="utf-8")
 zpath=OUT/"Finland_ABCs_complete_cleaned.zip"
 with ZipFile(zpath,"w",ZIP_DEFLATED,compresslevel=9) as z:
  for p in sorted(WORK.rglob("*")):
   if p.is_file(): z.write(p,p.relative_to(WORK))
 with ZipFile(zpath) as z:
  bad=z.testzip()
  if bad: raise RuntimeError("bad ZIP member "+bad)
  if "Finland_Clean_Collection.abc" not in z.namelist(): raise RuntimeError("merged file absent")
 print(report,flush=True)
 if recovered<75: raise RuntimeError(f"catastrophic recovery: {recovered}/183")
 return 0

if __name__=="__main__": raise SystemExit(main())
