const { chromium } = require('playwright');
(async()=>{
 const browser=await chromium.launch({headless:true, executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
 for (const [name,w,h] of [['desktop',1440,1000],['mobile',390,844]]) {
   const page=await browser.newPage({viewport:{width:w,height:h}});
   await page.goto('http://127.0.0.1:4175/',{waitUntil:'networkidle'});
   await page.locator('#consequence').scrollIntoViewIfNeeded();
   await page.waitForTimeout(1100);
   await page.screenshot({path:`work/consequence-${name}.png`,fullPage:false});
   const data=await page.locator('#consequence').evaluate(el=>({box:el.getBoundingClientRect().toJSON(),text:el.innerText,bg:getComputedStyle(el).backgroundColor}));
   console.log(name,JSON.stringify(data));
 }
 await browser.close();
})();
