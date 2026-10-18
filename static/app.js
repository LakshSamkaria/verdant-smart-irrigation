const $ = id => document.getElementById(id);
const state = { fields: [], budget: 250, unit: 10, result: null, charts: {} };
const sample = [
 {id:1,name:"North Field",crop:"Wheat",area:1.2,moisture:22,target_moisture:60,demand:120,priority:5,max_allocation:120},
 {id:2,name:"East Garden",crop:"Tomato",area:0.6,moisture:35,target_moisture:65,demand:70,priority:4,max_allocation:70},
 {id:3,name:"South Plot",crop:"Rice",area:1.5,moisture:48,target_moisture:75,demand:150,priority:5,max_allocation:150},
 {id:4,name:"West Field",crop:"Cotton",area:1.0,moisture:28,target_moisture:60,demand:95,priority:3,max_allocation:95}
];
const titles={dashboard:["Smart irrigation.","Plan smarter. Allocate better. Waste less."],fields:["Field management.","Your fields, your inputs, your water budget."],lab:["Algorithm lab.","Run real algorithms. Understand every decision."],compare:["Algorithm comparison.","Same data. Shared constraints. Measurable outcomes."],reports:["Reports & export.","Take your results from simulation to submission."]};
function esc(s){return String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]))}
function showAlert(msg){$("alert").textContent=msg;$("alert").classList.remove("hidden");window.scrollTo({top:0,behavior:"smooth"})}
function clearAlert(){$("alert").classList.add("hidden")}
function go(view){document.querySelectorAll(".view").forEach(v=>v.classList.add("hidden"));$("view-"+view).classList.remove("hidden");document.querySelectorAll(".nav").forEach(b=>b.classList.toggle("active",b.dataset.view===view));$("pageTitle").innerHTML=titles[view][0].replace(/\.$/,'')+'<span>.</span>';$("pageSub").textContent=titles[view][1];if(view==="compare")renderCompare();if(view==="fields")renderFields();window.scrollTo({top:0,behavior:"smooth"})}
document.querySelectorAll("[data-view]").forEach(b=>b.addEventListener("click",()=>go(b.dataset.view)));
document.querySelectorAll("[data-goto]").forEach(b=>b.addEventListener("click",()=>go(b.dataset.goto)));
function renderOverview(){
 $("waterMetric").textContent=state.budget;$("fieldMetric").textContent=state.fields.length;$("demandMetric").textContent=state.fields.reduce((s,f)=>s+Number(f.demand),0);
 $("benefitMetric").textContent=state.result?state.result.dp.total_benefit:"—";
 $("overviewRows").innerHTML=state.fields.map(f=>`<tr><td><div class="field-cell">${esc(f.name)}</div><div class="field-meta">${Number(f.area).toFixed(1)} ha</div></td><td>${esc(f.crop)}</td><td><div class="moisture"><div class="moisture-track"><div class="moisture-fill" style="width:${f.moisture}%"></div></div>${f.moisture}%</div></td><td>${f.demand} L</td><td><span class="priority ${f.target_moisture-f.moisture>=30?"high":f.target_moisture-f.moisture>=15?"medium":"low"}">${f.target_moisture-f.moisture>=30?"HIGH":f.target_moisture-f.moisture>=15?"MEDIUM":"LOW"}</span></td></tr>`).join("")||'<tr><td colspan="5" class="empty-state">No fields yet. Add a field to begin.</td></tr>';
 if(state.result) drawChart("overviewChart",["Greedy","Dynamic Programming"],[state.result.greedy.total_water_used,state.result.dp.total_water_used],"Water used (L)");else if(state.charts.overviewChart){state.charts.overviewChart.destroy();delete state.charts.overviewChart}
 $("chartEmpty").classList.toggle("hidden",!!state.result);
}
function renderFields(){
 $("budgetInput").value=state.budget;$("unitInput").value=String(state.unit);
 $("editRows").innerHTML=state.fields.map((f,i)=>`<tr data-row="${i}">
 <td><input data-k="name" value="${esc(f.name)}" aria-label="Field name"></td>
 <td><select data-k="crop">${["Wheat","Rice","Tomato","Cotton","Other"].map(c=>`<option ${f.crop===c?"selected":""}>${c}</option>`).join("")}</select></td>
 <td><input data-k="area" type="number" min=".01" step=".1" value="${f.area}"></td>
 <td><input data-k="moisture" type="number" min="0" max="100" value="${f.moisture}"></td>
 <td><input data-k="target_moisture" type="number" min="0" max="100" value="${f.target_moisture}"></td>
 <td><input data-k="demand" type="number" min="0" step="1" value="${f.demand}"></td>
 <td><select data-k="priority">${[1,2,3,4,5].map(n=>`<option value="${n}" ${Number(f.priority)===n?"selected":""}>${n}</option>`).join("")}</select></td>
 <td><input data-k="max_allocation" type="number" min="0" value="${f.max_allocation}"></td>
 <td><button class="remove" data-remove="${i}" aria-label="Remove ${esc(f.name)}">×</button></td></tr>`).join("")||'<tr><td colspan="9" class="empty-state">No fields yet. Add a field or load sample data.</td></tr>';
}
$("editRows").addEventListener("change",e=>{
 const tr=e.target.closest("[data-row]");if(!tr)return;
 const i=Number(tr.dataset.row),k=e.target.dataset.k;if(!k)return;
 let val=e.target.value;
 if(k!=="name"&&k!=="crop"){val=Number(val);if(!Number.isFinite(val)){showAlert("Please enter a valid number.");renderFields();return}}
 const f=state.fields[i];if(!f)return;
 if(k==="name"||k==="crop")f[k]=val.trim?val.trim():val;else f[k]=val;
 if(!f.name||f.area<=0||f.moisture<0||f.moisture>100||f.target_moisture<0||f.target_moisture>100||f.demand<0||f.priority<1||f.priority>5||f.max_allocation<0||f.demand>f.max_allocation){showAlert("Invalid field data. Area must be positive, moisture 0–100%, priority 1–5, and demand cannot exceed max allocation.");return}
 state.result=null;clearAlert();renderOverview();renderLabSummary();$("results").classList.add("hidden");
});
$("editRows").addEventListener("click",e=>{if(e.target.dataset.remove!==undefined){state.fields.splice(Number(e.target.dataset.remove),1);state.result=null;renderFields();renderOverview();$("results").classList.add("hidden")}});
$("budgetInput").addEventListener("change",e=>{const n=Number(e.target.value);if(!Number.isFinite(n)||n<0||n>10000000){showAlert("Water budget must be between 0 and 10,000,000 L.");e.target.value=state.budget;return}state.budget=Math.floor(n);state.result=null;renderOverview();renderLabSummary();$("results").classList.add("hidden");clearAlert()});
$("unitInput").addEventListener("change",e=>{state.unit=Number(e.target.value)||10;state.result=null;renderLabSummary();$("results").classList.add("hidden")});
$("addField").onclick=()=>{if(state.fields.length>=50){showAlert("Maximum 50 fields in this demo.");return}const id=Math.max(0,...state.fields.map(f=>f.id))+1;state.fields.push({id,name:"New Field "+id,crop:"Wheat",area:1,moisture:30,target_moisture:60,demand:50,priority:3,max_allocation:50});renderFields();renderOverview();state.result=null};
function loadSamples(){state.fields=sample.map(f=>({...f}));state.budget=250;state.unit=10;state.result=null;renderFields();renderOverview();renderLabSummary();$("results").classList.add("hidden");clearAlert()}
$("sampleBtn").onclick=loadSamples;
function renderLabSummary(){$("labBudget").textContent=state.budget+" L";$("labFields").textContent=state.fields.length;$("labUnit").textContent=state.unit+" L"}
function validate(){
 if(!state.fields.length)return "Add at least one field before running a simulation.";
 if(state.fields.length>50)return "Use 50 fields or fewer.";
 for(const f of state.fields){if(!f.name.trim()||!f.crop)return "Every field needs a name and crop.";if(f.area<=0||f.demand<0||f.max_allocation<0||f.demand>f.max_allocation)return `Check area, demand and maximum allocation for ${f.name}.`;if(f.moisture<0||f.moisture>100||f.target_moisture<0||f.target_moisture>100)return `Moisture values for ${f.name} must be 0–100%.`;if(f.priority<1||f.priority>5)return `Priority for ${f.name} must be 1–5.`}
 return null
}
async function runSimulation(){
 clearAlert();const err=validate();if(err){showAlert(err);return}
 state.budget=Math.floor(Number($("budgetInput").value||state.budget));state.unit=Number($("unitInput").value||state.unit);
 const btn=$("runBtn");btn.disabled=true;btn.textContent="Running algorithms…";
 try{
  const res=await fetch("/api/simulate",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({available_water:state.budget,unit_size:state.unit,fields:state.fields})});
  const data=await res.json();if(!res.ok)throw new Error(data.error||"Simulation failed.");
  state.result=data;$("results").classList.remove("hidden");renderResults();renderOverview();renderCompare();renderLabSummary();
 }catch(e){showAlert(e.message+" Make sure the Flask server is running.");}
 finally{btn.disabled=false;btn.textContent="▶ Run both algorithms"}
}
$("runBtn").onclick=runSimulation;$("compareRun").onclick=()=>state.result?renderCompare():runSimulation();
function renderResults(){
 const r=state.result,g=r.greedy,d=r.dp;
 $("gBenefit").textContent=g.total_benefit;$("dBenefit").textContent=d.total_benefit;$("gWater").textContent=`${g.total_water_used} L used · ${g.remaining_water} L left`;$("dWater").textContent=`${d.total_water_used} L used · ${d.remaining_water} L left`;$("dLeft").textContent=d.remaining_water+" L";$("dServed").textContent=d.fields_served;
 const gm=new Map(g.allocations.map(a=>[a.id,a])),dm=new Map(d.allocations.map(a=>[a.id,a]));
 $("resultRows").innerHTML=r.fields.map(f=>{const a=gm.get(f.id),b=dm.get(f.id);return `<tr><td><div class="field-cell">${esc(f.name)}</div><div class="field-meta">${esc(f.crop)}</div></td><td>${a.option_label}</td><td>${a.allocated_water} L</td><td>${b.option_label}</td><td>${b.allocated_water} L</td><td>${b.benefit}</td></tr>`}).join("");
 drawChart("resultChart",["Budget","Greedy used","DP used"],[r.available_water,g.total_water_used,d.total_water_used],"Water (L)");
 const diff=d.total_benefit-g.total_benefit;
 $("interpretation").innerHTML=`<p><strong>DP benefit:</strong> ${d.total_benefit}. <strong>Greedy benefit:</strong> ${g.total_benefit}.</p><p>${diff>0?`DP found ${diff} more benefit points for this defined model.`:diff<0?`Greedy scored ${-diff} more points in this run; check the chosen model and implementation assumptions.`:"Both algorithms achieved the same total benefit in this run."}</p><p><strong>Greedy limitation:</strong> ${esc(g.limitation)}</p><p><strong>DP scope:</strong> ${esc(d.limitation)}</p><p><strong>Discretization:</strong> ${r.unit_size} L per unit. The algorithm rounds each option up to a whole unit, so the reported allocation may leave unused water.</p>`;
 renderCompare();
}
function renderCompare(){
 if(!state.result){$("compareRows").innerHTML='<tr><td colspan="4" class="empty-state">Run the algorithms first.</td></tr>';return}
 const {greedy:g,dp:d}=state.result;
 const rows=[
 ["Total benefit",g.total_benefit,d.total_benefit,"Higher is better under the defined score"],
 ["Water used",g.total_water_used+" L",d.total_water_used+" L","Cannot exceed available budget"],
 ["Remaining water",g.remaining_water+" L",d.remaining_water+" L","Unused budget after chosen options"],
 ["Fields served",g.fields_served,d.fields_served,"Fields receiving partial or full irrigation"],
 ["Unmet demand",g.unmet_demand+" L",d.unmet_demand+" L","Demand minus allocated amount; based on original demand"],
 ["Execution time",g.execution_ms+" ms",d.execution_ms+" ms","Small local timings vary by machine"],
 ["Time complexity",g.complexity.time,d.complexity.time,"DP depends on discrete budget W and option count k"],
 ["Space complexity",g.complexity.space,d.complexity.space,"DP retains a table for reconstruction"]
 ];
 $("compareRows").innerHTML=rows.map(r=>`<tr><td><b>${r[0]}</b></td><td>${r[1]}</td><td>${r[2]}</td><td>${r[3]}</td></tr>`).join("");
}
function drawChart(id,labels,values,title){
 const canvas=$(id);if(!canvas||!window.Chart)return;
 if(state.charts[id])state.charts[id].destroy();
 state.charts[id]=new Chart(canvas,{type:"bar",data:{labels,datasets:[{label:title,data:values,backgroundColor:["#c8dcae","#679b60","#254d31"],borderRadius:7,maxBarThickness:45}]},options:{responsive:true,plugins:{legend:{display:false},tooltip:{callbacks:{label:c=>`${c.raw} L`}}},scales:{x:{grid:{display:false},ticks:{color:"#718071"}},y:{beginAtZero:true,grid:{color:"#edf0e9"},ticks:{color:"#718071"}}}}});
}
$("exportBtn").onclick=async()=>{
 if(!state.result){showAlert("Run a simulation before exporting a report.");go("lab");return}
 const res=await fetch("/api/export",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({result:state.result})});
 const blob=await res.blob(),url=URL.createObjectURL(blob),a=document.createElement("a");a.href=url;a.download="irrigation-report.csv";a.click();URL.revokeObjectURL(url);
};
$("printBtn").onclick=()=>window.print();
$("resetBtn").onclick=()=>{loadSamples();go("dashboard")};
loadSamples();renderLabSummary();renderOverview();
