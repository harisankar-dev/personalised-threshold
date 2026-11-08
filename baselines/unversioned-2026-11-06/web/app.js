const $ = (id) => document.getElementById(id);
const textTab = $('text-tab');
const imageTab = $('image-tab');
const textPanel = $('text-panel');
const imagePanel = $('image-panel');
const textInput = $('ad-text');
const fileInput = $('image-file');
const dropZone = $('drop-zone');
const errorBox = $('form-error');
let mode = 'text';
let selectedFile = null;
let previewUrl = null;

const examples = {
  generic: 'Discover our new fall collection. Shop now and save 20%.',
  cart: 'Your cart is waiting. Complete your purchase today.',
  combined: 'Based on your recent running-shoe searches, previous footwear purchases and location in Goa, we selected these styles for you.'
};
const cueNames = {
  direct_identifier: 'Direct personal identifier',
  observed_behavior: 'Observed browsing or search',
  sensitive_personal_fact: 'Sensitive personal fact',
  precise_location: 'Precise location reference',
  purchase_or_cart: 'Purchase or cart reference',
  purchase_history: 'Purchase or cart history',
  browsing_history: 'Browsing or search history',
  approximate_location: 'Approximate location',
  explicit_surveillance: 'Explicit tracking language',
  combined_signals: 'Combined personal signals',
  specific_activity_detail: 'Specific activity detail',
  no_consent: 'No consent indicated',
  stated_interest_targeting: 'Personal interest reference',
  personalized_claim: 'Personalization claim',
  sensitive_targeting: 'Sensitive targeting data',
  behavioral_targeting: 'Behavioral targeting',
  precise_location_targeting: 'Precise location targeting',
  broad_targeting: 'Broad targeting',
  countdown_pressure: 'Countdown pressure',
  scarcity_claim: 'Scarcity claim',
  extreme_discount: 'Extreme discount claim',
  urgent_call_to_action: 'Urgent call to action',
  alarmist_claim: 'Alarmist claim',
  excessive_exclamation: 'Repeated exclamation marks'
};

function setMode(next) {
  mode = next;
  const isText = next === 'text';
  textTab.classList.toggle('active', isText);
  imageTab.classList.toggle('active', !isText);
  textTab.setAttribute('aria-selected', String(isText));
  imageTab.setAttribute('aria-selected', String(!isText));
  textPanel.hidden = !isText;
  imagePanel.hidden = isText;
  hideError();
  setResultState('empty');
}
textTab.addEventListener('click', () => setMode('text'));
imageTab.addEventListener('click', () => setMode('image'));
[textTab, imageTab].forEach((tab) => tab.addEventListener('keydown', (event) => {
  if (event.key !== 'ArrowLeft' && event.key !== 'ArrowRight') return;
  event.preventDefault();
  const target = tab === textTab ? imageTab : textTab;
  target.click(); target.focus();
}));

textInput.addEventListener('input', () => {
  $('char-count').textContent = `${textInput.value.length.toLocaleString()} characters`;
  hideError();
  setResultState('empty');
});
document.querySelectorAll('.example-chip').forEach((button) => button.addEventListener('click', () => {
  setMode('text');
  textInput.value = examples[button.dataset.example];
  textInput.dispatchEvent(new Event('input'));
  textInput.focus();
}));

function hideError() { errorBox.hidden = true; errorBox.textContent = ''; }
function showError(message) { errorBox.textContent = message; errorBox.hidden = false; }

function removeFile() {
  selectedFile = null;
  fileInput.value = '';
  if (previewUrl) URL.revokeObjectURL(previewUrl);
  previewUrl = null;
  $('preview-img').removeAttribute('src');
  $('image-preview').hidden = true;
  $('drop-content').hidden = false;
  hideError();
  setResultState('empty');
}
function setFile(file) {
  if (!file) return;
  const allowed = ['image/png', 'image/jpeg', 'image/webp', 'image/bmp', 'image/tiff'];
  if (!allowed.includes(file.type)) { showError('Choose a PNG, JPG, WebP, BMP, or TIFF image.'); return; }
  if (file.size > 10 * 1024 * 1024) { showError('Choose an image under 10 MB.'); return; }
  removeFile();
  selectedFile = file;
  previewUrl = URL.createObjectURL(file);
  $('preview-img').src = previewUrl;
  $('file-name').textContent = file.name;
  $('file-size').textContent = `${(file.size / (1024 * 1024)).toFixed(2)} MB`;
  $('drop-content').hidden = true;
  $('image-preview').hidden = false;
}
fileInput.addEventListener('change', () => setFile(fileInput.files[0]));
$('remove-image').addEventListener('click', (event) => { event.preventDefault(); event.stopPropagation(); removeFile(); });
['dragenter', 'dragover'].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
  event.preventDefault(); dropZone.classList.add('dragover');
}));
['dragleave', 'drop'].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
  event.preventDefault(); dropZone.classList.remove('dragover');
}));
dropZone.addEventListener('drop', (event) => setFile(event.dataTransfer.files[0]));
$('targeting').addEventListener('input', () => setResultState('empty'));
$('visual-description').addEventListener('input', () => setResultState('empty'));

function readDataUrl(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result);
    reader.onerror = () => reject(new Error('Could not read this image. Choose another file.'));
    reader.readAsDataURL(file);
  });
}
function setResultState(state) {
  $('result-empty').hidden = state !== 'empty';
  $('result-loading').hidden = state !== 'loading';
  $('result-content').hidden = state !== 'content';
}
function renderResult(data) {
  const tier = data.tier || 'needs_review';
  const style = tier.startsWith('low') ? 'low' : tier.startsWith('moderate') ? 'moderate' : tier.startsWith('high') ? 'high' : 'review';
  const tierText = {low: 'Low ad intrusiveness risk', moderate: 'Moderate ad intrusiveness risk', high: 'High ad intrusiveness risk', review: 'Needs review'}[style];
  $('tier-pill').textContent = tierText;
  $('tier-pill').className = `tier-pill ${style}`;
  $('score-number').textContent = data.score_out_of_10 ?? '—';
  $('score-context').textContent = data.score_out_of_10 === null ? 'No score available' : 'Content risk score';
  $('score-breakdown').hidden = data.score_out_of_10 === null;
  $('privacy-score').textContent = data.privacy_score ?? '—';
  $('pressure-score').textContent = data.pressure_score ?? '—';
  const scale = $('score-scale');
  scale.className = `score-scale ${style}`;
  scale.replaceChildren();
  for (let i = 0; i < 10; i++) {
    const block = document.createElement('span');
    if (i < (data.score_out_of_10 || 0)) block.className = 'active';
    scale.append(block);
  }
  scale.setAttribute('aria-label', data.score_out_of_10 === null ? 'No score available' : `Intrusion risk score ${data.score_out_of_10} out of 10`);
  const list = $('evidence-list');
  list.replaceChildren();
  const cues = data.evidence || [];
  $('evidence-count').textContent = `${cues.length} cue${cues.length === 1 ? '' : 's'} found`;
  if (!cues.length) {
    const item = document.createElement('p');
    item.className = 'no-evidence';
    item.textContent = tier === 'needs_review' ? 'Add readable ad copy or a description to assess this creative.' : 'No privacy or pressure cues matched the current rubric.';
    list.append(item);
  } else {
    cues.forEach((cue) => {
      const row = document.createElement('div'); row.className = 'evidence-item';
      const detail = document.createElement('div');
      const name = document.createElement('strong'); name.textContent = cueNames[cue.cue] || cue.cue;
      const phrase = document.createElement('small'); phrase.textContent = cue.source === 'derived'
        ? 'Based on the separate personal-data cues above'
        : `Matched “${cue.matched}” in ${cue.source === 'targeting' ? 'targeting details' : 'ad copy'}`;
      const weight = document.createElement('span'); weight.textContent = `+${cue.weight}`;
      detail.append(name, phrase); row.append(detail, weight); list.append(row);
    });
  }
  const repairs = data.recommendations || [];
  $('repair-section').hidden = repairs.length === 0;
  const repairList = $('repair-list');
  repairList.replaceChildren();
  repairs.forEach((repair) => {
    const item = document.createElement('li');
    item.textContent = repair.action;
    repairList.append(item);
  });
  $('ocr-details').hidden = data.ocr_text === null;
  $('ocr-text').textContent = data.ocr_text || 'No readable text was found.';
  $('result-note').textContent = data.reason || 'Rubric score only. Not a measured consumer reaction.';
  setResultState('content');
  if (window.matchMedia('(max-width: 850px)').matches) $('result-title').scrollIntoView({behavior: 'smooth', block: 'start'});
}

$('clear-btn').addEventListener('click', () => {
  textInput.value = ''; textInput.dispatchEvent(new Event('input'));
  $('targeting').value = ''; $('visual-description').value = '';
  removeFile(); setResultState('empty'); setMode('text'); textInput.focus();
});

$('ad-form').addEventListener('submit', async (event) => {
  event.preventDefault(); hideError();
  const copy = mode === 'text' ? textInput.value.trim() : '';
  const visual = mode === 'image' ? $('visual-description').value.trim() : '';
  if (mode === 'text' && !copy) { showError('Paste ad copy to analyze.'); textInput.focus(); return; }
  if (mode === 'image' && !selectedFile && !visual) { showError('Choose an image or add a visual description.'); fileInput.focus(); return; }
  const button = $('analyze-btn'); button.disabled = true;
  $('button-text').textContent = 'Analyzing…'; setResultState('loading');
  try {
    const imageData = mode === 'image' && selectedFile ? await readDataUrl(selectedFile) : null;
    const response = await fetch('/api/analyze', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text: copy, image_data: imageData, targeting: $('targeting').value.trim(), visual_description: visual})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The ad could not be analyzed.');
    renderResult(data);
  } catch (error) {
    setResultState('empty'); showError(error.message || 'The ad could not be analyzed. Try again.');
  } finally {
    button.disabled = false; $('button-text').textContent = 'Analyze ad';
  }
});
