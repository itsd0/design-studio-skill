/* Design Studio — design-system probe.
 *
 * Injected by scripts/extract.py into a temporary copy of a page.
 * It walks the rendered document and reports the computed design system:
 * the colours, type, spacing, radii and shadows the page actually uses.
 *
 * The result is written into a script element carrying the id
 * __ds_design__ (single-quoted here on purpose, so the extractor cannot
 * mistake this comment for it).
 */
(function () {
  "use strict";

  var RID = "__ds_design__";
  var W = window;
  var MAX_SAMPLES = 3;

  function selector(el) {
    if (!el || el.nodeType !== 1) return "?";
    var s = el.tagName.toLowerCase();
    if (el.id) return s + "#" + el.id;
    var cls = (el.getAttribute("class") || "").trim().split(/\s+/).filter(Boolean).slice(0, 2);
    if (cls.length) s += "." + cls.join(".");
    return s;
  }

  function textOf(el) {
    var t = (el.textContent || "").replace(/\s+/g, " ").trim();
    return t.length > 48 ? t.slice(0, 48) + "…" : t;
  }

  function bump(map, key, sample) {
    if (!key) return;
    if (!map[key]) map[key] = { value: key, count: 0, samples: [] };
    map[key].count++;
    if (sample && map[key].samples.length < MAX_SAMPLES) map[key].samples.push(sample);
  }

  function rank(map) {
    var out = [];
    for (var k in map) if (map.hasOwnProperty(k)) out.push(map[k]);
    out.sort(function (a, b) { return b.count - a.count; });
    return out;
  }

  function measure() {
    var out = {
      ok: true,
      url: location.href,
      title: document.title || "",
      colors: { text: {}, background: {}, border: {}, fill: {}, link: {},
                buttonBg: {}, buttonText: {}, heading: {} },
      typography: {},
      spacing: { padding: {}, margin: {}, gap: {} },
      radii: {},
      shadows: {},
      layout: { maxWidths: {}, grids: {}, containers: {} },
      structure: { counts: {}, landmarks: [], headings: [] },
      media: { queries: [] }
    };

    var all = document.body ? document.body.querySelectorAll("*") : [];

    /* ── page-level facts: the anchors every other token is derived from ─ */
    var bodyCs = getComputedStyle(document.body);
    var htmlCs = getComputedStyle(document.documentElement);
    out.page = {
      bodyBg: bodyCs.backgroundColor,
      htmlBg: htmlCs.backgroundColor,
      bodyColor: bodyCs.color,
      bodyFont: bodyCs.fontFamily,
      bodySize: bodyCs.fontSize,
      bodyLineHeight: bodyCs.lineHeight,
      bodyLetterSpacing: bodyCs.letterSpacing,
      rootFontSize: htmlCs.fontSize
    };

    /* ── colours ─────────────────────────────────────────────────────── */
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      var cs = getComputedStyle(el);
      if (cs.display === "none" || cs.visibility === "hidden") continue;

      var sel = selector(el);
      var hasText = (el.textContent || "").trim().length > 0 &&
        Array.prototype.some.call(el.childNodes, function (n) {
          return n.nodeType === 3 && n.nodeValue.trim();
        });

      if (hasText) {
        bump(out.colors.text, cs.color, sel + " · " + textOf(el));
        bump(out.colors.text, cs.fill, sel + " · " + textOf(el));
      }
      if (cs.backgroundColor && cs.backgroundColor !== "rgba(0, 0, 0, 0)") {
        bump(out.colors.background, cs.backgroundColor, sel);
      }
      if (cs.borderTopWidth !== "0px" && cs.borderTopColor) {
        bump(out.colors.border, cs.borderTopColor, sel);
      }
      if (cs.backgroundImage && cs.backgroundImage !== "none") {
        var stops = cs.backgroundImage.match(/rgba?\([^)]+\)/g) || [];
        for (var g = 0; g < stops.length; g++) bump(out.colors.fill, stops[g], sel + " gradient");
      }
    }

    /* Links are the strongest accent signal; buttons the second. */
    var links = document.querySelectorAll("a");
    for (var la = 0; la < links.length; la++) {
      var lcs = getComputedStyle(links[la]);
      if (lcs.color) bump(out.colors.link, lcs.color, selector(links[la]));
    }
    var buttons = document.querySelectorAll("button, .btn, [role=button]");
    for (var bi = 0; bi < buttons.length; bi++) {
      var bcs = getComputedStyle(buttons[bi]);
      if (bcs.backgroundColor && bcs.backgroundColor !== "rgba(0, 0, 0, 0)") {
        bump(out.colors.buttonBg, bcs.backgroundColor, selector(buttons[bi]));
      }
      if (bcs.color) bump(out.colors.buttonText, bcs.color, selector(buttons[bi]));
    }
    var heads = document.querySelectorAll("h1, h2");
    for (var hi = 0; hi < heads.length; hi++) {
      var hcs = getComputedStyle(heads[hi]);
      if (hcs.color) bump(out.colors.heading, hcs.color, selector(heads[hi]));
    }

    /* ── typography ──────────────────────────────────────────────────── */
    var TAGS = ["h1", "h2", "h3", "h4", "p", "a", "button", "li", "span", "small", "code", "pre", "label", "td", "th", "blockquote"];
    for (var t = 0; t < TAGS.length; t++) {
      var nodes = document.querySelectorAll(TAGS[t]);
      for (var n = 0; n < nodes.length; n++) {
        var ne = nodes[n];
        var ncs = getComputedStyle(ne);
        if (ncs.display === "none") continue;
        var key = TAGS[t] + "|" + ncs.fontFamily + "|" + ncs.fontSize + "|" +
          ncs.fontWeight + "|" + ncs.lineHeight + "|" + ncs.letterSpacing + "|" + ncs.textTransform;
        bump(out.typography, key, selector(ne) + " · " + textOf(ne));
      }
    }

    /* ── spacing, radii, shadows ─────────────────────────────────────── */
    for (var s = 0; s < all.length; s++) {
      var e2 = all[s];
      var c2 = getComputedStyle(e2);
      if (c2.display === "none") continue;
      ["paddingTop", "paddingBottom", "paddingLeft", "paddingRight"].forEach(function (p) {
        var v = parseFloat(c2[p]);
        if (v > 0) bump(out.spacing.padding, String(Math.round(v)), selector(e2));
      });
      ["marginTop", "marginBottom", "marginLeft", "marginRight"].forEach(function (p) {
        var v = parseFloat(c2[p]);
        if (v > 0) bump(out.spacing.margin, String(Math.round(v)), selector(e2));
      });
      var gap = c2.rowGap !== "normal" ? c2.rowGap : c2.columnGap;
      if (gap && gap !== "normal") {
        var gv = parseFloat(gap);
        if (gv > 0) bump(out.spacing.gap, String(Math.round(gv)), selector(e2));
      }
      var r = parseFloat(c2.borderTopLeftRadius);
      if (r > 0) bump(out.radii, String(Math.round(r)), selector(e2));
      if (c2.boxShadow && c2.boxShadow !== "none") bump(out.shadows, c2.boxShadow, selector(e2));
      if (c2.maxWidth && c2.maxWidth !== "none") {
        var mw = parseFloat(c2.maxWidth);
        if (mw > 200) bump(out.layout.maxWidths, String(Math.round(mw)), selector(e2));
      }
      if (c2.display === "grid" || c2.display === "inline-grid") {
        bump(out.layout.grids, c2.gridTemplateColumns, selector(e2));
      }
    }

    /* ── structure ───────────────────────────────────────────────────── */
    var counts = {};
    ["a", "button", "input", "select", "textarea", "img", "svg", "form", "table", "nav", "header",
     "main", "footer", "section", "article", "aside", "h1", "h2", "h3", "ul", "ol", "li",
     "dialog", "details", "iframe", "video", "canvas"].forEach(function (tag) {
      var c = document.querySelectorAll(tag).length;
      if (c) counts[tag] = c;
    });
    out.structure.counts = counts;

    var landmarks = ["header", "nav", "main", "footer", "aside", "section[aria-label]", "section[aria-labelledby]"];
    for (var l = 0; l < landmarks.length; l++) {
      var ls = document.querySelectorAll(landmarks[l]);
      for (var m = 0; m < ls.length; m++) {
        out.structure.landmarks.push({
          tag: ls[m].tagName.toLowerCase(),
          label: ls[m].getAttribute("aria-label") ||
            (ls[m].getAttribute("aria-labelledby")
              ? (document.getElementById(ls[m].getAttribute("aria-labelledby")) || {}).textContent
              : "") || ""
        });
      }
    }

    for (var hh = 1; hh <= 3; hh++) {
      var hs = document.querySelectorAll("h" + hh);
      for (var q = 0; q < hs.length && q < 12; q++) {
        out.structure.headings.push({ level: hh, text: textOf(hs[q]) });
      }
    }

    /* ── media queries the page declares ─────────────────────────────── */
    for (var mi = 0; mi < document.styleSheets.length; mi++) {
      var sheet = document.styleSheets[mi];
      var rules;
      try { rules = sheet.cssRules; } catch (e) { continue; }
      for (var ri = 0; ri < rules.length; ri++) {
        if (rules[ri].type === 4 && rules[ri].conditionText) {
          out.media.queries.push(rules[ri].conditionText.replace(/\s+/g, " ").trim());
        }
      }
    }

    out.colors.text = rank(out.colors.text);
    out.colors.background = rank(out.colors.background);
    out.colors.border = rank(out.colors.border);
    out.colors.fill = rank(out.colors.fill);
    out.colors.link = rank(out.colors.link);
    out.colors.buttonBg = rank(out.colors.buttonBg);
    out.colors.buttonText = rank(out.colors.buttonText);
    out.colors.heading = rank(out.colors.heading);
    out.typography = rank(out.typography);
    out.spacing.padding = rank(out.spacing.padding);
    out.spacing.margin = rank(out.spacing.margin);
    out.spacing.gap = rank(out.spacing.gap);
    out.radii = rank(out.radii);
    out.shadows = rank(out.shadows);
    out.layout.maxWidths = rank(out.layout.maxWidths);
    out.layout.grids = rank(out.layout.grids);

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
      document.title = "__ds_design_ok__";
    } catch (e) {}
  }

  if (document.body && !W.__dsDesignPublished) {
    W.__dsDesignPublished = true;
    try { publish(measure()); } catch (e) { publish({ ok: false, error: String(e) }); }
  }

  if (!W.__dsDesignLate) {
    W.__dsDesignLate = true;
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
