/* Gaza Disease & Care Map - static site. All numbers come from data/data.json (built from the
   SQLite views); nothing is computed here except choosing colours and drawing. */
"use strict";

const I18N = {
  ar: {
    title: "خريطة الأمراض والرعاية في غزة",
    sub: "بيانات مجمّعة من مصادر عامة عن الأمراض غير الناتجة عن الإصابات المباشرة، من 2024 إلى 2026",
    banner: "بيانات مجمّعة من مصادر عامة، وليست نصيحة طبية ولا تشخيصاً. الحالات المعروضة «مشتبه بها» من المرافق التي تبلّغ فقط، والمعدلات تقريبية ولا تُقارَن مع بلدان أخرى. اقرأ «حدود البيانات» أسفل الصفحة.",
    tabs: { findings: "الخلاصة", disease: "حسب المرض", location: "حسب المكان", medicine: "حسب فئة الدواء" },
    disease: "المرض", year: "الفترة", yearOpt: (y, w) => y + " · حتى الأسبوع " + w,
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
    sitesTitle: "عدد المواقع التي أبلغت (شهرياً، متوسط الأسابيع)",
    sitesShade: "أشهر بأقل من 20 موقعاً مبلِّغاً: لا تُقارَن بغيرها",
    sitesNote: (m) => "عدد المواقع المبلِّغة (الوسيط الأسبوعي): " + Object.entries(m).map(([y, v]) => y + ": " + v).join(" · ") + ". في أول 14 أسبوعاً من 2024 أبلغ بين 1 و9 مواقع فقط، لذلك لا تُقارَن معدلات 2024 بالسنتين التاليتين.",
    medTitle: "حسب فئة الدواء",
    medBody: "كل سطر هنا له مصدر (صفحات علاج في WHO أو CDC) ويذكر فئة الدواء فقط، لا اسماً ولا جرعة: الدواء والجرعة يقررهما الطبيب. هذه إرشادات عامة وليست خاصة بغزة، وليست وصفة.",
    medDisease: "المرض", medClasses: "فئات الدواء في إرشادات العلاج", medRate: "حالات لكل 1000 مراجعة (القطاع)", medSrc: "المصدر",
    medNone: "لا توجد فئة دواء موثّقة لهذه الأمراض (النكاف، الإسهال الدموي، الشلل الرخو الحاد): لا مصدر فلا سطر.",
    supTitle: "مؤشرات نقص الإمداد: نسبة الأدوية الأساسية عند «صفر مخزون»",
    supBody: "المصادر تتعارض في تواريخ متقاربة، لذلك لا نجمعها ولا نرسم خطاً واحداً: كل رقم مع مصدره وتاريخه وصياغته الأصلية. أرقام وزارة الصحة كما تنقلها منظمة الصحة العالمية، وتعريف «صفر مخزون» غير مذكور فيها.",
    supDate: "التاريخ", supPct: "النسبة", supWord: "الصياغة", ncdSvcTitle: "جاهزية خدمات الأمراض المزمنة والصحة النفسية على مستوى القطاع (HeRAMS، يونيو 2025)",
    ncdSvcNote: "عدد الوحدات المتوقعة صغير في بعض الخدمات (3 إلى 33)، فالنسب تتغير كثيراً بوحدة واحدة. الترجمة العربية لأسماء الخدمات من إعدادنا.",
    ncdSvcHead: ["الخدمة", "متاحة", "جزئياً", "غير متاحة", "وحدات متوقعة", "دون المعيار"],
    copyLink: "نسخ رابط هذا العرض", copied: "تم النسخ", dlCsv: "تنزيل البيانات (CSV)", sites: "موقعاً مبلِّغاً",
    calcH: "كيف حُسب هذا الرقم؟",
    calc: (c, w) => `الحالات ÷ الاستشارات × 1000${formula(c)}الأسابيع من 1 إلى ${ltr(w)} فقط، لتُقارَن السنة الجارية بغيرها على الأسابيع نفسها. نجمع الحالات والاستشارات أولاً ثم نقسم (لا نأخذ متوسط معدلات). المصدر: EWARS.`,
    clipped: "▲ نقاط فوق السقف: أشهر بمواقع مبلِّغة قليلة جداً، قيمتها في التلميح؛ المحور مضبوط على الأشهر القابلة للمقارنة.",
    y2024: "† 2024: عدد المواقع المبلِّغة كان أقل بكثير (الوسيط 32.5 مقابل 201 في 2026)، فلا يُقارَن هذا العمود بغيره.",
    fTitle: "الخلاصة: ما تقوله البيانات، وما لا تقوله",
    fIntro: "كل رقم هنا محسوب من بيانات الموقع نفسها عند التحميل، وله رابط إلى العرض الذي يأتي منه. لا شيء مكتوب باليد.",
    fOpen: "افتح العرض", fCaveat: "تحفّظ",
    f1: (v, c, y) => [`${v}`, `لكل 1000 استشارة: التهاب الجهاز التنفسي الحاد هو الأكثر تسجيلاً في ${y} (${c} حالة مشتبهة)`, "الاستشارات تشمل إصابات الحرب، والمعدل ليس معدل إصابة في السكان."],
    f2: (v, a, y) => [`${v}`, `لكل 1000 استشارة: الجرب/القمل والقوباء والجدري المائي معاً في ${y}، أعلى من الإسهال المائي (${a})`, "هذه الأمراض أُضيفت للنظام منتصف 2025، فلا نقارنها بما قبل. الجمع صحيح لأن المقام واحد."],
    f3: (g, v, y) => [`${v}`, `لكل 1000 استشارة: ${g} أعلى محافظة في الإسهال المائي الحاد في ${y}`, "الفروق بين المحافظات تتأثر بنوع المرافق المبلِّغة في كل منها."],
    f4: (f, e) => [`${f} / ${e}`, "وحدة خدمة صحية تعمل ولو جزئياً من التي قيّمها HeRAMS (يونيو 2025)", "تقرير WHO غير نهائي، ويشمل المرافق المبلِّغة لـ HeRAMS فقط."],
    f5: (lo, hi, last, d) => [`${lo}%–${hi}%`, `من الأدوية الأساسية عند «صفر مخزون» حسب المصدر والتاريخ؛ آخر رقم ${last}% (${d})`, "المصادر تتعارض لتواريخ متقاربة؛ لذلك نعرض المدى لا رقماً واحداً."],
    f6: (a, b, c, d) => [`${a} → ${b}`, `يوماً: متوسط تأخر وصول التقارير، من 2024 إلى 2026؛ واكتمال التقارير ارتفع من ${c}% إلى ${d}%`, "البيانات صارت أكمل وأسرع؛ لهذا بالذات لا تُقارن 2024 بما بعدها."],
    readH: "للقراءة والتحقق",
    newer: (r) => `أحدث رقم بمقياس مختلف: ${r.value} ${r.measure_ar} (${r.source}، ${r.as_of}).`,
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
    foot: (m) => "آخر أسبوع في البيانات: " + ltr(m.last_year) + "، الأسبوع " + ltr(m.last_week) + ". تاريخ البناء: " + ltr(m.generated) + ". حدود المحافظات: OCHA / HDX COD-AB.",
    srcType: { "official statistic": "إحصاء رسمي", "survey": "مسح", "modelled estimate": "تقدير نمذجي", "press coverage": "تغطية صحفية", "clinical guidance": "إرشادات سريرية" },
    lang: "English",
  },
  en: {
    title: "Gaza Disease & Care Map",
    sub: "Aggregated public data on non-injury health conditions in the Gaza Strip, 2024–2026",
    banner: "Aggregated data from public sources. Not medical advice and not a diagnosis. Cases are suspected cases from reporting facilities only, and rates are approximate and not comparable with other countries. Read “Limits of the data” below.",
    tabs: { findings: "Key facts", disease: "By disease", location: "By location", medicine: "By medicine class" },
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
    sitesTitle: "Number of reporting locations (monthly mean of weeks)",
    sitesShade: "Months with fewer than 20 reporting locations: not comparable with others",
    sitesNote: (m) => "Reporting locations (weekly median): " + Object.entries(m).map(([y, v]) => y + ": " + v).join(" · ") + ". In the first 14 weeks of 2024 only 1 to 9 locations reported, so 2024 rates are not comparable with the following years.",
    medTitle: "By medicine class",
    medBody: "Every row here has a source (WHO or CDC treatment pages) and names only a medicine CLASS, never a drug or dose: the doctor decides. This is general guidance, not Gaza-specific and not a prescription.",
    medDisease: "Disease", medClasses: "Medicine classes in treatment guidance", medRate: "Cases per 1,000 consultations (Strip)", medSrc: "Source",
    medNone: "No documented medicine class for these diseases (mumps, bloody diarrhoea, acute flaccid paralysis): no source, no row.",
    supTitle: "Supply signals: share of essential medicines at \"zero stock\"",
    supBody: "Sources disagree for similar dates, so we do not merge them or draw one line: each figure keeps its source, date and original wording. These are Ministry of Health figures as quoted by others, and \"zero stock\" is not defined in them.",
    supDate: "As of", supPct: "Share", supWord: "Wording", ncdSvcTitle: "Readiness of chronic-disease and mental-health services, Gaza Strip (HeRAMS, June 2025)",
    ncdSvcNote: "Some services have very few expected units (3 to 33), so one unit moves the percentages a lot. Arabic service names are our translation.",
    ncdSvcHead: ["Service", "Available", "Partial", "Not available", "Units expected", "Below standard"],
    copyLink: "Copy link to this view", copied: "Copied", dlCsv: "Download data (CSV)", sites: "reporting sites",
    calcH: "How was this number calculated?",
    calc: (c, w) => `cases ÷ consultations × 1,000${formula(c)}Epi weeks 1 to ${w} only, so the current year is compared on the same weeks. Cases and consultations are summed first, then divided (never an average of rates). Source: EWARS.`,
    clipped: "▲ Points above the cap are months with very few reporting sites (value in the tooltip); the axis is scaled to the comparable months.",
    y2024: "† 2024: far fewer sites reported (median 32.5 vs 201 in 2026), so this column is not comparable with the others.",
    fTitle: "Key facts: what the data says, and what it does not",
    fIntro: "Every number here is computed from the site's own data when the page loads, and links to the view it comes from. Nothing is typed by hand.",
    fOpen: "Open the view", fCaveat: "Caveat",
    f1: (v, c, y) => [`${v}`, `per 1,000 consultations: acute respiratory infection is the most reported condition in ${y} (${c} suspected cases)`, "Consultations include war injuries; this is not a population incidence rate."],
    f2: (v, a, y) => [`${v}`, `per 1,000 consultations: scabies/lice, impetigo and chickenpox together in ${y}, above acute watery diarrhoea (${a})`, "These were added to the system in mid-2025, so no earlier comparison. Adding them is valid because the denominator is the same."],
    f3: (g, v, y) => [`${v}`, `per 1,000 consultations: ${g} is the highest governorate for acute watery diarrhoea in ${y}`, "Differences between governorates also reflect which facilities report there."],
    f4: (f, e) => [`${f} / ${e}`, "health service delivery units at least partially functioning, of those HeRAMS evaluated (June 2025)", "WHO says the analysis is not final; only facilities reporting to HeRAMS."],
    f5: (lo, hi, last, d) => [`${lo}%–${hi}%`, `of essential medicines at "zero stock", by source and date; latest figure ${last}% (${d})`, "Sources disagree for similar dates, so we show the range, not one number."],
    f6: (a, b, c, d) => [`${a} → ${b}`, `days average reporting delay (2024 → 2026); completeness rose from ${c}% to ${d}%`, "The data became more complete and faster, which is exactly why 2024 is not compared with later years."],
    readH: "Further reading and checks",
    newer: (r) => `Newer figure, different measure: ${r.value} ${r.measure_en} (${r.source}, ${r.as_of}).`,
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
    foot: (m) => "Latest week in the data: " + ltr(m.last_year) + " week " + ltr(m.last_week) + ". Built " + ltr(m.generated) + ". Boundaries: OCHA / HDX COD-AB.",
    srcType: { "official statistic": "official statistic", "survey": "survey", "modelled estimate": "modelled estimate", "press coverage": "press coverage", "clinical guidance": "clinical guidance" },
    lang: "العربية",
  },
};

const COLORS = ["#eaf2f7", "#bcd7e6", "#82b2cf", "#3f84ad", "#14527a"];   // 5 sequential steps
const GAP_COLOR = "#d9d9d9";
const LINE_COLORS = { gaza: "#1b6ca8", north_gaza: "#d1495b", deir_al_balah: "#2e8b57", khan_yunis: "#e08e0b", rafah: "#7b4fa3", strip: "#222222" };
const DOMAIN_COLORS = ["#2e8b57", "#9fcf9f", "#e0b84c", "#c9c9c9"];
const MIN_COVERAGE = 0.4;

const state = { lang: localStorageGet("lang") || "ar", tab: "findings", disease: "ari", year: null, loc: null };
let DATA, GEO, map, layers = {};

function localStorageGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function localStorageSet(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } }

const T = () => I18N[state.lang];
// numbers, dates and ranges keep left-to-right order inside right-to-left text
const ltr = (s) => `<bdi dir="ltr">${esc(s)}</bdi>`;
// a formula on its own left-to-right line, so wrapping can never reorder its parts
const formula = (c) => `<code class="formula" dir="ltr">${esc(c.cases.toLocaleString("en") + " ÷ " + c.consultations.toLocaleString("en") + " × 1,000 = " + c.per_1000)}</code>`;
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
      leg.push(`<span><i style="background:${c}"></i>${ltr(fmt(a) + "–" + fmt(b))}</span>`);
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
  const thrS = DATA.meta.low_sites_threshold;
  const isLow = (mi) => DATA.sites_month[mi] !== null && DATA.sites_month[mi] < thrS;
  const all = keys.flatMap((k) => series[k].map((p) => p[3]));
  if (!all.length) return `<p class="note">${esc(T().noData)}</p>`;
  // scale on comparable months; a month from 1-9 sites must not flatten the rest of the chart
  const comp = keys.flatMap((k) => series[k].filter((p) => !isLow(p[0])).map((p) => p[3]));
  const ymax = (comp.length ? Math.max(...comp) : Math.max(...all)) * 1.08 || 1;
  const clipped = all.some((v) => v > ymax);
  const n = DATA.months.length;
  const x = (i) => m.l + (i / (n - 1)) * (W - m.l - m.r);
  const y = (v) => H - m.b - (Math.min(v, ymax) / ymax) * (H - m.t - m.b);
  const thr = DATA.meta.low_sites_threshold;
  let svg = `<svg class="chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="${esc(T().trend)}" dir="ltr">`;
  DATA.sites_month.forEach((n, i) => {
    if (n !== null && n < thr) svg += `<rect x="${(x(i) - 8).toFixed(1)}" y="${m.t}" width="16" height="${H - m.t - m.b}" fill="#f3e3b5" opacity=".7"/>`;
  });
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
      const low = DATA.sites_month[mi] !== null && DATA.sites_month[mi] < thr;
      const tip = `<title>${esc(locName(loc(k)))} · ${DATA.months[mi]}: ${fmt(v)} (${fmt(cases)} ${esc(T().cases)}, ${wk} ${esc(T().weeks)}; ${esc(String(DATA.sites_month[mi]))} ${esc(T().sites)})</title>`;
      if (v > ymax) {
        const cx = x(mi), cy = m.t + 2;
        svg += `<path d="M${(cx - 4).toFixed(1)} ${cy + 6} L${cx.toFixed(1)} ${cy} L${(cx + 4).toFixed(1)} ${cy + 6} Z" fill="${LINE_COLORS[k]}">${tip}</path>`;
      } else {
        svg += `<circle cx="${x(mi).toFixed(1)}" cy="${y(v).toFixed(1)}" r="${k === "strip" ? 2.6 : 2}" fill="${low ? "#fff" : LINE_COLORS[k]}" stroke="${LINE_COLORS[k]}" stroke-width="${low ? 1.4 : 0}">${tip}</circle>`;
      }
    });
  });
  svg += "</svg>";
  const key = keys.map((k) => `<span class="${k === "strip" ? "dash" : ""}" style="--c:${LINE_COLORS[k]}">${esc(k === "strip" ? T().strip : locName(loc(k)))}</span>`).join("");
  return svg + `<div class="key">${key}<span style="--c:#f3e3b5;height:auto">${esc(T().sitesShade)}</span></div>` +
    (clipped ? `<p class="note">${esc(T().clipped)}</p>` : "") + sitesSvg();
}

/* how many locations reported: the denominator behind every rate */
function sitesSvg() {
  const W = 620, H = 90, m = { l: 44, r: 10, t: 6, b: 18 };
  const vals = DATA.sites_month, n = vals.length, thr = DATA.meta.low_sites_threshold;
  const ymax = Math.max(...vals.filter((v) => v !== null)) * 1.1;
  const bw = (W - m.l - m.r) / n;
  const y = (v) => H - m.b - (v / ymax) * (H - m.t - m.b);
  let svg = `<h3>${esc(T().sitesTitle)}</h3><svg class="chart" viewBox="0 0 ${W} ${H}" dir="ltr" role="img" aria-label="${esc(T().sitesTitle)}">`;
  svg += `<line x1="${m.l}" x2="${W - m.r}" y1="${y(thr)}" y2="${y(thr)}" stroke="#c0392b" stroke-dasharray="3 3"/><text x="${m.l - 6}" y="${y(thr) + 4}" text-anchor="end">${thr}</text>`;
  vals.forEach((v, i) => {
    if (v === null) return;
    svg += `<rect x="${(m.l + i * bw + 1).toFixed(1)}" y="${y(v).toFixed(1)}" width="${(bw - 2).toFixed(1)}" height="${(H - m.b - y(v)).toFixed(1)}" fill="${v < thr ? "#e0b84c" : "#7f93a3"}"><title>${DATA.months[i]}: ${v}</title></rect>`;
  });
  DATA.months.forEach((mo, i) => { if (mo.endsWith("-01") || mo.endsWith("-07")) svg += `<text x="${(m.l + i * bw + bw / 2).toFixed(1)}" y="${H - 4}" text-anchor="middle">${mo}</text>`; });
  return svg + `</svg><p class="note">${esc(T().sitesNote(DATA.sites_median))}</p>`;
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
    ? `<p><span class="big">${fmt(s.per_1000)}</span> ${esc(t.unit)} · ${esc(t.strip)} · ${fmt(s.cases)} ${esc(t.cases)}</p>
       ${s.consultations ? `<details class="calc"><summary>${esc(t.calcH)}</summary><p>${t.calc(s, DATA.meta.last_week)}</p></details>` : ""}` : "";
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
  const head = years.map((y) => `<th class="num">${y}${y === "2024" ? "†" : ""}</th>`).join("");
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
    <p class="note">* ${esc(t.partial)}</p><p class="note">${esc(t.y2024)}</p>
    ${herams}
    <h3>${esc(t.under5)}</h3><p>${ltr(u5txt)}</p>
    <h3>${esc(t.coverage)}</h3><p class="note">${ltr(covTxt)}</p>`;
}

/* ---- key facts: computed from DATA at load time, each linking to its source view ---- */
function findingsHtml() {
  const t = T();
  const y = String(DATA.meta.last_year);
  const S = (d) => (DATA.yearly[d] || {}).strip ? DATA.yearly[d].strip[y] : null;
  const cards = [];
  const link = (q) => "?" + new URLSearchParams({ lang: state.lang, ...q }).toString();
  const ari = S("ari");
  if (ari) cards.push([t.f1(fmt(ari.per_1000), fmt(ari.cases), y), { tab: "disease", disease: "ari", year: y }]);
  const skin = ["ectoparasitic", "impetigo", "chickenpox"].map(S).filter((v) => v && v.comparable);
  const awd = S("awd");
  if (skin.length === 3 && awd) {
    const cases = skin.reduce((a, v) => a + v.cases, 0);
    cards.push([t.f2(fmt(Math.round(cases * 100000 / awd.consultations) / 100), fmt(awd.per_1000), y), { tab: "disease", disease: "ectoparasitic", year: y }]);
  }
  const govs = DATA.locations.filter((l) => l.level === "governorate").map((l) => ({ l, c: cell("awd", l.key, y) })).filter((r) => r.c.status === "ok");
  if (govs.length) {
    govs.sort((a, b) => b.c.per_1000 - a.c.per_1000);
    cards.push([t.f3(locName(govs[0].l), fmt(govs[0].c.per_1000), y), { tab: "location", loc: govs[0].l.key, year: y }]);
  }
  const hs = Object.values(DATA.herams.hsdu);
  if (hs.length) {
    const c = t.f4(hs.reduce((a, v) => a + v[1], 0), hs.reduce((a, v) => a + v[0], 0));
    (DATA.service_signals || []).forEach((r) => { c[2] += " " + t.newer(r); });
    cards.push([c, { tab: "location", loc: "north_gaza" }]);
  }
  if (DATA.supply.length) {
    const p = DATA.supply.map((r) => r.pct), last = DATA.supply[DATA.supply.length - 1];
    cards.push([t.f5(Math.min(...p), Math.max(...p), last.pct, last.as_of), { tab: "medicine" }]);
  }
  const o = DATA.overview;
  if (o["2024"] && o[y]) cards.push([t.f6(o["2024"].mean_delay_days, o[y].mean_delay_days,
    Math.round(o["2024"].mean_completeness * 100), Math.round(o[y].mean_completeness * 100)), { tab: "disease", disease: "ari", year: y }]);
  const html = cards.map(([[big, text, cav], q]) => `<article class="fact"><p><span class="big">${ltr(big)}</span> ${esc(text)}</p>
    <p class="note"><strong>${esc(t.fCaveat)}:</strong> ${esc(cav)}</p><a href="${esc(link(q))}" data-view="${esc(JSON.stringify(q))}">${esc(t.fOpen)} →</a></article>`).join("");
  const reading = (DATA.reading || []).map((r) => `<li><a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)}</a>
    <span class="note">${esc(r.who)} · ${ltr(r.date)}${r.kind ? " · " + esc(r.kind) : ""}</span><br><span class="note">${esc(state.lang === "ar" && r.finding_ar ? r.finding_ar : r.finding)}</span></li>`).join("");
  return `<h2>${esc(t.fTitle)}</h2><p class="note">${esc(t.fIntro)}</p><div class="facts">${html}</div>
    ${reading ? `<h3>${esc(t.readH)}</h3><ul class="reading">${reading}</ul>` : ""}`;
}

function medicineHtml() {
  const t = T();
  const yr = String(state.year || DATA.meta.last_year);
  const srcName = (id) => (DATA.meta.sources.find((s) => s.id === id) || {}).name || id;
  const rowsM = DATA.diseases.filter((d) => DATA.medicine[d.key]).map((d) => {
    const c = cell(d.key, "strip", yr);
    const cls = DATA.medicine[d.key].map((m) => {
      const label = state.lang === "ar" ? m.class_ar : m.class_en;
      const link = m.url ? `<a href="${esc(m.url)}" target="_blank" rel="noopener">${esc(m.source.toUpperCase())}</a>` : esc(m.source);
      return `<li>${esc(label)} <span class="note">· ${link} · ${ltr(m.ref)}${m.note && state.lang !== "ar" ? " · " + esc(m.note) : ""}</span></li>`;
    }).join("");
    const rate = c && (c.status === "ok" || c.status === "partial") ? ltr(fmt(c.per_1000)) : "–";
    return `<tr><td>${esc(diseaseName(d))}</td><td><ul class="plain">${cls}</ul></td><td class="num">${rate}</td></tr>`;
  }).join("");
  const sup = DATA.supply.map((r) => `<tr><td>${ltr(r.as_of)}</td><td class="num">${ltr(r.pct + "%")}</td><td>${ltr(r.wording)}</td>
    <td>${esc(srcName(r.source))} · ${ltr(r.ref)}<br><span class="note">${esc(r.caveat)}</span></td></tr>`).join("");
  const ncd = DATA.herams.ncd.map((r) => `<tr><td>${esc(state.lang === "ar" ? r.ar : r.en)}${stackHtml([r.available, r.partial, r.not_available, 0])}</td>
    <td class="num">${ltr(r.available + "%")}</td><td class="num">${ltr(r.partial + "%")}</td><td class="num">${ltr(r.not_available + "%")}</td>
    <td class="num">${ltr(String(r.expected))}</td><td class="num">${ltr(r.not_standard + "/" + r.expected)}</td></tr>`).join("");
  return `<h2>${esc(t.medTitle)}</h2><p class="note">${esc(t.medBody)}</p>
    <table><thead><tr><th>${esc(t.medDisease)}</th><th>${esc(t.medClasses)}</th><th class="num">${esc(t.medRate)} · ${ltr(yr)}</th></tr></thead><tbody>${rowsM}</tbody></table>
    <p class="note">${esc(t.medNone)}</p>
    <h3>${esc(t.supTitle)}</h3><p class="note">${esc(t.supBody)}</p>
    <table><thead><tr><th>${esc(t.supDate)}</th><th class="num">${esc(t.supPct)}</th><th>${esc(t.supWord)}</th><th>${esc(t.medSrc)}</th></tr></thead><tbody>${sup}</tbody></table>
    <h3>${esc(t.ncdSvcTitle)}</h3><p class="note">${esc(t.ncdSvcNote)}</p>
    <table><thead><tr>${t.ncdSvcHead.map((h, i) => `<th${i ? ' class="num"' : ""}>${esc(h)}</th>`).join("")}</tr></thead><tbody>${ncd}</tbody></table>`;
}

/* ---- rendering ---- */
function render() {
  const t = T();
  document.documentElement.lang = state.lang;
  document.documentElement.dir = state.lang === "ar" ? "rtl" : "ltr";
  $("t-title").textContent = t.title; $("t-sub").textContent = t.sub; $("t-banner").textContent = t.banner;
  $("lang").textContent = t.lang;
  $("l-disease").textContent = t.disease; $("l-year").textContent = t.year;
  $("tabs").innerHTML = ["findings", "disease", "location", "medicine"].map((k) =>
    `<button role="tab" type="button" data-tab="${k}" aria-selected="${state.tab === k}">${esc(t.tabs[k])}</button>`).join("");
  $("disease").innerHTML = DATA.diseases.map((d) => `<option value="${d.key}"${d.key === state.disease ? " selected" : ""}>${esc(diseaseName(d))}</option>`).join("");
  const years = Object.keys(DATA.yearly.ari.strip).sort();
  if (!state.year) state.year = years[years.length - 1];
  $("year").innerHTML = years.map((y) => `<option value="${y}"${y === String(state.year) ? " selected" : ""}>${esc(t.yearOpt(y, DATA.meta.last_week))}</option>`).join("");
  $("l-disease-wrap").hidden = state.tab !== "disease";
  $("controls").hidden = state.tab === "findings";
  $("copy-link").textContent = t.copyLink; $("dl-csv").textContent = t.dlCsv;
  $("dl-csv").hidden = state.tab === "medicine";
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
  } else if (state.tab === "findings") {
    panel = findingsHtml();
  } else {
    panel = medicineHtml();
  }
  $("panel").innerHTML = panel;
  $("t-limits-h").textContent = t.limitsH;
  $("t-limits").innerHTML = t.limits.map((s) => `<li>${esc(s)}</li>`).join("");
  $("t-sources-h").textContent = t.sourcesH;
  $("sources").innerHTML = DATA.meta.sources.map((s) =>
    `<li><strong>${esc(s.name)}</strong> — ${esc(s.publisher)} · ${esc(t.srcType[s.type] || s.type)} · ${ltr(s.data_up_to)}<br><span class="note">${esc(s.caveats)}</span></li>`).join("");
  $("t-foot").innerHTML = t.foot(DATA.meta);
  document.title = t.title;
  syncUrl();
  if (map) setTimeout(() => map.invalidateSize(), 0);
}

/* keep the address bar equal to the current view, so any view can be shared as-is */
function syncUrl() {
  const q = new URLSearchParams({ lang: state.lang, tab: state.tab });
  if (state.tab === "disease") q.set("disease", state.disease);
  if (state.year) q.set("year", state.year);
  if (state.tab === "location" && state.loc) q.set("loc", state.loc);
  try { history.replaceState(null, "", "?" + q.toString()); } catch (e) { /* sandboxed preview */ }
}

/* the numbers behind the current view, as CSV (the same numbers the page shows) */
function csvForView() {
  const rowsOut = [];
  if (state.tab === "location" && state.loc) {
    rowsOut.push(["location", "disease", "year", "cases", "consultations", "per_1000_consultations", "weeks_reported", "comparable"]);
    DATA.diseases.forEach((d) => Object.entries((DATA.yearly[d.key] || {})[state.loc] || {}).forEach(([y, v]) =>
      rowsOut.push([state.loc, d.key, y, v.cases, v.consultations, v.per_1000, v.weeks, v.comparable])));
  } else {
    rowsOut.push(["disease", "location", "month", "cases", "consultations", "per_1000_consultations", "weeks_reported", "reporting_sites_month_mean"]);
    Object.entries(DATA.monthly[state.disease] || {}).forEach(([l, pts]) => pts.forEach(([mi, c, n, v, w]) =>
      rowsOut.push([state.disease, l, DATA.months[mi], c, n, v, w, DATA.sites_month[mi] ?? ""])));
  }
  const window = state.tab === "location" ? "every year uses epi weeks 1-" + DATA.meta.last_week + " (same weeks)"
    : "data up to " + DATA.meta.last_year + "-W" + DATA.meta.last_week;
  const note = "# Source: WHO/MoH EWARS via Gaza Disease & Care Map; suspected cases from reporting sites only; " +
    "a rate per 1,000 consultations, not incidence; " + window + "; 2024 had far fewer reporting sites";
  return note + "\n" + rowsOut.map((r) => r.map((v) => /[",\n]/.test(String(v)) ? `"${String(v).replace(/"/g, '""')}"` : v).join(",")).join("\n") + "\n";
}

/* Shareable views: ?lang=en&tab=location&disease=awd&year=2025&loc=rafah. Every value is checked against
   the data, so a hand-edited link can never inject anything into the page. */
function applyUrlParams() {
  const q = new URLSearchParams(location.search);
  if (["ar", "en"].includes(q.get("lang"))) state.lang = q.get("lang");
  if (["findings", "disease", "location", "medicine"].includes(q.get("tab"))) state.tab = q.get("tab");
  if (dis(q.get("disease") || "")) state.disease = q.get("disease");
  if (Object.keys(DATA.yearly.ari.strip).includes(q.get("year"))) state.year = q.get("year");
  const l = q.get("loc");
  if (l && l !== "strip" && loc(l)) state.loc = l;
  if (state.tab === "location" && !state.loc) state.loc = "gaza";
}

async function main() {
  const [d, g] = await Promise.all([fetch("data/data.json").then((r) => r.json()), fetch("data/governorates.geojson").then((r) => r.json())]);
  DATA = d; GEO = g;
  applyUrlParams();
  initMap();
  $("lang").addEventListener("click", () => { state.lang = state.lang === "ar" ? "en" : "ar"; localStorageSet("lang", state.lang); render(); });
  $("tabs").addEventListener("click", (e) => { const b = e.target.closest("button[data-tab]"); if (b) { state.tab = b.dataset.tab; if (state.tab === "location" && !state.loc) state.loc = "gaza"; render(); } });
  $("panel").addEventListener("click", (e) => {
    const a = e.target.closest("a[data-view]");
    if (!a) return;
    e.preventDefault();
    const q = JSON.parse(a.dataset.view);
    state.tab = q.tab; if (q.disease) state.disease = q.disease; if (q.year) state.year = q.year; if (q.loc) state.loc = q.loc;
    if (state.tab === "location" && !state.loc) state.loc = "gaza";
    render(); window.scrollTo({ top: 0, behavior: "smooth" });
  });
  $("disease").addEventListener("change", (e) => { state.disease = e.target.value; render(); });
  $("year").addEventListener("change", (e) => { state.year = e.target.value; render(); });
  $("copy-link").addEventListener("click", async () => {
    try { await navigator.clipboard.writeText(location.href); $("copied").textContent = T().copied; }
    catch (e) { $("copied").textContent = location.href; }
    setTimeout(() => { $("copied").textContent = ""; }, 2500);
  });
  $("dl-csv").addEventListener("click", () => {
    const blob = new Blob([csvForView()], { type: "text/csv;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `gaza-${state.tab === "location" ? state.loc : state.disease}.csv`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  });
  render();
}
main().catch((e) => { document.body.insertAdjacentHTML("afterbegin", `<p class="banner">Failed to load data: ${esc(e.message)}</p>`); });
