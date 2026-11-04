# -*- coding: utf-8 -*-
"""
validate_e2.py — Validacion y correccion del componente longitudinal E2 (commons-lang)
Reproduce, directamente desde Git:
  1) D3_ADJUDICACION_LINAJE_30.csv   (--follow 50% vs -M90% vs sin follow, con veredicto por archivo)
  2) D3_ARTIFACT_IDENTITY_CORREGIDO.csv (numeracion canonica anclada al path; chequeo --follow independiente)
  3) D3_FOLD_TRAIN_CORREGIDO.csv / D3_FOLD_TEST_CORREGIDO.csv (linaje -M90%, born-check por tag, ISO, snapshot_sha)
  4) D3_EXCLUSIONES.csv  (artefactos no nacidos en el corte)

Uso:
  py validate_e2.py <ruta_repo_commons-lang> <ruta_seleccion_30.txt> <carpeta_salida>
Ejemplo (Git Bash):
  py validate_e2.py repos/commons-lang D3_SELECCION_30.txt .

Parametros de corte (fijos, verificados contra los tags anotados del repo oficial):
  3.18.0 -> 2025-07-06 -> 5b59487808d0b86a94ad7a1ebd4c200e09b7be09
  3.19.0 -> 2025-09-19 -> 3d1eb7718a79d18cc2ab57e7ab3b894426ec7c2f
  3.20.0 -> 2025-11-12 -> 598dfc163b8b410fb3bb8794521206ec8dcec82a  (snapshot CIMPS / decision_time)
"""
import subprocess, csv, os, sys
from datetime import date

REPO = sys.argv[1] if len(sys.argv)>1 else "repos/commons-lang"
SEL  = sys.argv[2] if len(sys.argv)>2 else "D3_SELECCION_30.txt"
OUT  = sys.argv[3] if len(sys.argv)>3 else "."
DT_SHA = "598dfc163b8b410fb3bb8794521206ec8dcec82a"   # 3.20.0 = decision_time
SNAP = {
 "3.18.0": ("2025-07-06", "5b59487808d0b86a94ad7a1ebd4c200e09b7be09"),
 "3.19.0": ("2025-09-19", "3d1eb7718a79d18cc2ab57e7ab3b894426ec7c2f"),
 "3.20.0": ("2025-11-12", "598dfc163b8b410fb3bb8794521206ec8dcec82a"),
}
def git(*a): return subprocess.run(["git","-C",REPO,*a],capture_output=True,text=True).stdout
def D(s): y,m,d=map(int,s.split("-")); return date(y,m,d)

paths=[l.strip() for l in open(SEL,encoding="utf-8") if l.strip()]
canon=[(f"F{str(i+1).zfill(3)}",p) for i,p in enumerate(paths)]

def ncommits(path,follow,m90,ref):
    a=["log"]
    if follow: a.append("--follow")
    if m90: a.append("-M90%")
    a+=["--oneline",ref,"--",path]
    return len(git(*a).splitlines())

# 1) ADJUDICACION
adj=[]
for id_,p in canon:
    f50=ncommits(p,True,False,DT_SHA); f90=ncommits(p,True,True,DT_SHA); nf=ncommits(p,False,False,DT_SHA)
    dif=f50-f90
    r100=len([l for l in git("log","--follow","-M90%","--name-status","--diff-filter=R",DT_SHA,"--",p).splitlines() if l.startswith("R100")])
    org=git("log","--format=%h|%ad","--date=short",DT_SHA,"--",p).splitlines()
    org=org[-1] if org else ""
    if dif==0: ver="sin cambio de linaje"
    elif f90==nf: ver=f"nacido-en-lugar; --follow(50%) sobre-atribuyo {dif}; corregido={f90}"
    elif r100>0: ver=f"renames R100 reales ({r100}); corregido={f90} (conserva migracion legitima)"
    else: ver=f"REVISAR (dif={dif}, sin R100)"
    adj.append([id_,p,f50,f90,nf,dif,("SI" if dif>0 else "no"),r100,org,ver])
with open(os.path.join(OUT,"D3_ADJUDICACION_LINAJE_30.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["artifact_id","path","commits_follow50","commits_follow90_corr","commits_nofollow","dif_50_90","afectado_linaje","renames_R100","origin_commit_date","veredicto"]); w.writerows(adj)

# 2) IDENTIDAD CANONICA
idrows=[]
for id_,p in canon:
    raw=git("log","--follow","-M90%","--name-status","--diff-filter=AR","--format=@@%h|%ad","--date=short",DT_SHA,"--",p)
    blk=[]; cur=None
    for ln in raw.splitlines():
        if ln.startswith("@@"): cur=ln[2:].split("|")
        elif ln and cur:
            pr=ln.split("\t"); blk.append((cur[0],cur[1],pr))
    for commit,dt,pr in reversed(blk):
        if pr[0]=="A": idrows.append([id_,commit,dt,pr[1],"added","","","nacimiento (diff-filter=A, --follow -M90%)","no"])
        elif pr[0].startswith("R"): idrows.append([id_,commit,dt,pr[2],"renamed",pr[1],pr[2],f"{pr[0]} en --follow -M90% --name-status","no"])
with open(os.path.join(OUT,"D3_ARTIFACT_IDENTITY_CORREGIDO.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["artifact_id","commit","timestamp","path","change_type","rename_from","rename_to","evidence","ambiguity"]); w.writerows(idrows)

# 3) + 4) FOLDS + EXCLUSIONES
def exists_at(tag,path):
    return subprocess.run(["git","-C",REPO,"cat-file","-e",f"rel/commons-lang-{tag}:{path}"],capture_output=True).returncode==0
def feats(cut_sha,cut_date,p):
    pc=ncommits(p,True,True,cut_sha)
    contrib=len(set(git("log","--follow","-M90%","--format=%an",cut_sha,"--",p).splitlines()))
    ch=0
    for ln in git("log","--follow","-M90%","--numstat","--format=",cut_sha,"--",p).splitlines():
        q=ln.split("\t")
        if len(q)>=2 and q[0].isdigit() and q[1].isdigit(): ch+=int(q[0])+int(q[1])
    last=git("log","-1","--follow","-M90%","--format=%cs",cut_sha,"--",p).strip()
    dsc=(D(cut_date)-D(last)).days if last else None
    return pc,ch,contrib,last,dsc
def lab(cut_sha,next_sha,p):
    n=len(git("log","--oneline",f"{cut_sha}..{next_sha}","--",p).splitlines())
    fr=git("log","--reverse","--format=%cs",f"{cut_sha}..{next_sha}","--",p).splitlines()
    return (1 if n>0 else 0),(fr[0] if fr else "")
def build(cut_tag,next_tag,fname):
    cd,cs=SNAP[cut_tag]; nd,ns=SNAP[next_tag]; rows=[]; ex=[]
    for id_,p in canon:
        if not exists_at(cut_tag,p):
            ex.append([id_,p,f"{fname.split('_')[2]} {cut_tag}",cd,cs,"NO_NACIDO",f"no existe en rel/commons-lang-{cut_tag}; excluido (observacion sin pasado)"]); continue
        pc,ch,contrib,last,dsc=feats(cs,cd,p); lc,ml=lab(cs,ns,p)
        inv="OK"
        if last and D(last)>D(cd): inv="FALLA"
        if ml and D(ml)<=D(cd): inv="FALLA"
        rows.append([id_,p,cd,cs,pc,ch,contrib,dsc,lc,last,ml,inv])
    with open(os.path.join(OUT,fname),"w",newline="",encoding="utf-8") as f:
        w=csv.writer(f); w.writerow(["artifact_id","path","cut_date","snapshot_sha","prior_commits","churn","distinct_contributors","days_since_last_change","label_changed","max_feature_date","min_label_date","invariante"]); w.writerows(rows)
    return rows,ex
tr,ex1=build("3.18.0","3.19.0","D3_FOLD_TRAIN_CORREGIDO.csv")
te,ex2=build("3.19.0","3.20.0","D3_FOLD_TEST_CORREGIDO.csv")
with open(os.path.join(OUT,"D3_EXCLUSIONES.csv"),"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["artifact_id","path","fold_cut","cut_date","snapshot_sha","motivo","detalle"])
    for r in ex1+ex2: w.writerow(r)

print(f"Afectados linaje: {sum(1 for r in adj if r[5]>0)}/30")
print(f"TRAIN: {len(tr)} filas, FALLA={[r[0] for r in tr if r[11]=='FALLA']}, excluidos={[r[0] for r in ex1]}")
print(f"TEST : {len(te)} filas, FALLA={[r[0] for r in te if r[11]=='FALLA']}, excluidos={[r[0] for r in ex2]}")
print("Listo. CSVs en:", os.path.abspath(OUT))
