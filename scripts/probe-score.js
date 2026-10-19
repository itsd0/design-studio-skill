/* Design Studio — craft score probe.
 *
 * Measures the things a design review can check mechanically: hierarchy,
 * type discipline, accent budget, section rhythm, self-containment and —
 * the metric that separates a design skill from a style guide — how far
 * the artifact sits from the default AI look.
 *
 * The result is written into a script element carrying the id
 * __ds_score__ (single-quoted here on purpose, so the extractor cannot
 * mistake this comment for it).
 */
(function () {
  "use strict";

  var RID = "__ds_score__";
  var W = window;

  function normFamily(family) {
    return (family || "").replace(/["']/g, "").replace(/\s+/g, " ").trim();
  }

  function isDefaultStack(family) {
    var f = normFamily(family).toLowerCase();
    if (!f) return true;
    var defaults = ["system-ui", "-apple-system", "blinkmacsystemfont", "inter",
      "roboto", "arial", "helvetica", "segoe ui", "sans-serif", "noto sans"];
    var hasReal = false;
    for (var i = 0; i < defaults.length; i++) {
      if (f.indexOf(defaults[i]) !== -1) hasReal = true;
    }
    var interesting = ["charter", "georgia", "iowan", "times", "garamond",
      "baskerville", "palatino", "optima", "avenir", "futura", "gill sans",
      "trebuchet", "jetbrains", "ibm plex", "sf mono", "menlo", "cascadia",
      "source code", "fira", "iosevka", "courier"];
    for (var j = 0; j < interesting.length; j++) {
      if (f.indexOf(interesting[j]) !== -1) return false;
    }
    return hasReal;
  }

  function hueOf(rgb) {
    var r = rgb[0] / 255, g = rgb[1] / 255, b = rgb[2] / 255;
    var mx = Math.max(r, g, b), mn = Math.min(r, g, b), d = mx - mn;
    if (d === 0) return null;
    var h;
    if (mx === r) h = ((g - b) / d) % 6;
    else if (mx === g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
    h *= 60;
    if (h < 0) h += 360;
    return h;
  }

  function firstFamily(family) {
    var f = normFamily(family);
    if (!f) return "";
    return f.split(",")[0].trim().toLowerCase();
  }

  function parseColor(str) {
    if (!str) return null;
    var m = String(str).match(/rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/i);
    if (m) return [parseFloat(m[1]), parseFloat(m[2]), parseFloat(m[3])];
    m = String(str).match(/color\(srgb\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)/i);
    if (m) return [parseFloat(m[1]) * 255, parseFloat(m[2]) * 255, parseFloat(m[3]) * 255];
    m = String(str).match(/oklch\(\s*([\d.]+)(%?)\s+([\d.]+)\s+([\d.]+)/i);
    if (m) {
      var L = parseFloat(m[1]) / (m[2] === "%" ? 100 : 1);
      var C2 = parseFloat(m[3]);
      var H2 = parseFloat(m[4]);
      var C = C2;
      var H = H2 * Math.PI / 180;
      var a = C * Math.cos(H), b = C * Math.sin(H);
      var l_ = L + 0.3963377774 * a + 0.2158037573 * b;
      var m_ = L - 0.1055613458 * a - 0.0638541728 * b;
      var s_ = L - 0.0894841775 * a - 1.2914855480 * b;
      var l = l_ * l_ * l_, m2 = m_ * m_ * m_, s = s_ * s_ * s_;
      var lr = 4.0767416621 * l - 3.3077115913 * m2 + 0.2309699292 * s;
      var lg = -1.2684380046 * l + 2.6097574011 * m2 - 0.3413193965 * s;
      var lb = -0.0041960863 * l - 0.7034186147 * m2 + 1.7076147010 * s;
      function enc(c) {
        c = c < 0 ? 0 : c > 1 ? 1 : c;
        var v = c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
        return v * 255;
      }
      return [enc(lr), enc(lg), enc(lb)];
    }
    return null;
  }

  function measure() {
    var out = {
      ok: true,
      hierarchy: {},
      type: {},
      accent: {},
      rhythm: {},
      content: {},
      motion: {},
      defaultDistance: {}
    };

    var all = document.body ? document.body.querySelectorAll("*") : [];
    var root = getComputedStyle(document.documentElement);
    var accentToken = root.getPropertyValue("--accent").trim();
    var displayToken = normFamily(root.getPropertyValue("--font-display"));

    /* Resolve a token to the colour the browser actually paints — a token
     * written in oklch() must not be skipped for being unparseable. */
    function resolveColor(value) {
      if (!value) return null;
      var probeEl = document.createElement("span");
      probeEl.style.position = "absolute";
      probeEl.style.opacity = "0";
      probeEl.style.pointerEvents = "none";
      probeEl.style.color = value;
      document.body.appendChild(probeEl);
      var computed = getComputedStyle(probeEl).color;
      document.body.removeChild(probeEl);
      return parseColor(computed);
    }

    var accentRgb = resolveColor("var(--accent)");
    var accentOnRgb = resolveColor("var(--accent-on)");

    /* The page background, walking up until something opaque paints. */
    var pageBg = null;
    var bgNode = document.body;
    while (bgNode && !pageBg) {
      var bc = parseColor(getComputedStyle(bgNode).backgroundColor);
      if (bc && (bc[3] === undefined || bc[3] > 0.5)) pageBg = bc;
      bgNode = bgNode.parentElement;
    }
    if (!pageBg) pageBg = [255, 255, 255];

    /* ── hierarchy ─────────────────────────────────────────────────── */
    var h1s = document.querySelectorAll("h1");
    out.hierarchy.h1Count = h1s.length;
    out.hierarchy.h1Font = h1s.length ? normFamily(getComputedStyle(h1s[0]).fontFamily) : "";
    out.hierarchy.h1Size = h1s.length ? parseFloat(getComputedStyle(h1s[0]).fontSize) : 0;
    out.hierarchy.h1Text = h1s.length ? (h1s[0].textContent || "").trim().slice(0, 90) : "";
    out.hierarchy.headings = [].map.call(
      document.querySelectorAll("h1,h2,h3,h4,h5,h6"),
      function (h) { return parseInt(h.tagName[1], 10); }
    );

    /* A call to action that is above the fold. */
    var firstCta = null;
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      var tag = el.tagName.toLowerCase();
      if (tag !== "button" && tag !== "a") continue;
      var r = el.getBoundingClientRect();
      if (r.width < 8 || r.height < 8) continue;
      if (r.top < W.innerHeight * 0.75) {
        firstCta = {
          text: (el.textContent || "").trim().slice(0, 40),
          top: Math.round(r.top),
          width: Math.round(r.width),
          height: Math.round(r.height)
        };
        break;
      }
    }
    out.hierarchy.firstCta = firstCta;

    /* ── type discipline — measured per screen, not per page ───────── */
    var sizes = {}, families = {};
    var bodyFont = "";
    var screenBottom = W.innerHeight * 2;
    for (var t = 0; t < all.length; t++) {
      var e = all[t];
      if (!e.textContent || !e.textContent.trim()) continue;
      var cs = getComputedStyle(e);
      if (cs.display === "none") continue;
      var rect = e.getBoundingClientRect();
      if (rect.top > screenBottom) continue;   /* below the first two screens */
      var fs = Math.round(parseFloat(cs.fontSize));
      if (fs) sizes[fs] = (sizes[fs] || 0) + 1;
      var fam = firstFamily(cs.fontFamily);
      if (fam) families[fam] = (families[fam] || 0) + 1;
    }
    var bodyCs = getComputedStyle(document.body);
    bodyFont = normFamily(bodyCs.fontFamily);
    out.type.distinctSizes = Object.keys(sizes).length;
    out.type.sizeHistogram = sizes;
    out.type.distinctFamilies = Object.keys(families).length;
    out.type.familyHistogram = families;
    out.type.bodyFont = bodyFont;
    out.type.displayToken = displayToken;
    out.type.displayBound = !!(firstFamily(out.hierarchy.h1Font) &&
      firstFamily(displayToken) &&
      firstFamily(out.hierarchy.h1Font) === firstFamily(displayToken));
    out.type.headlineUsesDisplayFont = out.type.displayBound;

    /* ── accent budget ─────────────────────────────────────────────── */
    var accentUses = 0;
    var accentInFirstScreen = 0;
    var accentSamples = [];
    if (accentRgb) {
      for (var a = 0; a < all.length; a++) {
        var ae = all[a];
        var acs = getComputedStyle(ae);
        var hit = false;
        var bc2 = parseColor(acs.color);
        if (bc2 && Math.abs(bc2[0] - accentRgb[0]) < 8 && Math.abs(bc2[1] - accentRgb[1]) < 8 &&
          Math.abs(bc2[2] - accentRgb[2]) < 8) hit = true;
        if (!hit) {
          var bg2 = parseColor(acs.backgroundColor);
          if (bg2 && Math.abs(bg2[0] - accentRgb[0]) < 8 && Math.abs(bg2[1] - accentRgb[1]) < 8 &&
            Math.abs(bg2[2] - accentRgb[2]) < 8) hit = true;
        }
        if (!hit) continue;
        /* Only count an element that *carries* the accent itself: its own
         * text is painted in the accent, or it fills with the accent. An
         * inherited colour is not a visible accent moment. */
        var ownsText = Array.prototype.some.call(ae.childNodes, function (n) {
          return n.nodeType === 3 && n.nodeValue && n.nodeValue.trim();
        });
        var fills = false;
        var bg3 = parseColor(acs.backgroundColor);
        if (bg3 && Math.abs(bg3[0] - accentRgb[0]) < 8 && Math.abs(bg3[1] - accentRgb[1]) < 8 &&
          Math.abs(bg3[2] - accentRgb[2]) < 8) fills = true;
        if (!ownsText && !fills) continue;
        accentUses++;
        var ar = ae.getBoundingClientRect();
        if (ar.top < W.innerHeight) accentInFirstScreen++;
        if (accentSamples.length < 10) {
          accentSamples.push(ae.tagName.toLowerCase() +
            (ae.className && typeof ae.className === "string"
              ? "." + ae.className.trim().split(/\s+/)[0] : ""));
        }
      }
    }
    out.accent.token = accentToken;
    out.accent.resolved = accentRgb;
    out.accent.uses = accentUses;
    out.accent.usesInFirstScreen = accentInFirstScreen;
    out.accent.samples = accentSamples;
    out.accent.onAccent = root.getPropertyValue("--accent-on").trim();
    out.accent.onAccentResolved = accentOnRgb;

    /* ── rhythm ────────────────────────────────────────────────────── */
    var sections = document.querySelectorAll("section");
    var withId = 0;
    var gaps = {};
    for (var s = 0; s < sections.length; s++) {
      if (sections[s].getAttribute("data-design-id") ||
        sections[s].getAttribute("data-screen-label")) withId++;
      var scs = getComputedStyle(sections[s]);
      var pad = Math.round(parseFloat(scs.paddingTop));
      if (pad > 8) gaps[pad] = (gaps[pad] || 0) + 1;
    }
    out.rhythm.sections = sections.length;
    out.rhythm.sectionsAnchored = withId;
    out.rhythm.anchoredRatio = sections.length ? withId / sections.length : 1;
    out.rhythm.sectionPaddings = gaps;

    /* ── content ────────────────────────────────────────────────────── */
    var text = (document.body.innerText || "").replace(/\s+/g, " ").trim();
    out.content.words = text ? text.split(" ").length : 0;
    out.content.placeholders = (text.match(/\[REPLACE[^\]]*\]|lorem ipsum|TODO|FIXME|XXX/gi) || []).length;
    out.content.emptySections = 0;
    for (var es = 0; es < sections.length; es++) {
      var st = (sections[es].innerText || "").replace(/\s+/g, " ").trim();
      if (st.length < 12) out.content.emptySections++;
    }
    out.content.externalResources = 0;
    var exts = document.querySelectorAll(
      'link[href^="http"], script[src^="http"], img[src^="http"], iframe[src^="http"], source[src^="http"]'
    );
    out.content.externalResources = exts.length;

    /* ── motion ────────────────────────────────────────────────────── */
    var reduced = false;
    for (var ms = 0; ms < document.styleSheets.length; ms++) {
      var rules;
      try { rules = document.styleSheets[ms].cssRules; } catch (e) { continue; }
      for (var mr = 0; mr < rules.length; mr++) {
        if (rules[mr].type === 4 &&
          /prefers-reduced-motion/.test(rules[mr].conditionText || "")) {
          reduced = true;
        }
      }
    }
    out.motion.reducedMotionPath = reduced;
    var animated = 0;
    for (var an = 0; an < all.length; an++) {
      var acs2 = getComputedStyle(all[an]);
      if (acs2.animationName && acs2.animationName !== "none") animated++;
    }
    out.motion.animatedElements = animated;

    /* ── what kind of artifact is this? ─────────────────────────────── */
    var kind = (document.body.getAttribute("data-artifact") ||
      document.documentElement.getAttribute("data-artifact") || "").toLowerCase();
    if (!kind) {
      if (document.querySelector(".slide, [data-screen-label]")) kind = "deck";
      else if (document.querySelector(".run-link, .runs, .tool-call")) kind = "agent";
      else if (document.querySelector(".kpi, .kpis, .rail, .side")) kind = "dashboard";
      else kind = "page";
    }
    out.kind = kind;

    /* ── distance from the default look ────────────────────────────── */
    var accentHue = accentRgb ? hueOf(accentRgb) : null;
    out.defaultDistance = {
      headlineFont: out.hierarchy.h1Font,
      bodyFont: bodyFont,
      accentHue: accentHue,
      background: pageBg,
      headlineIsDefault: isDefaultStack(out.hierarchy.h1Font),
      bodyIsDefault: isDefaultStack(bodyFont),
      accentIsDefaultFamily: accentHue !== null &&
        (accentHue > 255 && accentHue < 300),           /* purple / indigo */
      backgroundIsDefaultFamily:
        pageBg[0] > 225 && pageBg[1] > 220 && pageBg[2] > 205, /* cream / warm white */
    };
    var d = out.defaultDistance;
    d.score = 0;
    d.away = [];
    if (!d.headlineIsDefault) { d.score++; d.away.push("headline font"); }
    if (!d.bodyIsDefault) { d.score++; d.away.push("body font"); }
    if (!d.accentIsDefaultFamily) { d.score++; d.away.push("accent family"); }
    if (!d.backgroundIsDefaultFamily) { d.score++; d.away.push("background family"); }

    return out;
  }

  function publish(payload) {
    try {
      var json = JSON.stringify(payload).replace(/</g, "\\u003c");
      var el = document.getElementById(RID);
      if (!el) {
        el = document.createElement("script");
        el.type = "application/json";
        el.id = RID;
        el.textContent = "";
        (document.body || document.documentElement).appendChild(el);
      }
      el.textContent = json;
    } catch (e) {}
  }

  if (document.body && !W.__dsScorePublished) {
    W.__dsScorePublished = true;
    try { publish(measure()); } catch (e) { publish({ ok: false, error: String(e) }); }
  }

  if (!W.__dsScoreLate) {
    W.__dsScoreLate = true;
    W.addEventListener("load", function () {
      setTimeout(function () {
        try {
          var d = measure();
          d.late = true;
          publish(d);
        } catch (e) {}
      }, 60);
    });
  }
})();
