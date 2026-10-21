const fs=require('fs');
exports.listings=(route,html)=>{
if(route==='web-development'){
const directory=html.match(/<section class="service-directory"[^>]*>([\s\S]*?)<\/section>/);
if(directory){const links=[...directory[1].matchAll(/<a [\s\S]*?<\/a>/g)].map(m=>m[0]);let offset=0;const groups=[['Core services',8,'The foundations of a considered digital presence.'],['Technology / stack',7,'A platform chosen around your requirements and your team.'],['Website types',6,'Experiences shaped around the way your business works.'],['Support &amp; maintenance',5,'Keep your website ready for its next chapter.']];html=html.replace(directory[0],groups.map(([name,count,description])=>{const items=links.slice(offset,offset+=count).join('');return `<section class="service-category"><div class="category-heading"><p class="page-eyebrow">${count} services</p><h2>${name}</h2><p>${description}</p></div><div class="service-directory">${items}</div></section>`;}).join(''));}
}
if(route==='case-studies'&&!html.includes('portfolio-description')){const summaries=['Chef Silvia wanted a visually engaging website to showcase her cookbook, custom illustrations, and culinary expertise.','Jennifer Wells, founder of Pawzody, wanted a modern and trustworthy website that would reflect her brand professionally and make it easier for customers to discover services, view previous work, and submit inquiries.','Louise De Silva approached us to revamp her existing website with a modern, elegant, and user-focused design.'];let i=0;html=html.replace(/(<h2>[^<]+ <span>↗<\/span><\/h2>)(<\/a>)/g,(_,h,end)=>h+`<p class="portfolio-description">${summaries[i++]}</p>`+end);}
return html;
};
