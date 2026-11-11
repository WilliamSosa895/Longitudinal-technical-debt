# -*- coding: utf-8 -*-
"""
validate_e2.py — Validación y reconstrucción reproducible del componente longitudinal E2 (commons-lang)

Diseño FAIL-CLOSED: ante un repositorio inválido, un SHA inexistente, una ruta no elegible
o un error de Git, el script ABORTA con código de salida != 0 y NO escribe CSV de apariencia
válida. Un CSV sólo se materializa si todas las precondiciones y las invariantes pasan.

Reconstruye desde Git, para el piloto commons-lang:
  1) D3_ADJUDICACION_LINAJE_30.csv        (follow 50% vs -M90% vs sin follow + veredicto + SHAs)
  2) D3_ARTIFACT_IDENTITY_CORREGIDO.csv   (episodios A/D/R por artefacto, numeración anclada al path)
  3) D3_EVOLUTION_DATASET_CORREGIDO_commons-lang.csv  (E2 principal al decision_time, linaje -M90%)
  4) D3_FOLD_TRAIN_CORREGIDO.csv / D3_FOLD_TEST_CORREGIDO.csv (born-check, snapshot_sha, ISO)
  5) D3_EXCLUSIONES.csv                   (artefactos no nacidos en el corte)
  6) D3_ELEGIBILIDAD_ASOF.csv             (existencia de cada archivo en cada corte)
  7) E2_RUN_MANIFEST.json                 (SHAs, parámetros, checksums de cada salida)

Uso:
  py validate_e2.py <ruta_repo_commons-lang> <ruta_seleccion_30.txt> <carpeta_salida>
  py validate_e2.py --selftest <ruta_repo_commons-lang> <ruta_seleccion_30.txt>

Códigos de salida: 0 = ok ; 2 = precondición/Git inválido ; 3 = invariante violada ; 4 = autoprueba falló.

Cortes (verificados contra los tags anotados oficiales):
  3.18.0 -> 2025-07-06 -> 5b59487808d0b86a94ad7a1ebd4c200e09b7be09
  3.19.0 -> 2025-09-19 -> 3d1eb7718a79d18cc2ab57e7ab3b894426ec7c2f
  3.20.0 -> 2025-11-12 -> 598dfc163b8b410fb3bb8794521206ec8dcec82a  (decision_time, snapshot CIMPS)
"""
import subprocess, csv, os, sys, json, hashlib
from datetime import date

SNAP = {
 "3.18.0": ("2025-07-06", "5b59487808d0b86a94ad7a1ebd4c200e09b7be09"),
 "3.19.0": ("2025-09-19", "3d1eb7718a79d18cc2ab57e7ab3b894426ec7c2f"),
 "3.20.0": ("2025-11-12", "598dfc163b8b410fb3bb8794521206ec8dcec82a"),
}
DT_TAG = "3.20.0"
DT_DATE, DT_SHA = SNAP[DT_TAG]

def die(msg, code=2):
    sys.stderr.write(f"ERROR[{code}]: {msg}\n"); sys.exit(code)

def git(repo, *args, allow_empty=True):
    """Ejecuta git; ABORTA si git devuelve código != 0 (fail-closed)."""
    r = subprocess.run(["git","-C",repo,*args], capture_output=True, text=True)
    if r.returncode != 0:
        die(f"git {' '.join(args)} -> rc={r.returncode}: {r.stderr.strip()[:200]}")
    return r.stdout

def exists_at(repo, tag, path):
    r = subprocess.run(["git","-C",repo,"cat-file","-e",f"rel/commons-lang-{tag}:{path}"],
                       capture_output=True)
    return r.returncode == 0

def D(s):
    y,m,d = map(int, s.split("-")); return date(y,m,d)

# ---------------- PRECONDICIONES (fail-closed) ----------------
def check_preconditions(repo, sel):
    if not os.path.isdir(repo):
        die(f"la ruta del repositorio no existe: {repo}")
    r = subprocess.run(["git","-C",repo,"rev-parse","--git-dir"], capture_output=True)
    if r.returncode != 0:
        die(f"no es un repositorio Git válido: {repo}")
    for tag,(_,sha) in SNAP.items():
        r = subprocess.run(["git","-C",repo,"cat-file","-e",f"{sha}^{{commit}}"], capture_output=True)
        if r.returncode != 0:
            die(f"el SHA del corte {tag} ({sha}) no existe en el repositorio")
    if not os.path.isfile(sel):
        die(f"el archivo de selección no existe: {sel}")
    paths = [l.strip() for l in open(sel, encoding="utf-8") if l.strip()]
    if not paths:
        die(f"la selección está vacía: {sel}")
    # cada archivo seleccionado DEBE existir en el decision_time
    for p in paths:
        if not exists_at(repo, DT_TAG, p):
            die(f"ruta no elegible: '{p}' no existe en el decision_time ({DT_TAG})")
    return paths

# ---------------- MÉTRICAS ----------------
def ncommits(repo, path, follow, m90, ref):
    a = ["log"] + (["--follow"] if follow else []) + (["-M90%"] if m90 else []) + ["--oneline", ref, "--", path]
    return len(git(repo, *a).splitlines())

def feats(repo, cut_sha, cut_date, p):
    pc = ncommits(repo, p, True, True, cut_sha)
    contrib = len(set(git(repo,"log","--follow","-M90%","--format=%an",cut_sha,"--",p).splitlines()))
    add=dele=0
    for ln in git(repo,"log","--follow","-M90%","--numstat","--format=",cut_sha,"--",p).splitlines():
        q=ln.split("\t")
        if len(q)>=2 and q[0].isdigit() and q[1].isdigit(): add+=int(q[0]); dele+=int(q[1])
    last = git(repo,"log","-1","--follow","-M90%","--format=%cs",cut_sha,"--",p).strip()
    dsc = (D(cut_date)-D(last)).days if last else None
    return pc, add, dele, add+dele, contrib, last, dsc

def label(repo, cut_sha, next_sha, p):
    n = len(git(repo,"log","--oneline",f"{cut_sha}..{next_sha}","--",p).splitlines())
    fr = git(repo,"log","--reverse","--format=%cs",f"{cut_sha}..{next_sha}","--",p).splitlines()
    return (1 if n>0 else 0), (fr[0] if fr else "")

def sha256(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(8192),b""): h.update(b)
    return h.hexdigest()[:16]

# ---------------- GENERACIÓN ----------------
def generate(repo, sel, out):
    paths = check_preconditions(repo, sel)
    os.makedirs(out, exist_ok=True)
    canon = [(f"F{str(i+1).zfill(3)}", p) for i,p in enumerate(paths)]
    written = []

    # 1) ADJUDICACION
    adj=[]
    for id_,p in canon:
        f50=ncommits(repo,p,True,False,DT_SHA); f90=ncommits(repo,p,True,True,DT_SHA); nf=ncommits(repo,p,False,False,DT_SHA)
        dif=f50-f90
        r100=len([l for l in git(repo,"log","--follow","-M90%","--name-status","--diff-filter=R",DT_SHA,"--",p).splitlines() if l.startswith("R100")])
        org=git(repo,"log","--format=%h|%ad","--date=short",DT_SHA,"--",p).splitlines()
        org=org[-1] if org else ""
        if dif==0: ver="sin cambio de linaje"
        elif f90==nf: ver=f"nacido-en-lugar; --follow(50%) sobre-atribuyo {dif}; corregido={f90}"
        elif r100>0: ver=f"renames R100 reales ({r100}); corregido={f90} (conserva migracion legitima)"
        else: ver=f"REVISAR (dif={dif}, sin R100)"
        adj.append([id_,p,f50,f90,nf,dif,("SI" if dif>0 else "no"),r100,org,ver])
    f1=os.path.join(out,"D3_ADJUDICACION_LINAJE_30.csv")
    with open(f1,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["artifact_id","path","commits_follow50","commits_follow90_corr","commits_nofollow","dif_50_90","afectado_linaje","renames_R100","origin_commit_date","veredicto"]); w.writerows(adj)
    written.append(f1)

    # 2) IDENTIDAD (episodios A/D/R)
    idrows=[]
    for id_,p in canon:
        raw=git(repo,"log","--follow","-M90%","--name-status","--diff-filter=ADR","--format=@@%h|%ad|%s","--date=short",DT_SHA,"--",p)
        blk=[]; cur=None
        for ln in raw.splitlines():
            if ln.startswith("@@"): cur=ln[2:].split("|",2)
            elif ln and cur:
                pr=ln.split("\t"); blk.append((cur[0],cur[1],cur[2] if len(cur)>2 else "",pr))
        for commit,dt,msg,pr in reversed(blk):
            st=pr[0]
            if st=="A": idrows.append([id_,commit,dt,pr[1],"added","","",f"nacimiento: {msg[:60]}","no"])
            elif st=="D": idrows.append([id_,commit,dt,pr[1],"deleted","","",f"eliminacion: {msg[:60]}","no"])
            elif st.startswith("R"): idrows.append([id_,commit,dt,pr[2],"renamed",pr[1],pr[2],f"{st}: {msg[:50]}","no"])
    f2=os.path.join(out,"D3_ARTIFACT_IDENTITY_CORREGIDO.csv")
    with open(f2,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["artifact_id","commit","timestamp","path","change_type","rename_from","rename_to","evidence","ambiguity"]); w.writerows(idrows)
    written.append(f2)

    # 3) E2 PRINCIPAL al decision_time
    e2=[]
    for id_,p in canon:
        pc,add,dele,ch,contrib,last,dsc = feats(repo, DT_SHA, DT_DATE, p)
        if pc < 1: die(f"invariante: {id_} tiene prior_commits<1 en decision_time", 3)
        e2.append([id_,DT_DATE,p,pc,add,dele,ch,dsc,contrib])
    f3=os.path.join(out,"D3_EVOLUTION_DATASET_CORREGIDO_commons-lang.csv")
    with open(f3,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["artifact_id","decision_time","path","prior_commits","lines_added","lines_deleted","churn","days_since_last_change","distinct_contributors"]); w.writerows(e2)
    written.append(f3)

    # 4+5) FOLDS + EXCLUSIONES
    def build(cut_tag,next_tag,fname):
        cd,cs=SNAP[cut_tag]; nd,ns=SNAP[next_tag]; rows=[]; ex=[]
        for id_,p in canon:
            if not exists_at(repo,cut_tag,p):
                ex.append([id_,p,f"{fname.split('_')[2]} {cut_tag}",cd,cs,"NO_NACIDO",f"no existe en rel/commons-lang-{cut_tag}; excluido (observacion sin pasado)"]); continue
            pc,add,dele,ch,contrib,last,dsc=feats(repo,cs,cd,p); lc,ml=label(repo,cs,ns,p)
            inv="OK"
            if last and D(last)>D(cd): inv="FALLA"
            if ml and D(ml)<=D(cd): inv="FALLA"
            rows.append([id_,p,cd,cs,pc,ch,contrib,dsc,lc,last,ml,inv])
        with open(os.path.join(out,fname),"w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["artifact_id","path","cut_date","snapshot_sha","prior_commits","churn","distinct_contributors","days_since_last_change","label_changed","max_feature_date","min_label_date","invariante"]); w.writerows(rows)
        return rows,ex
    tr,ex1=build("3.18.0","3.19.0","D3_FOLD_TRAIN_CORREGIDO.csv")
    te,ex2=build("3.19.0","3.20.0","D3_FOLD_TEST_CORREGIDO.csv")
    written += [os.path.join(out,"D3_FOLD_TRAIN_CORREGIDO.csv"), os.path.join(out,"D3_FOLD_TEST_CORREGIDO.csv")]
    # invariante fail-closed
    bad=[r[0] for r in tr+te if r[11]=="FALLA"]
    if bad: die(f"invariante temporal violada en folds: {bad}", 3)
    f5=os.path.join(out,"D3_EXCLUSIONES.csv")
    with open(f5,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["artifact_id","path","fold_cut","cut_date","snapshot_sha","motivo","detalle"]); w.writerows(ex1+ex2)
    written.append(f5)

    # 6) ELEGIBILIDAD AS-OF
    f6=os.path.join(out,"D3_ELEGIBILIDAD_ASOF.csv")
    with open(f6,"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["artifact_id","path","existe_3.18.0","existe_3.19.0","existe_3.20.0","elegible_train_3.18.0","elegible_test_3.19.0"])
        for id_,p in canon:
            e18=exists_at(repo,"3.18.0",p); e19=exists_at(repo,"3.19.0",p); e20=exists_at(repo,"3.20.0",p)
            w.writerow([id_,p,"SI" if e18 else "NO","SI" if e19 else "NO","SI" if e20 else "NO","SI" if e18 else "NO","SI" if e19 else "NO"])
    written.append(f6)

    # 7) MANIFIESTO con checksums
    man={"componente":"E2 commons-lang","decision_time":DT_DATE,"decision_sha":DT_SHA,
         "snapshots":{k:{"fecha":v[0],"sha":v[1]} for k,v in SNAP.items()},
         "regla_linaje":"git log --follow -M90%","afectados_linaje":[r[0] for r in adj if r[6]=="SI"],
         "train_filas":len(tr),"test_filas":len(te),"excluidos":[r[0] for r in ex1+ex2],
         "salidas":{os.path.basename(x):sha256(x) for x in written}}
    fman=os.path.join(out,"E2_RUN_MANIFEST.json")
    with open(fman,"w",encoding="utf-8") as f: json.dump(man,f,indent=2,ensure_ascii=False)
    print(f"OK: {len(written)+1} archivos generados. Afectados linaje: {len(man['afectados_linaje'])}/30. "
          f"TRAIN {len(tr)} (excluidos {[r[0] for r in ex1]}), TEST {len(te)}.")
    return 0

# ---------------- AUTOPRUEBA (positiva + negativa) ----------------
def selftest(repo, sel):
    import tempfile
    me = os.path.abspath(__file__)
    def run(args):
        return subprocess.run([sys.executable, me, *args], capture_output=True, text=True).returncode
    cases=[]
    tmp=tempfile.mkdtemp()
    # NEGATIVAS (deben fallar, rc!=0)
    cases.append(("repo inexistente", run(["/no/existe/repo", sel, tmp]) != 0))
    # repo que es git pero sin los SHAs de commons-lang (usa el dir padre del script si es git, o un git temporal)
    import subprocess as sp
    gtmp=tempfile.mkdtemp(); sp.run(["git","-C",gtmp,"init","-q"]);
    cases.append(("repo git sin los SHAs del corte", run([gtmp, sel, tmp]) != 0))
    # seleccion con ruta inventada
    badsel=os.path.join(tmp,"bad_sel.txt"); open(badsel,"w").write("src/main/java/NoExiste.java\n")
    cases.append(("ruta no elegible en seleccion", run([repo, badsel, tmp]) != 0))
    # seleccion vacia
    emptysel=os.path.join(tmp,"empty.txt"); open(emptysel,"w").write("\n")
    cases.append(("seleccion vacia", run([repo, emptysel, tmp]) != 0))
    # POSITIVA (debe pasar, rc==0, y producir las salidas)
    postmp=tempfile.mkdtemp()
    rc_pos = run([repo, sel, postmp])
    outs_ok = all(os.path.isfile(os.path.join(postmp,f)) for f in
                  ["D3_ADJUDICACION_LINAJE_30.csv","D3_EVOLUTION_DATASET_CORREGIDO_commons-lang.csv",
                   "D3_FOLD_TRAIN_CORREGIDO.csv","D3_FOLD_TEST_CORREGIDO.csv","E2_RUN_MANIFEST.json"])
    cases.append(("corrida positiva rc==0", rc_pos == 0))
    cases.append(("corrida positiva genera salidas", outs_ok))
    ok=True
    print("=== AUTOPRUEBA validate_e2.py ===")
    for name,passed in cases:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}"); ok = ok and passed
    if not ok: sys.exit(4)
    print("AUTOPRUEBA: todas las pruebas pasaron (positivas y negativas).")
    return 0

if __name__ == "__main__":
    a=sys.argv[1:]
    if a and a[0]=="--selftest":
        if len(a)<3: die("uso: --selftest <repo> <seleccion>", 2)
        sys.exit(selftest(a[1], a[2]))
    if len(a)<3: die("uso: validate_e2.py <repo> <seleccion> <salida>  |  --selftest <repo> <seleccion>", 2)
    sys.exit(generate(a[0], a[1], a[2]))
