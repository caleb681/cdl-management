import {test, before, after} from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const AxeBuilder=require(process.env.AXE_MODULE||'@axe-core/playwright').default;
const base=process.env.PREVIEW_URL||'http://127.0.0.1:8796';
const evidence=process.env.EVIDENCE_DIR||'../evidence';
const routes=[...new Set((await readFile(new URL('../sitemap.xml',import.meta.url),'utf8')).match(/<loc>(.*?)<\/loc>/g).map(x=>new URL(x.slice(5,-6)).pathname))];
let browser;
before(async()=>{browser=await chromium.launch({headless:true});await mkdir(evidence,{recursive:true});});
after(async()=>{await browser?.close();});
async function page(options={}){
 const context=await browser.newContext({bypassCSP:true,...options});
 await context.route('**/*',route=>{
  if(new URL(route.request().url()).origin!==new URL(base).origin)return route.abort();
  return route.continue();
 });
 return context.newPage();
}
async function fill(p,kind='audit'){
 await p.locator('#name').fill('Synthetic QA');await p.locator('#showroom').fill('Synthetic QA Showroom');
 await p.locator('#email').fill('qa@example.invalid');
 await p.locator('#phone').fill('555-0100');
 if(kind==='audit'){
  await p.locator('#city').fill('Test City, MO');await p.locator('#revenue').selectOption({label:'Under $50k / mo'});
  await p.locator('#goal').selectOption({label:'More local customers / leads'});
 }else await p.locator('#vertical').selectOption('Flooring');
}
test('all public routes render at desktop and mobile without overflow, missing content, console errors or serious accessibility violations',async()=>{
 const report=[];const p=await page();const errors=[];p.on('pageerror',e=>errors.push(e.message));
 for(const width of [1440,390,320]){
  await p.setViewportSize({width,height:960});
  for(const route of routes){
   const response=await p.goto(base+route);assert.equal(response.status(),200,route);
   assert.match(response.headers()['x-robots-tag'],/noindex/);
   await p.evaluate(()=>document.fonts.ready);
   const layout=await p.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,h1:document.querySelectorAll('h1').length,main:document.querySelectorAll('main').length,images:[...document.images].filter(x=>!x.complete||!x.naturalWidth).length}));
   assert.ok(layout.scroll<=layout.width,`${route} ${width} overflow ${layout.scroll}`);assert.equal(layout.h1,1);assert.equal(layout.main,1);assert.equal(layout.images,0);
   const actions=await p.locator('.btn:not(.secondary):not([disabled])').evaluateAll(es=>{
    const luminance=color=>{const c=color.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;});return .2126*c[0]+.7152*c[1]+.0722*c[2];};
    return es.filter(e=>e.getClientRects().length).map(e=>{const s=getComputedStyle(e),fg=luminance(s.color),bg=luminance(s.backgroundColor);return{text:e.innerText,foreground:s.color,background:s.backgroundColor,contrast:(Math.max(fg,bg)+.05)/(Math.min(fg,bg)+.05)};});
   });
   for(const action of actions)assert.ok(action.contrast>=4.5,`${route} ${width}: unreadable primary action ${action.text} (${action.contrast.toFixed(2)}:1)`);
   const a=await new AxeBuilder({page:p}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
   const bad=a.violations.filter(x=>['serious','critical'].includes(x.impact));
   report.push({route,width,layout,actions,violations:a.violations.map(x=>({id:x.id,impact:x.impact,nodes:x.nodes.map(n=>n.target)})),incomplete:a.incomplete.map(x=>({id:x.id,impact:x.impact,nodes:x.nodes.map(n=>n.target)}))});
   assert.equal(bad.length,0,JSON.stringify({route,width,bad:bad.map(x=>({id:x.id,nodes:x.nodes.map(n=>n.target)}))}));
  }
 }
 assert.deepEqual(errors,[]);await writeFile(evidence+'/layouts-accessibility.json',JSON.stringify(report,null,2));await p.context().close();
});
test('audit acknowledgement hides form and tracks only once; double submit sends once',async()=>{
 const p=await page();let count=0,payload;
 await p.route('https://formsubmit.co/**',async r=>{count++;payload=r.request().postDataJSON();await new Promise(r=>setTimeout(r,200));await r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({success:'true'})});});
 await p.goto(base+'/contact/');await p.evaluate(()=>window.cdlTrackLead=()=>window.qaTracked=(window.qaTracked||0)+1);await fill(p);await p.locator('#name').fill('  Synthetic QA  ');
 await p.locator('[type=submit]').click();await p.locator('form').evaluate(f=>f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})));
 await p.getByText('Your application was accepted.',{exact:false}).waitFor();assert.equal(count,1);assert.equal(payload.name,'Synthetic QA');assert.equal(payload.monthly_revenue,'Under $50k / mo');assert.equal(payload.showroom,'Synthetic QA Showroom');assert.equal(await p.evaluate(()=>window.qaTracked),1);
 assert.equal(await p.locator('.form-fields').isVisible(),false);await p.context().close();
});
test('audit can be acknowledged without optional phone, revenue, goal or website',async()=>{
 const p=await page();let payload,count=0;
 await p.route('https://formsubmit.co/**',r=>{count++;payload=r.request().postDataJSON();return r.fulfill({status:200,contentType:'application/json',body:'{"success":true}'});});
 await p.goto(base+'/contact/');
 await p.locator('#name').fill('Synthetic QA');await p.locator('#showroom').fill('Synthetic QA Showroom');
 await p.locator('#city').fill('Test City, MO');await p.locator('#email').fill('qa@example.invalid');
 await p.locator('[type=submit]').click();await p.getByRole('status').filter({hasText:'application was accepted'}).waitFor();
 assert.equal(count,1);for(const key of ['phone','monthly_revenue','biggest_goal','website'])assert.equal(payload[key],'');
 await p.context().close();
});
test('transition inquiries preserve the selected service path without granting a credit',async()=>{
 for(const goal of ['Switch providers: website only','Switch providers: SEO and advertising']){
  const p=await page();let payload,count=0;
  await p.route('https://formsubmit.co/**',r=>{count++;payload=r.request().postDataJSON();return r.fulfill({status:200,contentType:'application/json',body:'{"success":true}'});});
  await p.goto(base+'/contact/#switching');
  assert.match(await p.locator('#switching').innerText(),/proposed/i);
  assert.match(await p.locator('#switching').innerText(),/does not (activate|approve)/i);
  await fill(p);await p.locator('#goal').selectOption({label:goal});
  await p.locator('[type=submit]').click();
  await p.getByRole('status').filter({hasText:'application was accepted'}).waitFor();
  assert.equal(count,1);assert.equal(payload.biggest_goal,goal);
  assert.doesNotMatch(await p.getByRole('status').innerText(),/(credit|offer|eligibility).{0,12}(approved|activated|granted)/i);
  await p.context().close();
 }
});
test('explicit rejection keeps values, allows correction and does not track',async()=>{
 const p=await page();let count=0;
 await p.route('https://formsubmit.co/**',r=>{count++;return r.fulfill({status:422,contentType:'application/json',body:'{"success":false}'});});
 await p.goto(base+'/contact/');await p.evaluate(()=>window.cdlTrackLead=()=>window.qaTracked=true);await fill(p);await p.locator('[type=submit]').click();await p.getByRole('status').filter({hasText:'not accepted'}).waitFor();
 assert.equal(await p.locator('#name').inputValue(),'Synthetic QA');assert.equal(await p.locator('[type=submit]').isEnabled(),true);assert.equal(await p.evaluate(()=>window.qaTracked),undefined);assert.equal(count,1);await p.context().close();
});
test('non-JSON rejection allows a corrected retry and tracks only the acknowledged request',async()=>{
 for(const kind of ['audit','mockup']){
  const p=await page();let count=0;
  await p.route(kind==='audit'?'https://formsubmit.co/**':'**/api/intake',r=>{
   count++;return count===1?r.fulfill({status:422,contentType:'text/html',body:'<html>Check the request</html>'}):r.fulfill({status:200,contentType:'application/json',body:kind==='audit'?'{"success":true}':'{"ok":true}'});
  });
  await p.goto(base+(kind==='audit'?'/contact/':'/free-mockup/'));await p.evaluate(()=>window.cdlTrackLead=()=>window.qaTracked=(window.qaTracked||0)+1);await fill(p,kind);
  await p.locator('[type=submit]').click();await p.getByRole('status').filter({hasText:'not accepted'}).waitFor();
  assert.equal(await p.locator('#email').inputValue(),'qa@example.invalid');assert.equal(await p.locator('[type=submit]').isEnabled(),true);assert.equal(await p.evaluate(()=>window.qaTracked||0),0);
  await p.locator('#name').fill('Corrected Synthetic QA');await p.locator('[type=submit]').click();await p.getByRole('status').filter({hasText:'was accepted'}).waitFor();
  assert.equal(count,2);assert.equal(await p.evaluate(()=>window.qaTracked),1);assert.equal(await p.locator('.form-fields').isVisible(),false);await p.context().close();
 }
});
for(const mode of ['network','server','invalid-json','unacknowledged'])test(`unconfirmed ${mode} outcome retains details and blocks automatic retry`,async()=>{
 const p=await page();let count=0;
 await p.route('https://formsubmit.co/**',r=>{count++;if(mode==='network')return r.abort();return r.fulfill({status:mode==='server'?500:200,contentType:mode==='invalid-json'?'text/html':'application/json',body:mode==='invalid-json'?'<html>Error</html>':'{"success":false}'});});
 await p.goto(base+'/contact/');await fill(p);await p.locator('[type=submit]').click();await p.getByRole('status').filter({hasText:'could not confirm'}).waitFor();
 assert.equal(await p.locator('#email').inputValue(),'qa@example.invalid');assert.equal(await p.locator('[type=submit]').isEnabled(),false);await p.locator('form').evaluate(f=>f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})));assert.equal(count,1);await p.context().close();
});
test('invalid required fields cannot send and honeypot cannot send',async()=>{
 const p=await page();let count=0;await p.route('https://formsubmit.co/**',r=>{count++;return r.abort();});await p.goto(base+'/contact/');await p.locator('[type=submit]').click();assert.equal(count,0);await fill(p);await p.locator('#name').fill('   ');await p.locator('[type=submit]').click();assert.equal(count,0);assert.equal(await p.locator('#name').evaluate(el=>el.validity.customError),true);await p.locator('#name').fill('Synthetic QA');assert.equal(await p.locator('#name').evaluate(el=>el.validity.customError),false);await p.locator('#company_website_hp').evaluate(el=>el.value='bot');await p.locator('[type=submit]').click();assert.equal(count,0);await p.context().close();
});
test('a request timeout is held as an uncertain delivery without an automatic retry',async()=>{
 const p=await page();let count=0;
 await p.addInitScript(()=>{const original=window.setTimeout;window.setTimeout=(fn,ms,...args)=>original(fn,ms===18000?40:ms,...args);});
 await p.route('https://formsubmit.co/**',async r=>{count++;await new Promise(r=>setTimeout(r,150));await r.abort();});
 await p.goto(base+'/contact/');await fill(p);await p.locator('[type=submit]').click();await p.getByRole('status').filter({hasText:'could not confirm'}).waitFor();assert.equal(count,1);assert.equal(await p.locator('[type=submit]').isEnabled(),false);assert.equal(await p.locator('#email').inputValue(),'qa@example.invalid');await p.context().close();
});
test('mockup request retains current endpoint and sends correct contact field; explicit receipt required',async()=>{
 const p=await page();let payload,count=0;await p.route('**/api/intake',r=>{count++;payload=r.request().postDataJSON();return r.fulfill({status:200,contentType:'application/json',body:'{"ok":true}'});});await p.goto(base+'/free-mockup/');await fill(p,'mockup');await p.locator('#website').fill('example.invalid');await p.locator('[type=submit]').click();await p.getByRole('status').filter({hasText:'design request was accepted'}).waitFor();assert.equal(count,1);assert.equal(payload.name,'Synthetic QA');assert.equal(payload.contact_name,'Synthetic QA');assert.equal(payload.website,'https://example.invalid');assert.equal(payload.source,'free-mockup');await p.context().close();
});
test('keyboard navigation, mobile Escape focus, FAQ and reduced motion',async()=>{
 const p=await page({viewport:{width:390,height:844},reducedMotion:'reduce'});await p.goto(base+'/');await p.keyboard.press('Tab');assert.equal(await p.evaluate(()=>document.activeElement.textContent),'Skip to content');await p.keyboard.press('Enter');assert.equal(await p.evaluate(()=>document.activeElement.id),'main');await p.getByRole('button',{name:'Menu'}).click();assert.equal(await p.locator('#mobile-menu').isVisible(),true);await p.keyboard.press('Escape');assert.equal(await p.locator('#mobile-menu').isVisible(),false);assert.equal(await p.getByRole('button',{name:'Menu'}).evaluate(el=>el===document.activeElement),true);
 await p.locator('.faq-list summary').first().click();assert.equal(await p.locator('.faq-list details').first().getAttribute('open'),'');assert.equal(await p.evaluate(()=>getComputedStyle(document.documentElement).scrollBehavior),'auto');await p.context().close();
});
test('open mobile navigation resets when the viewport switches to desktop',async()=>{
 const p=await page({viewport:{width:390,height:844}});await p.goto(base+'/');
 await p.getByRole('button',{name:'Menu'}).click();await p.locator('#mobile-menu a').first().focus();
 await p.setViewportSize({width:1440,height:1000});await p.locator('#mobile-menu').waitFor({state:'hidden'});
 assert.equal(await p.locator('.menu-toggle').getAttribute('aria-expanded'),'false');assert.equal(await p.locator('.site-header .brand').evaluate(el=>el===document.activeElement),true);
 await p.setViewportSize({width:390,height:844});assert.equal(await p.locator('#mobile-menu').isVisible(),false);
 await p.getByRole('button',{name:'Menu'}).click();assert.equal(await p.locator('#mobile-menu').isVisible(),true);await p.context().close();
});
test('core services, pricing and articles are available with JavaScript disabled',async()=>{
 const p=await page({javaScriptEnabled:false});for(const route of ['/','/services/local-seo/','/pricing/','/blog/local-seo-for-flooring-stores/']){await p.goto(base+route);assert.ok((await p.locator('main').innerText()).length>800);assert.equal(await p.locator('h1').count(),1);}await p.goto(base+'/contact/');assert.match(await p.locator('noscript').innerText(),/email/);assert.equal(await p.locator('[type=submit]').isDisabled(),true);assert.equal(await p.locator('form').getAttribute('method'),'post');await p.context().close();
});
test('capture current desktop and mobile review images',async()=>{
 const p=await page();for(const [label,width,height] of [['desktop',1440,1000],['mobile',390,844]]){await p.setViewportSize({width,height});await p.goto(base+'/');await p.screenshot({path:evidence+'/homepage-'+label+'.png',fullPage:true});}await p.context().close();
});
test('local preview blocks real external form delivery; missing pages return404',async()=>{
 const p=await page({bypassCSP:false});let reached=0;
 await p.route('https://formsubmit.co/**',r=>{reached++;return r.abort();});
 const response=await p.goto(base+'/contact/');assert.match(response.headers()['content-security-policy'],/connect-src 'self'/);
 await fill(p);await p.locator('[type=submit]').click();await p.getByRole('status').filter({hasText:'could not confirm'}).waitFor();assert.equal(reached,0);
 const missing=await p.goto(base+'/this-page-does-not-exist/');assert.equal(missing.status(),404);assert.match(missing.headers()['x-robots-tag'],/noindex/);assert.match(await p.locator('h1').innerText(),/back/);await p.context().close();
});
test('malformed encoded addresses return400 and the isolated preview remains available',async()=>{
 const child=spawn(process.execPath,[fileURLToPath(new URL('../tools/preview.mjs',import.meta.url))],{env:{...process.env,PORT:'0'},stdio:['ignore','pipe','pipe']});
 try{
  const url=await new Promise((resolve,reject)=>{let text='';const timeout=setTimeout(()=>reject(Error('Preview startup timed out')),5000);child.stdout.on('data',data=>{text+=data;const match=text.match(/http:\/\/127\.0\.0\.1:\d+/);if(match){clearTimeout(timeout);resolve(match[0]);}});child.on('error',reject);child.on('exit',code=>reject(Error('Preview exited '+code)));});
  const bad=await fetch(url+'/%E0%A4%A');assert.equal(bad.status,400);assert.equal(await bad.text(),'Invalid address');
  const valid=await fetch(url+'/');assert.equal(valid.status,200);assert.match(await valid.text(),/Marketing built for/);
 }finally{child.kill('SIGTERM');}
});
