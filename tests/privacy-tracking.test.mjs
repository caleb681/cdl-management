import {test, before, after} from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {readFile} from 'node:fs/promises';
const require=createRequire(import.meta.url);
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const script=await readFile(new URL('../assets/track.js',import.meta.url),'utf8');
const formScript=await readFile(new URL('../assets/site.js',import.meta.url),'utf8');
const key='cdl-privacy-choice-v1';
const origin='https://cdl-privacy-test.invalid';
const markup=`<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Privacy test fixture</title></head><body><form><label>Unsaved details<input name="details"></label><button>Send fixture</button></form><footer><details id="privacy-choices"><summary>Privacy choices</summary><p data-privacy-status role="status">Advertising measurement is off until you allow it.</p><button data-privacy-choice="allow" disabled>Allow advertising measurement</button><button data-privacy-choice="decline" disabled>Decline advertising measurement</button><button data-privacy-reload hidden>Reload to apply fully</button></details></footer><script src="/track.js" defer></script></body></html>`;
const sdk=`window.qaSdkLoads=(window.qaSdkLoads||0)+1;window.qaEvents=window.qaEvents||[];window.fbq.callMethod=function(){window.qaEvents.push(Array.from(arguments));};`;
let browser;
before(async()=>{browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_EXECUTABLE_PATH?{executablePath:process.env.CHROMIUM_EXECUTABLE_PATH}:{})});});
after(async()=>{await browser?.close();});

async function fixture(options={}){
 const context=await browser.newContext({javaScriptEnabled:options.javaScriptEnabled!==false});
 const requests=[],intakeRequests=[];let sdkRequests=0,releaseSdk;
 const pendingSdk=options.delaySdk?new Promise(resolve=>releaseSdk=resolve):Promise.resolve();
 await context.addInitScript(({key,choice,gpc,dnt,brokenStorage})=>{
  if(choice!==undefined&&!sessionStorage.getItem('qa-privacy-seeded')){
   localStorage.setItem(key,typeof choice==='string'?choice:JSON.stringify(choice));
   sessionStorage.setItem('qa-privacy-seeded','true');
  }
  if(gpc!==undefined)Object.defineProperty(navigator,'globalPrivacyControl',{configurable:true,get:()=>gpc});
  if(dnt!==undefined)Object.defineProperty(navigator,'doNotTrack',{configurable:true,get:()=>dnt});
  if(brokenStorage){
   if(brokenStorage==='read')Storage.prototype.getItem=function(){throw Error('Synthetic storage failure');};
   else {
    Storage.prototype.setItem=function(){throw Error('Synthetic storage failure');};
    if(brokenStorage==='allwrite')Storage.prototype.removeItem=function(){throw Error('Synthetic removal failure');};
   }
  }
 },{key,choice:options.choice,gpc:options.gpc,dnt:options.dnt,brokenStorage:options.brokenStorage});
 await context.route('**/*',async route=>{
  const url=route.request().url();requests.push(url);
  if(url===origin+'/'||url==='http://127.0.0.1/'){
   let body=options.noControls?markup.replace(/<footer>.*?<\/footer>/s,''):markup;
   if(options.realForm){
    body=body.replace(/<form>.*?<\/form>/s,`<form data-lead-form="${options.realForm}" method="post"><fieldset class="form-fields"><label>Name<input name="name" required value="Synthetic QA"></label><label>Showroom<input name="showroom" required value="Synthetic Showroom"></label><label>Email<input name="email" type="email" required value="qa@example.invalid"></label><input name="city" value="Synthetic City"><input name="vertical" value="Flooring"><button type="submit" disabled>Send fixture</button><p class="form-fallback">Synthetic fallback</p></fieldset><div role="status"></div></form>`);
    body=body.replace('<script src="/track.js"', '<script src="/site.js" defer></script><script src="/track.js"');
   }
   return route.fulfill({status:200,contentType:'text/html',body});
  }
  if(url===origin+'/track.js'||url==='http://127.0.0.1/track.js')return route.fulfill({status:200,contentType:'application/javascript',body:script});
  if(url===origin+'/site.js')return route.fulfill({status:200,contentType:'application/javascript',body:formScript});
  if(options.realForm&&(url===origin+'/api/intake/audit'||url===origin+'/api/intake')){
   intakeRequests.push({url,method:route.request().method(),payload:route.request().postDataJSON()});
   let body={ok:true,status:'received_unverified',request_kind:options.realForm,request_id:'7255f3e8-bb92-4ae2-b28c-11604028f0d1',duplicate:options.response==='duplicate'};
   if(options.response==='uncertain')body={};
   if(options.response==='wrong-kind')body.request_kind=options.realForm==='audit'?'mockup':'audit';
   if(options.response==='missing-kind')delete body.request_kind;
   if(options.response==='missing-id')delete body.request_id;
   if(options.response==='invalid-id')body.request_id='not-a-uuid';
   if(options.response==='wrong-status')body.status='approved';
   if(options.response==='missing-duplicate')delete body.duplicate;
   if(options.response==='invalid-duplicate')body.duplicate='false';
   if(options.response==='legacy')body=options.realForm==='audit'?{success:true}:{ok:true};
   return route.fulfill({status:options.response==='reject'?422:200,contentType:'application/json',body:JSON.stringify(body)});
  }
  if(url==='https://connect.facebook.net/en_US/fbevents.js'){
   sdkRequests++;await pendingSdk;
   return options.sdkError?route.abort():route.fulfill({status:200,contentType:'application/javascript',body:sdk});
  }
  return route.abort(); // Every request is fulfilled locally or blocked; never live SDK traffic.
 });
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(options.preview?'http://127.0.0.1/':origin+'/',{waitUntil:'domcontentloaded'});
 if(!options.noControls)await page.locator('#privacy-choices').evaluate(el=>el.open=true);
 const events=()=>page.evaluate(()=>window.qaEvents||[]);
 return {context,page,events,errors,requests,intakeRequests,sdkRequests:()=>sdkRequests,releaseSdk:()=>releaseSdk?.()};
}
const saved=choice=>({version:1,choice,savedAt:Date.now()});
const allow=f=>f.page.locator('[data-privacy-choice="allow"]').click();
const decline=f=>f.page.locator('[data-privacy-choice="decline"]').click();
async function loaded(f){await f.page.waitForFunction(()=>window.qaEvents?.some(e=>e[0]==='track'&&e[1]==='PageView'));}
async function close(f){assert.deepEqual(f.errors,[]);await f.context.close();}

test('fresh, ignored and declined choices never request Meta; forms remain available',async()=>{
 const f=await fixture();assert.equal(f.sdkRequests(),0);
 await f.page.locator('input').fill('Unsaved synthetic details');
 assert.equal(await f.page.evaluate(()=>window.cdlTrackLead('Growth Audit')),false);
 await decline(f);assert.equal(f.sdkRequests(),0);assert.deepEqual(await f.events(),[]);
 assert.equal(await f.page.locator('input').inputValue(),'Unsaved synthetic details');
 assert.equal(await f.page.locator('form button').isEnabled(),true);await close(f);
});
for(const options of [{gpc:true},{dnt:'1'},{gpc:true,choice:saved('allow')},{dnt:'1',choice:saved('allow')},{preview:true,choice:saved('allow')}])test(`privacy signals and preview override allow ${JSON.stringify(options)}`,async()=>{
 const f=await fixture(options);assert.equal(await f.page.locator('[data-privacy-choice="allow"]').isDisabled(),true);
 assert.equal(await f.page.evaluate(()=>window.cdlTrackLead('Growth Audit')),false);assert.equal(f.sdkRequests(),0);assert.deepEqual(await f.events(),[]);await close(f);
});
for(const choice of ['not json',{version:2,choice:'allow',savedAt:Date.now()},{version:1,choice:'allow',savedAt:0},saved('decline')])test(`invalid, expired and declined saved state stays off ${JSON.stringify(choice)}`,async()=>{
 const f=await fixture({choice});assert.equal(f.sdkRequests(),0);assert.deepEqual(await f.events(),[]);await close(f);
});
test('explicit allow preserves pixel and events, rejects arbitrary form data, and does not backfill',async()=>{
 const f=await fixture({gpc:false,dnt:'0'});
 assert.equal(await f.page.evaluate(()=>window.cdlTrackLead('Growth Audit')),false);
 await allow(f);await loaded(f);await allow(f);
 assert.equal(f.sdkRequests(),1);
 assert.equal(await f.page.evaluate(()=>window.cdlTrackLead('qa@example.invalid')),false);
 assert.equal(await f.page.evaluate(()=>window.cdlTrackLead('Growth Audit')),true);
 assert.equal(await f.page.evaluate(()=>window.cdlTrackLead('Growth Audit')),false);
 assert.equal(await f.page.evaluate(()=>window.cdlTrackLead('Free Mockup')),true);
 assert.deepEqual(await f.events(),[['init','1792164632076086'],['track','PageView'],['track','Lead',{content_name:'Growth Audit'}],['track','Lead',{content_name:'Free Mockup'}]]);
 const preference=await f.page.evaluate(key=>JSON.parse(localStorage.getItem(key)),key);
 assert.deepEqual(Object.keys(preference).sort(),['choice','savedAt','version']);assert.equal(preference.choice,'allow');await close(f);
});
test('saved allow loads once and pageshow does not duplicate PageView',async()=>{
 const f=await fixture({choice:saved('allow')});await loaded(f);
 await f.page.evaluate(()=>{dispatchEvent(new Event('pageshow'));dispatchEvent(new Event('focus'));});
 assert.equal(f.sdkRequests(),1);assert.equal((await f.events()).filter(e=>e[1]==='PageView').length,1);await close(f);
});
test('withdrawal never reloads unsaved form, stops wrapper, then explicit reload uses saved decline',async()=>{
 const f=await fixture();await allow(f);await loaded(f);await f.page.locator('input').fill('Keep this synthetic text');
 await decline(f);assert.equal(await f.page.locator('input').inputValue(),'Keep this synthetic text');
 assert.equal(await f.page.locator('[data-privacy-reload]').isVisible(),true);
 assert.match(await f.page.locator('[data-privacy-status]').innerText(),/Copy or finish any form details/);
 assert.equal(await f.page.evaluate(()=>window.cdlTrackLead('Free Mockup')),false);
 assert.equal((await f.events()).filter(e=>e[1]==='Lead').length,0);
 await Promise.all([f.page.waitForNavigation(),f.page.locator('[data-privacy-reload]').click()]);
 assert.equal(f.sdkRequests(),1);assert.deepEqual(await f.events(),[]);await close(f);
});
test('decline during SDK load does not flush previously denied or loading events',async()=>{
 const f=await fixture({delaySdk:true});
 await f.page.evaluate(()=>window.cdlTrackLead('Growth Audit'));await allow(f);
 await f.page.waitForFunction(()=>!!document.querySelector('[data-cdl-meta]'));
 await f.page.evaluate(()=>window.cdlTrackLead('Free Mockup'));await decline(f);f.releaseSdk();
 await f.page.waitForFunction(()=>window.qaSdkLoads===1);assert.deepEqual(await f.events(),[]);await close(f);
});
test('cross-tab rejection and a changed browser signal are rechecked before Lead',async()=>{
 for(const signal of [false,true]){
  const f=await fixture();await allow(f);await loaded(f);
  await f.page.evaluate(({key,signal})=>{
   if(signal)Object.defineProperty(navigator,'globalPrivacyControl',{configurable:true,get:()=>true});
   else {localStorage.setItem(key,JSON.stringify({version:1,choice:'decline',savedAt:Date.now()}));dispatchEvent(new StorageEvent('storage',{key}));}
  },{key,signal});
  assert.equal(await f.page.evaluate(()=>window.cdlTrackLead('Growth Audit')),false);
  assert.equal((await f.events()).filter(e=>e[1]==='Lead').length,0);await close(f);
 }
});
for(const brokenStorage of ['read','write'])test(`storage ${brokenStorage} failure leaves measurement off`,async()=>{
 const f=await fixture({brokenStorage});if(brokenStorage==='write')await allow(f);
 assert.equal(f.sdkRequests(),0);assert.equal(await f.page.evaluate(()=>window.cdlTrackLead('Growth Audit')),false);
 assert.match(await f.page.locator('[data-privacy-status]').innerText(),/off on this page/);await close(f);
});
test('SDK failure leaves form usable and wrapper off',async()=>{
 const f=await fixture({sdkError:true});await allow(f);await f.page.waitForFunction(()=>document.querySelector('[data-privacy-status]').textContent.includes('could not be enabled'));
 assert.equal(await f.page.evaluate(()=>window.cdlTrackLead('Growth Audit')),false);assert.equal(await f.page.locator('form button').isEnabled(),true);await close(f);
});
test('failed decline write removes a stale saved allow before manual reload',async()=>{
 const f=await fixture({choice:saved('allow'),brokenStorage:'write'});await loaded(f);
 await decline(f);assert.equal(await f.page.evaluate(()=>window.cdlTrackLead('Growth Audit')),false);
 assert.equal(await f.page.evaluate(key=>localStorage.getItem(key),key),null);
 await Promise.all([f.page.waitForNavigation(),f.page.locator('[data-privacy-reload]').click()]);
 assert.equal(f.sdkRequests(),1);assert.deepEqual(await f.events(),[]);await close(f);
});
test('when neither saving nor removal works, stale allow cannot reactivate this page or trigger unsafe reload',async()=>{
 const f=await fixture({choice:saved('allow'),brokenStorage:'allwrite'});await loaded(f);
 await f.page.locator('input').fill('Keep these details');await decline(f);
 assert.equal(await f.page.evaluate(()=>window.cdlTrackLead('Growth Audit')),false);
 assert.equal(await f.page.locator('[data-privacy-reload]').isDisabled(),true);
 assert.match(await f.page.locator('[data-privacy-status]').innerText(),/could not remember an off choice/);
 assert.equal(await f.page.locator('input').inputValue(),'Keep these details');
 assert.equal((await f.events()).filter(e=>e[1]==='Lead').length,0);await close(f);
});
test('real form acknowledgement sends only the allowed lead and never backfills an earlier submission',async()=>{
 for(const kind of ['audit','mockup'])for(const allowed of [false,true]){
  const f=await fixture({realForm:kind});
  if(allowed){await allow(f);await loaded(f);}
  await f.page.locator('form [type=submit]').click();
  await f.page.waitForFunction(()=>document.querySelector('form .form-fields').hidden);
  assert.equal(f.intakeRequests.length,1);assert.equal(f.intakeRequests[0].method,'POST');
  assert.equal(f.intakeRequests[0].url,origin+(kind==='audit'?'/api/intake/audit':'/api/intake'));
  assert.equal(f.intakeRequests[0].payload.business_name,'Synthetic Showroom');
  if(kind==='audit')assert.equal(f.intakeRequests[0].payload.city,'Synthetic City');
  assert.equal(f.requests.some(url=>url.includes('formsubmit.co')),false);
  assert.equal((await f.events()).filter(e=>e[1]==='Lead').length,allowed?1:0);
  if(!allowed){await allow(f);await loaded(f);assert.equal((await f.events()).filter(e=>e[1]==='Lead').length,0);}
  assert.doesNotMatch(JSON.stringify(await f.events()),/qa@example|Synthetic Showroom|Synthetic City/);
  await close(f);
 }
});
test('both real form kinds suppress Lead for rejection, uncertain receipt and duplicate receipt',async()=>{
 for(const kind of ['audit','mockup'])for(const response of ['reject','uncertain','duplicate']){
  const f=await fixture({realForm:kind,response});await allow(f);await loaded(f);
  await f.page.locator('form [type=submit]').click();
  await f.page.waitForFunction(()=>!/Sending|^$/.test(document.querySelector('form [role=status]').textContent));
  assert.equal(f.intakeRequests.length,1);
  assert.equal((await f.events()).filter(e=>e[1]==='Lead').length,0);
  assert.equal(await f.page.locator('form .form-fields').isVisible(),response!=='duplicate');await close(f);
 }
});
test('both form kinds reject incomplete, mismatched and legacy acknowledgement contracts without tracking',async()=>{
 for(const kind of ['audit','mockup'])for(const response of ['wrong-kind','missing-kind','missing-id','invalid-id','wrong-status','missing-duplicate','invalid-duplicate','legacy']){
  const f=await fixture({realForm:kind,response});await allow(f);await loaded(f);
  await f.page.locator('form [type=submit]').click();
  await f.page.waitForFunction(()=>!/Sending|^$/.test(document.querySelector('form [role=status]').textContent));
  assert.equal(f.intakeRequests.length,1);
  assert.equal((await f.events()).filter(e=>e[1]==='Lead').length,0);
  assert.equal(await f.page.locator('form .form-fields').isVisible(),true);
  assert.equal(await f.page.locator('form [type=submit]').isDisabled(),true);await close(f);
 }
});
test('absent controls and disabled JavaScript cannot load tracking',async()=>{
 for(const options of [{noControls:true},{javaScriptEnabled:false}]){
  const f=await fixture(options);assert.equal(f.sdkRequests(),0);assert.deepEqual(await f.events(),[]);await close(f);
 }
});
test('privacy copy is current, distinguishes wrapper and providers, and contains no configured GA4',async()=>{
 const {execFileSync}=await import('node:child_process');
 const copy=execFileSync('python3',['-B','-c','from privacy_policy import privacy_content; print(privacy_content())'],{cwd:new URL('../tools/',import.meta.url),encoding:'utf8'});
 assert.match(copy,/Last updated November 5, 2026/);assert.match(copy,/Google Analytics is not currently configured/);
 assert.match(copy,/short-lived keyed identifiers/);assert.match(copy,/not every operation of Meta/);
 assert.match(copy,/Growth audit and homepage design forms send requests to our website's intake service/);
 assert.doesNotMatch(copy,/FormSubmit/i);
 assert.doesNotMatch(copy,/We only collect|process information only|reply STOP|we do not share/i);
 assert.doesNotMatch(script,/googletagmanager|gtag\(|G-[A-Z0-9]+/);
});
