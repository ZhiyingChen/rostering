const basePath = location.pathname.startsWith('/rostering') ? '/rostering' : '';
const apiUrl = (path) => `${basePath}${path}`;
const parameterNames = ['计划开始时刻','计划结束时刻','服务车辆','装货时间','卸货时间','备货时间','去程时间','返程时间','服务时间','维修时间','最大工作时间'];
const activityLabels = ['装货','去程','服务','返程','卸货','备货','维修','空闲'];
const descriptions = {计划开始时刻:'通常为 0',计划结束时刻:'720 = 30 天',服务车辆:'每小时最低在岗数',装货时间:'任务开始准备',卸货时间:'任务结束处理',备货时间:'再次出发前准备',去程时间:'驶向服务区',返程时间:'驶回基地',服务时间:'现场连续服务',维修时间:'强制维护时长',最大工作时间:'维修前累计上限'};
let result = null;
let currentView = 'vehicle';
let timeWindow = 'all';
let windowStart = 0;
let tablePage = 1;
const pageSize = 20;

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
    result = data; timeWindow = 'all'; windowStart = data.hours[0]; tablePage = 1; renderResults(); setStatus(true, '求解服务在线');
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
  document.querySelector('#activityFilter').innerHTML = '<option value="">全部活动</option>' + activityLabels.map(label => `<option value="${label}">${label}</option>`).join('');
  document.querySelector('#vehicleFilter').innerHTML = '<option value="">全部车辆</option>' + result.vehicles.map(vehicle => `<option value="${vehicle.id}">车辆 ${vehicle.id}</option>`).join('');
  document.querySelector('#download').disabled = false;
  document.querySelector('#segmentInfo').textContent = '点击甘特图中的任务片段，查看车辆、活动和起止时间。';
  document.querySelector('#vehicleSummary').innerHTML = result.vehicles.map(vehicle => `<article><strong>车辆 ${vehicle.id}</strong><span>服务 ${vehicle.service_hours}h · 工作 ${vehicle.work_hours}h</span><span>维修 ${vehicle.maintenance_hours}h · 空闲 ${vehicle.states.filter(state => state === 7).length}h</span></article>`).join('');
  renderVisual(); renderTable();
}
function currentTimeRange() {
  const first=result.hours[0], last=result.hours[result.hours.length-1], limit=last+1;
  if(timeWindow==='all') return {start:first,end:limit,labelEnd:last};
  const size=Number(timeWindow), end=Math.min(limit,windowStart+size);
  return {start:windowStart,end,labelEnd:Math.min(last,end)};
}
function renderAxis(start,end) {
  const divisions = window.innerWidth < 700 ? 3 : 6;
  return Array.from({length:divisions+1},(_,index)=>`<i style="left:${index*100/divisions}%">${Math.round(start+(end-start)*index/divisions)}h</i>`).join('');
}
function renderCoverage() {
  const start=result.hours[0], end=result.hours[result.hours.length-1]+1, required=result.parameters['服务车辆'];
  const maximum=Math.max(...result.coverage,required,1), x=hour=>60+(hour-start)/(end-start)*920, y=value=>215-value/maximum*165;
  const points=result.coverage.map((value,index)=>`${x(result.hours[index])},${y(value)}`).join(' ');
  const ticks=Array.from({length:7},(_,i)=>{const hour=start+(end-start)*i/6;return `<text x="${x(hour)}" y="250" text-anchor="${i===0?'start':i===6?'end':'middle'}">${Math.min(end-1,Math.round(hour))}h</text>`}).join('');
  return `<svg class="coverage-svg" viewBox="0 0 1020 270" role="img" aria-label="完整时域服务覆盖曲线，需求 ${required} 辆"><path d="M60 45V215H980" fill="none" stroke="#dbe5ee"/><path d="M60 ${y(required)}H980" stroke="#f79009" stroke-dasharray="6 4"/><polyline points="${points}" fill="none" stroke="#0e9384" stroke-width="3"/><g fill="#63788d" font-size="12">${ticks}<text x="12" y="${y(required)+4}">${required} 辆</text><text x="64" y="27">实线：服务车辆 · 虚线：最低需求</text></g></svg>`;
}
function renderVisual() {
  if(!result) return;
  const visual=document.querySelector('#visual'), controls=document.querySelector('#timelineControls');
  if(currentView==='coverage'){
    controls.hidden=true;
    visual.innerHTML=renderCoverage(); return;
  }
  controls.hidden=false; const {start,end,labelEnd}=currentTimeRange(),duration=end-start;
  document.querySelector('#timeRange').textContent=`${start}–${end}h`;
  const slider=document.querySelector('#timelineRange'); slider.min=result.hours[0]; slider.max=Math.max(result.hours[0],result.hours[result.hours.length-1]+1-(timeWindow==='all'?duration:Number(timeWindow))); slider.value=start; slider.disabled=timeWindow==='all';
  document.querySelectorAll('[data-window]').forEach(button=>button.classList.toggle('active',button.dataset.window===String(timeWindow)));
  const rows=result.vehicles.map(vehicle=>{const segments=result.segments.filter(segment=>segment.vehicle===vehicle.id&&segment.end>start&&segment.start<end).map(segment=>{const left=100*(Math.max(start,segment.start)-start)/duration,width=100*(Math.min(end,segment.end)-Math.max(start,segment.start))/duration;return `<i class="timeline-segment state-${segment.state}" data-vehicle="${segment.vehicle}" data-start="${segment.start}" style="left:${left}%;width:${width}%" title="车辆 ${segment.vehicle} · ${segment.activity} · ${segment.start}–${segment.end}h"></i>`}).join('');return `<div class="timeline-row"><b>车辆 ${vehicle.id}</b><section class="timeline-track">${segments}</section></div>`}).join('');
  visual.innerHTML=`<div class="timeline"><div class="timeline-axis"><span>车辆</span><section class="axis-track">${renderAxis(start,end)}</section></div>${rows}</div>`;
}
function filteredSegments(){const query=document.querySelector('#search').value.trim().toLowerCase(),activity=document.querySelector('#activityFilter').value,vehicle=document.querySelector('#vehicleFilter').value;return result.segments.filter(item=>(!query||`车辆 ${item.vehicle} ${item.activity}`.toLowerCase().includes(query))&&(!activity||item.activity===activity)&&(!vehicle||item.vehicle===Number(vehicle))).sort((a,b)=>a.start-b.start||a.vehicle-b.vehicle);}
function dayTime(hour) { const relative=hour-result.hours[0]; return `第 ${Math.floor(relative/24)+1} 天 · ${String(relative%24).padStart(2,'0')}:00`; }
function renderTable() {
  if(!result) return; const rows=filteredSegments(),pages=Math.max(1,Math.ceil(rows.length/pageSize)); tablePage=Math.min(tablePage,pages); const visible=rows.slice((tablePage-1)*pageSize,tablePage*pageSize);
  document.querySelector('#tableMeta').textContent=`共 ${rows.length.toLocaleString()} 条任务片段，每页 ${pageSize} 条`;
  document.querySelector('#table').innerHTML=`<table><thead><tr><th>车辆</th><th>活动</th><th>开始时刻</th><th>结束时刻</th><th>持续时间</th></tr></thead><tbody>${visible.map(item=>`<tr><td data-label="车辆">车辆 ${item.vehicle}</td><td data-label="活动"><span class="activity-cell"><i class="state-${item.state}"></i>${item.activity}</span></td><td data-label="开始时刻">${item.start}h<small>${dayTime(item.start)}</small></td><td data-label="结束时刻">${item.end}h<small>${dayTime(item.end)}</small></td><td data-label="持续时间">${item.end-item.start} 小时</td></tr>`).join('')||'<tr><td colspan="5">没有符合筛选条件的任务，请调整筛选。</td></tr>'}</tbody></table>`;
  const pagination=document.querySelector('#pagination'); pagination.hidden=rows.length<=pageSize; document.querySelector('#pageMeta').textContent=`第 ${tablePage} / ${pages} 页`; document.querySelector('#prevPage').disabled=tablePage===1; document.querySelector('#nextPage').disabled=tablePage===pages;
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
document.querySelector('#search').oninput=()=>{tablePage=1;renderTable()};
document.querySelector('#activityFilter').onchange=()=>{tablePage=1;renderTable()};
document.querySelector('#vehicleFilter').onchange=()=>{tablePage=1;renderTable()};
document.querySelector('#visual').onclick=event=>{
  const target=event.target.closest('[data-vehicle]'); if(!target||!result)return;
  const item=result.segments.find(segment=>segment.vehicle===Number(target.dataset.vehicle)&&segment.start===Number(target.dataset.start));
  document.querySelector('#segmentInfo').textContent=`车辆 ${item.vehicle} · ${item.activity} · ${item.start}–${item.end}h · 持续 ${item.end-item.start} 小时`;
  document.querySelector('#vehicleFilter').value=String(item.vehicle); document.querySelector('#activityFilter').value=item.activity; tablePage=1;renderTable();
};
document.querySelector('#prevPage').onclick=()=>{tablePage--;renderTable()};
document.querySelector('#nextPage').onclick=()=>{tablePage++;renderTable()};
document.querySelectorAll('[data-window]').forEach(button=>button.onclick=()=>{timeWindow=button.dataset.window;windowStart=result.hours[0];renderVisual()});
document.querySelector('#timelineRange').oninput=event=>{windowStart=Number(event.target.value);renderVisual()};
document.querySelector('#viewVehicle').onclick=()=>{currentView='vehicle';document.querySelector('#viewVehicle').className='active';document.querySelector('#viewCoverage').className='';renderVisual()};
document.querySelector('#viewCoverage').onclick=()=>{currentView='coverage';document.querySelector('#viewCoverage').className='active';document.querySelector('#viewVehicle').className='';renderVisual()};
loadExample();
window.addEventListener('resize',()=>{if(result)renderVisual()});
