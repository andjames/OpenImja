const validationRoot = "../data/validation";
const numeric = (value, digits = 3, suffix = "") => value === "" || value == null || !Number.isFinite(Number(value)) ? "—" : `${Number(value).toFixed(digits)}${suffix}`;
const field = (label, value) => `<dt>${label}</dt><dd>${value || "—"}</dd>`;
const metric = (label, value, detail = "") => `<div class="metric"><span>${label}</span><b>${value}</b>${detail ? `<span>${detail}</span>` : ""}</div>`;

function parseCsv(text) {
  const rows = []; let row = [], value = "", quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index], next = text[index + 1];
    if (char === '"' && quoted && next === '"') { value += char; index += 1; }
    else if (char === '"') quoted = !quoted;
    else if (char === "," && !quoted) { row.push(value); value = ""; }
    else if ((char === "\n" || char === "\r") && !quoted) { if (char === "\r" && next === "\n") index += 1; row.push(value); if (row.some(cell => cell !== "")) rows.push(row); row = []; value = ""; }
    else value += char;
  }
  if (value || row.length) { row.push(value); rows.push(row); }
  const [header, ...body] = rows;
  return body.map(cells => Object.fromEntries(header.map((name, index) => [name, cells[index] || ""])));
}

function pairId(row) { return `${row.sentinel2_product_id}|${row.sentinel1_product_id}`; }
function polygons(feature) { if (!feature) return []; if (feature.geometry.type === "Polygon") return [feature.geometry.coordinates]; return feature.geometry.type === "MultiPolygon" ? feature.geometry.coordinates : []; }

function mapFrame(target, features, extent, layers, emptyText) {
  const element = document.querySelector(target);
  if (!window.d3) { element.textContent = "D3 could not be loaded."; return; }
  if (!features.length) { element.innerHTML = `<p class="empty">${emptyText}</p>`; return; }
  const width = 360, height = 270, pad = 20, [minX, maxX, minY, maxY] = extent;
  const x = value => pad + (value - minX) / (maxX - minX || 1) * (width - 2 * pad), y = value => height - pad - (value - minY) / (maxY - minY || 1) * (height - 2 * pad);
  const path = ring => `${ring.map(([lon, lat], index) => `${index ? "L" : "M"}${x(lon).toFixed(1)},${y(lat).toFixed(1)}`).join(" ")}Z`;
  const svg = window.d3.select(element).html("").append("svg").attr("viewBox", `0 0 ${width} ${height}`).attr("aria-label", "Paired lake-boundary comparison");
  svg.append("rect").attr("width", width).attr("height", height).attr("fill", "#e8efec"); svg.append("path").attr("d", `M${pad} ${height - pad}H${width - pad}M${pad} ${pad}V${height - pad}`).attr("stroke", "#b7c6c2");
  layers.forEach(layer => features.filter(feature => feature.properties.layer === layer.name).forEach(feature => polygons(feature).forEach(rings => svg.append("path").attr("d", rings.map(path).join(" ")).attr("fill", layer.fill).attr("fill-opacity", layer.opacity).attr("stroke", layer.stroke || layer.fill).attr("stroke-width", layer.width || 1.4).attr("fill-rule", "evenodd"))));
}

function sharedExtent(features) {
  const points = features.flatMap(feature => polygons(feature).flat(2)); if (!points.length) return [0, 1, 0, 1];
  const xs = points.map(point => point[0]), ys = points.map(point => point[1]), paddingX = Math.max((Math.max(...xs) - Math.min(...xs)) * .08, .00015), paddingY = Math.max((Math.max(...ys) - Math.min(...ys)) * .08, .00015);
  return [Math.min(...xs) - paddingX, Math.max(...xs) + paddingX, Math.min(...ys) - paddingY, Math.max(...ys) + paddingY];
}

function renderPair(row, geometry) {
  const pairFeatures = geometry.features.filter(feature => feature.properties.pair_id === pairId(row)), extent = sharedExtent(pairFeatures);
  const hasSarGeometry = pairFeatures.some(feature => feature.properties.layer === "sar");
  mapFrame("#optical-map", pairFeatures, extent, [{name:"optical", fill:"#247d8d", opacity:.72, stroke:"#125563", width:2}], "Optical boundary not retained.");
  mapFrame("#sar-map", pairFeatures, extent, [{name:"sar", fill:"#715b91", opacity:.68, stroke:"#4d3c70", width:2}], "No SAR lake geometry was retained: this scene was rejected before a defensible component was found.");
  if (hasSarGeometry) mapFrame("#difference-map", pairFeatures, extent, [{name:"optical", fill:"#d5e5e2", opacity:.55, stroke:"#8daaa4"}, {name:"sar", fill:"#eadbe9", opacity:.55, stroke:"#b48cad"}, {name:"optical_omission", fill:"#d97b36", opacity:.76, stroke:"#a95220"}, {name:"sar_commission", fill:"#bb4f8d", opacity:.76, stroke:"#8d3267"}, {name:"intersection", fill:"#247d8d", opacity:.9, stroke:"#125563", width:1.6}], "A spatial-difference layer is unavailable because no SAR geometry was retained.");
  else document.querySelector("#difference-map").innerHTML = "<p class=\"empty\">A spatial-difference layer is unavailable because no SAR geometry was retained.</p>";
  document.querySelector("#pair-metrics").innerHTML = metric("OPTICAL AREA", numeric(row.sentinel2_area_km2, 3, " km²"), row.sentinel2_observed_at.slice(0, 10)) + metric("SAR AREA", numeric(row.sentinel1_area_km2, 3, " km²"), row.sentinel1_observed_at.slice(0, 10)) + metric("TIME SEPARATION", numeric(row.temporal_separation_hours, 1, " h"), `${numeric(row.temporal_separation_days, 2, " days")} · SAR relative to optical`) + metric("AREA DIFFERENCE", numeric(row.absolute_area_difference_km2, 3, " km²"), `${numeric(row.percentage_area_difference, 1, "%")} of optical area`) + metric("POLYGON IoU", numeric(row.iou, 3), "Intersection over union; descriptive only");
  document.querySelector("#pair-provenance").innerHTML = field("Optical product", row.sentinel2_product_id) + field("SAR product", row.sentinel1_product_id) + field("SAR state", `<span class="state state-${row.sentinel1_state}">${row.sentinel1_state || "unknown"}</span>`) + field("Orbit / polarization", `${row.sentinel1_orbit_pass || "—"} / ${row.sentinel1_polarization || "—"}`) + field("SAR QA", row.sentinel1_quality_flags || "None") + field("Optical QA", row.sentinel2_quality_flags || "None") + field("Optical omission", numeric(row.optical_omission_fraction, 3)) + field("SAR commission", numeric(row.sar_commission_fraction, 3)) + field("Centroid displacement", numeric(row.centroid_displacement_degrees, 5, "°"));
}

async function loadValidation() {
  const [pairsResponse, geometryResponse] = await Promise.all([fetch(`${validationRoot}/s1-s2-pairs.csv`), fetch(`${validationRoot}/s1-s2-pair-geometries.geojson`)]);
  if (!pairsResponse.ok || !geometryResponse.ok) throw new Error("Validation artifacts are unavailable. Run the pairing and geometry build commands.");
  const pairs = parseCsv(await pairsResponse.text()), geometry = await geometryResponse.json(); if (!pairs.length) throw new Error("No Sentinel-1 / Sentinel-2 pairs are available yet.");
  let index = 0; const label = document.querySelector("#pair-label"), prev = document.querySelector("#pair-prev"), next = document.querySelector("#pair-next");
  const show = () => { const row = pairs[index]; label.textContent = `${row.sentinel2_observed_at.slice(0,10)} optical / ${row.sentinel1_observed_at.slice(0,10)} SAR · ${row.sentinel1_state || "unknown"}`; prev.disabled = index === 0; next.disabled = index === pairs.length - 1; renderPair(row, geometry); };
  prev.addEventListener("click", () => { if (index > 0) { index -= 1; show(); } }); next.addEventListener("click", () => { if (index < pairs.length - 1) { index += 1; show(); } }); show();
}

loadValidation().catch(error => { document.querySelector("#pair-label").textContent = error.message; ["#optical-map", "#sar-map", "#difference-map"].forEach(target => { document.querySelector(target).innerHTML = `<p class="empty">${error.message}</p>`; }); });
