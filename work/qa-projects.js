const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 for(const c of [{n:'desktop',w:1440,h:1000},{n:'mobile',w:390,h:844}]){
  const p=await b.newPage({viewport:{width:c.w,height:c.h}});
  await p.goto('http://127.0.0.1:4175/?qa=gallery-'+Date.now(),{waitUntil:'domcontentloaded',timeout:30000});
  await p.locator('#work').scrollIntoViewIfNeeded(); await p.waitForTimeout(800);
  await p.locator('#work').screenshot({path:`D:/Dev-Projects/gbl-tech-v2/work/projects-${c.n}-after.jpg`});
  const cards=await p.locator('.project').evaluateAll(es=>es.map(e=>{const r=e.getBoundingClientRect();return {x:r.x,y:r.y,w:r.width,h:r.height}}));
  console.log(c.n,JSON.stringify(cards)); await p.close();
 }
 await b.close();
})();
