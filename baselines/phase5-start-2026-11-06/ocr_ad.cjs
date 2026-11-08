// Extract English text from an ad image with local Tesseract.js language data.
const path = require('path');
const fs = require('fs');
const { createRequire } = require('module');

async function main() {
  const image = process.argv[2];
  if (!image || !fs.existsSync(image)) throw new Error('Image file not found');
  const langPath = path.join(__dirname, 'models');
  if (!fs.existsSync(path.join(langPath, 'eng.traineddata'))) {
    throw new Error('Missing models/eng.traineddata. See MODEL_README.md.');
  }
  let Tess;
  try { Tess = require('tesseract.js'); }
  catch (_) {
    const bundled = path.join(process.env.USERPROFILE || '', '.cache', 'codex-runtimes',
      'codex-primary-runtime', 'dependencies', 'node', 'node_modules', 'tesseract.js');
    Tess = createRequire(path.join(bundled, 'package.json'))(bundled);
  }
  const worker = await Tess.createWorker('eng', 1, {langPath, gzip: false, cacheMethod: 'none'});
  try {
    const { data } = await worker.recognize(image);
    process.stdout.write(JSON.stringify({text: (data.text || '').trim(), confidence: data.confidence || 0}));
  } finally { await worker.terminate(); }
}

main().catch(e => { console.error(e.message); process.exit(1); });
