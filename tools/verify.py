"""Check all built public pages, local links, metadata and structured data."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json, xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
class Page(HTMLParser):
 def __init__(self,text):
  super().__init__();self.ids=[];self.refs=[];self.h1=0;self.main=0;self.titles=0;self.canonical=[];self.descriptions=[];self.json=[];self.in_json=False;self.buffer='';self.images=[];self.feed(text)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if 'id' in a:self.ids.append(a['id'])
  if tag=='h1':self.h1+=1
  if tag=='main':self.main+=1
  if tag=='title':self.titles+=1
  if tag=='meta' and a.get('name')=='description':self.descriptions.append(a.get('content',''))
  if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
  if tag=='a' and 'href' in a:self.refs.append(a['href'])
  if tag in ['img','script'] and a.get('src'):self.refs.append(a['src'])
  if tag=='link' and a.get('rel') in ['stylesheet','icon']:self.refs.append(a['href'])
  if tag=='img':self.images.append(a)
  if tag=='script' and a.get('type')=='application/ld+json':self.in_json=True;self.buffer=''
 def handle_data(self,data):
  if self.in_json:self.buffer+=data
 def handle_endtag(self,tag):
  if tag=='script' and self.in_json:self.json.append(json.loads(self.buffer));self.in_json=False

def verify():
 pages={p:Page(p.read_text()) for p in ROOT.rglob('index.html') if not any(x in p.parts for x in ['source','command','functions','node_modules','.git'])}
 errors=[];references=0;canon=[]
 for file,page in pages.items():
  relative=file.relative_to(ROOT);route='/' if relative==Path('index.html') else '/'+str(relative.parent)+'/'
  if page.h1!=1:errors.append(f'{relative}: {page.h1} H1s')
  if page.main!=1:errors.append(f'{relative}: needs one main')
  if page.titles!=1:errors.append(f'{relative}: needs one title')
  if len(page.descriptions)!=1 or not page.descriptions[0]:errors.append(f'{relative}: missing description')
  if page.canonical!=['https://cdlmanagement.com'+route]:errors.append(f'{relative}: canonical mismatch')
  canon+=page.canonical
  if len(page.ids)!=len(set(page.ids)):errors.append(f'{relative}: duplicate ID')
  if not page.json:errors.append(f'{relative}: missing structured data')
  if '<script src="/assets/track.js" defer>' not in file.read_text():errors.append(f'{relative}: tracking missing/defer')
  if '—' in file.read_text():errors.append(f'{relative}: em dash')
  for img in page.images:
   if not all(k in img for k in ['alt','width','height']):errors.append(f'{relative}: image alt/dimensions missing')
  for ref in page.refs:
   u=urlsplit(ref)
   if u.scheme or u.netloc:continue
   references+=1
   path=unquote(u.path);target=ROOT/path.lstrip('/') if path.startswith('/') else file.parent/path
   if not path:target=file
   if target.is_dir():target=target/'index.html'
   if not target.exists():errors.append(f'{relative}: missing {ref}');continue
   if u.fragment and target.suffix=='.html':
    other=pages.get(target) or Page(target.read_text())
    if u.fragment not in other.ids:errors.append(f'{relative}: missing anchor {ref}')
 if len(set(canon))!=len(canon):errors.append('duplicate canonical')
 sitemap=ET.parse(ROOT/'sitemap.xml');urls=[x.text for x in sitemap.findall('.//{*}loc')]
 if set(urls)!=set(canon):errors.append('sitemap does not match public pages')
 # Exclude source, tests and tooling from the production asset upload.
 ignore=(ROOT/'.assetsignore').read_text().splitlines()
 for name in ['source','tools','tests','package.json']:
  if name not in ignore:errors.append('asset exclusion missing: '+name)
 if errors:raise SystemExit('\n'.join(errors))
 print(json.dumps({'pages':len(pages),'local_references':references,'unique_canonicals':len(canon),'sitemap_urls':len(urls),'errors':0},indent=2))

if __name__=='__main__':verify()
