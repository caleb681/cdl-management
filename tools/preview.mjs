import {createServer} from 'node:http';
import {readFile,stat} from 'node:fs/promises';
import {resolve,extname,sep} from 'node:path';
const root=resolve(import.meta.dirname,'..');
const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript; charset=utf-8','.svg':'image/svg+xml','.webp':'image/webp','.jpg':'image/jpeg','.xml':'application/xml','.txt':'text/plain'};
const server=createServer(async(req,res)=>{
  // Only a loopback test may disable this header to audit production indexability.
  if(process.env.LOCAL_INDEXABILITY_AUDIT!=='1')res.setHeader('X-Robots-Tag','noindex, nofollow');
  res.setHeader('Cache-Control','no-store');
  // Local review cannot transmit leads, execute the Meta Pixel, or submit an HTML form.
  // Automated browsers bypass this local-only policy and intercept every provider request.
  res.setHeader('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; form-action 'none'; base-uri 'none'; frame-ancestors 'none'");
  let path;
  try{path=decodeURIComponent(new URL(req.url,'http://localhost').pathname);}
  catch{res.writeHead(400,{'Content-Type':'text/plain; charset=utf-8'});res.end('Invalid address');return;}
  if(path.startsWith('/api/') || path.startsWith('/source/') || path.startsWith('/tools/') || path.startsWith('/tests/') || path.includes('/.')){res.writeHead(404);res.end('Unavailable in local preview');return;}
  if(req.method!=='GET'&&req.method!=='HEAD'){res.writeHead(405);res.end();return;}
  try{
    let file=resolve(root,'.'+path);
    if(!file.startsWith(root+sep)&&file!==root)throw Error();
    const info=await stat(file);
    if(info.isDirectory())file=resolve(file,'index.html');
    const data=await readFile(file);res.writeHead(200,{'Content-Type':types[extname(file)]||'application/octet-stream'});res.end(req.method==='HEAD'?null:data);
  }catch{res.writeHead(404,{'Content-Type':'text/html; charset=utf-8','X-Robots-Tag':'noindex'});res.end(await readFile(resolve(root,'404.html')));}
});
server.listen(Number(process.env.PORT||8796),'127.0.0.1',()=>console.log('CDL local preview: http://127.0.0.1:'+server.address().port));
