/* Gaza Disease & Care Map - static site. All numbers come from data/data.json (built from the
   SQLite views); nothing is computed here except choosing colours and drawing. */
"use strict";

const I18N = {
  ar: {
    title: "خريطة الأمراض والرعاية في غزة",
    sub: "بيانات مجمّعة من مصادر عامة عن الأمراض غير الناتجة عن الإصابات المباشرة، 2024–2026",
    banner: "بيانات مجمّعة من مصادر عامة، وليست نصيحة طبية ولا تشخيصاً. الحالات المعروضة «مشتبه بها» من المرافق التي تبلّغ فقط، والمعدلات تقريبية ولا تُقارَن مع بلدان أخرى. اقرأ «حدود البيانات» أسفل الصفحة.",
    tabs: { disease: "حسب المرض", location: "حسب المكان", medicine: "حسب فئة الدواء" },
    disease: "المرض", year: "الفترة", yearOpt: (y, w) => y + " (الأسابيع 1–" + w + ")",
    unit: "حالات لكل 1,000 استشارة",
    noData: "لا بيانات كافية", partial: "تغطية ضعيفة", notComparable: "غير قابل للمقارنة",
    legendTitle: "حالات لكل 1,000 استشارة:", legendGap: "لا بيانات كافية / غير قابل للمقارنة",
    mapNote: "الألوان تقارن المحافظات الخمس في الفترة المختارة. الرمادي: غُطّي أقل من 40% من الأسابيع، أو أن المرض لم يكن مُدرجاً في النظام. حدود المحافظات إدارية من OCHA قبل الحرب، ولا تعكس خطوط السيطرة الحالية.",
    reported: (a, b) => "وصل التقرير في " + a + " من " + b + " أسبوعاً",
    trend: "الاتجاه الشهري", trendNote: "الفجوات في الخط تعني أشهراً لم تصل عنها تقارير كافية (أقل من 3 أسابيع)، لا أنها صفر.",
    strip: "قطاع غزة (مجمَّع)", rank: "ترتيب المحافظات", cases: "حالة", weeks: "أسبوع",
    pickLoc: "اختر محافظة من الخريطة لعرض تفاصيلها.", location: "المحافظة", allDiseases: "كل الأمراض (نفس الأسابيع)",
    disease_col: "المرض", ncd: "الأمراض المزمنة والصحة النفسية: جاهزية الخدمات (HeRAMS، يونيو 2025)",
    avail: "متاحة", part: "متاحة جزئياً", notav: "غير متاحة", notnorm: "لا تُقدَّم عادةً",
    hsdu: "وحدات الخدمة الصحية التي تعمل ولو جزئياً", noHerams: "لا صفحة لهذه المحافظة في تقرير HeRAMS.",
    under5: "حصة الأطفال دون 5 سنوات من حالات الإسهال المائي الحاد",
    coverage: "تغطية التبليغ الأسبوعي", lateNote: "أُضيف هذا المرض إلى النظام في منتصف 2025؛ أرقام 2025 جزئية ولا تُقارَن بـ 2026.",
    medTitle: "حسب فئة الدواء",
    medBody: "هذا القسم فارغ عمداً. ربط المرض بفئة الدواء يحتاج مصدراً لكل سطر (إرشادات WHO أو تقارير الإمداد)، ولا نكتبه من الذاكرة. ولا نعرض أسماء أدوية أو جرعات في أي حال: الدواء يقرره الطبيب.",
    limitsH: "حدود البيانات",
    limits: [
      "المصدر الرئيسي (EWARS) يعدّ حالات مشتبه بها من مرافق مبلِّغة فقط، وعدد هذه المرافق يتغير، لذا نقسم على إجمالي الاستشارات. هذا مقياس تقريبي وليس معدل إصابة.",
      "إجمالي الاستشارات يشمل إصابات الحرب، فتركيبة المرافق تؤثر في المعدل. انخفاض معدل لا يعني بالضرورة تحسناً.",
      "أسابيع كثيرة لم يصل عنها تقرير، خاصة في 2024 (الشمال 25 من 52 أسبوعاً). الأسبوع الغائب ليس صفراً.",
      "لا يوجد في هذه المصادر: الجنس، اللغة، الحساسية والربو، أو أي تفصيل أدق من المحافظة.",
      "الجدري المائي والجرب/القمل والقوباء أُضيفت إلى النظام في منتصف 2025، فلا تُقارَن السنوات قبلها.",
      "جاهزية الخدمات (HeRAMS) تخص المرافق التي تبلّغ HeRAMS فقط، وتقرير WHO غير نهائي؛ لا توجد صفحة لرفح.",
      "لم نتحقق سريرياً من أي شيء. هذا عرض للبيانات المنشورة وليس تقييماً صحياً.",
    ],
    sourcesH: "المصادر",
    foot: (m) => "آخر أسبوع في البيانات: " + m.last_year + "، الأسبوع " + m.last_week + ". تاريخ البناء: " + m.generated + ". حدود المحافظات: OCHA / HDX COD-AB.",
    srcType: { "official statistic": "إحصاء رسمي", "survey": "مسح", "modelled estimate": "تقدير نمذجي", "press coverage": "تغطية صحفية" },
    lang: "English",
  },
  en: {
    title: "Gaza Disease & Care Map",
    sub: "Aggregated public data on non-injury health conditions in the Gaza Strip, 2024–2026",
    banner: "Aggregated data from public sources. Not medical advice and not a diagnosis. Cases are suspected cases from reporting facilities only, and rates are approximate and not comparable with other countries. Read “Limits of the data” below.",
    tabs: { disease: "By disease", location: "By location", medicine: "By medicine class" },
    disease: "Disease", year: "Period", yearOpt: (y, w) => y + " (weeks 1–" + w + ")",
    unit: "cases per 1,000 consultations",
    noData: "Not enough data", partial: "Low coverage", notComparable: "Not comparable",
    legendTitle: "Cases per 1,000 consultations:", legendGap: "Not enough data / not comparable",
    mapNote: "Colours compare the five governorates in the chosen period. Grey: under 40% of weeks reported, or the disease was not yet in the system. Governorate limits are OCHA pre-war administrative boundaries and do not show present-day control lines.",
    reported: (a, b) => "reported in " + a + " of " + b + " weeks",
    trend: "Monthly trend", trendNote: "Gaps in a line are months with too few reports (under 3 weeks), not zeros.",
    strip: "Gaza Strip (pooled)", rank: "Governorate ranking", cases: "cases", weeks: "weeks",
    pickLoc: "Pick a governorate on the map to see its details.", location: "Governorate", allDiseases: "All diseases (same weeks)",
    disease_col: "Disease", ncd: "NCD and mental health: service readiness (HeRAMS, June 2025)",
    avail: "Available", part: "Partially available", notav: "Not available", notnorm: "Not normally provided",
    hsdu: "Health service delivery units at least partially functioning", noHerams: "No page for this governorate in the HeRAMS report.",
    under5: "Share of acute watery diarrhoea cases in children under 5",
    coverage: "Weekly reporting coverage", lateNote: "This disease was added to the system in mid-2025; 2025 figures are partial and not comparable with 2026.",
    medTitle: "By medicine class",
    medBody: "This section is intentionally empty. Linking a disease to a medicine class needs a source for every row (WHO guidance or supply reports) and we will not write it from memory. We never show drug names or doses: medicines are decided by a doctor.",
    limitsH: "Limits of the data",
    limits: [
      "The main source (EWARS) counts suspected cases from reporting facilities only, and the number of facilities changes, so we divide by total consultations. This is a proxy, not an incidence rate.",
      "Total consultations include war injuries, so the facility mix affects the rate. A falling rate does not necessarily mean things improved.",
      "Many weeks never reported, especially in 2024 (North Gaza 25 of 52 weeks). A missing week is not a zero.",
      "Not available in these sources: sex, language, allergies and asthma, or anything finer than governorate.",
      "Chickenpox, ectoparasitic infections and impetigo were added mid-2025, so earlier years are not comparable.",
      "Service readiness (HeRAMS) covers only facilities that report to HeRAMS, WHO says the analysis is not final, and Rafah has no page.",
      "Nothing here is clinically validated. This displays published data; it is not a health assessment.",
    ],
    sourcesH: "Sources",
    foot: (m) => "Latest week in the data: " + m.last_year + " week " + m.last_week + ". Built " + m.generated + ". Boundaries: OCHA / HDX COD-AB.",
    srcType: { "official statistic": "official statistic", "survey": "survey", "modelled estimate": "modelled estimate", "press coverage": "press coverage" },
    lang: "العربية",
  },
};

const COLORS = ["#eaf2f7", "#bcd7e6", "#82b2cf", "#3f84ad", "#14527a"];   // 5 sequential steps
const GAP_COLOR = "#d9d9d9";
const LINE_COLORS = { gaza: "#1b6ca8", north_gaza: "#d1495b", deir_al_balah: "#2e8b57", khan_yunis: "#e08e0b", rafah: "#7b4fa3", strip: "#222222" };
const DOMAIN_COLORS = ["#2e8b57", "#9fcf9f", "#e0b84c", "#c9c9c9"];
const MIN_COVERAGE = 0.4;

const state = { lang: localStorageGet("lang") || "ar", tab: "disease", disease: "ari", year: null, loc: null };
let DATA, GEO, map, layers = {};

function localStorageGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function localStorageSet(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } }

const T = () => I18N[state.lang];
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const fmt = (n) => (n === null || n === undefined ? "–" : Number(n).toLocaleString("en", { maximumFractionDigits: 2 }));
const diseaseName = (d) => (state.lang === "ar" ? d.name_ar : d.name_en);
const locName = (l) => (state.lang === "ar" ? l.name_ar : l.name_en);
const dis = (key) => DATA.diseases.find((d) => d.key === key);
const loc = (key) => DATA.locations.find((l) => l.key === key);

/* ---- value lookup: what the map shows for (disease, location, year) ---- */
function cell(disease, locKey, year) {
  const y = (((DATA.yearly[disease] || {})[locKey]) || {})[String(year)];
  if (!y) return { status: "nodata" };
  if (!y.comparable) return { ...y, status: "notcomparable" };
  const window = DATA.meta.last_week;
  const perLoc = locKey === "strip" ? y.weeks / 5 : y.weeks;   // strip counts location-weeks
  if (perLoc < MIN_COVERAGE * window) return { ...y, status: "partial" };
  return { ...y, status: "ok" };
}

function scale(values) {
  const max = Math.max(...values, 0.0001);
  const step = max / COLORS.length;
  return { max, color: (v) => COLORS[Math.min(COLORS.length - 1, Math.floor(v / step))], step };
}

/* ---- map ---- */
function initMap() {
  // no basemap tiles => Leaflet has no zoom limits unless we set them (otherwise fitBounds returns NaN)
  map = L.map("map", { zoomControl: true, attributionControl: true, scrollWheelZoom: false, zoomSnap: 0.25, minZoom: 8, maxZoom: 14 });
  map.attributionControl.setPrefix(false);
  map.attributionControl.addAttribution("Boundaries: OCHA / HDX COD-AB");
  const layer = L.geoJSON(GEO, {
    style: { weight: 1.5, color: "#ffffff", fillOpacity: 0.95, fillColor: GAP_COLOR },
    onEachFeature: (f, lyr) => {
      layers[f.properties.key] = lyr;
      lyr.on("click", () => { state.loc = f.properties.key; render(); });
    },
  }).addTo(map);
  map.fitBounds(layer.getBounds(), { padding: [10, 10] });
}

function paintMap() {
  const t = T();
  const keys = Object.keys(layers);
  const cells = Object.fromEntries(keys.map((k) => [k, cell(state.disease, k, state.year)]));
  const okVals = keys.filter((k) => cells[k].status === "ok").map((k) => cells[k].per_1000);
  const sc = scale(okVals);
  keys.forEach((k) => {
    const c = cells[k];
    const l = layers[k];
    l.setStyle({ fillColor: c.status === "ok" ? sc.color(c.per_1000) : GAP_COLOR,
                 weight: state.loc === k ? 3.5 : 1.5, color: state.loc === k ? "#111" : "#ffffff" });
    const name = locName(loc(k));
    const lines = [`<strong>${esc(name)}</strong>`];
    if (c.status === "ok" || c.status === "partial") {
      lines.push(`${fmt(c.per_1000)} ${esc(t.unit)}`, `${fmt(c.cases)} ${esc(t.cases)}`, esc(t.reported(c.weeks, DATA.meta.last_week)));
      if (c.status === "partial") lines.push(`<em>${esc(t.partial)}</em>`);
    } else if (c.status === "notcomparable") {
      lines.push(`<em>${esc(t.notComparable)}</em>`);
    } else {
      lines.push(`<em>${esc(t.noData)}</em>`);
    }
    l.unbindTooltip();
    l.bindTooltip(lines.join("<br>"), { sticky: true, direction: "top", className: "gov-tip" });
    l.unbindPopup();
  });
  // permanent short labels
  keys.forEach((k) => {
    const c = cells[k];
    // the map container is forced LTR (Leaflet), so give each label its own direction
    const txt = `<span dir="${state.lang === "ar" ? "rtl" : "ltr"}">${esc(locName(loc(k)))}${c.status === "ok" ? ": " + fmt(c.per_1000) : ""}</span>`;
    layers[k].unbindTooltip();
    layers[k].bindTooltip(txt, { permanent: true, direction: "center", className: "gov-label" });
  });
  // legend
  const leg = [`<span>${esc(t.legendTitle)}</span>`];
  if (okVals.length) {
    COLORS.forEach((c, i) => {
      const a = i * sc.step, b = (i + 1) * sc.step;
      leg.push(`<span><i style="background:${c}"></i>${fmt(a)}–${fmt(b)}</span>`);
    });
  }
  leg.push(`<span><i style="background:${GAP_COLOR}"></i>${esc(t.legendGap)}</span>`);
  $("legend").innerHTML = leg.join("");
}

/* ---- trend chart: monthly per-1,000 lines, gaps where months are missing ---- */
function trendSvg(disease) {
  const W = 620, H = 260, m = { l: 44, r: 10, t: 10, b: 28 };
  const series = DATA.monthly[disease] || {};
  const keys = ["strip", "gaza", "north_gaza", "deir_al_balah", "khan_yunis", "rafah"].filter((k) => series[k]);
  const all = keys.flatMap((k) => series[k].map((p) => p[3]));
  if (!all.length) return `<p class="note">${esc(T().noData)}</p>`;
  const ymax = Math.max(...all) * 1.08 || 1;
  const n = DATA.months.length;
  const x = (i) => m.l + (i / (n - 1)) * (W - m.l - m.r);
  const y = (v) => H - m.b - (v / ymax) * (H - m.t - m.b);
  let svg = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(T().trend)}" dir="ltr">`;
  for (let g = 0; g <= 4; g++) {
    const v = (ymax * g) / 4;
    svg += `<line x1="${m.l}" x2="${W - m.r}" y1="${y(v)}" y2="${y(v)}" stroke="#e5e2d9"/><text x="${m.l - 6}" y="${y(v) + 4}" text-anchor="end">${fmt(Math.round(v * 10) / 10)}</text>`;
  }
  DATA.months.forEach((mo, i) => {
    if (mo.endsWith("-01") || mo.endsWith("-07")) svg += `<text x="${x(i)}" y="${H - 8}" text-anchor="middle">${mo}</text>`;
  });
  keys.forEach((k) => {
    const pts = series[k];
    let d = "", prev = -2;
    pts.forEach(([mi, , , v]) => { d += (mi === prev + 1 ? "L" : "M") + x(mi).toFixed(1) + " " + y(v).toFixed(1); prev = mi; });
    const dash = k === "strip" ? ' stroke-dasharray="5 3"' : "";
    svg += `<path d="${d}" fill="none" stroke="${LINE_COLORS[k]}" stroke-width="${k === "strip" ? 2.5 : 1.6}"${dash}/>`;
    pts.forEach(([mi, cases, cons, v, wk]) => {
      svg += `<circle cx="${x(mi).toFixed(1)}" cy="${y(v).toFixed(1)}" r="${k === "strip" ? 2.6 : 2}" fill="${LINE_COLORS[k]}"><title>${esc(locName(loc(k)))} · ${DATA.months[mi]}: ${fmt(v)} (${fmt(cases)} ${esc(T().cases)}, ${wk} ${esc(T().weeks)})</title></circle>`;
    });
  });
  svg += "</svg>";
  const key = keys.map((k) => `<span class="${k === "strip" ? "dash" : ""}" style="--c:${LINE_COLORS[k]}">${esc(k === "strip" ? T().strip : locName(loc(k)))}</span>`).join("");
  return svg + `<div class="key">${key}</div>`;
}

function rankingHtml() {
  const t = T();
  const rows = DATA.locations.filter((l) => l.level === "governorate").map((l) => ({ l, c: cell(state.disease, l.key, state.year) }));
  const vals = rows.filter((r) => r.c.status === "ok").map((r) => r.c.per_1000);
  const max = Math.max(...vals, 0.0001);
  rows.sort((a, b) => (b.c.per_1000 || -1) - (a.c.per_1000 || -1));
  const body = rows.map(({ l, c }) => {
    const shown = c.status === "ok" || c.status === "partial";
    const tag = c.status === "partial" ? ` <span class="pill">${esc(t.partial)}</span>` : c.status === "notcomparable" ? ` <span class="pill">${esc(t.notComparable)}</span>` : "";
    return `<tr><td>${esc(locName(l))}${tag}</td><td class="num">${shown ? fmt(c.per_1000) : "–"}</td>
      <td style="width:35%">${c.status === "ok" ? `<div class="bar" style="width:${(100 * c.per_1000 / max).toFixed(0)}%"></div>` : ""}</td>
      <td class="num dim">${shown ? fmt(c.cases) : ""}</td><td class="num dim">${shown ? esc(c.weeks) : ""}</td></tr>`;
  }).join("");
  const s = cell(state.disease, "strip", state.year);
  const strip = s.status === "ok" || s.status === "partial"
    ? `<p><span class="big">${fmt(s.per_1000)}</span> ${esc(t.unit)} · ${esc(t.strip)} · ${fmt(s.cases)} ${esc(t.cases)}</p>` : "";
  return `${strip}<h3>${esc(t.rank)}</h3><table><thead><tr><th>${esc(t.location)}</th><th class="num">${esc(t.unit)}</th><th></th><th class="num">${esc(t.cases)}</th><th class="num">${esc(t.weeks)}</th></tr></thead><tbody>${body}</tbody></table>`;
}

function stackHtml(vals) {
  return `<div class="stack">${vals.map((v, i) => `<span style="width:${v}%;background:${DOMAIN_COLORS[i]}" title="${v}%"></span>`).join("")}</div>`;
}

function locationHtml() {
  const t = T();
  if (!state.loc || state.loc === "strip") return `<p class="note">${esc(t.pickLoc)}</p>`;
  const l = loc(state.loc);
  const years = Object.keys(DATA.yearly.ari[state.loc] || {}).sort();
  const rows = DATA.diseases.map((d) => {
    const cs = years.map((y) => cell(d.key, state.loc, y));
    return { d, cs, sel: cs[years.indexOf(String(state.year))] };
  }).filter((r) => r.cs.some((c) => c.status === "ok" || c.status === "partial"));
  rows.sort((a, b) => ((b.sel && b.sel.per_1000) || 0) - ((a.sel && a.sel.per_1000) || 0));
  const head = years.map((y) => `<th class="num">${y}</th>`).join("");
  const body = rows.map((r) => `<tr><td>${esc(diseaseName(r.d))}</td>${r.cs.map((c) => {
    const ok = c.status === "ok" || c.status === "partial";
    return `<td class="num ${c.status === "ok" ? "" : "dim"}">${ok ? fmt(c.per_1000) + (c.status === "ok" ? "" : "*") : "–"}</td>`;
  }).join("")}</tr>`).join("");
  const cov = DATA.coverage[state.loc] || {};
  const covTxt = years.map((y) => cov[y] ? `${y}: ${cov[y][1]}/${cov[y][0]}` : "").filter(Boolean).join(" · ");
  const dom = (DATA.herams.domains[state.loc] || {})["NCD and mental health"];
  const hs = DATA.herams.hsdu[state.loc];
  const herams = dom ? `<h3>${esc(t.ncd)}</h3>${stackHtml(dom)}
      <div class="key" style="margin-top:4px">${[t.avail, t.part, t.notav, t.notnorm].map((n, i) => `<span style="--c:${DOMAIN_COLORS[i]}">${esc(n)} ${dom[i]}%</span>`).join("")}</div>
      ${hs ? `<p class="note">${esc(t.hsdu)}: ${hs[1]} / ${hs[0]}</p>` : ""}`
    : `<h3>${esc(t.ncd)}</h3><p class="note">${esc(t.noHerams)}${hs ? " " + esc(t.hsdu) + ": " + hs[1] + " / " + hs[0] : ""}</p>`;
  const u5 = DATA.awd_under5_share[state.loc] || {};
  const u5txt = years.filter((y) => u5[y] !== undefined).map((y) => `${y}: ${u5[y]}%`).join(" · ");
  return `<h2>${esc(locName(l))}</h2><h3>${esc(t.allDiseases)} · ${esc(t.unit)}</h3>
    <table><thead><tr><th>${esc(t.disease_col)}</th>${head}</tr></thead><tbody>${body}</tbody></table>
    <p class="note">* ${esc(t.partial)}</p>
    ${herams}
    <h3>${esc(t.under5)}</h3><p>${esc(u5txt)}</p>
    <h3>${esc(t.coverage)}</h3><p class="note">${esc(covTxt)}</p>`;
}

/* ---- rendering ---- */
function render() {
  const t = T();
  document.documentElement.lang = state.lang;
  document.documentElement.dir = state.lang === "ar" ? "rtl" : "ltr";
  $("t-title").textContent = t.title; $("t-sub").textContent = t.sub; $("t-banner").textContent = t.banner;
  $("lang").textContent = t.lang;
  $("l-disease").textContent = t.disease; $("l-year").textContent = t.year;
  $("tabs").innerHTML = ["disease", "location", "medicine"].map((k) =>
    `<button role="tab" type="button" data-tab="${k}" aria-selected="${state.tab === k}">${esc(t.tabs[k])}</button>`).join("");
  $("disease").innerHTML = DATA.diseases.map((d) => `<option value="${d.key}"${d.key === state.disease ? " selected" : ""}>${esc(diseaseName(d))}</option>`).join("");
  const years = Object.keys(DATA.yearly.ari.strip).sort();
  if (!state.year) state.year = years[years.length - 1];
  $("year").innerHTML = years.map((y) => `<option value="${y}"${y === String(state.year) ? " selected" : ""}>${esc(t.yearOpt(y, DATA.meta.last_week))}</option>`).join("");
  $("controls").hidden = state.tab === "medicine";
  $("l-disease-wrap").style.display = state.tab === "location" ? "none" : "";
  const d = dis(state.disease);
  const showNote = d.late_added && state.tab !== "medicine";
  $("disease-note").hidden = !showNote;
  $("disease-note").className = "note warn";
  $("disease-note").textContent = showNote ? t.lateNote : "";
  $("map-note").textContent = t.mapNote;
  paintMap();
  let panel;
  if (state.tab === "disease") {
    panel = `<h2>${esc(diseaseName(d))} · ${esc(t.trend)}</h2>${trendSvg(state.disease)}<p class="note">${esc(t.trendNote)} ${esc(t.unit)}.</p>${rankingHtml()}`;
  } else if (state.tab === "location") {
    panel = locationHtml();
  } else {
    panel = `<h2>${esc(t.medTitle)}</h2><p>${esc(t.medBody)}</p>`;
  }
  $("panel").innerHTML = panel;
  $("t-limits-h").textContent = t.limitsH;
  $("t-limits").innerHTML = t.limits.map((s) => `<li>${esc(s)}</li>`).join("");
  $("t-sources-h").textContent = t.sourcesH;
  $("sources").innerHTML = DATA.meta.sources.map((s) =>
    `<li><strong>${esc(s.name)}</strong> — ${esc(s.publisher)} · ${esc(t.srcType[s.type] || s.type)} · ${esc(s.data_up_to)}<br><span class="note">${esc(s.caveats)}</span></li>`).join("");
  $("t-foot").textContent = t.foot(DATA.meta);
  document.title = t.title;
  if (map) setTimeout(() => map.invalidateSize(), 0);
}

async function main() {
  const [d, g] = await Promise.all([fetch("data/data.json").then((r) => r.json()), fetch("data/governorates.geojson").then((r) => r.json())]);
  DATA = d; GEO = g;
  initMap();
  $("lang").addEventListener("click", () => { state.lang = state.lang === "ar" ? "en" : "ar"; localStorageSet("lang", state.lang); render(); });
  $("tabs").addEventListener("click", (e) => { const b = e.target.closest("button[data-tab]"); if (b) { state.tab = b.dataset.tab; if (state.tab === "location" && !state.loc) state.loc = "gaza"; render(); } });
  $("disease").addEventListener("change", (e) => { state.disease = e.target.value; render(); });
  $("year").addEventListener("change", (e) => { state.year = e.target.value; render(); });
  render();
}
main().catch((e) => { document.body.insertAdjacentHTML("afterbegin", `<p class="banner">Failed to load data: ${esc(e.message)}</p>`); });
