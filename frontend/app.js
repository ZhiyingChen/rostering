const basePath = location.pathname.startsWith('/rostering') ? '/rostering' : '';
const apiUrl = (path) => `${basePath}${path}`;
const parameterNames = ['计划开始时刻','计划结束时刻','服务车辆','装货时间','卸货时间','备货时间','去程时间','返程时间','服务时间','维修时间','最大工作时间'];
const activityLabels = ['装货','去程','服务','返程','卸货','备货','维修','空闲'];
const descriptions = {计划开始时刻:'通常为 0',计划结束时刻:'720 = 30 天',服务车辆:'每小时最低在岗数',装货时间:'任务开始准备',卸货时间:'任务结束处理',备货时间:'再次出发前准备',去程时间:'驶向服务区',返程时间:'驶回基地',服务时间:'现场连续服务',维修时间:'强制维护时长',最大工作时间:'维修前累计上限'};
let result = null;
let currentView = 'vehicle';
let timeOffset = 0;
function getTimeWindow(){const value=document.querySelector('#timeWindow').value;return value==='all'?result.hours.length:Number(value)}
function visibleRange(){const size=Math.min(getTimeWindow(),result.hours.length),max=Math.max(0,result.hours.length-size);timeOffset=Math.min(Math.max(0,timeOffset),max);return{start:timeOffset,end:Math.min(result.hours.length,timeOffset+size),size}}

function renderScenario(scenario) {
  const metrics = [
    [`${scenario.planning_span_hours}h`, '计划跨度', '0–720 小时'],
    [scenario.hourly_slots, '小时刻度', '含起止时刻'],
    [scenario.required_service_vehicles, '每小时服务车辆', '最低覆盖需求'],
    [`${scenario.required_service_vehicle_hours}h`, '需求车·小时', '小时刻度 × 需求'],
    [`${scenario.task_cycle_hours}h`, '单趟完整周期', '六个连续环节'],
    [`${scenario.max_work_hours}h`, '累计工作上限', `随后维修 ${scenario.maintenance_hours}h`],
  ];
  document.querySelector('#scenarioMetrics').innerHTML = metrics.map(([value,label,note]) => `<article><strong>${value}</strong><span>${label}</span><small>${note}</small></article>`).join('');
}

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
    renderScenario(data.scenario);
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
    result = data; timeOffset = 0; renderResults(); setStatus(true, '求解服务在线');
  } catch (error) { showError(error.message); }
  finally { button.disabled = false; button.textContent = '运行车辆排班模拟'; }
}
function renderResults() {
  const kpi = result.kpis;
  document.querySelector('#runMeta').textContent = `${result.runtime_seconds}s · 原始轮转算法`;
  document.querySelector('#kpis').innerHTML = [[kpi.vehicles,'最少车辆'],[`${kpi.coverage_percent}%`,'全时域覆盖'],[`${kpi.work_hours}h`,'总执行工时'],[`${kpi.shortage_vehicle_hours}h`,'启动期缺口'],[`${kpi.work_spread_hours}h`,'工时差异']].map(([value,label]) => `<article><span>${label}</span><strong>${value}</strong></article>`).join('');
  document.querySelector('#warnings').innerHTML = result.warnings.map(message => `<div class="warning">${message}</div>`).join('');
  document.querySelector('#solvedScale').innerHTML = `<strong>本次实际输出：</strong>${kpi.vehicles} 辆车 × ${result.hours.length} 个小时刻度 = <b>${(kpi.vehicles * result.hours.length).toLocaleString('zh-CN')}</b> 个车辆小时状态；求解耗时 ${result.runtime_seconds}s。`;
  document.querySelector('#legend').innerHTML = activityLabels.map((label,index) => `<span><i class="state-${index}"></i>${label}</span>`).join('');
  renderVisual(); renderTable();
}
function renderVisual() {
  if (!result) return;
  const visual=document.querySelector('#visual'),range=visibleRange(),hours=result.hours.slice(range.start,range.end),first=hours[0],last=hours[hours.length-1];
  const cell=range.size<=24?28:range.size<=72?14:range.size<=168?8:3,width=hours.length*cell,step=range.size<=24?3:range.size<=72?6:range.size<=168?24:72;
  const ticks=hours.map((hour,index)=>({hour,index})).filter(({hour,index})=>index===0||index===hours.length-1||(hour-first)%step===0);
  const axis=`<div class="time-axis-label">时间</div><div class="time-axis-track" style="width:${width}px">${ticks.map(({hour,index})=>`<span style="left:${index*cell}px">${hour}h</span>`).join('')}</div>`;
  document.querySelector('#timeRange').textContent=`${first}h – ${last}h / 共 ${result.hours.length} 个刻度`;
  document.querySelector('#previousTime').disabled=range.start===0; document.querySelector('#nextTime').disabled=range.end>=result.hours.length;
  if(currentView==='coverage'){
    const coverage=result.coverage.slice(range.start,range.end),max=Math.max(...coverage,result.parameters['服务车辆']);
    visual.innerHTML=`<div class="time-axis">${axis}</div><div class="coverage-layout"><span>在岗</span><div class="coverage-chart" style="width:${width}px">${coverage.map((value,index)=>`<div class="bar ${value<result.parameters['服务车辆']?'short':''}" style="width:${cell}px;height:${Math.max(3,value/max*100)}%" title="${hours[index]}h：${value} 辆"></div>`).join('')}</div></div><p class="chart-note">每根柱表示一个小时；红色低于需求。使用上方按钮浏览完整时域。</p>`;
  }else{
    visual.innerHTML=`<div class="timeline"><div class="time-axis">${axis}</div>${result.vehicles.map(vehicle=>`<div class="timeline-row"><span>车辆 ${vehicle.id}</span><div style="width:${width}px">${vehicle.states.slice(range.start,range.end).map((state,index)=>`<i class="state-${state}" style="width:${cell}px" title="${hours[index]}h · ${activityLabels[state]}"></i>`).join('')}</div></div>`).join('')}</div>`;
  }
}
function renderTable() {
  if (!result) return;
  const query = document.querySelector('#search').value.trim().toLowerCase();
  const rows = result.segments.filter(item => !query || `车辆 ${item.vehicle} ${item.activity}`.toLowerCase().includes(query));
  document.querySelector('#rowCount').textContent=`共 ${rows.length} 条`;
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
document.querySelector('#timeWindow').onchange=()=>{timeOffset=0;renderVisual()};
document.querySelector('#previousTime').onclick=()=>{timeOffset-=getTimeWindow();renderVisual()};
document.querySelector('#nextTime').onclick=()=>{timeOffset+=getTimeWindow();renderVisual()};
document.querySelector('#viewVehicle').onclick = () => { currentView='vehicle'; document.querySelector('#viewVehicle').classList.add('active'); document.querySelector('#viewCoverage').classList.remove('active'); renderVisual(); };
document.querySelector('#viewCoverage').onclick = () => { currentView='coverage'; document.querySelector('#viewCoverage').classList.add('active'); document.querySelector('#viewVehicle').classList.remove('active'); renderVisual(); };
loadExample();
