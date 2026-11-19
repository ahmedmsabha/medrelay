# إطلاق «خريطة الأمراض والرعاية في غزة» (M5)

> مسوّدات فقط. لم يُنشر شيء ولم يُرفع الموقع. كل بند في «قبل النشر» قرارك أنت.

## 1. قبل النشر (قائمة تحقق)

| # | البند | الحالة |
|---|---|---|
| 1 | كل رقم في المنشورات مطابق لمصدره | تم: انظر الجدول في القسم 2 واختبارات `test_source_audit.py` (70 اختباراً تنجح) |
| 2 | **إذن/إبلاغ WHO oPt أو منسق EWARS في وزارة الصحة** بنشر معدلات مشتقة من لوحتهم | **لم يتم.** README الخام يطلبه. ممكن عبر المشرف |
| 3 | قرار المشرف في سؤال Q3 (فئات الأدوية) | لم يُحسم؛ التبويب معبّأ بفئات موثّقة من WHO/CDC دون أسماء أدوية أو جرعات، ويحتاج مراجعة المشرف قبل النشر |
| 4 | أين يُستضاف الموقع (GitHub Pages أو Netlify أو Cloudflare Pages) | لم يُقرَّر. الموقع ثابت: يُنشر مجلد `gaza_map/site/` كما هو |
| 5 | اسم المستودع وظهور مجلد `medrelay` | المستودع `medrelay` يضم أيضاً مشروع MedRelay؛ قرر إن كنت تريد فصل الموقع في مستودع مستقل قبل النشر |
| 6 | أن تستطيع شرح كل رقم وكل قرار (هدف الاجتماع) | استخدم أسئلة الفهم في المذكرات 06–09 |
| 7 | فحص الصفحة بعيني عربي قبل النشر (نصوص التحذير، الاتجاه، المصطلحات الطبية) | يحتاج منك: راجع الشرائح في `gaza_map/site/screenshots/` |
| 8 | المنشورات: لا نكتب سبباً لأي ارتفاع أو انخفاض | التزمنا به في المسوّدات أدناه |

## 2. كل رقم يُذكر ومصدره

| الرقم | المصدر وطريقة التحقق |
|---|---|
| الشمال أبلغت 25 من 52 أسبوعاً في 2024 | `ewars_coverage.csv` (من بيانات لوحة EWARS)؛ الأسابيع 2 وغيرها غائبة؛ يظهر في صفحة المحافظة |
| 127 وحدة خدمة صحية جرى تقييمها، 44 منها تعمل ولو جزئياً | PDF HeRAMS يونيو 2025: «Out of 127 HSDUs evaluated» وصفحة قطاع غزة «Out of 44 HSDUs». المجاميع الخمسة 27+39+25+21+15 = 127، و17+18+8+1+0 = 44 |
| شمال غزة 1 من 21، رفح 0 من 15 | صفحتا المحافظتين في PDF HeRAMS («Out of 21 HSDUs evaluated»، «Out of 15 HSDUs evaluated») |
| إسهال مائي لكل 1,000 استشارة: 119 ثم 51 ثم 38 (أسابيع 1–45) | حساب من EWARS (`v_by_disease`). **لا تنشر هذا كمقارنة:** المقام يشمل الإصابات، وعدد المواقع المبلِّغة تغيّر (وسيط 32.5 في 2024 مقابل 201 في 2026) |
| 51% من الأدوية الأساسية بمخزون صفر (PCBS، مارس 2026) مقابل 44% (WHO Sitrep 68، 31 مارس 2026) | الجدول في تبويب الدواء؛ المصادر تتعارض ولا نجمعها. لا تنشر رقماً منها منفرداً |
| 20 خدمة أمراض مزمنة وصحة نفسية، مثلاً علاج الاضطرابات النفسية متاح كلياً في 21% من 19 وحدة | HeRAMS يونيو 2025، الصفحة 10 من PDF؛ ملف `herams_ncd_services_strip_2025-06.csv` |
| 462,862 حالة إسهال مائي و1,341,805 تنفسي في 2026 (حتى الأسبوع 45) | مطابقة للوحة EWARS يوم 2026-11-19 (462.9k و1.3M) |

## 3. مسوّدات X (العربية)

1. بنيتُ «خريطة الأمراض والرعاية في غزة»: بيانات WHO ووزارة الصحة المنشورة عن الأمراض غير الناتجة عن الإصابات، من 2024 إلى 2026، حسب المرض والمحافظة. ليست نصيحة طبية. [الرابط]
2. أهم درس: البيانات ناقصة. محافظة الشمال لم تُبلِّغ إلا عن 25 من 52 أسبوعاً في 2024. الأسبوع الغائب ليس صفراً، فالخريطة تتركه رمادياً بدل أن تلوّنه، والخط ينقطع بدل أن يهبط.
3. ومن تقرير HeRAMS (WHO، يونيو 2025): من 127 وحدة خدمة صحية جرى تقييمها، 44 فقط تعمل ولو جزئياً. في شمال غزة وحدة واحدة من 21، وفي رفح صفر من 15. هذا ما قاله المصدر، وهو غير نهائي.

## 4. X drafts (English)

1. I built the Gaza Disease & Care Map: published WHO / Ministry of Health data on non-injury diseases, 2024–2026, by disease and governorate. Not medical advice. [link]
2. Biggest lesson: the data is incomplete. North Gaza reported only 25 of 52 weeks in 2024. A missing week is not a zero, so the map shows grey instead of a colour and the line breaks instead of dropping.
3. From WHO's HeRAMS report (June 2025): of 127 health service units evaluated, 44 were at least partially functioning. North Gaza: 1 of 21. Rafah: 0 of 15. That is what the source says; WHO states it is not final.

(الأطوال 166–211 حرفاً، تحت حد 280.)

## 5. LinkedIn (English, يمكن ترجمتها)

**I mapped two years of public health data from Gaza. The hardest lesson was about what's missing.**

For a one-week project I built an interactive map of non-injury health conditions in the Gaza Strip (infectious and
other diseases, 2024–2026) using public WHO / Ministry of Health surveillance data (EWARS) and WHO's HeRAMS
service-readiness report. It is bilingual (Arabic RTL / English) and every figure is tied to its source.

What I learned building it:
- **Raw counts lie.** The number of reporting facilities changes, so I normalise by consultations. Still only a proxy.
- **A missing week is not a zero.** North Gaza reported 25 of 52 weeks in 2024. The map shows grey, and lines break.
- **A zero can mean "not tracked".** Three diseases were only added to the system in mid-2025, so I flag those years as not comparable.
- **Two independent calculations must agree.** The database, a Python script and the dashboard totals are cross-checked in 76 tests.
- **Say what you don't know.** No sex, language, allergy/asthma or sub-governorate data exists in these sources. Every medicine-class row
  links to a WHO or CDC page, names no drug or dose, and diseases without a source have no row.

This is a display of published data, not a health assessment and not medical advice.
Data: WHO / Palestinian MoH (EWARS), WHO (HeRAMS), OCHA/HDX (boundaries). [link] · Code and notes in the repository.

## 6. ما لم نفعله (ولا نقوله في أي منشور)

- لا نفسّر سبب أي ارتفاع أو انخفاض (لم نجد مصدراً للأسباب بعد).
- لا نقول إن الأرقام «إجمالي المصابين»: هي حالات مشتبه بها من مرافق تبلّغ فقط.
- لا ندّعي تحققاً سريرياً. لا نعرض أدوية أو جرعات.
- لا نذكر الحساسية/الربو ولا الجنس ولا اللغة: غير متوفرة.

