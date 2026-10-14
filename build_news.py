import json, urllib.request, urllib.parse, xml.etree.ElementTree as ET, re, html
from datetime import datetime, timezone
from pathlib import Path

CATEGORIES = {
 'Suisse & Monde': 'Suisse actualité internationale',
 'Horlogerie': 'industrie horlogère suisse montres manufactures innovation',
 'Sciences & Technologies': 'science technologie laser spatial aviation',
 'Économie': 'économie suisse internationale industrie',
}

def get_news(query):
    url='https://news.google.com/rss/search?'+urllib.parse.urlencode({'q':query,'hl':'fr','gl':'CH','ceid':'CH:fr'})
    request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 ThunderbirdNewsDashboard/1.0'})
    with urllib.request.urlopen(request,timeout=25) as response:
        root=ET.fromstring(response.read())
    out=[]
    for item in root.findall('./channel/item')[:8]:
        title=html.unescape(re.sub('<[^>]+>','',item.findtext('title') or '')).strip()
        link=item.findtext('link') or ''
        source=item.find('source')
        publisher=(source.text or '').strip() if source is not None else ''
        if publisher and title.endswith(' - '+publisher):title=title[:-(len(publisher)+3)]
        if title and link.startswith('https://'):
            out.append({'title':title,'url':link,'source':publisher,'published':item.findtext('pubDate') or ''})
    return out

result={'updated':datetime.now(timezone.utc).isoformat(timespec='seconds'),'categories':{},'errors':{}}
for name,query in CATEGORIES.items():
    try: result['categories'][name]=get_news(query)
    except Exception as e:
        result['categories'][name]=[]
        result['errors'][name]=str(e)
Path(__file__).with_name('news.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print({k:len(v) for k,v in result['categories'].items()})
