/* Design Studio — render verification probe.
 *
 * Injected by scripts/verify.py into a temporary copy of an artifact.
 * It runs inside the page, measures the *rendered* result, and writes a
 * JSON result into a <script> element carrying that id.
 *
 * The result element carries the id __ds_probe__ (written with single quotes
 * here on purpose, so the extractor cannot mistake this comment for it).
 *
 * The file is injected twice:
 *   1. in the head — installs error capture before the page's own scripts run
 *   2. at the end of the body — takes the first measurement
 * A second measurement is published after `load` + `document.fonts.ready`
 * so font swaps and late images are included in the numbers.
 *
 * No dependencies, no build step, no network.
 */
(function () {
  "use strict";

  var RID = "__ds_probe__";
  var MAX = 40; /* max entries kept per list */

  var W = window;
  if (!W.__ds) {
    W.__ds = { errors: [], published: false, lateScheduled: false };
  }

  /* ── error capture (head injection) ─────────────────────────────────── */
  if (!W.__ds.errorsInstalled) {
    W.__ds.errorsInstalled = true;
    W.addEventListener("error", function (e) {
      W.__ds.errors.push({
        message: String((e && e.message) || "script error"),
        source: String((e && e.filename) || "") + ":" + String((e && e.lineno) || "")
      });
    });
    W.addEventListener("unhandledrejection", function (e) {
      W.__ds.errors.push({
        message: "unhandled rejection: " + String((e && e.reason) || e),
        source: ""
      });
    });
    var nativeError = console.error;
    console.error = function () {
      try {
        W.__ds.errors.push({
          message: Array.prototype.map.call(arguments, function (a) {
            return String(a);
          }).join(" "),
          source: "console.error"
        });
      } catch (err) {}
      return nativeError.apply(console, arguments);
    };
  }

  /* ── helpers ────────────────────────────────────────────────────────── */

  function selector(el) {
    if (!el || el.nodeType !== 1) return "?";
    var s = el.tagName.toLowerCase();
    if (el.id) return s + "#" + el.id;
    var cls = (el.getAttribute("class") || "").trim().split(/\s+/).filter(Boolean).slice(0, 2);
    if (cls.length) s += "." + cls.join(".");
    var p = el.parentElement;
    if (p && p.children) {
      var same = Array.prototype.filter.call(p.children, function (c) {
        return c.tagName === el.tagName;
      });
      if (same.length > 1) s += ":nth-of-type(" + (same.indexOf(el) + 1) + ")";
    }
    return s;
  }

  function textOf(el) {
    var t = (el.textContent || "").replace(/\s+/g, " ").trim();
    return t.length > 70 ? t.slice(0, 70) + "…" : t;
  }

  function parseColor(str) {
    if (!str) return null;
    str = String(str).trim();
    if (str === "transparent") return [0, 0, 0, 0];

    var m = str.match(/^rgba?\(([^)]+)\)$/i);
    if (m) {
      var p = m[1].split(/[\s,\/]+/).filter(Boolean);
      var r = parseFloat(p[0]);
      var g = parseFloat(p[1]);
      var b = parseFloat(p[2]);
      var a = p.length > 3 ? parseFloat(p[3]) : 1;
      if (isNaN(r) || isNaN(g) || isNaN(b)) return null;
      return [r, g, b, isNaN(a) ? 1 : a];
    }

    /* Chrome serialises color-mix() results as color(srgb r g b) — the
     * components are 0-1 (or percentages). */
    m = str.match(/^color\(srgb\s+([^)]+)\)$/i);
    if (m) {
      var q = m[1].split(/[\s\/]+/).filter(Boolean);
      if (q.length < 3) return null;
      var vals = q.slice(0, 3).map(function (v) {
        if (v.slice(-1) === "%") return parseFloat(v) * 2.55;
        return parseFloat(v) * 255;
      });
      var alpha = 1;
      if (q.length > 3) {
        var av = q[3];
        alpha = av.slice(-1) === "%" ? parseFloat(av) / 100 : parseFloat(av);
      }
      if (vals.some(isNaN)) return null;
      return [vals[0], vals[1], vals[2], isNaN(alpha) ? 1 : alpha];
    }

    /* oklch() — as authored or as Chrome's canonical form. */
    m = str.match(/^oklch\(\s*([\d.]+%?)\s+([\d.]+)\s+([\d.]+)(?:deg)?\s*\)/i);
    if (m) {
      var L = parseFloat(m[1]) / (m[1].slice(-1) === "%" ? 100 : 1);
      var C = parseFloat(m[2]);
      var H = parseFloat(m[3]) * Math.PI / 180;
      var aa = C * Math.cos(H);
      var bb = C * Math.sin(H);
      var l_ = L + 0.3963377774 * aa + 0.2158037573 * bb;
      var m_ = L - 0.1055613458 * aa - 0.0638541728 * bb;
      var s_ = L - 0.0894841775 * aa - 1.2914855480 * bb;
      var l = l_ * l_ * l_;
      var m2 = m_ * m_ * m_;
      var s = s_ * s_ * s_;
      var lr = 4.0767416621 * l - 3.3077115913 * m2 + 0.2309699292 * s;
      var lg = -1.2684380046 * l + 2.6097574011 * m2 - 0.3413193965 * s;
      var lb = -0.0041960863 * l - 0.7034186147 * m2 + 1.7076147010 * s;
      function enc(c) {
        c = c < 0 ? 0 : c > 1 ? 1 : c;
        var v = c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
        return v * 255;
      }
      return [enc(lr), enc(lg), enc(lb), 1];
    }

    return null;
  }

  function over(fg, bg) {
    var a = fg[3];
    return [
      fg[0] * a + bg[0] * (1 - a),
      fg[1] * a + bg[1] * (1 - a),
      fg[2] * a + bg[2] * (1 - a),
      1
    ];
  }

  function composite(stack) {
    var out = [255, 255, 255, 1];
    for (var i = stack.length - 1; i >= 0; i--) {
      out = over(stack[i], out);
    }
    return out;
  }

  function luminance(c) {
    var s = c.slice(0, 3).map(function (v) {
      v = v / 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * s[0] + 0.7152 * s[1] + 0.0722 * s[2];
  }

  function ratio(a, b) {
    var l1 = luminance(a);
    var l2 = luminance(b);
    var hi = Math.max(l1, l2);
    var lo = Math.min(l1, l2);
    return (hi + 0.05) / (lo + 0.05);
  }

  function visible(el, cs) {
    if (cs.display === "none" || cs.visibility === "hidden") return false;
    if (parseFloat(cs.opacity) === 0) return false;
    var r = el.getBoundingClientRect();
    return !(r.width === 0 && r.height === 0);
  }

  function hasOwnText(el) {
    var kids = el.childNodes;
    for (var i = 0; i < kids.length; i++) {
      if (kids[i].nodeType === 3 && kids[i].nodeValue && kids[i].nodeValue.trim()) return true;
    }
    return false;
  }

  /* Effective background of an element: walk up until an opaque layer. */
  function backgroundFor(el) {
    var stack = [];
    var node = el;
    var image = false;
    while (node && node.nodeType === 1) {
      var cs = getComputedStyle(node);
      if (cs.backgroundImage && cs.backgroundImage !== "none") image = true;
      var c = parseColor(cs.backgroundColor);
      if (c && c[3] > 0) {
        stack.push(c);
        if (c[3] >= 1) return { color: composite(stack), image: image };
      }
      node = node.parentElement;
    }
    stack.push([255, 255, 255, 1]);
    return { color: composite(stack), image: image };
  }

  /* ── the measurement ────────────────────────────────────────────────── */

  function measure() {
    var doc = document.documentElement;
    var vw = doc.clientWidth;
    var data = {
      ok: true,
      late: false,
      viewport: { w: vw, inner: W.innerWidth, h: W.innerHeight, dpr: W.devicePixelRatio || 1 },
      doc: {
        scrollWidth: doc.scrollWidth,
        clientWidth: vw,
        bodyScrollWidth: document.body ? document.body.scrollWidth : 0
      },
      counts: { elements: 0, textNodes: 0 },
      docOverflow: doc.scrollWidth > vw + 1,
      overflow: [],
      clipped: [],
      truncated: [],
      contrast: [],
      contrastSkipped: 0,
      tapTargets: [],
      images: [],
      minContent: [],
      focus: null,
      viewportMeta: null,
      errors: []
    };

    var all = document.body ? document.body.querySelectorAll("*") : [];
    data.counts.elements = all.length;

    /* A deck is a horizontal scroller by design — slides sit in a row and
     * the runtime scrolls between them. Everything else is measured against
     * the viewport. */
    var slides = document.querySelectorAll(".slide, [data-screen-label]");
    var isDeck = slides.length > 0;
    data.deck = isDeck;

    function nearestSlide(el) {
      var n = el;
      while (n && n !== document.body) {
        if (n.nodeType === 1 && n.classList &&
            (n.classList.contains("slide") || n.hasAttribute("data-screen-label"))) {
          return n;
        }
        n = n.parentElement;
      }
      return null;
    }

    /* Content inside a deliberate scroller (overflow auto/scroll/hidden) is
     * not page overflow — it is contained. */
    function containedByScroller(el) {
      var n = el.parentElement;
      while (n && n !== document.documentElement) {
        var ox = getComputedStyle(n).overflowX;
        if (ox === "auto" || ox === "scroll" || ox === "hidden" || ox === "clip") return true;
        n = n.parentElement;
      }
      return false;
    }

    /* 1 · horizontal overflow — elements that stick out of their frame */
    for (var i = 0; i < all.length; i++) {
      var el = all[i];
      var cs = getComputedStyle(el);
      if (cs.position === "fixed") continue;
      if (!visible(el, cs)) continue;

      var frameRight = vw;
      if (isDeck) {
        var slide = nearestSlide(el);
        if (!slide || slide === el) continue; /* the slide IS the frame */
        var sRect = slide.getBoundingClientRect();
        var sPad = parseFloat(getComputedStyle(slide).paddingRight) || 0;
        frameRight = sRect.left + slide.clientWidth - sPad;
      } else if (containedByScroller(el)) {
        continue;
      }

      var r = el.getBoundingClientRect();
      var overRight = r.right - frameRight;
      if (overRight <= 1) continue;
      /* Ignore children that merely inherit an overflowing parent. */
      var p = el.parentElement;
      var pOver = 0;
      if (p) {
        var pr = p.getBoundingClientRect();
        pOver = pr.right - frameRight;
      }
      if (overRight > pOver + 1) {
        data.overflow.push({
          sel: selector(el),
          right: Math.round(r.right),
          width: Math.round(r.width),
          text: textOf(el)
        });
      }
    }
    data.overflow.sort(function (a, b) { return b.right - a.right; });
    data.overflow = data.overflow.slice(0, MAX);

    /* The document itself only overflows when the overflow is not the
     * deck's own slide track. */
    var deckExpected = 0;
    if (isDeck && slides.length) {
      var firstRect = slides[0].getBoundingClientRect();
      deckExpected = Math.ceil(slides.length * firstRect.width);
    }
    data.docOverflow =
      doc.scrollWidth > vw + 1 && (!isDeck || doc.scrollWidth > deckExpected + 2);
    data.deckExpectedWidth = deckExpected;

    /* 2 · clipped text — content cut off without an ellipsis */
    for (var j = 0; j < all.length; j++) {
      var cel = all[j];
      var ccs = getComputedStyle(cel);
      var ox = ccs.overflowX;
      if (ox !== "hidden" && ox !== "clip") continue;
      if (!visible(cel, ccs)) continue;
      if (cel.scrollWidth <= cel.clientWidth + 1) continue;
      /* Code blocks scroll or clip on purpose. */
      var tag = cel.tagName.toLowerCase();
      if (tag === "pre" || tag === "code" || tag === "kbd" || tag === "samp") continue;
      /* Screen-reader-only text is hidden on purpose. */
      if (cel.clientWidth <= 2 || cel.clientHeight <= 2) continue;
      var excerpt = textOf(cel);
      if (!excerpt) continue;
      var intentional =
        ccs.textOverflow === "ellipsis" &&
        (ccs.whiteSpace === "nowrap" || ccs.whiteSpace === "pre");

      /* Find the descendant that actually sticks out, so the report names
       * the culprit instead of the box that hides it. */
      var cRect = cel.getBoundingClientRect();
      var cPad = parseFloat(ccs.paddingRight) || 0;
      var limit = cRect.left + cel.clientWidth - cPad;
      var culprit = null;
      var kids = cel.querySelectorAll("*");
      for (var q = 0; q < kids.length; q++) {
        var kid = kids[q];
        var kcs = getComputedStyle(kid);
        if (kcs.position === "fixed") continue;
        if (!visible(kid, kcs)) continue;
        var kr = kid.getBoundingClientRect();
        if (kr.right - limit <= 1) continue;
        if (!culprit || kr.right > culprit.right) {
          culprit = { sel: selector(kid), right: Math.round(kr.right), text: textOf(kid) };
        }
      }

      var entry = {
        sel: selector(cel),
        scrollWidth: cel.scrollWidth,
        clientWidth: cel.clientWidth,
        text: excerpt
      };
      if (culprit) {
        entry.culprit = culprit.sel;
        entry.culpritRight = culprit.right;
        entry.culpritText = culprit.text;
      }
      if (intentional) data.truncated.push(entry);
      else data.clipped.push(entry);
    }
    data.clipped = data.clipped.slice(0, MAX);
    data.truncated = data.truncated.slice(0, MAX);

    /* 3 · computed text contrast */
    var seen = {};
    for (var k = 0; k < all.length; k++) {
      var tel = all[k];
      var tcs = getComputedStyle(tel);
      if (!visible(tel, tcs)) continue;
      if (!hasOwnText(tel)) continue;
      data.counts.textNodes++;
      var bg = backgroundFor(tel);
      if (bg.image) {
        data.contrastSkipped++;
        continue;
      }
      var fg = parseColor(tcs.color);
      if (!fg) continue;
      var fgSolid = fg[3] < 1 ? over(fg, bg.color) : fg;
      var size = parseFloat(tcs.fontSize) || 16;
      var weight = parseInt(tcs.fontWeight, 10) || 400;
      var large = size >= 24 || (size >= 18.66 && weight >= 700);
      var min = large ? 3.0 : 4.5;
      var cr = ratio(fgSolid, bg.color);
      if (cr >= min) continue;
      var key =
        selector(tel) + "|" + tcs.color + "|" + Math.round(cr * 10) + "|" + (large ? "L" : "N");
      if (seen[key]) continue;
      seen[key] = 1;
      data.contrast.push({
        sel: selector(tel),
        color: tcs.color,
        background: "rgb(" +
          Math.round(bg.color[0]) + ", " +
          Math.round(bg.color[1]) + ", " +
          Math.round(bg.color[2]) + ")",
        ratio: Math.round(cr * 100) / 100,
        required: min,
        size: Math.round(size * 10) / 10,
        large: large,
        text: textOf(tel)
      });
    }
    data.contrast.sort(function (a, b) { return a.ratio - b.ratio; });
    data.contrast = data.contrast.slice(0, MAX);

    /* 4 · tap targets (WCAG 2.2 AA 2.5.8 — 24×24 CSS px) */
    var INTERACTIVE =
      'a[href], button, input:not([type="hidden"]), select, textarea, ' +
      '[role="button"], [role="link"], [role="tab"], [role="menuitem"], ' +
      '[tabindex]:not([tabindex="-1"])';
    var targets = document.querySelectorAll(INTERACTIVE);
    var TEXT_CONTAINERS = /^(p|li|td|th|dd|blockquote|figcaption|label)$/i;

    /* Collect every target box first — WCAG 2.5.8 lets an undersized
     * target pass when a 24px circle around it hits nothing else. */
    var boxes = [];
    for (var b = 0; b < targets.length; b++) {
      var bt = targets[b];
      var bcs = getComputedStyle(bt);
      if (!visible(bt, bcs)) continue;
      if (bt.disabled) continue;
      var br = bt.getBoundingClientRect();
      if (!br.width && !br.height) continue;
      boxes.push({
        el: bt,
        cs: bcs,
        rect: br,
        cx: br.left + br.width / 2,
        cy: br.top + br.height / 2
      });
    }

    for (var t = 0; t < boxes.length; t++) {
      var tg = boxes[t].el;
      var tcs2 = boxes[t].cs;
      var tr = boxes[t].rect;
      if (tr.width >= 24 && tr.height >= 24) continue;

      /* WCAG 2.5.8 exempts targets that sit inline in a sentence or block of
       * text. A flex/grid parent blockifies the link, so the text context is
       * looked up through the ancestors, not just the direct parent. */
      if (tg.tagName === "A" && tg.hasAttribute("href")) {
        var exempt = false;
        var n = tg.parentElement;
        while (n && n !== document.body) {
          if (n.nodeType === 1 && TEXT_CONTAINERS.test(n.tagName)) { exempt = true; break; }
          n = n.parentElement;
        }
        if (!exempt && tcs2.display === "inline") {
          var par = tg.parentElement;
          var pd = par ? getComputedStyle(par).display : "";
          if (pd !== "flex" && pd !== "grid" &&
              pd !== "inline-flex" && pd !== "inline-grid") {
            exempt = true; /* flowing with the surrounding sentence */
          }
        }
        if (exempt) continue;
      }

      /* Spacing exception: nothing else within 24px of this target. */
      var spaced = true;
      for (var o = 0; o < boxes.length; o++) {
        if (o === t) continue;
        var dx = boxes[o].cx - boxes[t].cx;
        var dy = boxes[o].cy - boxes[t].cy;
        if (Math.sqrt(dx * dx + dy * dy) < 24) { spaced = false; break; }
      }
      if (spaced) continue;

      data.tapTargets.push({
        sel: selector(tg),
        width: Math.round(tr.width * 10) / 10,
        height: Math.round(tr.height * 10) / 10,
        text: textOf(tg)
      });
    }
    data.tapTargets = data.tapTargets.slice(0, MAX);

    /* 5 · images without intrinsic dimensions (layout shift risk) */
    var imgs = document.querySelectorAll("img");
    for (var m = 0; m < imgs.length; m++) {
      var img = imgs[m];
      var ics = getComputedStyle(img);
      if (!visible(img, ics)) continue;
      if (img.getAttribute("width") || img.getAttribute("height")) continue;
      data.images.push({
        sel: selector(img),
        src: (img.getAttribute("src") || "").slice(0, 80),
        alt: (img.getAttribute("alt") || "").slice(0, 60)
      });
    }
    data.images = data.images.slice(0, MAX);

    /* 6 · focus indicator — static scan of the shipped stylesheets.
     * CSSOM hides longhands when a shorthand contains var(), so the
     * declaration text is parsed instead of the resolved properties. */
    var focusRules = [];
    function declText(r) {
      var t = r.cssText || "";
      var i = t.indexOf("{");
      var j = t.lastIndexOf("}");
      return i >= 0 && j > i ? t.slice(i + 1, j) : "";
    }
    function visibleDecl(decl) {
      var parts = decl.toLowerCase().split(";");
      for (var p = 0; p < parts.length; p++) {
        var part = parts[p];
        var ci = part.indexOf(":");
        if (ci < 0) continue;
        var prop = part.slice(0, ci).trim();
        var val = part.slice(ci + 1).trim();
        if (!prop || !val) continue;
        if (prop === "outline") {
          if (val !== "none" && val !== "0" && val !== "0px") return true;
        } else if (prop === "outline-style") {
          if (val !== "none" && val !== "hidden") return true;
        } else if (prop === "outline-width") {
          if (val !== "0" && val !== "0px" && val !== "medium") return true;
        } else if (prop === "outline-color") {
          if (val !== "transparent" && val !== "inherit" && val !== "currentcolor") return true;
        } else if (prop === "box-shadow") {
          if (val !== "none") return true;
        } else if (prop === "border" || prop === "border-color" ||
                   prop === "border-width" || prop === "border-style" ||
                   prop === "border-bottom" || prop === "border-top" ||
                   prop === "border-left" || prop === "border-right") {
          if (val !== "none" && val !== "transparent" && val !== "inherit" &&
              val !== "currentcolor" && val !== "0" && val !== "0px" && val !== "medium") {
            return true;
          }
        } else if (prop === "text-decoration" || prop === "text-decoration-line") {
          if (val !== "none") return true;
        } else if (prop === "background" || prop === "background-color") {
          if (val !== "transparent" && val !== "inherit" && val !== "currentcolor") return true;
        }
      }
      return false;
    }
    function scan(rules) {
      if (!rules) return;
      for (var n = 0; n < rules.length; n++) {
        var r = rules[n];
        if (r.type === 1 && r.selectorText && r.selectorText.indexOf(":focus") !== -1) {
          var decl = declText(r);
          focusRules.push({
            sel: r.selectorText,
            decl: decl.replace(/\s+/g, " ").trim().slice(0, 160),
            visible: visibleDecl(decl)
          });
        } else if (r.type === 4 && r.cssRules) {
          scan(r.cssRules);
        }
      }
    }
    for (var s = 0; s < document.styleSheets.length; s++) {
      try {
        scan(document.styleSheets[s].cssRules);
      } catch (e) {
        /* cross-origin stylesheet — not inspectable */
      }
    }
    var hasIndicator = focusRules.some(function (r) { return r.visible; });
    data.focus = {
      rules: focusRules.length,
      hasIndicator: hasIndicator,
      selectors: focusRules.slice(0, 6).map(function (r) { return r.sel; }),
      declarations: focusRules.slice(0, 4).map(function (r) { return r.decl; })
    };

    /* 7 · viewport meta */
    var vm = document.querySelector('meta[name="viewport"]');
    data.viewportMeta = vm ? vm.getAttribute("content") : null;

    /* 8 · collected runtime errors */
    data.errors = W.__ds.errors.slice(0, 20);

    /* 9 · min-content pressure. A table (or nowrap block) that only fits
     * because the current font is narrow will overflow on the next platform
     * whose font fallback is wider. Force the min-content width and compare
     * it with the space actually available. */
    var tight = document.querySelectorAll("table, [data-mincontent]");
    for (var t2 = 0; t2 < tight.length; t2++) {
      var tb = tight[t2];
      var tcs3 = getComputedStyle(tb);
      if (!visible(tb, tcs3)) continue;
      if (tcs3.position === "fixed") continue;
      var host = tb.parentElement;
      if (!host) continue;
      /* Inside a scroller the width is allowed to exceed the box. */
      var contained = false;
      var anc = host;
      while (anc && anc !== document.documentElement) {
        var ox2 = getComputedStyle(anc).overflowX;
        if (ox2 === "auto" || ox2 === "scroll" || ox2 === "hidden" || ox2 === "clip") {
          contained = true;
          break;
        }
        anc = anc.parentElement;
      }
      if (contained) continue;
      var hcs = getComputedStyle(host);
      var avail = host.clientWidth
        - (parseFloat(hcs.paddingLeft) || 0)
        - (parseFloat(hcs.paddingRight) || 0);
      if (avail <= 0) continue;
      var prevWidth = tb.style.width;
      tb.style.width = "min-content";
      var minW = tb.getBoundingClientRect().width;
      tb.style.width = prevWidth;
      if (minW - avail > 1) {
        data.minContent.push({
          sel: selector(tb),
          minContent: Math.round(minW),
          available: Math.round(avail),
          overflow: true
        });
      } else if (minW > avail * 0.97) {
        data.minContent.push({
          sel: selector(tb),
          minContent: Math.round(minW),
          available: Math.round(avail),
          overflow: false
        });
      }
    }

    return data;
  }

  /* ── publish ────────────────────────────────────────────────────────── */

  function publish(payload) {
    try {
      var json = JSON.stringify(payload);
      /* Escape "<" so the JSON can never close its own script element. */
      json = json.replace(/</g, "\\u003c");
      var el = document.getElementById(RID);
      if (!el) {
        el = document.createElement("script");
        el.type = "application/json";
        el.id = RID;
        el.textContent = "";
        (document.body || document.documentElement).appendChild(el);
      }
      el.textContent = json;
      document.title = "__ds_probe_ok__";
    } catch (e) {
      /* nothing else we can do — the Python side will report a missing result */
    }
  }

  /* First measurement: only meaningful once <body> exists. */
  if (document.body && !W.__ds.published) {
    W.__ds.published = true;
    try {
      publish(measure());
    } catch (e) {
      publish({ ok: false, error: String(e) });
    }
  }

  /* Re-measure after load + webfont settle. */
  if (!W.__ds.lateScheduled) {
    W.__ds.lateScheduled = true;
    W.addEventListener("load", function () {
      var run = function () {
        try {
          var d = measure();
          d.late = true;
          publish(d);
        } catch (e) {}
      };
      if (W.document.fonts && W.document.fonts.ready && W.document.fonts.ready.then) {
        W.document.fonts.ready.then(function () { setTimeout(run, 30); });
      } else {
        setTimeout(run, 30);
      }
    });
  }
})();
