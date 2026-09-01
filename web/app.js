const dataRoot = "../data";
const formatArea = (v) => `${Number(v).toFixed(3)} km²`;
const noData = (text) => `<p class="empty">${text}</p>`;

function metric(label, value, detail = "") {
  return `<div class="metric"><span>${label}</span><b>${value}</b>${detail ? `<span>${detail}</span>` : ""}</div>`;
}

function drawChart(rows) {
  const target = document.querySelector("#chart");
  if (!rows.length) { target.innerHTML = noData("No usable optical candidates or published measurements are available yet."); return; }
  if (!window.d3) { target.innerHTML = noData("The D3 chart library could not be loaded."); return; }
  const d3 = window.d3, width = 800, height = 270, margin = {top:24, right:24, bottom:45, left:66};
  const data = rows.map(row => ({...row, date: new Date(row.date)})).sort((a,b) => a.date-b.date);
  const values = data.map(row => row.area), extent = d3.extent(values), padding = Math.max((extent[1]-extent[0])*.12, .05);
  const x = d3.scaleTime().domain(d3.extent(data, row => row.date)).range([margin.left, width-margin.right]);
  const y = d3.scaleLinear().domain([Math.max(0, extent[0]-padding), extent[1]+padding]).nice().range([height-margin.bottom, margin.top]);
  const svg = d3.select(target).html("").append("svg").attr("viewBox", `0 0 ${width} ${height}`).attr("preserveAspectRatio", "none").attr("aria-label", "Historical optical lake-area chart");
  svg.append("g").attr("transform", `translate(0,${height-margin.bottom})`).call(d3.axisBottom(x).ticks(Math.min(6, data.length)).tickFormat(d3.timeFormat("%Y"))).call(group => group.select(".domain").attr("stroke", "#cdd7d5"));
  svg.append("g").attr("transform", `translate(${margin.left},0)`).call(d3.axisLeft(y).ticks(5).tickFormat(value => `${value.toFixed(2)} km²`)).call(group => group.selectAll(".tick line").attr("x2", width-margin.left-margin.right).attr("stroke", "#e1e8e5")).call(group => group.select(".domain").remove());
  const published = data.filter(row => ["reviewed", "published"].includes(row.observationState));
  if (published.length > 1) svg.append("path").datum(published).attr("fill", "none").attr("stroke", "#247d8d").attr("stroke-width", 2.5).attr("d", d3.line().x(row => x(row.date)).y(row => y(row.area)));
  svg.append("g").selectAll("circle").data(data).join("circle").attr("cx", row => x(row.date)).attr("cy", row => y(row.area)).attr("r", 6).attr("fill", row => row.observationState === "processed" ? "#fbfcf8" : "#247d8d").attr("stroke", "#247d8d").attr("stroke-width", 2.5).append("title").text(row => `${row.date.toISOString().slice(0,10)} · ${formatArea(row.area)} · ${row.sensor} · ${row.observationState}`);
  const legend = svg.append("g").attr("transform", `translate(${margin.left},${height-12})`).attr("font-size", 11).attr("fill", "#617276");
  legend.append("circle").attr("cx", 6).attr("cy", 0).attr("r", 5).attr("fill", "#247d8d"); legend.append("text").attr("x", 17).attr("y", 4).text("reviewed / published");
  legend.append("circle").attr("cx", 172).attr("cy", 0).attr("r", 5).attr("fill", "#fbfcf8").attr("stroke", "#247d8d").attr("stroke-width", 2); legend.append("text").attr("x", 183).attr("y", 4).text("processed candidate");
}

function boundaryPolygons(featureCollection) {
  return featureCollection.features.flatMap(feature => {
    const geometry = feature.geometry || {};
    if (geometry.type === "Polygon") return [geometry.coordinates];
    if (geometry.type === "MultiPolygon") return geometry.coordinates;
    return [];
  });
}

async function setupBoundaryTimeline(rows) {
  const target = document.querySelector("#map"), controls = document.querySelector("#boundary-controls");
  if (!window.d3 || !rows.length) { target.innerHTML = noData("No published derived boundary is available."); return; }
  const loaded = await Promise.all(rows.map(async row => ({...row, geometry: await (await fetch(`../${row.boundary_geojson_url}`)).json()})));
  const items = loaded.map(item => ({...item, polygons: boundaryPolygons(item.geometry)})).filter(item => item.polygons.length);
  if (!items.length) { target.innerHTML = noData("Published boundary geometry is unavailable."); return; }
  const allPoints = items.flatMap(item => item.polygons.flat(2)), xs=allPoints.map(point=>point[0]), ys=allPoints.map(point=>point[1]);
  const minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys), width=400,height=300;
  const sx=x=>20+(x-minX)/(maxX-minX||1)*360, sy=y=>280-(y-minY)/(maxY-minY||1)*250;
  const ringPath=ring=>`${ring.map(([x,y],index)=>`${index?"L":"M"}${sx(x).toFixed(1)},${sy(y).toFixed(1)}`).join(" ")}Z`;
  const svg=window.d3.select(target).html("").append("svg").attr("viewBox",`0 0 ${width} ${height}`).attr("aria-label","Published lake-boundary timeline");
  svg.append("rect").attr("width",width).attr("height",height).attr("fill","#e8efec");
  svg.append("path").attr("d","M20 280H380M20 20V280").attr("stroke","#b7c6c2");
  let index=items.length-1;
  const label=document.querySelector("#boundary-label"),previous=document.querySelector("#boundary-prev"),next=document.querySelector("#boundary-next");
  const render=direction=>{const item=items[index],group=svg.append("g").attr("class","boundary-frame").attr("opacity",0).attr("transform",`translate(${direction*14},0)`);group.selectAll("path.water").data(item.polygons).join("path").attr("class","water").attr("d",rings=>rings.map(ringPath).join(" ")).attr("fill","#247d8d").attr("fill-opacity",.72).attr("stroke","#125563").attr("stroke-width",2).attr("fill-rule","evenodd").attr("clip-rule","evenodd");group.transition().duration(360).attr("opacity",1).attr("transform","translate(0,0)");svg.selectAll(".boundary-frame").filter(function(){return this!==group.node();}).transition().duration(300).attr("opacity",0).attr("transform",`translate(${-direction*14},0)`).remove();label.textContent=`${item.observed_at.slice(0,10)} · ${item.sensor} · ${formatArea(item.lake_area_km2)}`;previous.disabled=index===0;next.disabled=index===items.length-1;};
  previous.addEventListener("click",()=>{if(index>0){index-=1;render(-1);}});next.addEventListener("click",()=>{if(index<items.length-1){index+=1;render(1);}});controls.hidden=false;render(1);
}

function parseArchiveCsv(text) {
  const [header, ...lines] = text.trim().split("\n");
  const fields = header.split(",");
  return lines.filter(Boolean).map(line => Object.fromEntries(fields.map((field, i) => [field, line.split(",")[i] || ""])));
}

function drawObservability(archive, observability) {
  const target = document.querySelector("#observability-content");
  const latestPeriod = observability.periods.find(period => period.period_days === 365) || observability.periods.at(-1);
  const acquired = archive.filter(row => row.available === "True").length;
  const usable = archive.filter(row => row.usable === "True").length;
  const rejected = archive.filter(row => row.observation_state === "rejected").length;
  const published = archive.filter(row => ["reviewed", "published"].includes(row.observation_state)).length;
  target.innerHTML = metric("ARCHIVE ACQUIRED", acquired, "All scanned seasonal optical scenes") + metric("ARCHIVE USABLE", usable, "Candidates pending or after review") + metric("ARCHIVE REJECTED", rejected, "Retained with QA reasons") + metric("PUBLISHED", published, "Only these enter the public area series") + metric("LAST 365 DAYS", latestPeriod ? `${latestPeriod.optical_acquisitions} optical` : "—", latestPeriod ? `${latestPeriod.usable_optical} usable · ${latestPeriod.rejected_optical} rejected` : "No coverage summary");
  const recent = archive.filter(row => row.available === "True").sort((a, b) => b.observed_at.localeCompare(a.observed_at)).slice(0, 8);
  document.querySelector("#recent-scenes").innerHTML = recent.length ? `<h3>Recent assessed scenes</h3><table><thead><tr><th>Date</th><th>Sensor</th><th>State</th><th>Reason</th></tr></thead><tbody>${recent.map(row => `<tr><td>${row.observed_at.slice(0,10)}</td><td>${row.sensor || "—"}</td><td><span class="state state-${row.observation_state}">${row.observation_state}</span></td><td>${row.rejection_reasons || "Pending review"}</td></tr>`).join("")}</tbody></table>` : noData("No canonical-geometry scenes have been assessed yet.");
}

async function load() {
  const [latestResponse, archiveResponse, observabilityResponse] = await Promise.all([fetch(`${dataRoot}/latest/imja-tsho.json`), fetch(`${dataRoot}/archive/optical-scenes.csv`), fetch(`${dataRoot}/observability/imja-tsho.json`)]);
  if (!latestResponse.ok) throw new Error("Latest observation file could not be read.");
  const latest = await latestResponse.json();
  const archive = archiveResponse.ok ? parseArchiveCsv(await archiveResponse.text()) : [];
  const observability = observabilityResponse.ok ? await observabilityResponse.json() : {periods: []};
  const chartRows = archive.filter(row => ["processed", "reviewed", "published"].includes(row.observation_state) && Number.isFinite(Number(row.lake_area_km2))).map(row => ({date:row.observed_at.slice(0,10),area:Number(row.lake_area_km2),sensor:row.sensor,observationState:row.observation_state}));
  const publishedRows = chartRows.filter(row => ["reviewed", "published"].includes(row.observationState));
  const publishedBoundaries = archive.filter(row => ["reviewed", "published"].includes(row.observation_state) && row.boundary_geojson_url && Number.isFinite(Number(row.lake_area_km2))).sort((a,b)=>a.observed_at.localeCompare(b.observed_at));
  drawObservability(archive, observability);
  drawChart(chartRows);
  const target = document.querySelector("#latest-content"), provenance = document.querySelector("#provenance");
  const canonicalLatest = latest.latest_observation && latest.latest_observation.provenance?.geometry_version === observability.geometry_version;
  if (latest.status !== "valid_observation" || !canonicalLatest) {
    target.innerHTML = noData("No reviewed satellite observation is published. This interface will not substitute an assumed value.");
    document.querySelector("#map").innerHTML = noData("No reviewed derived boundary is published.");
    provenance.innerHTML = `<dt>Publication status</dt><dd>NO CANONICAL-GEOMETRY PUBLICATION</dd><dt>Archive geometry</dt><dd>${observability.geometry_version || "UNKNOWN"}</dd><dt>Note</dt><dd>The page retains older records on disk but will not present them as current after a geometry correction.</dd>`;
    return;
  }
  const obs=latest.latest_observation, previous=publishedRows.filter(r => r.date < obs.observed_at.slice(0,10)).at(-1), yearAgo=publishedRows.filter(r=>Math.abs(new Date(r.date)-new Date(obs.observed_at)) < 380*864e5 && Math.abs(new Date(r.date)-new Date(obs.observed_at)) > 300*864e5).at(-1);
  const delta = r => r ? `${(obs.value-r.area >= 0 ? "+" : "")}${(obs.value-r.area).toFixed(3)} km²` : "—";
  target.innerHTML = metric("AREA", formatArea(obs.value), "Derived probable-water extent") + metric("OBSERVED", new Date(obs.observed_at).toISOString().slice(0,10), obs.source) + metric("CHANGE / PREVIOUS", delta(previous), previous ? previous.date : "No prior valid observation") + metric("FRESHNESS", `<span class="fresh">${obs.freshness.status}</span>`, `${obs.freshness.age_days} days old · data age only`) + metric("CHANGE / ~1 YEAR", delta(yearAgo), yearAgo ? yearAgo.date : "No comparable annual record");
  provenance.innerHTML = `<dt>Source product</dt><dd>${obs.source_product}</dd><dt>Method</dt><dd>${obs.method} · v${obs.method_version}</dd><dt>Parameters</dt><dd>${JSON.stringify(obs.parameters)}</dd><dt>Quality flags</dt><dd>${obs.quality_flags.join(", ") || "None"}</dd><dt>Processed</dt><dd>${obs.processed_at}</dd><dt>Code revision</dt><dd>${obs.provenance.code_version}</dd>`;
  try { await setupBoundaryTimeline(publishedBoundaries); } catch { document.querySelector("#map").innerHTML=noData("Published boundary files could not be loaded."); }
}
load().catch(error => { document.querySelector("#latest-content").innerHTML=noData(error.message); document.querySelector("#map").innerHTML=noData("Data files unavailable; serve the repository through a web server."); });
