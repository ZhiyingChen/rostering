const basePath = location.pathname.startsWith('/rostering') ? '/rostering' : '';
const apiUrl = (path) => `${basePath}${path}`;
const parameterNames = ['计划开始时刻','计划结束时刻','服务车辆','装货时间','卸货时间','备货时间','去程时间','返程时间','服务时间','维修时间','最大工作时间'];
const activityLabels = ['装货','去程','服务','返程','卸货','备货','维修','空闲'];
const descriptions = {计划开始时刻:'通常为 0',计划结束时刻:'720 = 30 天',服务车辆:'每小时最低在岗数',装货时间:'任务开始准备',卸货时间:'任务结束处理',备货时间:'再次出发前准备',去程时间:'驶向服务区',返程时间:'驶回基地',服务时间:'现场连续服务',维修时间:'强制维护时长',最大工作时间:'维修前累计上限'};
let result = null;
let currentView = 'vehicle';

function setStatus(ok, text) {
  document.querySelector('#serviceDot').className = ok ? 'ok' : 'bad';
  document.querySelector('#serviceText').textContent = text;
}
function renderForm(values) {
  document.querySelector('#form').innerHTML = parameterNames.map(name => `<label><span>${name}<small>${descriptions[name]}</small></span><input type="number" min="0" value="${values[name] ?? 0}" data-name="${name}"></label>`).join('');
}
async function loadExample(scroll = false) {
  try {
    const response = await fetch(apiUrl('/api/example'));
    if (!response.ok) throw new Error(`服务返回 ${response.status}`);
    const data = await response.json();
    renderForm(data.parameters);
    setStatus(true, '求解服务在线');
    if (scroll) document.querySelector('#simulation').scrollIntoView({behavior:'smooth'});
  } catch (error) {
    setStatus(false, '求解服务连接失败');
    showError(`无法加载示例数据：${error.message}。本应用不需要 API Key，请刷新页面后重试。`);
  }
}
function showError(message = '') {
  const box = document.querySelector('#formError');
  box.textContent = message;
  box.classList.toggle('hidden', !message);
}
async function solve() {
  const button = document.querySelector('#solve');
  const parameters = Object.fromEntries([...document.querySelectorAll('#form input')].map(input => [input.dataset.name, Number(input.value)]));
  button.disabled = true; button.textContent = '算法求解中…'; showError();
  try {
    const response = await fetch(apiUrl('/api/solve'), {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({parameters})});
    const data = await response.json();
    if (!response.ok) throw new Error(Array.isArray(data.detail) ? data.detail[0].msg : data.detail || '求解失败');
    result = data; renderResults(); setStatus(true, '求解服务在线');
  } catch (error) { showError(error.message); }
  finally { button.disabled = false; button.textContent = '运行车辆排班模拟'; }
}
function renderResults() {
  const kpi = result.kpis;
  document.querySelector('#runMeta').textContent = `${result.runtime_seconds}s · 原始轮转算法`;
  document.querySelector('#kpis').innerHTML = [[kpi.vehicles,'最少车辆'],[`${kpi.coverage_percent}%`,'全时域覆盖'],[`${kpi.work_hours}h`,'总执行工时'],[`${kpi.shortage_vehicle_hours}h`,'启动期缺口'],[`${kpi.work_spread_hours}h`,'工时差异']].map(([value,label]) => `<article><span>${label}</span><strong>${value}</strong></article>`).join('');
  document.querySelector('#warnings').innerHTML = result.warnings.map(message => `<div class="warning">${message}</div>`).join('');
  document.querySelector('#legend').innerHTML = activityLabels.map((label,index) => `<span><i class="state-${index}"></i>${label}</span>`).join('');
  renderVisual(); renderTable();
}
function renderVisual() {
  if (!result) return;
  const visual = document.querySelector('#visual');
  if (currentView === 'coverage') {
    const max = Math.max(...result.coverage, result.parameters['服务车辆']);
    visual.innerHTML = `<div class="coverage-chart">${result.coverage.map((value,index) => `<div class="bar ${value < result.parameters['服务车辆'] ? 'short' : ''}" style="height:${Math.max(3,value/max*100)}%" title="${result.hours[index]}h：${value} 辆"></div>`).join('')}</div><p class="chart-note">每根柱表示一个小时的在岗服务车辆数；红色表示低于需求。</p>`;
  } else {
    visual.innerHTML = `<div class="timeline">${result.vehicles.map(vehicle => `<div class="timeline-row"><span>车辆 ${vehicle.id}</span><div>${vehicle.states.map(state => `<i class="state-${state}" title="${activityLabels[state]}"></i>`).join('')}</div></div>`).join('')}</div>`;
  }
}
function renderTable() {
  if (!result) return;
  const query = document.querySelector('#search').value.trim().toLowerCase();
  const rows = result.segments.filter(item => !query || `车辆 ${item.vehicle} ${item.activity}`.toLowerCase().includes(query));
  document.querySelector('#table').innerHTML = `<table><thead><tr><th>车辆</th><th>开始</th><th>结束</th><th>时长</th><th>活动</th></tr></thead><tbody>${rows.map(item => `<tr><td>车辆 ${item.vehicle}</td><td>${item.start}h</td><td>${item.end}h</td><td>${item.end-item.start}h</td><td><i class="state-${item.state}"></i>${item.activity}</td></tr>`).join('')}</tbody></table>`;
}
function download() {
  if (!result) return showError('请先运行一次模拟。');
  const rows = [['vehicle','start','end','duration','activity'], ...result.segments.map(item => [item.vehicle,item.start,item.end,item.end-item.start,item.activity])];
  const blob = new Blob(['\ufeff' + rows.map(row => row.join(',')).join('\n')], {type:'text/csv'});
  const link = document.createElement('a'); link.href = URL.createObjectURL(blob); link.download = 'vehicle-scheduling-result.csv'; link.click(); URL.revokeObjectURL(link.href);
}
document.querySelector('#docsLink').href = apiUrl('/docs');
document.querySelector('#loadExample').onclick = () => loadExample();
document.querySelector('#loadExampleTop').onclick = () => loadExample(true);
document.querySelector('#solve').onclick = solve;
document.querySelector('#download').onclick = download;
document.querySelector('#search').oninput = renderTable;
document.querySelector('#viewVehicle').onclick = () => { currentView='vehicle'; document.querySelector('#viewVehicle').classList.add('active'); document.querySelector('#viewCoverage').classList.remove('active'); renderVisual(); };
document.querySelector('#viewCoverage').onclick = () => { currentView='coverage'; document.querySelector('#viewCoverage').classList.add('active'); document.querySelector('#viewVehicle').classList.remove('active'); renderVisual(); };
loadExample();
