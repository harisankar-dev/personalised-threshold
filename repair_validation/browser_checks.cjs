// Targeted real-Chrome checks for the English OCR and privacy repair.
const fs = require('fs');
const path = require('path');
const { chromium } = require(process.env.PLAYWRIGHT_MODULE ||
  'C:/Users/imhar/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');

const root = path.resolve(__dirname, '..');
const records = [];

async function main() {
  const browser = await chromium.launch({executablePath: process.env.CHROME_EXE ||
    'C:/Program Files/Google/Chrome/Application/chrome.exe', headless: true});
  const page = await browser.newPage({viewport: {width: 1280, height: 900}});
  const assert = (condition, message) => { if (!condition) throw new Error(message); };
  const run = async (name, options, check) => {
    await page.goto('http://127.0.0.1:8765/');
    if (options.image) {
      await page.locator('#image-tab').click();
      await page.locator('#image-file').setInputFiles(options.image);
    } else {
      await page.locator('#ad-text').fill(options.text || 'Explore our collection.');
    }
    const economics = ['revision-cost', 'targeting-cost', 'variant-cost', 'segmentation-cost',
      'management-cost', 'variant-count', 'contribution-margin', 'audience-reach', 'cpc', 'cpm',
      'conversion-rate-pct'];
    if (Object.keys(options.fields || {}).some(id => economics.includes(id)))
      await page.locator('#economics-details summary').click();
    for (const [id, value] of Object.entries(options.fields || {})) {
      const field = page.locator('#' + id);
      if (await field.evaluate(node => node.tagName) === 'SELECT') await field.selectOption(String(value));
      else await field.fill(String(value));
    }
    const responsePromise = page.waitForResponse(response => response.url().endsWith('/api/analyze'));
    await page.locator('#analyze-btn').click();
    const response = await responsePromise;
    const data = await response.json();
    await page.locator('#result-content').waitFor({state: 'visible'});
    check(data);
    records.push({name, status: response.status(), tier: data.tier, score: data.score_out_of_10,
      cues: (data.evidence || []).map(row => row.cue), action: data.strategy?.action,
      ocr_excerpt: data.ocr_text ? data.ocr_text.slice(0, 260) : null, warning: data.ocr_warning});
    console.log('PASS', name, data.tier, data.score_out_of_10, data.strategy?.action);
  };
  try {
    const hier = path.join(root, 'phase14_validation/local_source/hiertext_gate/candidate_extract/validation');
    await run('01 real English print ad extraction', {image: path.join(hier, '4976c8479dc54b42.jpg')},
      data => assert(data.ocr_text && data.ocr_text.includes('Inner Ford'), 'verified headline missing'));
    await run('02 real promotional deadline success', {image: path.join(root, 'phase14_validation/local_source/altair.jpg')},
      data => assert(data.ocr_text.includes('limited time only') && data.evidence.some(row => row.cue === 'urgent_call_to_action'), 'deadline missed'));
    await run('03 difficult retail deadline remains review', {image: path.join(hier, 'd19b4b14a1d1e02b.jpg')},
      data => assert(data.tier === 'needs_review' && !data.evidence.some(row => row.cue === 'urgent_call_to_action'), 'known OCR miss not represented honestly'));
    await run('04 viewer location claim', {text: 'We know where you live. Time starts now.'},
      data => assert(data.tier === 'high_intrusive' && data.evidence.some(row => row.cue === 'precise_location'), 'location claim missed'));
    await run('05 tracked activity claim', {text: "We've tracked your activity across our site."},
      data => assert(data.evidence.some(row => row.cue === 'explicit_surveillance'), 'activity claim missed'));
    await run('06 seller email image', {image: path.join(root, 'phase13_validation/local_source/ad_538.jpg')},
      data => assert(!data.evidence.some(row => row.cue === 'direct_identifier'), 'seller email became viewer identity'));
    await run('07 ordinary registration field', {text: 'Enter your phone number to register.'},
      data => assert(!data.evidence.some(row => row.cue === 'direct_identifier'), 'ordinary form falsely flagged'));
    await run('08 unreadable image abstention', {image: path.join(root, 'phase13_validation/local_source/synthetic_blank.png')},
      data => assert(data.tier === 'needs_review' && data.score === null, 'unreadable image did not abstain'));
    await run('09 unknown permission hold', {text: 'Explore our collection.', fields: {
      'targeting-method': 'behavioral', 'data-source': 'first_party_behavior', 'consent-status': 'unknown'}},
      data => assert(data.strategy.action === 'hold_for_review', 'unknown permission was not held'));
    await run('10 affordable revision arithmetic', {text: 'Last chance to buy.', fields: {
      'total-budget': '100', 'committed-spend': '80', 'revision-cost': '10'}},
      data => assert(data.strategy.action === 'revise_one_creative' && data.strategy.available_budget_headroom === '20.00', 'budget action/headroom incorrect'));
  } finally {
    await browser.close();
    const output = path.join(__dirname, 'local_results');
    fs.mkdirSync(output, {recursive: true});
    fs.writeFileSync(path.join(output, 'browser_results.json'), JSON.stringify(records, null, 2));
  }
}

main().catch(error => { console.error(error.stack); process.exitCode = 1; });
