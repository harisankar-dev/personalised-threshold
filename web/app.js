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
  removeFile();
  const allowed = ['image/png', 'image/jpeg', 'image/webp', 'image/bmp', 'image/tiff'];
  if (!allowed.includes(file.type)) { showError('Choose a PNG, JPG, WebP, BMP, or TIFF image.'); return; }
  if (!file.size || file.size > 10 * 1024 * 1024) { showError('Choose a non-empty image under 10 MB.'); return; }
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
const campaignFields = {
  currency: 'currency', objective: 'objective', targeting_method: 'targeting-method',
  product_category: 'product-category', channel: 'channel', data_source: 'data-source',
  consent_status: 'consent-status', audience_eligibility: 'audience-eligibility',
  total_budget: 'total-budget', committed_spend: 'committed-spend',
  revision_cost: 'revision-cost', targeting_cost: 'targeting-cost',
  variant_cost: 'variant-cost', segmentation_cost: 'segmentation-cost',
  management_cost: 'management-cost', variant_count: 'variant-count',
  contribution_margin: 'contribution-margin', audience_reach: 'audience-reach',
  cpc: 'cpc', cpm: 'cpm', conversion_rate_pct: 'conversion-rate-pct',
  scenario_option: 'scenario-option',
  worst_incremental_conversions: 'worst-conversions',
  central_incremental_conversions: 'central-conversions',
  best_incremental_conversions: 'best-conversions'
};
Object.values(campaignFields).forEach((id) => $(id).addEventListener('input', () => setResultState('empty')));
function campaignInput() {
  return Object.fromEntries(Object.entries(campaignFields).map(([key, id]) => [key, $(id).value.trim()]));
}

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
  $('ad-form').setAttribute('aria-busy', String(state === 'loading'));
}
function displayMoney(value, currency) {
  if (value === null || value === undefined) return 'Unknown';
  return `${currency} ${Number(value).toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;
}
function renderCompatibility(assessment) {
  const section = $('compatibility-result');
  section.hidden = !assessment;
  if (!assessment) return;
  $('compatibility-summary').textContent = assessment.data_source_review_required
    ? 'Review the declared targeting method, data source and permission before launch. Consumer response is unknown.'
    : 'The creative and campaign declarations can be reviewed; consumer response to this ad is unknown.';
  const list = $('compatibility-checks'); list.replaceChildren();
  [...(assessment.creative_signals || []), ...(assessment.prelaunch_checks || [])].forEach((message) => {
    const li = document.createElement('li'); li.textContent = message; list.append(li);
  });
  $('compatibility-next-test').textContent = assessment.next_test || '';
}
function renderStrategy(strategy) {
  const section = $('strategy-result');
  section.hidden = !strategy;
  if (!strategy) return;
  const actionNames = {
    keep_current_campaign: 'Keep the current campaign',
    revise_one_creative: 'Revise one creative in this campaign',
    hold_for_review: 'Hold for review before launch'
  };
  $('strategy-action').textContent = actionNames[strategy.action] || strategy.action;
  $('strategy-reason').textContent = strategy.reason;
  $('strategy-budget').textContent = strategy.available_budget_headroom === null
    ? 'Available budget headroom: unknown. Enter both total budget and already committed spend to check affordability.'
    : `Available headroom within the total budget: ${displayMoney(strategy.available_budget_headroom, strategy.currency)}.`;
  const reported = strategy.baseline_metrics_user_entered || {};
  const context = [
    ['Existing CPC', 'cpc', true], ['Existing CPM', 'cpm', true],
    ['Existing conversion rate', 'conversion_rate_pct', false],
    ['Eligible reach', 'audience_reach', false],
    ['Contribution margin', 'contribution_margin', true]
  ].filter(([, key]) => reported[key] !== null && reported[key] !== undefined)
    .map(([label, key, money]) => `${label}: ${money ? displayMoney(reported[key], strategy.currency) : key === 'conversion_rate_pct' ? reported[key] + '%' : Number(reported[key]).toLocaleString()}`);
  $('baseline-context').hidden = context.length === 0;
  $('baseline-context').textContent = context.length ? `${context.join(' · ')}. Reported context only; no uplift is predicted.` : '';
  const rows = $('strategy-options'); rows.replaceChildren();
  (strategy.options || []).forEach((option) => {
    const tr = document.createElement('tr');
    const cells = [option.name, displayMoney(option.incremental_implementation_cost, strategy.currency),
      option.budget_feasible === null ? 'Unknown' : option.budget_feasible ? 'Within budget' : 'Over budget',
      option.permission_status || 'Unverified',
      option.break_even_incremental_conversions === null ? 'Unknown' : String(option.break_even_incremental_conversions)];
    cells.forEach((value) => { const td = document.createElement('td'); td.textContent = value; tr.append(td); });
    rows.append(tr);
  });
  const scenario = strategy.scenario;
  const hasScenario = scenario && Object.values(scenario.results || {}).some((item) => item.user_entered_incremental_conversions !== null);
  $('scenario-result').hidden = !hasScenario;
  if (hasScenario) {
    const selected = strategy.options.find((option) => option.key === scenario.option);
    $('scenario-label').textContent = `${selected?.name || scenario.option} · hypothetical user-entered outcomes`;
    const box = $('scenario-values'); box.replaceChildren();
    ['worst', 'central', 'best'].forEach((label) => {
      const item = scenario.results[label];
      const row = document.createElement('div');
      const title = document.createElement('strong'); title.textContent = label[0].toUpperCase() + label.slice(1);
      const count = item.user_entered_incremental_conversions;
      const value = document.createElement('span'); value.textContent = count === null
        ? 'Not entered' : `${count} extra ${count === 1 ? 'conversion' : 'conversions'} · net ${displayMoney(item.net_incremental_value, strategy.currency)}`;
      row.append(title, value); box.append(row);
    });
  }
  const personas = $('persona-list'); personas.replaceChildren();
  const sources = strategy.survey_personas?.sources || {};
  Object.entries(sources).forEach(([name, source]) => {
    const heading = document.createElement('h4');
    heading.textContent = `${name === 'genz' ? 'Gen Z personalized-ad survey' : 'Romano–Han unsolicited-ad survey'} · ${source.respondents} responses`;
    personas.append(heading);
    const list = document.createElement('ul');
    Object.entries(source.counts).forEach(([key, count]) => {
      const item = document.createElement('li');
      const valueLabel = name === 'genz' ? 'relevance' : 'perceived benefits';
      const profileLabel = `${key.startsWith('higher_value') ? 'Higher' : 'Lower'} ${valueLabel}, ${key.endsWith('higher_concern') ? 'higher' : 'lower'} concern`;
      item.textContent = `${profileLabel}: ${count} responses (${(count / source.respondents * 100).toFixed(1)}%)`;
      list.append(item);
    });
    personas.append(list);
  });
  const warnings = $('strategy-warnings'); warnings.replaceChildren();
  const notes = [...(strategy.warnings || [])];
  if (strategy.missing_inputs?.length) notes.push(`Not entered: ${strategy.missing_inputs.map((x) => x.replaceAll('_', ' ')).join(', ')}.`);
  notes.forEach((note) => { const li = document.createElement('li'); li.textContent = note; warnings.append(li); });
}
function renderResult(data) {
  const tier = data.tier || 'needs_review';
  const style = tier.startsWith('low') ? 'low' : tier.startsWith('moderate') ? 'moderate' : tier.startsWith('high') ? 'high' : 'review';
  const tierText = {low: 'Low screening tier', moderate: 'Moderate screening tier', high: 'High screening tier', review: 'Needs review'}[style];
  $('tier-pill').textContent = tierText;
  $('tier-pill').className = `tier-pill ${style}`;
  $('score-number').textContent = data.score_out_of_10 ?? '—';
  $('score-context').textContent = data.score_out_of_10 === null ? 'No score available' : 'Rubric cue points';
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
  scale.setAttribute('aria-label', data.score_out_of_10 === null ? 'No score available' : `Exploratory cue score ${data.score_out_of_10} out of 10`);
  const analyzed = [];
  if (mode === 'image' && selectedFile) analyzed.push(`Image: ${selectedFile.name}`);
  if (data.input_text) analyzed.push(`Ad copy: ${data.input_text.slice(0, 240)}${data.input_text.length > 240 ? '…' : ''}`);
  if (data.ocr_text) analyzed.push(`OCR: ${data.ocr_text.slice(0, 240)}${data.ocr_text.length > 240 ? '…' : ''}`);
  if (data.visual_description) analyzed.push(`Your visual description: ${data.visual_description.slice(0, 240)}${data.visual_description.length > 240 ? '…' : ''}`);
  if (data.targeting) analyzed.push('Targeting details supplied');
  $('input-summary').textContent = analyzed.join(' · ') || 'No readable ad text was available.';
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
        : `Matched “${cue.matched}” in ${cue.source === 'targeting' ? 'targeting details' : (mode === 'image' ? 'image OCR or your description' : 'ad copy')}`;
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
  $('result-note').textContent = data.reason || 'Exploratory rubric score only. Not a measured consumer reaction.';
  $('threshold-status').textContent = data.threshold_decision?.reason || 'Insufficient evidence for a consumer-level recommendation from the current data.';
  renderCompatibility(data.compatibility);
  renderStrategy(data.strategy);
  setResultState('content');
  if (window.matchMedia('(max-width: 850px)').matches) $('result-title').scrollIntoView({behavior: 'smooth', block: 'start'});
}

$('clear-btn').addEventListener('click', () => {
  textInput.value = ''; textInput.dispatchEvent(new Event('input'));
  $('targeting').value = ''; $('visual-description').value = '';
  $('ad-form').querySelectorAll('input[type="number"]').forEach((input) => { input.value = ''; });
  $('objective').value = 'unknown'; $('targeting-method').value = 'unknown';
  $('product-category').value = 'unknown'; $('channel').value = 'unknown'; $('data-source').value = 'unknown';
  $('consent-status').value = 'unknown'; $('audience-eligibility').value = 'unknown';
  $('currency').value = 'INR'; $('scenario-option').value = 'one_variant';
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
      body: JSON.stringify({text: copy, image_data: imageData, targeting: $('targeting').value.trim(),
        visual_description: visual, campaign: campaignInput()})
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
