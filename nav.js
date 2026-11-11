// Shared menu + notes panel. Edit LINKS once; every page loads this file.
(function () {
  const CTA = "Join our Skool community: Delivery Pilot https://www.skool.com/delivery-pilot-8938";
  const LINKS = [
    ["architecture.html", "🏛️ Architecture"],
    ["index.html", "🏠 Project"],
    ["preprod.html", "📝 Pre-prod"],
    ["prod.html", "🎬 Prod"],
    ["postprod.html", "✅ Post-prod"],
    ["player.html", "▶️ Player & output"],
    ["run.html", "🧪 Run & links"],
    ["http://localhost:3000/LongForm", "🎞️ Remotion Studio", true],
    ["metadata.html", "📺 YouTube metadata"],
    ["spec.html", "📘 Master spec v3"],
    ["readme.html", "📄 README (Shorts flow)"],
    ["https://www.skool.com/delivery-pilot-8938", "🚀 Join Delivery Pilot", true],
  ];
  const here = location.pathname.split("/").pop() || "index.html";
  const nav = document.createElement("nav");
  nav.innerHTML = '<b>🎬 Claude Missing Features</b>' + LINKS.map(([h, t, ext]) =>
    `<a href="${h}" ${ext ? 'target="_blank" rel="noopener"' : ""} class="${h === here ? "on" : ""}">${t}</a>`).join("");
  const css = document.createElement("style");
  css.textContent = `body{margin:0;background:#0b0b0f;color:#eee;font:16px/1.6 system-ui,sans-serif}
  nav{position:sticky;top:0;z-index:9;display:flex;flex-wrap:wrap;gap:6px 16px;align-items:center;padding:10px 20px;background:#14141c;border-bottom:1px solid #2a2a38}
  nav b{margin-right:12px}nav a{color:#bbb;text-decoration:none;padding:4px 8px;border-radius:8px}nav a:hover,nav a.on{background:#ff7a3d;color:#000}
  main{max-width:960px;margin:0 auto;padding:24px 20px 120px}h1,h2,h3{line-height:1.25}a{color:#ff9a66}
  code,pre{background:#1a1a24;border-radius:6px}code{padding:1px 5px}pre{padding:12px;overflow:auto}
  table{border-collapse:collapse;width:100%;margin:12px 0}td,th{border:1px solid #2a2a38;padding:6px 10px;text-align:left;vertical-align:top}
  button,.btn{background:#ff7a3d;color:#000;border:0;border-radius:8px;padding:8px 14px;font-weight:700;cursor:pointer;text-decoration:none;display:inline-block}
  #notes{position:fixed;right:16px;bottom:16px;z-index:10}#notes .panel{display:none;width:min(360px,90vw);background:#14141c;border:1px solid #2a2a38;border-radius:12px;padding:10px}
  #notes.open .panel{display:block}#notes textarea{width:100%;height:160px;background:#0b0b0f;color:#eee;border:1px solid #2a2a38;border-radius:8px;box-sizing:border-box}
  .copy{margin-left:8px;font-size:12px;padding:3px 8px}@media(max-width:600px){nav{padding:8px 12px}}`;
  document.head.appendChild(css);
  document.body.prepend(nav);

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
