// Shared menu + notes panel. Edit LINKS once; every page loads this file.
(function () {
  const P = window.PROJECT || {}, C = P.community || {};
  const CTA = C.url ? `Join our ${C.platform || ""} community: ${C.name || ""} ${C.url}` : "";   // from project.json
  // Menu grouped by what you are doing. Edit GROUPS once; every page loads this file.
  const GROUPS = [
    ["🧭 Start", [["architecture.html", "🏛️ Architecture"], ["environment.html", "🧰 Environment"], ["timeline.html", "⏱️ Time & order"], ["spec.html", "📘 Master spec (prompt)"]]],
    ["🎬 Make", [["index.html", "🏠 Project"], ["preprod.html", "📝 Pre-prod"], ["prod.html", "🎬 Prod"], ["postprod.html", "✅ Post-prod"], ["run.html", "🧪 Run & links"], ["publish.html", "📣 Publish"]]],
    ["🔎 Review", [["player.html", "▶️ Player"], ["script.html", "📜 Script"], ["artifacts.html", "🧩 Artifacts"], ["edl.html", "✂️ EDL"], ["changelog.html", "🗒️ Changelog"], ["metadata.html", "📺 YouTube metadata"]]],
    ["🔗 Links", [["http://localhost:3000/LongForm", "🎞️ Remotion Studio", true], ["readme.html", "📄 README"],
      ...(C.url ? [[C.url, "🚀 Join " + (C.name || "the community"), true]] : []),
      ...((P.links || []).map((l) => [l.url, l.label, true])),
      ...[["youtube", "▶️ YouTube post"], ["linkedin", "💼 LinkedIn post"], ["x", "✖️ X post"]].filter(([k]) => (P.publish || {})[k]).map(([k, t]) => [P.publish[k], t, true])]],
  ];
  if (P.title) document.title = P.title + ": " + (document.title.split(":").pop().trim() || "page");   // title from project.json
  const here = location.pathname.split("/").pop() || "index.html";
  const nav = document.createElement("nav");
  nav.innerHTML = '<b class="brand">🎬 ' + (P.brand || document.title.split(":")[0]) + '</b><button id="navtoggle" title="Collapse or expand the menu">▾ Menu</button>' + GROUPS.map(([g, items]) =>
    `<span class="grp"><i>${g}</i>` + items.map(([h, t, ext]) =>
      `<a href="${h}" ${ext ? 'target="_blank" rel="noopener"' : ""} class="${h === here ? "on" : ""}">${t}</a>`).join("") + "</span>").join("");
  const css = document.createElement("style");
  css.textContent = `body{margin:0;background:#0b0b0f;color:#eee;font:16px/1.6 system-ui,sans-serif}
  nav{position:sticky;top:0;z-index:9;display:flex;flex-wrap:wrap;gap:6px 16px;align-items:center;padding:10px 20px;background:#14141c;border-bottom:1px solid #2a2a38}
  nav .brand{margin-right:8px}#navtoggle{margin-left:auto;order:2;padding:4px 12px;background:#2a2a38;color:#eee;font-weight:600}nav.collapsed .grp{display:none}nav.collapsed{padding:6px 20px}.grp{display:flex;flex-wrap:wrap;align-items:center;gap:2px 4px;padding:2px 10px;border-left:1px solid #2a2a38}.grp i{font-style:normal;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:#7a7a92;margin-right:4px}nav a{color:#bbb;text-decoration:none;padding:4px 8px;border-radius:8px}nav a:hover,nav a.on{background:#ff7a3d;color:#000}
  main{max-width:960px;margin:0 auto;padding:24px 20px 120px}h1,h2,h3{line-height:1.25}a{color:#ff9a66}
  code,pre{background:#1a1a24;border-radius:6px}code{padding:1px 5px}pre{padding:12px;overflow:auto}
  table{border-collapse:collapse;width:100%;margin:12px 0}td,th{border:1px solid #2a2a38;padding:6px 10px;text-align:left;vertical-align:top}
  button,.btn{background:#ff7a3d;color:#000;border:0;border-radius:8px;padding:8px 14px;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block}
  #notes{position:fixed;right:16px;bottom:16px;z-index:10}#notes .panel{display:none;width:min(360px,90vw);background:#14141c;border:1px solid #2a2a38;border-radius:12px;padding:10px}
  #notes.open .panel{display:block}#notes textarea{width:100%;height:160px;background:#0b0b0f;color:#eee;border:1px solid #2a2a38;border-radius:8px;box-sizing:border-box}
  .copy{margin-left:8px;font-size:12px;padding:3px 8px}@media(max-width:600px){nav{padding:8px 12px}}`;
  document.head.appendChild(css);
  document.body.prepend(nav);
  const tg = nav.querySelector("#navtoggle");
  const setCollapsed = (c) => { nav.classList.toggle("collapsed", c); tg.textContent = c ? "▸ Menu" : "▾ Menu"; tg.setAttribute("aria-expanded", String(!c)); try { localStorage.setItem("nav:collapsed", c ? "1" : "0"); } catch (e) {} };
  let startCollapsed = false; try { startCollapsed = localStorage.getItem("nav:collapsed") === "1"; } catch (e) {}
  setCollapsed(startCollapsed);
  tg.onclick = () => setCollapsed(!nav.classList.contains("collapsed"));

  window.copyText = (t) => navigator.clipboard.writeText(t).catch(() => {
    const a = document.createElement("textarea"); a.value = t; document.body.appendChild(a); a.select(); document.execCommand("copy"); a.remove();
  });

  // Notes panel (autosave per page; key n opens, Esc closes)
  const key = "notes:" + here, box = document.createElement("div"); box.id = "notes";
  box.innerHTML = '<button id="nb">📝 Notes</button><div class="panel"><textarea></textarea><p><button id="nc">Copy</button> <button id="nd">Download</button> <button id="nx">Clear</button></p></div>';
  document.body.appendChild(box);
  const ta = box.querySelector("textarea");
  try { ta.value = localStorage.getItem(key) || ""; } catch (e) {}
  const full = () => `${document.title}\n${location.href}\n${new Date().toString()}\n\n${ta.value}\n\n${CTA}\n`;
  ta.oninput = () => { try { localStorage.setItem(key, ta.value); } catch (e) {} };
  box.querySelector("#nb").onclick = () => box.classList.toggle("open");
  box.querySelector("#nc").onclick = () => window.copyText(full());
  box.querySelector("#nd").onclick = () => { const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([full()])); a.download = here + "-notes.txt"; a.click(); };
  box.querySelector("#nx").onclick = () => { ta.value = ""; ta.oninput(); };
  addEventListener("keydown", (e) => {
    if (e.target.tagName === "TEXTAREA" || e.target.tagName === "INPUT") { if (e.key === "Escape") box.classList.remove("open"); return; }
    if (e.key === "n") { box.classList.add("open"); ta.focus(); e.preventDefault(); } else if (e.key === "Escape") box.classList.remove("open");
  });
})();
