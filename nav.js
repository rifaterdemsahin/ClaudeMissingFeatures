// Shared menu + notes panel. Edit LINKS once; every page loads this file.
(function () {
  const P = window.PROJECT || {}, C = P.community || {};
  const CTA = C.url ? `Join our ${C.platform || ""} community: ${C.name || ""} ${C.url}` : "";   // from project.json
  // Menu grouped by what you are doing. Edit GROUPS once; every page loads this file.
  const GROUPS = [
    ["🧭 Start", [["architecture.html", "🏛️ Architecture"], ["environment.html", "🧰 Environment"], ["timeline.html", "⏱️ Time & order"], ["pipeline.html", "🗺️ Pipeline"], ["evals.html", "🧪 Evals"], ["spec.html", "📘 Master spec (prompt)"]]],
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
  #notes{position:fixed;right:16px;bottom:16px;z-index:10}#notes .panel{display:none;width:min(400px,94vw);max-height:85vh;overflow-y:auto;background:#14141c;border:1px solid #2a2a38;border-radius:12px;padding:12px;box-shadow:0 8px 24px rgba(0,0,0,.5)}
  #notes.open .panel{display:block}#notes textarea{width:100%;height:100px;background:#0b0b0f;color:#eee;border:1px solid #2a2a38;border-radius:8px;padding:8px;box-sizing:border-box;font-family:inherit;font-size:13px;resize:vertical}
  #notes .btn-row{display:flex;gap:6px;flex-wrap:wrap;margin:8px 0}#notes .btn-row button{padding:6px 10px;font-size:12px}
  #notes .s-item{background:#0b0b0f;border:1px solid #2a2a38;border-radius:8px;padding:8px;margin-bottom:8px;font-size:12px}
  #notes .s-meta{display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;font-size:11px}
  #notes .s-acts{display:flex;gap:6px;margin-top:6px}#notes .s-acts button{padding:3px 8px;font-size:11px}
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

  // Notes panel (autosave per page + save multiple notes with page URL; key n opens, Esc closes)
  const key = "notes:" + here, box = document.createElement("div"); box.id = "notes";
  box.innerHTML = '<button id="nb">📝 Notes</button><div class="panel"><textarea placeholder="Type a note..."></textarea><p class="btn-row"><button id="ns">💾 Save</button> <button id="nc">Copy</button> <button id="nd">Download</button> <button id="nx">Clear</button></p><div id="savednotes" style="border-top:1px solid #2a2a38;padding-top:8px;margin-top:8px"></div></div>';
  document.body.appendChild(box);
  const ta = box.querySelector("textarea"), listEl = box.querySelector("#savednotes");
  try { ta.value = localStorage.getItem(key) || ""; } catch (e) {}
  const full = () => `${document.title}\n${location.href}\n${new Date().toString()}\n\n${ta.value}\n\n${CTA}\n`;
  ta.oninput = () => { try { localStorage.setItem(key, ta.value); } catch (e) {} };

  const LIST_KEY = "site:saved_notes";
  const getSaved = () => { try { return JSON.parse(localStorage.getItem(LIST_KEY)) || []; } catch (e) { return []; } };
  const setSaved = (l) => { try { localStorage.setItem(LIST_KEY, JSON.stringify(l)); } catch (e) {} };

  const renderSaved = () => {
    const list = getSaved();
    if (!list.length) {
      listEl.innerHTML = '<div style="opacity:.5;font-size:12px">No saved notes yet. Click 💾 Save to save notes with page URL.</div>';
      return;
    }
    listEl.innerHTML = `<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px"><span style="font-weight:700;font-size:12px">Saved notes (${list.length})</span><button id="nclrall" style="background:#2a2a38;color:#ddd;padding:2px 8px;font-size:11px">Clear all</button></div>` +
      list.map((n, i) => `
        <div class="s-item">
          <div class="s-meta">
            <a href="${n.url}" style="color:#ff7a3d;text-decoration:none;font-weight:700" title="${n.url}">🔗 ${n.page}</a>
            <span style="opacity:.6">${n.time}</span>
          </div>
          <div style="white-space:pre-wrap;color:#eee;line-height:1.3">${n.text.replace(/&/g, "&amp;").replace(/</g, "&lt;")}</div>
          <div class="s-acts">
            <button class="ncopy" data-i="${i}" style="background:#2a2a38;color:#eee">Copy</button>
            <button class="ndel" data-i="${i}" style="background:#3a1c1c;color:#fca5a5">Delete</button>
          </div>
        </div>
      `).join("");
    listEl.querySelectorAll(".ncopy").forEach(b => b.onclick = () => {
      const it = getSaved()[+b.dataset.i];
      if (it) window.copyText(`${it.page} (${it.url})\n${it.time}\n\n${it.text}`);
    });
    listEl.querySelectorAll(".ndel").forEach(b => b.onclick = () => {
      const cur = getSaved(); cur.splice(+b.dataset.i, 1); setSaved(cur); renderSaved();
    });
    const clr = listEl.querySelector("#nclrall");
    if (clr) clr.onclick = () => { if (confirm("Clear all saved notes?")) { setSaved([]); renderSaved(); } };
  };

  box.querySelector("#nb").onclick = () => { box.classList.toggle("open"); renderSaved(); };
  box.querySelector("#ns").onclick = () => {
    const txt = ta.value.trim();
    if (!txt) return;
    const cur = getSaved();
    cur.unshift({
      id: Date.now(),
      url: location.href,
      page: here || location.pathname.split("/").pop() || "index.html",
      title: document.title,
      text: txt,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    });
    setSaved(cur);
    ta.value = "";
    ta.oninput();
    renderSaved();
  };
  box.querySelector("#nc").onclick = () => window.copyText(full());
  box.querySelector("#nd").onclick = () => { const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([full()])); a.download = here + "-notes.txt"; a.click(); };
  box.querySelector("#nx").onclick = () => { ta.value = ""; ta.oninput(); };
  renderSaved();
  addEventListener("keydown", (e) => {
    if (e.target.tagName === "TEXTAREA" || e.target.tagName === "INPUT") { if (e.key === "Escape") box.classList.remove("open"); return; }
    if (e.key === "n") { box.classList.add("open"); ta.focus(); e.preventDefault(); } else if (e.key === "Escape") box.classList.remove("open");
  });
})();
