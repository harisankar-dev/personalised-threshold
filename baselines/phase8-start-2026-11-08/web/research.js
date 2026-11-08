const put = (id, value) => { document.getElementById(id).textContent = String(value); };
const fixed = (value, places = 3) => Number(value).toFixed(places);
const interval = (bounds, places = 3) => `[${fixed(bounds[0], places)}, ${fixed(bounds[1], places)}]`;

function render(data) {
  const upad = data.engagement.upad;
  put('upad-n', upad.holdout_n.toLocaleString());
  put('upad-base-auc', fixed(upad.constant_auc));
  put('upad-model-auc', fixed(upad.logistic_auc));
  put('upad-base-brier', fixed(upad.constant_brier, 5));
  put('upad-model-brier', fixed(upad.logistic_brier, 5));

  const criteo = data.engagement.criteo;
  put('criteo-n', criteo.holdout_n.toLocaleString());
  put('criteo-c-base', fixed(criteo.control.constant.brier, 5));
  put('criteo-c-model', fixed(criteo.control.logistic.brier, 5));
  put('criteo-t-base', fixed(criteo.treatment.constant.brier, 5));
  put('criteo-t-model', fixed(criteo.treatment.logistic.brier, 5));
  put('criteo-auuc', fixed(criteo.auuc_gain, 5));
  put('criteo-ci', `95% bootstrap interval ${interval(criteo.auuc_gain_interval, 5)}`);

  const survey = data.intrusiveness.romano_han;
  put('survey-n', survey.respondents.toLocaleString());
  put('survey-test-n', survey.holdout_n);
  put('survey-base', fixed(survey.baseline_mae));
  put('survey-v1', fixed(survey.v1_mae));
  put('survey-v2', fixed(survey.v2_mae));
  put('survey-v1-high', `${survey.high_below_5_v1} / ${survey.high_n}`);
  put('survey-v2-high', `${survey.high_below_5_v2} / ${survey.high_n}`);
  put('survey-overlap', fixed(survey.privacy_intrusion_pearson));
  put('interval-overall', `${survey.overall_interval_covered} / ${survey.overall_interval_n}`);
  put('interval-low', `${survey.low_interval_covered} / ${survey.low_n}`);
  put('interval-high', survey.high_upper_below_5);

  const independent = data.intrusiveness.independent_web_ads;
  put('independent-n', independent.respondents.toLocaleString());
  put('independent-test-n', independent.holdout_n);
  put('independent-base', fixed(independent.baseline_mae));
  put('independent-model', fixed(independent.model_mae));
  put('independent-negative', fixed(independent.negative_mae));
  put('independent-negative-n', independent.negative_n);

  const vietnam = data.privacy_trust.vietnam;
  put('vietnam-rho', fixed(vietnam.trust_purchase_rho));
  put('vietnam-n', vietnam.respondents);
  put('vietnam-ci', interval(vietnam.trust_purchase_interval));
  const genz = data.privacy_trust.genz;
  put('genz-rho', fixed(genz.personalization_privacy_rho));
  put('genz-n', genz.respondents);
  put('genz-purchase', fixed(genz.personalization_purchase_rho));

  const threshold = data.threshold;
  put('threshold-value', threshold.status);
  put('threshold-reason', threshold.reason);
  const levels = document.getElementById('level-list');
  levels.replaceChildren();
  threshold.levels.forEach((level) => {
    const row = document.createElement('li');
    const number = document.createElement('span');
    number.className = 'level-number';
    number.textContent = `0${level.level}`;
    const name = document.createElement('strong');
    name.textContent = level.name;
    const state = document.createElement('span');
    state.className = 'level-state';
    state.textContent = 'No validated response estimate';
    row.append(number, name, state);
    levels.append(row);
  });
  document.getElementById('dashboard-loading').hidden = true;
  document.getElementById('dashboard-content').hidden = false;
}

fetch('/api/research', {cache: 'no-store'})
  .then(async (response) => {
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Research results are unavailable.');
    render(data);
  })
  .catch((error) => {
    document.getElementById('dashboard-loading').hidden = true;
    const box = document.getElementById('dashboard-error');
    box.textContent = error.message || 'Research results are unavailable.';
    box.hidden = false;
  });
