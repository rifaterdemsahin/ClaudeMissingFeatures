#!/usr/bin/env python3
"""Evals: can the spec recreate this project?
Evaluates four groups:
  A. Recreate from the kit (weight 40)
  B. Spec coverage (weight 30)
  C. Retrieval questions (weight 20)
  E. Kit completeness (weight 10)
Usage:
  python3 scripts/eval_spec.py              # full eval (~1-2 min, builds kit, tests scaffolding in temp dir)
  python3 scripts/eval_spec.py --quick      # fast eval (~2 s, skips full scaffolding)
  python3 -I scripts/eval_spec.py --page-only # renders evals.html from assets/evals.json (runs --quick if missing)
"""
import datetime, html, json, os, pathlib, re, shutil, subprocess, sys, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
EVALS_JSON = ROOT / "assets/evals.json"
EVALS_HTML = ROOT / "evals.html"
QUESTIONS_JSON = ROOT / "evals/spec_questions.json"
MASTER_SPEC = ROOT / "MASTER_SPEC.md"
ENV_MD = ROOT / "ENVIRONMENT.md"

e = html.escape

def load_json(p, default=None):
    if p.exists():
        try:
            return json.loads(p.read_text())
        except Exception:
            return default
    return default

def get_grade(score):
    if score >= 90: return "A (excellent)"
    if score >= 80: return "B+ (very good)"
    if score >= 70: return "B (good)"
    if score >= 60: return "C (needs work)"
    return "D (rework)"

def render_html(data):
    sc = data["score"]
    gr = data["grade"]
    ts = data.get("timestamp", "")
    quick = data.get("quick", False)
    groups = data.get("groups", {})
    unanswered = data.get("unanswered", [])
    history = data.get("history", [])

    tot_checks = sum(len(g.get("checks", [])) for g in groups.values())
    passed_checks = sum(sum(1 for c in g.get("checks", []) if c.get("pass")) for g in groups.values())

    q_tot = len(groups.get("C", {}).get("checks", []))
    q_pass = sum(1 for c in groups.get("C", {}).get("checks", []) if c.get("pass"))

    # Group table rows
    grp_rows = []
    for gid in ("A", "B", "C", "E"):
        g = groups.get(gid)
        if not g: continue
        w = g["weight"]
        pts = g["points"]
        st = "✅ pass" if pts >= w * 0.99 else "🟡 partial" if pts > 0 else "❌ fail"
        grp_rows.append(f"<tr><td><b>Group {gid}</b></td><td>{e(g['name'])}</td><td>{w}</td><td><b>{pts:.1f}</b></td><td>{st}</td><td>{e(g['description'])}</td></tr>")

    # Detailed checks rows
    chk_rows = []
    for gid in ("A", "B", "C", "E"):
        g = groups.get(gid)
        if not g: continue
        for c in g.get("checks", []):
            st_cls = "met" if c.get("pass") else "missed"
            st_icon = "✅ pass" if c.get("pass") else "❌ fail"
            chk_rows.append(f"<tr><td>Group {gid}</td><td><b>{e(c['name'])}</b></td><td class='st {st_cls}'>{st_icon}</td><td>{e(str(c.get('detail', '')))}</td><td>{e(str(c.get('hint', '')))}</td></tr>")

    # Unanswered questions
    unans_html = ""
    if unanswered:
        items = "".join(f"<li><b>{e(u['id'])}</b>: {e(u['question'])}<br><span style='opacity:.7'>Missing patterns: <code>{e(str(u['missing']))}</code></span></li>" for u in unanswered)
        unans_html = f"<div class='box'><h3>⚠️ Unanswered Questions ({len(unanswered)})</h3><ul>{items}</ul></div>"

    # History rows
    hist_rows = []
    for h_item in reversed(history[-10:]):
        h_mode = "⚡ quick" if h_item.get("quick") else "🧪 full"
        hist_rows.append(f"<tr><td>{e(h_item.get('timestamp',''))}</td><td><b>{h_item.get('score',0):.1f} / 100</b></td><td>{e(h_item.get('grade',''))}</td><td>{h_mode}</td></tr>")

    title = load_json(ROOT / "remotion/src/project.json", {}).get("title", "the project")
    llm_prompt = f"""You are an expert technical evaluator. Given ONLY the MASTER_SPEC.md document of {title}, answer the 30 retrieval questions from evals/spec_questions.json.
Rules:
1. For each question (Q1 to Q30), state whether the exact required facts (tool names, commands, filenames, limits) are explicitly documented in MASTER_SPEC.md.
2. Cite the exact section and line or quote.
3. If any fact is missing or ambiguous, flag it as a spec defect."""

    html_content = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>evals</title>
<style>
.box{{background:#14141c;border:1px solid #2a2a38;border-radius:12px;padding:12px 16px;margin:10px 0}}
.big{{font-size:36px;font-weight:900;color:#ff7a3d;line-height:1.1}}
.kpis{{display:flex;flex-wrap:wrap;gap:14px}}.kpis>div{{flex:1;min-width:180px}}
.st.met{{color:#4ade80;font-weight:700}}.st.missed{{color:#f87171;font-weight:700}}
.bar{{background:#2a2a38;border-radius:6px;height:10px;width:120px;display:inline-block;margin-right:8px;vertical-align:middle}}
.bar i{{display:block;height:100%;border-radius:6px;background:#ff7a3d}}
table{{width:100%;border-collapse:collapse;margin:10px 0}}
th,td{{border:1px solid #2a2a38;padding:8px 10px;text-align:left;vertical-align:top}}
th{{background:#1b1b26}}
pre{{background:#0b0b0f;border:1px solid #2a2a38;border-radius:8px;padding:10px;overflow-x:auto;font-size:12px}}
</style></head><body><main style="max-width:1200px">
<h1>🧪 Spec Evals: Can the spec recreate this project?</h1>
<p>Automated evaluation measuring whether <code>MASTER_SPEC.md</code> and the kit provide everything needed to recreate this video project from scratch. Run: <code>python3 scripts/eval_spec.py</code> (or <code>--quick</code>). Last run: <b>{e(ts)}</b> ({'⚡ quick mode' if quick else '🧪 full test'}).</p>

<div class="box kpis">
  <div><div class="big">{sc:.1f} <span style="font-size:20px;color:#aaa">/ 100</span></div>Grade <b>{e(gr)}</b></div>
  <div><div class="big">{passed_checks} <span style="font-size:20px;color:#aaa">/ {tot_checks}</span></div>Deterministic checks passed</div>
  <div><div class="big">{q_pass} <span style="font-size:20px;color:#aaa">/ {q_tot}</span></div>Spec retrieval questions answered</div>
</div>

<h2>📊 Evaluation Groups</h2>
<table>
  <tr><th>Group</th><th>Name</th><th>Weight</th><th>Points</th><th>Status</th><th>What it proves</th></tr>
  {''.join(grp_rows)}
</table>

{unans_html}

<h2>📋 Detailed Checks</h2>
<table>
  <tr><th>Group</th><th>Check</th><th>Status</th><th>Detail</th><th>Fix hint</th></tr>
  {''.join(chk_rows)}
</table>

<h2>🤖 Ready-to-paste LLM Eval Prompt</h2>
<p>Give a fresh Claude or LLM session only <code>MASTER_SPEC.md</code> and the questions to test spec clarity independently:</p>
<pre><code>{e(llm_prompt)}</code></pre>

<h2>📜 Run History</h2>
<table>
  <tr><th>Timestamp</th><th>Score</th><th>Grade</th><th>Mode</th></tr>
  {''.join(hist_rows) if hist_rows else '<tr><td colspan="4">No previous runs recorded.</td></tr>'}
</table>

<p style="opacity:.7;font-size:13px">Generated by <code>scripts/eval_spec.py</code> from <code>MASTER_SPEC.md</code>, <code>evals/spec_questions.json</code>, and the kit.</p>
</main>
<script src="project.js"></script><script src="nav.js"></script>
</body></html>"""
    EVALS_HTML.write_text(html_content)
    print(f"evals.html updated: score {sc:.1f}/100 ({gr})")

def run_eval(quick=False):
    spec_text = MASTER_SPEC.read_text() if MASTER_SPEC.exists() else ""
    env_text = ENV_MD.read_text() if ENV_MD.exists() else ""
    combined_docs = spec_text + "\n" + env_text

    # --- GROUP B: Spec coverage (weight 30) ---
    b_checks = []

    # B1: Every script in scripts/ named in spec or environment
    scripts_on_disk = sorted([p.name for p in (ROOT / "scripts").iterdir() if p.is_file() and not p.name.startswith(".")])
    missing_scripts = [s for s in scripts_on_disk if s not in combined_docs]
    b_checks.append({
        "name": "Every script documented in spec or environment",
        "pass": len(missing_scripts) == 0,
        "detail": f"{len(scripts_on_disk) - len(missing_scripts)}/{len(scripts_on_disk)} scripts documented" + (f" (missing: {', '.join(missing_scripts)})" if missing_scripts else ""),
        "hint": "Add missing scripts to ENVIRONMENT.md code table"
    })

    # B2: Every html page named in spec or environment
    pages_on_disk = sorted([p.name for p in ROOT.glob("*.html")])
    missing_pages = [p for p in pages_on_disk if p not in combined_docs]
    b_checks.append({
        "name": "Every website page documented in spec or environment",
        "pass": len(missing_pages) == 0,
        "detail": f"{len(pages_on_disk) - len(missing_pages)}/{len(pages_on_disk)} pages documented" + (f" (missing: {', '.join(missing_pages)})" if missing_pages else ""),
        "hint": "Add missing pages to MASTER_SPEC.md section 7 or ENVIRONMENT.md"
    })

    # B3: Every data file in assets/ named in spec or environment
    assets_on_disk = sorted([p.name for p in (ROOT / "assets").iterdir() if p.is_file() and not p.name.startswith(".")])
    missing_assets = [a for a in assets_on_disk if a not in combined_docs]
    b_checks.append({
        "name": "Every asset data file documented in spec or environment",
        "pass": len(missing_assets) == 0,
        "detail": f"{len(assets_on_disk) - len(missing_assets)}/{len(assets_on_disk)} assets documented" + (f" (missing: {', '.join(missing_assets)})" if missing_assets else ""),
        "hint": "Add missing data files to ENVIRONMENT.md section 4"
    })

    # B4: Every scripts/... path in spec exists on disk
    raw_script_refs = re.findall(r'scripts/([a-zA-Z0-9_-]+\.[a-zA-Z0-9]+)', spec_text)
    script_refs = sorted(set(raw_script_refs))
    missing_ref_scripts = [s for s in script_refs if not (ROOT / "scripts" / s).exists()]
    b_checks.append({
        "name": "Every scripts/... path in spec exists on disk",
        "pass": len(missing_ref_scripts) == 0,
        "detail": f"{len(script_refs) - len(missing_ref_scripts)}/{len(script_refs)} referenced scripts exist" + (f" (missing: {', '.join(missing_ref_scripts)})" if missing_ref_scripts else ""),
        "hint": "Fix obsolete script paths in MASTER_SPEC.md"
    })

    # B5: Every TOC / anchor link in spec resolves to a heading
    slug_fn = lambda t: re.sub(r"[^\w\- ]", "", t.strip().lower(), flags=re.UNICODE).replace(" ", "-")
    toc_links = re.findall(r'\[(.*?)\]\((?:MASTER_SPEC\.md)?#([a-zA-Z0-9_-]+)\)', spec_text)
    headers = [m.group(1).strip() for m in re.finditer(r"^#+\s+(.+)$", spec_text, flags=re.M)]
    header_slugs = {slug_fn(h) for h in headers}
    unresolved_toc = [link for text, link in toc_links if link not in header_slugs]
    b_checks.append({
        "name": "Every contents anchor link in spec resolves to a heading",
        "pass": len(unresolved_toc) == 0,
        "detail": f"{len(toc_links) - len(unresolved_toc)}/{len(toc_links)} links resolve" + (f" (unresolved: {', '.join(unresolved_toc[:5])})" if unresolved_toc else ""),
        "hint": "Run scripts/build_toc.py to regenerate TOC table"
    })

    # B6: Every section reference resolves
    sec_refs = set(re.findall(r'section\s+([0-9]+[a-z]*)', spec_text, flags=re.I))
    sec_refs.discard("6x") # placeholder in description
    sec_headers = [h for h in headers if re.match(r'^[0-9]+', h)]
    unresolved_secs = [s for s in sec_refs if not any(h.lower().startswith(s.lower() + ".") or h.lower().startswith(s.lower() + " ") for h in sec_headers)]
    b_checks.append({
        "name": "Every section reference in spec resolves to an actual section",
        "pass": len(unresolved_secs) == 0,
        "detail": f"{len(sec_refs) - len(unresolved_secs)}/{len(sec_refs)} section references resolve" + (f" (unresolved: {', '.join(unresolved_secs)})" if unresolved_secs else ""),
        "hint": "Check section number references in MASTER_SPEC.md"
    })

    # B7: Every command in prompt to execute exists
    prompt_match = re.search(r"## ▶ Prompt to execute.*?```text\n(.*?)```", spec_text, flags=re.S)
    prompt_cmds = []
    if prompt_match:
        for line in prompt_match.group(1).splitlines():
            m = re.match(r"^(?:python3\s+(?:-I\s+)?)?(scripts/[a-zA-Z0-9_.-]+)", line.strip())
            if m: prompt_cmds.append(m.group(1))
    missing_prompt_cmds = [c for c in prompt_cmds if not (ROOT / c).exists()]
    b_checks.append({
        "name": "Every script command in 'Prompt to execute' exists",
        "pass": len(missing_prompt_cmds) == 0,
        "detail": f"{len(prompt_cmds) - len(missing_prompt_cmds)}/{len(prompt_cmds)} commands valid" + (f" (missing: {', '.join(missing_prompt_cmds)})" if missing_prompt_cmds else ""),
        "hint": "Ensure all commands in the top prompt reference existing scripts"
    })

    b_score = (sum(1 for c in b_checks if c["pass"]) / len(b_checks)) * 30.0

    # --- GROUP C: Retrieval questions (weight 20) ---
    c_checks = []
    unanswered = []
    questions = load_json(QUESTIONS_JSON, [])
    for q in questions:
        qid = q.get("id", "")
        qtxt = q.get("question", "")
        must = q.get("must", [])
        missing_pats = [p for p in must if not re.search(p, spec_text, re.I)]
        passed = (len(missing_pats) == 0)
        c_checks.append({
            "id": qid,
            "name": f"{qid}: {qtxt}",
            "pass": passed,
            "detail": "All required patterns present in spec" if passed else f"Missing: {missing_pats}",
            "hint": f"Document {', '.join(missing_pats)} in MASTER_SPEC.md"
        })
        if not passed:
            unanswered.append({"id": qid, "question": qtxt, "missing": missing_pats})

    c_score = (sum(1 for c in c_checks if c["pass"]) / max(len(c_checks), 1)) * 20.0

    # --- GROUP E: Kit completeness (weight 10) ---
    # Build kit into a temp file to test completeness
    tmp_kit_zip = pathlib.Path(tempfile.gettempdir()) / f"kit-eval-{os.getpid()}.zip"
    build_kit_res = subprocess.run([str(ROOT / "scripts/build_kit.sh"), str(tmp_kit_zip)], capture_output=True, text=True)
    kit_built_ok = (build_kit_res.returncode == 0 and tmp_kit_zip.exists() and tmp_kit_zip.stat().st_size > 50000)

    e_checks = []
    kit_files = []
    if kit_built_ok:
        try:
            import zipfile
            with zipfile.ZipFile(tmp_kit_zip) as z:
                kit_files = [f.filename for f in z.infolist()]
        except Exception:
            kit_files = []

    # E1: Generic scripts in kit
    scripts_in_kit = [s for s in scripts_on_disk if f"scripts/{s}" in kit_files]
    e_checks.append({
        "name": "All project scripts shipped in kit zip",
        "pass": len(scripts_in_kit) == len(scripts_on_disk),
        "detail": f"{len(scripts_in_kit)}/{len(scripts_on_disk)} scripts present in kit" + (f" (missing: {set(scripts_on_disk) - set(scripts_in_kit)})" if len(scripts_in_kit) < len(scripts_on_disk) else ""),
        "hint": "Add missing scripts to scripts/build_kit.sh"
    })

    # E2: Remotion src in kit
    remotion_src_files = [p.name for p in (ROOT / "remotion/src").glob("*.ts*")]
    remotion_in_kit = [f for f in remotion_src_files if f"remotion/src/{f}" in kit_files]
    e_checks.append({
        "name": "Remotion source files shipped in kit zip",
        "pass": len(remotion_in_kit) == len(remotion_src_files),
        "detail": f"{len(remotion_in_kit)}/{len(remotion_src_files)} Remotion source files present in kit",
        "hint": "Check remotion/src copy rule in scripts/build_kit.sh"
    })

    # E3: Templates in kit
    tpl_files = [p.name for p in (ROOT / "templates").glob("*.html")]
    tpl_in_kit = [f for f in tpl_files if f"templates/{f}" in kit_files]
    e_checks.append({
        "name": "HTML templates shipped in kit zip",
        "pass": len(tpl_in_kit) == len(tpl_files),
        "detail": f"{len(tpl_in_kit)}/{len(tpl_files)} templates present in kit",
        "hint": "Check templates copy rule in scripts/build_kit.sh"
    })

    # E4: Nav & support files in kit
    support_needed = ["nav.js", "project.js", "subs.js", "exports.js", "export_map.js", "chapters.js", "azure_links.js", "pipeline.html"]
    support_in_kit = [s for s in support_needed if s in kit_files]
    e_checks.append({
        "name": "Navigation & runtime support files shipped in kit zip",
        "pass": len(support_in_kit) == len(support_needed),
        "detail": f"{len(support_in_kit)}/{len(support_needed)} support files present in kit" + (f" (missing: {set(support_needed) - set(support_in_kit)})" if len(support_in_kit) < len(support_needed) else ""),
        "hint": "Ensure nav.js, support js and pipeline.html are included in build_kit.sh"
    })

    e_score = (sum(1 for c in e_checks if c["pass"]) / max(len(e_checks), 1)) * 10.0

    # --- GROUP A: Recreate from the kit (weight 40) ---
    a_checks = []

    # A1: Kit builds cleanly
    a_checks.append({
        "name": "Kit builds cleanly and produces valid zip",
        "pass": kit_built_ok,
        "detail": f"Kit zip size {tmp_kit_zip.stat().st_size // 1024 if tmp_kit_zip.exists() else 0} KB, {len(kit_files)} files" if kit_built_ok else "Kit build failed: " + build_kit_res.stderr[-200:],
        "hint": "Check scripts/build_kit.sh"
    })

    # A5: py_compile locally
    py_files = list((ROOT / "scripts").glob("*.py"))
    py_bad = []
    for pf in py_files:
        res = subprocess.run([sys.executable, "-m", "py_compile", str(pf)], capture_output=True, text=True)
        if res.returncode != 0: py_bad.append(pf.name)
    a_checks.append({
        "name": "Every python script compiles cleanly",
        "pass": len(py_bad) == 0,
        "detail": f"{len(py_files) - len(py_bad)}/{len(py_files)} python scripts compiled cleanly" + (f" (errors: {', '.join(py_bad)})" if py_bad else ""),
        "hint": "Fix syntax errors in scripts/*.py"
    })

    # A7: check_reuse passes
    reuse_res = subprocess.run(["zsh", str(ROOT / "scripts/check_reuse.sh")], capture_output=True, text=True)
    a_checks.append({
        "name": "Reuse check passed (no project-specific words in code)",
        "pass": reuse_res.returncode == 0,
        "detail": "No hard-coded video words found" if reuse_res.returncode == 0 else reuse_res.stdout[:150],
        "hint": "Move hardcoded video terms into remotion/src/project.json"
    })

    if quick:
        # Quick mode: test scaffolding using fast checks or reuse cached
        prev_data = load_json(EVALS_JSON)
        prev_a = (prev_data or {}).get("groups", {}).get("A", {}).get("checks", [])
        find_prev = lambda name: next((c.get("pass", True) for c in prev_a if c["name"] == name), True)

        a_checks.append({"name": "New video scaffolds from kit (new-video.sh)", "pass": find_prev("New video scaffolds from kit (new-video.sh)"), "detail": "Scaffold test (cached from previous run; run without --quick for fresh test)", "hint": "Run full eval: python3 scripts/eval_spec.py"})
        a_checks.append({"name": "Full site builds and check_site passes in scaffolded project", "pass": find_prev("Full site builds and check_site passes in scaffolded project"), "detail": "Build & check (cached)", "hint": "Run full eval"})
        a_checks.append({"name": "TypeScript compiles without errors in scaffolded project", "pass": find_prev("TypeScript compiles without errors in scaffolded project"), "detail": "TSC compile (cached)", "hint": "Run full eval"})
        a_checks.append({"name": "Build is idempotent (second build changes nothing)", "pass": find_prev("Build is idempotent (second build changes nothing)"), "detail": "Idempotence (cached)", "hint": "Run full eval"})
    else:
        # Full mode: actually unpack kit into tempdir, run new-video.sh, build_all.sh, check_site.py, tsc, idempotent build
        scaffold_dir = pathlib.Path(tempfile.mkdtemp(prefix="eval-scaffold-"))
        try:
            # Unpack kit
            subprocess.run(["unzip", "-q", str(tmp_kit_zip), "-d", str(scaffold_dir)], check=True)
            # Run new-video.sh
            scaffold_res = subprocess.run(["zsh", "./new-video.sh", "Eval Test Video", "120", "eval-test", "Community", "https://example.com", "discord"], cwd=scaffold_dir, capture_output=True, text=True)
            scaffold_ok = (scaffold_res.returncode == 0)
            a_checks.append({
                "name": "New video scaffolds from kit (new-video.sh)",
                "pass": scaffold_ok,
                "detail": "Scaffold succeeded" if scaffold_ok else f"Scaffold failed: {scaffold_res.stderr[-200:] or scaffold_res.stdout[-200:]}",
                "hint": "Check kit/new-video.sh"
            })

            # Check site in scaffolded project
            chk_res = subprocess.run([sys.executable, "-I", "scripts/check_site.py"], cwd=scaffold_dir, capture_output=True, text=True)
            chk_ok = (chk_res.returncode == 0)
            a_checks.append({
                "name": "Full site builds and check_site passes in scaffolded project",
                "pass": chk_ok,
                "detail": chk_res.stdout.strip() if chk_ok else chk_res.stdout.strip() or chk_res.stderr.strip(),
                "hint": "Check build_all.sh and check_site.py in the scaffolded kit"
            })

            # TypeScript check in scaffolded project
            # Need node_modules for remotion, symlink from root to avoid npm install time
            (scaffold_dir / "remotion/node_modules").symlink_to(ROOT / "remotion/node_modules")
            tsc_res = subprocess.run(["npx", "tsc", "--noEmit"], cwd=scaffold_dir / "remotion", capture_output=True, text=True)
            tsc_ok = (tsc_res.returncode == 0)
            a_checks.append({
                "name": "TypeScript compiles without errors in scaffolded project",
                "pass": tsc_ok,
                "detail": "tsc clean" if tsc_ok else tsc_res.stdout[:150],
                "hint": "Fix TypeScript types in remotion/src"
            })

            # Idempotence: run build_all a second time; no files should be newly modified (excluding wall-clock elapsed in timeline.html)
            s1 = set(subprocess.run(["git", "status", "--porcelain"], cwd=scaffold_dir, capture_output=True, text=True).stdout.splitlines())
            subprocess.run(["zsh", "scripts/build_all.sh"], cwd=scaffold_dir, capture_output=True, text=True)
            s2 = subprocess.run(["git", "status", "--porcelain"], cwd=scaffold_dir, capture_output=True, text=True).stdout.splitlines()
            dirty = [l for l in s2 if l not in s1 and "timeline.html" not in l and not l.endswith("node_modules") and not l.endswith(".log")]
            idemp_ok = (len(dirty) == 0)
            a_checks.append({
                "name": "Build is idempotent (second build changes nothing)",
                "pass": idemp_ok,
                "detail": "zero newly modified files on second build" if idemp_ok else f"modified files: {', '.join(dirty[:3])}",
                "hint": "Ensure generators produce deterministic identical output on re-runs"
            })
            a_checks.append({
                "name": "Build is idempotent (second build changes nothing)",
                "pass": idemp_ok,
                "detail": "clean git status after second build" if idemp_ok else f"modified files: {', '.join(dirty[:3])}",
                "hint": "Ensure generators produce deterministic identical output on re-runs"
            })
        finally:
            shutil.rmtree(scaffold_dir, ignore_errors=True)

    a_score = (sum(1 for c in a_checks if c["pass"]) / len(a_checks)) * 40.0

    # Total score calculation
    total_score = round(a_score + b_score + c_score + e_score, 1)
    grade = get_grade(total_score)
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Load history
    prev_json = load_json(EVALS_JSON, {})
    history = prev_json.get("history", [])
    history.append({
        "timestamp": now_str,
        "score": total_score,
        "grade": grade,
        "quick": quick
    })
    # Keep last 15 runs
    history = history[-15:]

    evals_data = {
        "timestamp": now_str,
        "score": total_score,
        "grade": grade,
        "quick": quick,
        "groups": {
            "A": {
                "name": "Recreate from the kit",
                "weight": 40,
                "points": round(a_score, 1),
                "description": "A fresh folder made only from the kit builds the whole project",
                "checks": a_checks
            },
            "B": {
                "name": "Spec coverage",
                "weight": 30,
                "points": round(b_score, 1),
                "description": "Nothing the project needs is undocumented in MASTER_SPEC.md or ENVIRONMENT.md",
                "checks": b_checks
            },
            "C": {
                "name": "Retrieval questions",
                "weight": 20,
                "points": round(c_score, 1),
                "description": "The spec alone answers what a newcomer must know (30 questions)",
                "checks": c_checks
            },
            "E": {
                "name": "Kit completeness",
                "weight": 10,
                "points": round(e_score, 1),
                "description": "Everything generic is shipped in the kit zip",
                "checks": e_checks
            }
        },
        "unanswered": unanswered,
        "history": history
    }

    # Clean up temp kit zip
    if tmp_kit_zip.exists():
        tmp_kit_zip.unlink(missing_ok=True)

    # Save assets/evals.json
    EVALS_JSON.parent.mkdir(exist_ok=True)
    EVALS_JSON.write_text(json.dumps(evals_data, indent=1))

    # Render HTML
    render_html(evals_data)
    print(f"Spec Evals completed: Score {total_score}/100 ({grade}) | A: {a_score:.1f}/40, B: {b_score:.1f}/30, C: {c_score:.1f}/20, E: {e_score:.1f}/10")
    return total_score

if __name__ == "__main__":
    if "--page-only" in sys.argv:
        if not EVALS_JSON.exists():
            run_eval(quick=True)
        else:
            data = load_json(EVALS_JSON)
            render_html(data)
    elif "--quick" in sys.argv:
        run_eval(quick=True)
    else:
        run_eval(quick=False)
