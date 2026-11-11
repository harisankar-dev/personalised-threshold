// Real Chrome form and image-upload checks. Source JPGs stay in ignored local_source/.
const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE ||
  'C:/Users/imhar/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const root = path.resolve(__dirname, '..');
const source = path.join(__dirname, 'local_source');
const records = [];

async function main() {
  const browser = await chromium.launch({executablePath: process.env.CHROME_EXE ||
    'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true});
  try {
    const page = await browser.newPage({viewport: {width: 1280, height: 900}});
    const run = async (name, options = {}, check = () => {}) => {
      await page.goto('http://127.0.0.1:8765/');
      if (options.viewport) await page.setViewportSize(options.viewport);
      if (options.image) {
        await page.locator('#image-tab').click();
        await page.locator('#image-file').setInputFiles(path.join(source, options.image));
      } else {
        await page.locator('#ad-text').fill(options.text || 'Explore our collection.');
      }
      const economics = ['revision-cost','targeting-cost','variant-cost','segmentation-cost','management-cost',
        'variant-count','contribution-margin','audience-reach','cpc','cpm','conversion-rate-pct'];
      if (Object.keys(options.fields || {}).some(key => economics.includes(key)))
        await page.locator('#economics-details summary').click();
      if (Object.keys(options.fields || {}).some(key => ['scenario-option','worst-conversions','central-conversions','best-conversions'].includes(key)))
        await page.locator('#scenario-details summary').click();
      for (const [id, value] of Object.entries(options.fields || {})) {
        const field = page.locator('#' + id);
        if (await field.evaluate(node => node.tagName) === 'SELECT') await field.selectOption(String(value));
        else await field.fill(String(value));
      }
      const responsePromise = page.waitForResponse(r => r.url().endsWith('/api/analyze'));
      await page.locator('#analyze-btn').click();
      const response = await responsePromise;
      const data = await response.json();
      await page.locator('#result-content').waitFor({state:'visible'});
      const ui = {tier: await page.locator('#tier-pill').innerText(), score: await page.locator('#score-number').innerText(),
        note: await page.locator('#result-note').innerText(), ocr: await page.locator('#ocr-text').innerText(),
        strategy: await page.locator('#strategy-action').innerText(),
        horizontalOverflow: await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)};
      check(data, ui);
      records.push({name, pass:true, status:response.status(), tier:data.tier, score:data.score_out_of_10,
        cues:(data.evidence || []).map(x=>x.cue), strategy:data.strategy?.action,
        ocr_text:data.ocr_text ? data.ocr_text.slice(0,280) : null,
        ocr_warning:data.ocr_warning, note:ui.note, horizontalOverflow:ui.horizontalOverflow});
      console.log('PASS', name, data.tier, data.score_out_of_10, data.strategy?.action);
    };
    const assert = (ok, message) => { if (!ok) throw new Error(message); };
    await run('01 clear English ad image', {image:'ad_516.jpg'}, (d,u)=>assert(d.ocr_text.includes('GOOD CRUNCH'), 'clear headline missing'));
    await run('02 limited-time offer image', {image:'synthetic_deadline.png'}, (d,u)=>assert(d.evidence.some(x=>x.cue==='urgent_call_to_action'), 'deadline cue missing'));
    await run('03 small English print', {image:'ad_517.jpg'}, (d,u)=>assert(d.tier==='needs_review', 'small print was falsely reassured'));
    await run('04 text over photograph', {image:'ad_500.jpg'}, (d,u)=>assert(d.ocr_text && d.ocr_text.includes('Curl'), 'photo headline absent'));
    await run('05 angled headline', {image:'ad_510.jpg'}, (d,u)=>assert(d.ocr_text && d.ocr_text.includes('BUY'), 'angled promotion absent'));
    await run('06 seller phone image', {image:'ad_389.jpg'}, (d,u)=>assert(!d.evidence.some(x=>x.cue==='direct_identifier'), 'seller phone false alarm'));
    await run('07 seller email image', {image:'ad_538.jpg'}, (d,u)=>assert(!d.evidence.some(x=>x.cue==='direct_identifier'), 'seller email false alarm'));
    await run('08 viewer identity claim', {text:'We know your phone number.'}, (d,u)=>assert(d.evidence.some(x=>x.cue==='direct_identifier'), 'viewer claim missed'));
    await run('09 negated urgency', {text:"We don't use limited-time offers."}, (d,u)=>assert(!d.evidence.some(x=>x.cue==='urgent_call_to_action'), 'negation false alarm'));
    await run('10 ordinary generic ad', {text:'Explore our collection.'}, (d,u)=>assert(d.tier==='low_intrusive', 'generic ad tier'));
    await run('11 OCR-empty image', {image:'synthetic_blank.png'}, (d,u)=>assert(d.tier==='needs_review' && d.score===null, 'empty image not abstained'));
    await run('12 poor-quality image', {image:'synthetic_poor.png'}, (d,u)=>assert(d.tier==='needs_review' || !!d.ocr_warning, 'poor quality not warned'));
    await run('13 mixed-language image', {image:'ad_483.jpg'}, (d,u)=>assert(d.ocr_warning || d.tier==='needs_review', 'mixed language lacks caveat'));
    await run('14 unknown targeting source', {fields:{'targeting-method':'behavioral','data-source':'unknown'}},
      (d,u)=>assert(d.strategy.action==='hold_for_review', 'unknown source not held'));
    await run('15 unverified consent', {fields:{'targeting-method':'behavioral','data-source':'first_party_behavior','consent-status':'unknown'}},
      (d,u)=>assert(d.strategy.action==='hold_for_review', 'unverified permission not held'));
    await run('16 affordable revision', {text:'Last chance to buy.',fields:{'total-budget':'100','committed-spend':'80','revision-cost':'10'}},
      (d,u)=>assert(d.strategy.action==='revise_one_creative', 'affordable revision absent'));
    await run('17 unaffordable revision', {text:'Last chance to buy.',fields:{'total-budget':'100','committed-spend':'95','revision-cost':'10'}},
      (d,u)=>assert(d.strategy.action==='hold_for_review', 'unaffordable revision not held'));
    await page.goto('http://127.0.0.1:8765/');
    await page.locator('#ad-text').fill('Last chance to buy.');
    await page.locator('#total-budget').fill('100');
    await page.locator('#committed-spend').fill('120');
    let invalidResponse = page.waitForResponse(r => r.url().endsWith('/api/analyze'));
    await page.locator('#analyze-btn').click();
    let invalid = await invalidResponse;
    await page.locator('#form-error').waitFor({state:'visible'});
    assert(invalid.status()===400, 'invalid budget not rejected');
    await page.locator('#committed-spend').fill('80');
    let recoveredResponse = page.waitForResponse(r => r.url().endsWith('/api/analyze'));
    await page.locator('#analyze-btn').click();
    let recovered = await recoveredResponse;
    await page.locator('#result-content').waitFor({state:'visible'});
    assert(recovered.status()===200, 'budget recovery failed');
    records.push({name:'18 budget validation and recovery',pass:true,invalid_status:invalid.status(),recovered_status:recovered.status()});
    console.log('PASS 18 budget validation and recovery');
    await run('19 positive hypothetical scenario', {fields:{'variant-cost':'10','contribution-margin':'20','central-conversions':'2'}},
      (d,u)=>assert(d.strategy.scenario.results.central.user_entered_incremental_conversions===2, 'scenario lost'));
    await run('20 mobile 390px', {viewport:{width:390,height:844}},
      (d,u)=>assert(!u.horizontalOverflow && d.threshold_decision.status==='insufficient_evidence', 'mobile overflow or threshold'));
    await run('21 generic phone-entry instruction', {text:'Enter your phone number to sign up.'},
      (d,u)=>assert(!d.evidence.some(x=>x.cue==='direct_identifier'), 'generic instruction false alarm'));
  } finally {
    await browser.close();
    fs.writeFileSync(path.join(__dirname,'browser_results_v1.json'), JSON.stringify(records,null,2));
  }
}
main().catch(e=>{console.error(e.stack);process.exitCode=1});
