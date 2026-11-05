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
test('privacy choices remain readable and usable at narrow widths without changing entered form details',async()=>{
 const p=await page();
 for(const width of [1440,390,320]){
  await p.setViewportSize({width,height:900});await p.goto(base+'/contact/');await fill(p);
  await p.locator('#privacy-choices summary').click();
  await p.locator('[data-privacy-choice="decline"]').click();
  assert.match(await p.locator('[data-privacy-status]').innerText(),/off/);
  assert.equal(await p.locator('#email').inputValue(),'qa@example.invalid');
  assert.equal(await p.locator('[type=submit]').isEnabled(),true);
  for(const b of await p.locator('.privacy-choice:visible').all()){
   const box=await b.boundingBox();assert.ok(box.width>=44&&box.height>=44);assert.ok(box.x>=0&&box.x+box.width<=width);
  }
  const a=await new AxeBuilder({page:p}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
  assert.deepEqual(a.violations.map(x=>x.id),[]);
 }
 await p.context().close();
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
 await p.locator('[type=submit]').click();await p.locator('form').getByRole('status').filter({hasText:'application was accepted'}).waitFor();
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
  await p.locator('form').getByRole('status').filter({hasText:'application was accepted'}).waitFor();
  assert.equal(count,1);assert.equal(payload.biggest_goal,goal);
  assert.doesNotMatch(await p.locator('form').getByRole('status').innerText(),/(credit|offer|eligibility).{0,12}(approved|activated|granted)/i);
  await p.context().close();
 }
});
test('explicit rejection keeps values, allows correction and does not track',async()=>{
 const p=await page();let count=0;
 await p.route('https://formsubmit.co/**',r=>{count++;return r.fulfill({status:422,contentType:'application/json',body:'{"success":false}'});});
 await p.goto(base+'/contact/');await p.evaluate(()=>window.cdlTrackLead=()=>window.qaTracked=true);await fill(p);await p.locator('[type=submit]').click();await p.locator('form').getByRole('status').filter({hasText:'not accepted'}).waitFor();
 assert.equal(await p.locator('#name').inputValue(),'Synthetic QA');assert.equal(await p.locator('[type=submit]').isEnabled(),true);assert.equal(await p.evaluate(()=>window.qaTracked),undefined);assert.equal(count,1);await p.context().close();
});
test('non-JSON rejection allows a corrected retry and tracks only the acknowledged request',async()=>{
 for(const kind of ['audit','mockup']){
  const p=await page();let count=0;
  await p.route(kind==='audit'?'https://formsubmit.co/**':'**/api/intake',r=>{
   count++;return count===1?r.fulfill({status:422,contentType:'text/html',body:'<html>Check the request</html>'}):r.fulfill({status:200,contentType:'application/json',body:kind==='audit'?'{"success":true}':'{"ok":true}'});
  });
  await p.goto(base+(kind==='audit'?'/contact/':'/free-mockup/'));await p.evaluate(()=>window.cdlTrackLead=()=>window.qaTracked=(window.qaTracked||0)+1);await fill(p,kind);
  await p.locator('[type=submit]').click();await p.locator('form').getByRole('status').filter({hasText:'not accepted'}).waitFor();
  assert.equal(await p.locator('#email').inputValue(),'qa@example.invalid');assert.equal(await p.locator('[type=submit]').isEnabled(),true);assert.equal(await p.evaluate(()=>window.qaTracked||0),0);
  await p.locator('#name').fill('Corrected Synthetic QA');await p.locator('[type=submit]').click();await p.locator('form').getByRole('status').filter({hasText:'was accepted'}).waitFor();
  assert.equal(count,2);assert.equal(await p.evaluate(()=>window.qaTracked),1);assert.equal(await p.locator('.form-fields').isVisible(),false);await p.context().close();
 }
});
for(const mode of ['network','server','invalid-json','unacknowledged'])test(`unconfirmed ${mode} outcome retains details and blocks automatic retry`,async()=>{
 const p=await page();let count=0;
 await p.route('https://formsubmit.co/**',r=>{count++;if(mode==='network')return r.abort();return r.fulfill({status:mode==='server'?500:200,contentType:mode==='invalid-json'?'text/html':'application/json',body:mode==='invalid-json'?'<html>Error</html>':'{"success":false}'});});
 await p.goto(base+'/contact/');await fill(p);await p.locator('[type=submit]').click();await p.locator('form').getByRole('status').filter({hasText:'could not confirm'}).waitFor();
 assert.equal(await p.locator('#email').inputValue(),'qa@example.invalid');assert.equal(await p.locator('[type=submit]').isEnabled(),false);await p.locator('form').evaluate(f=>f.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true})));assert.equal(count,1);await p.context().close();
});
test('invalid required fields cannot send and honeypot cannot send',async()=>{
 const p=await page();let count=0;await p.route('https://formsubmit.co/**',r=>{count++;return r.abort();});await p.goto(base+'/contact/');await p.locator('[type=submit]').click();assert.equal(count,0);await fill(p);await p.locator('#name').fill('   ');await p.locator('[type=submit]').click();assert.equal(count,0);assert.equal(await p.locator('#name').evaluate(el=>el.validity.customError),true);await p.locator('#name').fill('Synthetic QA');assert.equal(await p.locator('#name').evaluate(el=>el.validity.customError),false);await p.locator('#company_website_hp').evaluate(el=>el.value='bot');await p.locator('[type=submit]').click();assert.equal(count,0);await p.context().close();
});
test('a request timeout is held as an uncertain delivery without an automatic retry',async()=>{
 const p=await page();let count=0;
 await p.addInitScript(()=>{const original=window.setTimeout;window.setTimeout=(fn,ms,...args)=>original(fn,ms===18000?40:ms,...args);});
 await p.route('https://formsubmit.co/**',async r=>{count++;await new Promise(r=>setTimeout(r,150));await r.abort();});
 await p.goto(base+'/contact/');await fill(p);await p.locator('[type=submit]').click();await p.locator('form').getByRole('status').filter({hasText:'could not confirm'}).waitFor();assert.equal(count,1);assert.equal(await p.locator('[type=submit]').isEnabled(),false);assert.equal(await p.locator('#email').inputValue(),'qa@example.invalid');await p.context().close();
});
test('mockup request retains current endpoint and sends correct contact field; explicit receipt required',async()=>{
 const p=await page();let payload,count=0;await p.route('**/api/intake',r=>{count++;payload=r.request().postDataJSON();return r.fulfill({status:200,contentType:'application/json',body:'{"ok":true}'});});await p.goto(base+'/free-mockup/');await fill(p,'mockup');await p.locator('#website').fill('example.invalid');await p.locator('[type=submit]').click();await p.locator('form').getByRole('status').filter({hasText:'design request was accepted'}).waitFor();assert.equal(count,1);assert.equal(payload.name,'Synthetic QA');assert.equal(payload.contact_name,'Synthetic QA');assert.equal(payload.website,'https://example.invalid');assert.equal(payload.source,'free-mockup');await p.context().close();
});
test('an acknowledged duplicate design request is clear and does not count another conversion',async()=>{
 const p=await page();let count=0;
 await p.route('**/api/intake',r=>{count++;return r.fulfill({status:200,contentType:'application/json',body:'{"ok":true,"duplicate":true}'});});
 await p.goto(base+'/free-mockup/');await p.evaluate(()=>window.cdlTrackLead=()=>window.qaTracked=true);await fill(p,'mockup');
 await p.locator('[type=submit]').click();await p.locator('form').getByRole('status').filter({hasText:'already received'}).waitFor();
 assert.equal(count,1);assert.equal(await p.evaluate(()=>window.qaTracked),undefined);
 assert.equal(await p.locator('.form-fields').isVisible(),false);assert.equal(await p.locator('form').getByRole('status').locator('a[href^="mailto:"]').count(),1);
 await p.context().close();
});
test('explicit body timeout, size and media-type rejection keeps details editable without counting a lead',async()=>{
 for(const code of [408,413,415]){
  const p=await page();await p.route('**/api/intake',r=>r.fulfill({status:code,contentType:'application/json',body:'{"error":"Invalid request"}'}));
  await p.goto(base+'/free-mockup/');await p.evaluate(()=>window.cdlTrackLead=()=>window.qaTracked=true);await fill(p,'mockup');
  await p.locator('[type=submit]').click();await p.locator('form').getByRole('status').filter({hasText:'not accepted'}).waitFor();
  assert.equal(await p.locator('#email').inputValue(),'qa@example.invalid');assert.equal(await p.locator('[type=submit]').isEnabled(),true);
  assert.equal(await p.evaluate(()=>window.qaTracked),undefined);await p.context().close();
 }
});
test('optional website validation rejects unsafe addresses and allows correction',async()=>{
 const p=await page();let count=0;
 await p.route('**/api/intake',r=>{count++;return r.fulfill({status:200,contentType:'application/json',body:'{"ok":true}'});});
 await p.goto(base+'/free-mockup/');await fill(p,'mockup');
 for(const address of ['ftp://example.invalid','https://name:password@example.invalid','bad address']){
  await p.locator('#website').fill(address);await p.locator('[type=submit]').click();assert.equal(count,0);
  assert.equal(await p.locator('#website').evaluate(e=>e.validity.customError),true);
 }
 await p.locator('#website').fill('example.invalid');assert.equal(await p.locator('#website').evaluate(e=>e.validity.customError),false);
 await p.locator('[type=submit]').click();await p.locator('form').getByRole('status').filter({hasText:'was accepted'}).waitFor();assert.equal(count,1);
 await p.context().close();
});
test('keyboard navigation, mobile Escape focus, FAQ and reduced motion',async()=>{
 const p=await page({viewport:{width:390,height:844},reducedMotion:'reduce'});await p.goto(base+'/');await p.keyboard.press('Tab');assert.equal(await p.evaluate(()=>document.activeElement.textContent),'Skip to content');await p.keyboard.press('Enter');assert.equal(await p.evaluate(()=>document.activeElement.id),'main');await p.locator('.menu-toggle').click();assert.equal(await p.locator('#mobile-menu').isVisible(),true);await p.keyboard.press('Escape');assert.equal(await p.locator('#mobile-menu').isVisible(),false);assert.equal(await p.locator('.menu-toggle').evaluate(el=>el===document.activeElement),true);
 await p.locator('.faq-list summary').first().click();assert.equal(await p.locator('.faq-list details').first().getAttribute('open'),'');assert.equal(await p.evaluate(()=>getComputedStyle(document.documentElement).scrollBehavior),'auto');await p.context().close();
});
test('open mobile navigation resets when the viewport switches to desktop',async()=>{
 const p=await page({viewport:{width:390,height:844}});await p.goto(base+'/');
 await p.locator('.menu-toggle').click();await p.locator('#mobile-menu a').first().focus();
 await p.setViewportSize({width:1440,height:1000});await p.waitForFunction(()=>document.querySelector('.mobile-disclosure').open===false);
 assert.equal(await p.locator('.mobile-disclosure').evaluate(el=>el.open),false);assert.equal(await p.locator('.site-header .brand').evaluate(el=>el===document.activeElement),true);
 await p.setViewportSize({width:390,height:844});assert.equal(await p.locator('#mobile-menu').isVisible(),false);
 await p.locator('.menu-toggle').click();assert.equal(await p.locator('#mobile-menu').isVisible(),true);await p.context().close();
});
test('core services, pricing and articles are available with JavaScript disabled',async()=>{
 const p=await page({javaScriptEnabled:false});for(const route of ['/','/services/local-seo/','/pricing/','/blog/local-seo-for-flooring-stores/']){await p.goto(base+route);assert.ok((await p.locator('main').innerText()).length>800);assert.equal(await p.locator('h1').count(),1);}await p.goto(base+'/contact/');assert.equal(await p.locator('.form-fallback').isVisible(),true);assert.match(await p.locator('.form-fallback').innerText(),/email/);assert.equal(await p.locator('[type=submit]').isDisabled(),true);assert.equal(await p.locator('form').getAttribute('method'),'post');await p.context().close();
});
test('mobile navigation and form fallback remain usable when JavaScript is absent',async()=>{
 for(const missingScript of [false,true]){
  const p=await page({viewport:{width:390,height:844},javaScriptEnabled:missingScript});
  if(missingScript)await p.route('**/assets/site.js',r=>r.abort());
  await p.goto(base+'/contact/');
  await p.locator('.menu-toggle').focus();await p.keyboard.press('Enter');
  assert.equal(await p.locator('#mobile-menu').isVisible(),true);
  await p.keyboard.press('Space');assert.equal(await p.locator('#mobile-menu').isVisible(),false);
  assert.equal(await p.locator('.form-fallback').isVisible(),true);
  assert.equal(await p.locator('.form-fallback a[href^="tel:"]').count(),1);
  assert.equal(await p.locator('.form-fallback a[href^="mailto:"]').count(),1);
  assert.equal(await p.locator('[type=submit]').isDisabled(),true);
  await p.context().close();
 }
});
test('delayed JavaScript preserves a mobile menu already opened by the visitor',async()=>{
 const p=await page({viewport:{width:390,height:844}});let release;
 const ready=new Promise(resolve=>release=resolve);
 await p.route('**/assets/site.js',async r=>{await ready;await r.continue();});
 await p.goto(base+'/contact/',{waitUntil:'commit'});
 await p.locator('.menu-toggle').click();assert.equal(await p.locator('#mobile-menu').isVisible(),true);
 release();await p.locator('.form-fallback').waitFor({state:'hidden'});
 assert.equal(await p.locator('#mobile-menu').isVisible(),true);
 await p.keyboard.press('Escape');assert.equal(await p.locator('#mobile-menu').isVisible(),false);
 await p.context().close();
});
test('offline hints do not send prematurely or prevent an explicit later attempt',async()=>{
 for(const reconnect of [true,false]){
  const p=await page();let count=0;
  await p.addInitScript(()=>{window.qaOnline=false;Object.defineProperty(navigator,'onLine',{get:()=>window.qaOnline});});
  await p.route('https://formsubmit.co/**',r=>{count++;return r.fulfill({status:200,contentType:'application/json',body:'{"success":true}'});});
  await p.goto(base+'/contact/');await fill(p);await p.locator('[type=submit]').click();
  assert.match(await p.locator('form').getByRole('status').innerText(),/We have not sent/);assert.equal(count,0);
  assert.equal(await p.locator('[type=submit]').isEnabled(),true);assert.equal(await p.locator('#email').inputValue(),'qa@example.invalid');
  if(reconnect)await p.evaluate(()=>window.qaOnline=true);
  await p.getByRole('button',{name:'Try sending anyway'}).click();
  await p.locator('form').getByRole('status').filter({hasText:'application was accepted'}).waitFor();assert.equal(count,1);
  await p.context().close();
 }
});
test('pending requests lock editing, rejected requests restore it and recovery contacts are actionable',async()=>{
 for(const kind of ['audit','mockup']){
  const p=await page();let release,payload;
  const ready=new Promise(resolve=>release=resolve);
  await p.route(kind==='audit'?'https://formsubmit.co/**':'**/api/intake',async r=>{payload=r.request().postDataJSON();await ready;await r.fulfill({status:422,contentType:'text/html',body:'Rejected'});});
  await p.goto(base+(kind==='audit'?'/contact/':'/free-mockup/'));await fill(p,kind);
  await p.locator('[type=submit]').click();assert.equal(await p.locator('#email').isDisabled(),true);
  assert.match(await p.locator('form').getByRole('status').innerText(),/Sending your request/);
  assert.equal(await p.locator('form').getByRole('status').evaluate(e=>e===document.activeElement),true);
  assert.equal(await p.locator('.form-fields').getAttribute('aria-busy'),'true');
  assert.equal(await p.locator('form').getAttribute('aria-busy'),null);
  assert.equal(await p.locator('#name').isDisabled(),true);assert.equal(await p.locator('select').first().isDisabled(),true);
  release();await p.locator('form').getByRole('status').filter({hasText:'not accepted'}).waitFor();
  assert.equal(payload.email,'qa@example.invalid');assert.equal(await p.locator('#email').isEnabled(),true);
  assert.equal(await p.locator('[type=submit]').isEnabled(),true);
  assert.equal(await p.locator('form').getByRole('status').locator('a[href="tel:+16606653889"]').count(),1);
  assert.equal(await p.locator('form').getByRole('status').locator('a[href="mailto:caleb@cdl1.net"]').count(),1);
  await p.context().close();
 }
});
test('capture current desktop and mobile review images',async()=>{
 const p=await page();for(const [label,width,height] of [['desktop',1440,1000],['mobile',390,844]]){await p.setViewportSize({width,height});await p.goto(base+'/');await p.screenshot({path:evidence+'/homepage-'+label+'.png',fullPage:true});}await p.context().close();
});
test('local preview blocks real external form delivery; missing pages return404',async()=>{
 const p=await page({bypassCSP:false});let reached=0;
 await p.route('https://formsubmit.co/**',r=>{reached++;return r.abort();});
 const response=await p.goto(base+'/contact/');assert.match(response.headers()['content-security-policy'],/connect-src 'self'/);
 await fill(p);await p.locator('[type=submit]').click();await p.locator('form').getByRole('status').filter({hasText:'could not confirm'}).waitFor();assert.equal(reached,0);
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

// Paste into tests/browser.test.mjs; uses its test, assert, page() and base.
// Browser-only regressions, not a screen-reader or native-zoom certification.
test('keyboard focus stays visible against representative light and dark surfaces',async()=>{
 const p=await page({viewport:{width:1280,height:900},reducedMotion:'reduce'});
 try{
  await p.goto(base+'/');
  for(const selector of ['.hero-actions .btn','#main .contact-links a[href^="tel:"]','.site-footer a[href^="tel:"]']){
   const target=p.locator(selector).first();
   await target.focus();await p.keyboard.press('Tab');await p.keyboard.press('Shift+Tab');
   const style=await target.evaluate(el=>{
    const color=value=>{const parts=value.match(/[\d.]+/g).map(Number);return{rgb:parts.slice(0,3),alpha:parts[3]??1};};
    const foreground=color(getComputedStyle(el).outlineColor);
    let ancestor=el.parentElement,background;
    while(ancestor){
     const candidate=color(getComputedStyle(ancestor).backgroundColor);
     if(candidate.alpha>0){background=candidate;break;}
     ancestor=ancestor.parentElement;
    }
    return{focused:el===document.activeElement,visible:el.matches(':focus-visible'),
     outlineStyle:getComputedStyle(el).outlineStyle,outlineWidth:parseFloat(getComputedStyle(el).outlineWidth),
     foreground,background};
   });
   assert.ok(style.focused&&style.visible,selector+' needs keyboard-visible focus');
   assert.ok(style.outlineStyle!=='none'&&style.outlineWidth>0,selector+' needs a visible outline');
   assert.ok(style.background,selector+' needs a measurable surrounding surface');
   // Fail explicitly if a new translucent design needs compositing, rather than
   // silently calculating an invalid ratio from uncomposited colors.
   assert.equal(style.foreground.alpha,1,selector+' outline requires alpha compositing');
   assert.equal(style.background.alpha,1,selector+' surface requires alpha compositing');
   const luminance=rgb=>rgb.map(v=>v/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4)
    .reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
   const a=luminance(style.foreground.rgb),b=luminance(style.background.rgb);
   const contrast=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);
   assert.ok(contrast>=3,selector+' focus contrast '+contrast.toFixed(2)+' must be at least 3:1');
  }
 }finally{await p.context().close();}
});

test('200 percent modeled text enlargement preserves reflow, Menu and hero content',async()=>{
 const p=await page({viewport:{width:390,height:844},reducedMotion:'reduce'});
 try{
  for(const route of ['/','/contact/','/pricing/','/switch/','/compare/broadlume/']){
   await p.goto(base+route);
   // Snapshot before applying changes so inherited sizes are doubled once.
   // This reproduces the original text-only stress case, not native zoom.
   await p.evaluate(()=>{
    const sizes=[...document.querySelectorAll('body *')].map(el=>[el,parseFloat(getComputedStyle(el).fontSize)]);
    for(const[el,size]of sizes)el.style.fontSize=size*2+'px';
   });
   const layout=await p.evaluate(()=>{
    const menu=document.querySelector('.menu-toggle'),r=menu.getBoundingClientRect();
    return{width:innerWidth,height:innerHeight,scrollWidth:document.documentElement.scrollWidth,
     menu:{left:r.left,right:r.right,top:r.top,bottom:r.bottom,width:r.width,height:r.height}};
   });
   assert.ok(layout.scrollWidth<=layout.width+1,route+' has page-level horizontal overflow');
   assert.ok(layout.menu.width>0&&layout.menu.height>0,route+' Menu must remain visible');
   assert.ok(layout.menu.left>=0&&layout.menu.right<=layout.width+1&&layout.menu.top>=0&&layout.menu.bottom<=layout.height+1,
    route+' Menu must remain inside the viewport');
   await p.locator('.menu-toggle').focus();await p.keyboard.press('Enter');
   assert.ok(await p.locator('#mobile-menu').isVisible(),route+' enlarged Menu must open');
   await p.keyboard.press('Escape');
   assert.equal(await p.locator('#mobile-menu').isVisible(),false,route+' enlarged Menu must close');
   if(route==='/'){
    const content=await p.locator('.hero h1').evaluate(heading=>{
     const hero=heading.closest('.hero').getBoundingClientRect();
     const range=document.createRange();range.selectNodeContents(heading);
     return{text:heading.textContent.trim(),hero:{left:hero.left,right:hero.right,top:hero.top,bottom:hero.bottom},
      rects:[...range.getClientRects()].filter(r=>r.width&&r.height).map(r=>({left:r.left,right:r.right,top:r.top,bottom:r.bottom}))};
    });
    assert.ok(content.text&&content.rects.length,'hero heading must retain rendered text');
    for(const r of content.rects)assert.ok(r.left>=content.hero.left-1&&r.right<=content.hero.right+1&&r.top>=content.hero.top-1&&r.bottom<=content.hero.bottom+1,
     'enlarged hero heading must fit inside its clipping ancestor');
    const cta=p.locator('.hero-actions .btn');
    await cta.focus();
    assert.ok(await cta.evaluate(el=>el===document.activeElement),'hero CTA must remain keyboard reachable');
   }
  }
 }finally{await p.context().close();}
});
