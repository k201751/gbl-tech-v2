const {chromium}=require('playwright');
(async()=>{
 const b=await chromium.launch({headless:true,executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 const p=await b.newPage({viewport:{width:1440,height:1000}});
 await p.goto('http://127.0.0.1:4175/?inspect=projects',{waitUntil:'domcontentloaded',timeout:30000});
 await p.locator('#work').scrollIntoViewIfNeeded();
 await p.waitForTimeout(1000);
 await p.screenshot({path:'D:/Dev-Projects/gbl-tech-v2/work/projects-before.jpg'});
 const info=await p.locator('#work').evaluate(e=>({bg:getComputedStyle(e).backgroundColor,top:e.getBoundingClientRect().top,height:e.getBoundingClientRect().height}));
 console.log(JSON.stringify(info));
 await b.close();
})();
