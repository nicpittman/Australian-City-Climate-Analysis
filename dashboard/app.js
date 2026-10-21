const DATA = {
  comparisons: "../analysis/comparisons.csv",
  monthly: "../analysis/monthly_2026_anomalies.csv",
  weighted: "../analysis/population_weighted_proxy.csv",
  soi: "../analysis/soi_monthly_1980_2026.csv"
};

const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep"];
const measureLabels = {
  tmean_c: "mean temperature",
  tmax_c: "maximum temperature",
  tmin_c: "minimum temperature"
};
const order = ["Perth", "Adelaide", "Melbourne", "Sydney", "Brisbane", "Darwin", "Alice Springs", "Hobart"];
const state = {};

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines.shift().split(",");
  return lines.map(line => {
    const values = line.split(",");
    return Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""]));
  });
}

function unique(values) {
  return [...new Set(values)];
}

function optionList(select, values, selected) {
  select.innerHTML = values.map(value => `<option value="${value}"${value === selected ? " selected" : ""}>${value}</option>`).join("");
}

function svgNode(tag, attributes = {}, text = "") {
  const node = document.createElementNS("http://www.w3.org/2000/svg", tag);
  Object.entries(attributes).forEach(([key, value]) => node.setAttribute(key, value));
  if (text) node.textContent = text;
  return node;
}

function makeSvg(height) {
  return svgNode("svg", { viewBox: `0 0 1040 ${height}`, "aria-hidden": "true" });
}

function signed(value, digits = 2) {
  const number = Number(value);
  return `${number >= 0 ? "+" : ""}${number.toFixed(digits)}°C`;
}

function rangeWords(value) {
  return value
    .replace("Jan", "January")
    .replace("Apr", "April")
    .replace("May", "May")
    .replace("Aug", "August")
    .replace("Sep", "September")
    .replace("–", " to ");
}

function updateContextLabels() {
  const period = rangeWords(document.querySelector("#window").value);
  const baseline = rangeWords(document.querySelector("#baseline").value);
  const selected = `${period} 2026 compared with ${baseline}`;
  document.querySelector("#city-baseline").textContent = selected;
  document.querySelector("#monthly-baseline").textContent = `January to September 2026 compared with ${baseline}`;
  document.querySelector("#day-night-baseline").textContent = selected;
  document.querySelector("#rainfall-baseline").textContent = selected;
}

function currentRows() {
  const period = document.querySelector("#window").value;
  const baseline = document.querySelector("#baseline").value;
  const measure = document.querySelector("#measure").value;
  return state.comparisons.filter(row => row.primary === "True" && row.supported === "True" && row.window === period && row.baseline === baseline && row.element === measure);
}

function renderCards(rows) {
  const period = document.querySelector("#window").value;
  const baseline = document.querySelector("#baseline").value;
  const measure = document.querySelector("#measure").value;
  const weighted = state.weighted.find(row => row.window === period && row.baseline === baseline && row.element === measure);
  const warmest = [...rows].sort((a, b) => Number(b.anomaly) - Number(a.anomaly))[0];
  document.querySelector("#weighted").textContent = weighted ? signed(weighted.anomaly) : "Not available";
  document.querySelector("#warmest").textContent = warmest ? `${warmest.city} ${signed(warmest.anomaly)}` : "Not available";
  document.querySelector("#coverage").textContent = weighted ? `${(Number(weighted.share) * 100).toFixed(1)}%` : "Not available";
}

function renderCityChart(rows) {
  const holder = document.querySelector("#city-chart");
  holder.replaceChildren();
  const sorted = order.map(city => rows.find(row => row.city === city)).filter(Boolean);
  const width = 1040, height = 390, left = 135, right = 75, top = 20, bottom = 48;
  const innerWidth = width - left - right;
  const max = Math.max(1, ...sorted.map(row => Math.abs(Number(row.anomaly))));
  const limit = Math.ceil(max * 2) / 2;
  const x = value => left + ((value + limit) / (2 * limit)) * innerWidth;
  const svg = makeSvg(height);
  for (let tick = -limit; tick <= limit + .001; tick += limit / 2) {
    const px = x(tick);
    svg.append(svgNode("line", { x1: px, x2: px, y1: top, y2: height - bottom, class: Math.abs(tick) < .001 ? "zero" : "grid" }));
    svg.append(svgNode("text", { x: px, y: height - 19, "text-anchor": "middle", class: "axis" }, `${tick > 0 ? "+" : ""}${tick.toFixed(1)}`));
  }
  sorted.forEach((row, index) => {
    const value = Number(row.anomaly);
    const y = top + index * 40 + 5;
    const zero = x(0), end = x(value);
    svg.append(svgNode("text", { x: left - 14, y: y + 17, "text-anchor": "end", class: "axis" }, row.city));
    const bar = svgNode("rect", { x: Math.min(zero, end), y, width: Math.max(2, Math.abs(end - zero)), height: 24, rx: 3, fill: value >= 0 ? "#dc6500" : "#087fb8" });
    bar.append(svgNode("title", {}, `${row.city}: ${signed(value)} compared with ${row.baseline}`));
    svg.append(bar);
    svg.append(svgNode("text", { x: value >= 0 ? end + 8 : end - 8, y: y + 17, "text-anchor": value >= 0 ? "start" : "end", class: "value" }, signed(value)));
  });
  holder.append(svg);
  const days = sorted[0]?.current_days || "";
  document.querySelector("#city-note").textContent = `${measureLabels[document.querySelector("#measure").value]} • ${days} daily observations in the selected 2026 period`;
}

function heatColor(value, limit) {
  const strength = Math.min(1, Math.abs(value) / limit);
  const target = value >= 0 ? [220, 101, 0] : [8, 127, 184];
  const start = [244, 244, 238];
  return `rgb(${start.map((channel, index) => Math.round(channel + (target[index] - channel) * strength)).join(",")})`;
}

function renderHeatmap() {
  const baseline = document.querySelector("#baseline").value;
  const measure = document.querySelector("#measure").value;
  const column = `${measure.replace("_c", "")}_c_anomaly`;
  const rows = state.monthly.filter(row => row.baseline === baseline && order.includes(row.city));
  const width = 1040, height = 390, left = 135, top = 45, cellW = 92, cellH = 39;
  const values = rows.map(row => Number(row[column])).filter(Number.isFinite);
  const limit = Math.max(1, ...values.map(Math.abs));
  const svg = makeSvg(height);
  monthNames.forEach((month, index) => svg.append(svgNode("text", { x: left + index * cellW + cellW / 2, y: 25, "text-anchor": "middle", class: "axis" }, month)));
  order.forEach((city, cityIndex) => {
    const y = top + cityIndex * cellH;
    svg.append(svgNode("text", { x: left - 14, y: y + 24, "text-anchor": "end", class: "axis" }, city));
    monthNames.forEach((_, monthIndex) => {
      const row = rows.find(item => item.city === city && Number(item.month) === monthIndex + 1);
      if (!row) return;
      const value = Number(row[column]);
      const rect = svgNode("rect", { x: left + monthIndex * cellW, y, width: cellW - 4, height: cellH - 4, rx: 3, fill: heatColor(value, limit) });
      rect.append(svgNode("title", {}, `${city}, ${monthNames[monthIndex]}: ${signed(value)}`));
      svg.append(rect);
      svg.append(svgNode("text", { x: left + monthIndex * cellW + (cellW - 4) / 2, y: y + 23, "text-anchor": "middle", fill: Math.abs(value) / limit > .55 ? "white" : "#173f3b", "font-size": 12, "font-weight": 700 }, `${value >= 0 ? "+" : ""}${value.toFixed(1)}`));
    });
  });
  document.querySelector("#heatmap").replaceChildren(svg);
}

function renderAnnual() {
  const rows = state.annual.map(row => ({ year: Number(row.year), anomaly: Number(row.anomaly) }));
  const width = 1040, height = 340, left = 65, right = 35, top = 20, bottom = 52;
  const innerWidth = width - left - right, innerHeight = height - top - bottom;
  const firstYear = Math.min(...rows.map(row => row.year));
  const lastYear = Math.max(...rows.map(row => row.year));
  const max = Math.max(1, ...rows.map(row => Math.abs(row.anomaly)));
  const limit = Math.ceil(max * 2) / 2;
  const x = year => left + (year - firstYear) / (lastYear - firstYear) * innerWidth;
  const y = value => top + (limit - value) / (2 * limit) * innerHeight;
  const zero = y(0);
  const barWidth = Math.max(5, innerWidth / (lastYear - firstYear + 1) - 3);
  const svg = makeSvg(height);
  [-limit, -limit / 2, 0, limit / 2, limit].forEach(tick => {
    const py = y(tick);
    svg.append(svgNode("line", { x1: left, x2: width - right, y1: py, y2: py, class: Math.abs(tick) < .001 ? "zero" : "grid" }));
    svg.append(svgNode("text", { x: left - 10, y: py + 4, "text-anchor": "end", class: "axis" }, `${tick > 0 ? "+" : ""}${tick.toFixed(1)}`));
  });
  for (let year = Math.ceil(firstYear / 5) * 5; year <= lastYear; year += 5) {
    svg.append(svgNode("text", { x: x(year), y: height - 18, "text-anchor": "middle", class: "axis" }, year));
  }
  rows.forEach(row => {
    const py = y(row.anomaly);
    const bar = svgNode("rect", {
      x: x(row.year) - barWidth / 2,
      y: Math.min(zero, py),
      width: barWidth,
      height: Math.max(2, Math.abs(zero - py)),
      fill: row.anomaly >= 0 ? "#dc6500" : "#087fb8",
      opacity: row.year === 2026 ? 1 : .72,
    });
    bar.append(svgNode("title", {}, `${row.year}: ${signed(row.anomaly)}`));
    svg.append(bar);
  });
  document.querySelector("#annual-chart").replaceChildren(svg);
  document.querySelector("#annual-note").textContent = `${rows.length} years have complete January to September results for all eight city series. The series is a city population proxy, not a national land average.`;
}

function renderDayNight() {
  const period = document.querySelector("#window").value;
  const baseline = document.querySelector("#baseline").value;
  const rows = state.comparisons.filter(row => row.primary === "True" && row.supported === "True" && row.window === period && row.baseline === baseline);
  const paired = order.map(city => ({
    city,
    maximum: rows.find(row => row.city === city && row.element === "tmax_c"),
    minimum: rows.find(row => row.city === city && row.element === "tmin_c")
  })).filter(row => row.maximum && row.minimum);
  const width = 1040, height = 390, left = 135, right = 75, top = 48, bottom = 48;
  const innerWidth = width - left - right;
  const values = paired.flatMap(row => [Number(row.maximum.anomaly), Number(row.minimum.anomaly)]);
  const max = Math.max(1, ...values.map(Math.abs));
  const limit = Math.ceil(max * 2) / 2;
  const x = value => left + ((value + limit) / (2 * limit)) * innerWidth;
  const svg = makeSvg(height);
  svg.append(svgNode("circle", { cx: 700, cy: 17, r: 6, fill: "#dc6500" }));
  svg.append(svgNode("text", { x: 713, y: 21, class: "axis" }, "Maximum temperature"));
  svg.append(svgNode("circle", { cx: 875, cy: 17, r: 6, fill: "#00877d" }));
  svg.append(svgNode("text", { x: 888, y: 21, class: "axis" }, "Minimum temperature"));
  for (let tick = -limit; tick <= limit + .001; tick += limit / 2) {
    const px = x(tick);
    svg.append(svgNode("line", { x1: px, x2: px, y1: top, y2: height - bottom, class: Math.abs(tick) < .001 ? "zero" : "grid" }));
    const digits = Number.isInteger(tick * 2) ? 1 : 2;
    svg.append(svgNode("text", { x: px, y: height - 18, "text-anchor": "middle", class: "axis" }, `${tick > 0 ? "+" : ""}${tick.toFixed(digits)}`));
  }
  paired.forEach((row, index) => {
    const maximum = Number(row.maximum.anomaly);
    const minimum = Number(row.minimum.anomaly);
    const y = top + index * 36 + 15;
    svg.append(svgNode("text", { x: left - 14, y: y + 4, "text-anchor": "end", class: "axis" }, row.city));
    svg.append(svgNode("line", { x1: x(minimum), x2: x(maximum), y1: y, y2: y, stroke: "#9aaba8", "stroke-width": 3 }));
    const maxPoint = svgNode("circle", { cx: x(maximum), cy: y, r: 7, fill: "#dc6500" });
    maxPoint.append(svgNode("title", {}, `${row.city} maximum temperature: ${signed(maximum)}`));
    const minPoint = svgNode("circle", { cx: x(minimum), cy: y, r: 7, fill: "#00877d" });
    minPoint.append(svgNode("title", {}, `${row.city} minimum temperature: ${signed(minimum)}`));
    svg.append(maxPoint, minPoint);
  });
  document.querySelector("#day-night-chart").replaceChildren(svg);
}

function renderRainfall() {
  const period = document.querySelector("#window").value;
  const baseline = document.querySelector("#baseline").value;
  const rows = order.map(city => state.rainfall.find(row => row.city === city && row.window === period && row.baseline === baseline)).filter(Boolean);
  const minimumYears = baseline === "1980–1989" ? 8 : 20;
  const isUsable = row => row.ratio !== "" && Number(row.baseline_years) >= minimumYears && Number(row.current_days) === Number(row.expected_days);
  const usable = rows.filter(isUsable);
  const percentages = usable.map(row => Number(row.ratio) * 100);
  const limit = Math.max(150, Math.ceil(Math.max(100, ...percentages) / 25) * 25);
  const width = 1040, height = 390, left = 135, right = 75, top = 20, bottom = 55;
  const innerWidth = width - left - right;
  const x = value => left + value / limit * innerWidth;
  const svg = makeSvg(height);
  for (let tick = 0; tick <= limit; tick += 50) {
    const px = x(tick);
    svg.append(svgNode("line", { x1: px, x2: px, y1: top, y2: height - bottom, class: tick === 100 ? "baseline-line" : "grid" }));
    svg.append(svgNode("text", { x: px, y: height - 24, "text-anchor": "middle", class: "axis" }, `${tick}%`));
  }
  rows.forEach((row, index) => {
    const y = top + index * 39 + 4;
    svg.append(svgNode("text", { x: left - 14, y: y + 17, "text-anchor": "end", class: "axis" }, row.city));
    if (isUsable(row)) {
      const value = Number(row.ratio) * 100;
      const bar = svgNode("rect", { x: x(0), y, width: Math.max(2, x(value) - x(0)), height: 24, rx: 3, fill: value >= 100 ? "#00877d" : "#087fb8" });
      bar.append(svgNode("title", {}, `${row.city}: ${Number(row.current).toFixed(1)} mm, ${value.toFixed(0)}% of the ${rangeWords(baseline)} average`));
      svg.append(bar);
      svg.append(svgNode("text", { x: x(value) + 8, y: y + 17, class: "value" }, `${value.toFixed(0)}%`));
    } else {
      svg.append(svgNode("text", { x: left + 8, y: y + 17, fill: "#7a8987", "font-size": 12 }, "Insufficient complete record"));
    }
  });
  svg.append(svgNode("text", { x: left + innerWidth / 2, y: height - 3, "text-anchor": "middle", class: "axis" }, "Rainfall as a percentage of the historical average"));
  document.querySelector("#rainfall-chart").replaceChildren(svg);
  document.querySelector("#rainfall-rule").textContent = `Only cities with a complete 2026 period and at least ${minimumYears} complete baseline years are shown.`;
  document.querySelector("#rainfall-note").textContent = `${usable.length} of ${rows.length} cities meet the strict completeness rule for this selection. Rainfall is not population weighted.`;
}

function renderSoi() {
  const rows = state.soi.filter(row => Number(row.year) === 2026 && Number(row.month) <= 9);
  const width = 1040, height = 300, left = 65, right = 35, top = 22, bottom = 50;
  const innerWidth = width - left - right, innerHeight = height - top - bottom;
  const limit = 35;
  const x = index => left + index * innerWidth / (rows.length - 1);
  const y = value => top + (limit - value) * innerHeight / (2 * limit);
  const svg = makeSvg(height);
  [-30, -15, 0, 15, 30].forEach(tick => {
    svg.append(svgNode("line", { x1: left, x2: width - right, y1: y(tick), y2: y(tick), class: tick === 0 ? "zero" : "grid" }));
    svg.append(svgNode("text", { x: left - 10, y: y(tick) + 4, "text-anchor": "end", class: "axis" }, tick));
  });
  const points = rows.map((row, index) => `${x(index)},${y(Number(row.soi))}`).join(" ");
  svg.append(svgNode("polyline", { points, fill: "none", stroke: "#00877d", "stroke-width": 4, "stroke-linejoin": "round", "stroke-linecap": "round" }));
  rows.forEach((row, index) => {
    svg.append(svgNode("circle", { cx: x(index), cy: y(Number(row.soi)), r: 5, fill: "#00877d" }));
    svg.append(svgNode("text", { x: x(index), y: height - 20, "text-anchor": "middle", class: "axis" }, monthNames[index]));
  });
  document.querySelector("#soi-chart").replaceChildren(svg);
}

function render() {
  const rows = currentRows();
  updateContextLabels();
  renderCards(rows);
  renderCityChart(rows);
  renderHeatmap();
  renderAnnual();
  renderDayNight();
  renderRainfall();
  renderSoi();
}

async function start() {
  try {
    if (window.CLIMATE_RESULTS) {
      Object.assign(state, window.CLIMATE_RESULTS);
    } else {
      const entries = await Promise.all(Object.entries(DATA).map(async ([key, url]) => {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`${url} returned ${response.status}`);
        return [key, parseCsv(await response.text())];
      }));
      Object.assign(state, Object.fromEntries(entries));
      state.rainfall = state.comparisons.filter(row => row.element === "rain_mm");
    }
    optionList(document.querySelector("#window"), unique(state.comparisons.filter(row => row.primary === "True").map(row => row.window)), "Jan–Sep");
    optionList(document.querySelector("#baseline"), unique(state.comparisons.filter(row => row.primary === "True").map(row => row.baseline)), "2000–2025");
    document.querySelectorAll("select").forEach(select => select.addEventListener("change", render));
    render();
  } catch (error) {
    const message = document.querySelector("#error");
    message.hidden = false;
    message.textContent = `The dashboard could not load its results. Run python run.py --download to rebuild them. ${error.message}`;
  }
}

start();
