"""Trunk sticker v2 for WHITE VINYL: navy ring band, white (unprinted) letters except orange E / teal V, white emblem with navy outline.
usage: make_sticker2.py [diameter_mm=50] [outline_units=6]"""
import sys, os, re, math, subprocess
from svgpathtools import parse_path, Line, CubicBezier, Arc
D=float(sys.argv[1]) if len(sys.argv)>1 else 50.0
OL=float(sys.argv[2]) if len(sys.argv)>2 else 6.0       # emblem outline width in 958-unit canvas (6 units = 0.31 mm at 50 mm)
L=r"C:\Thrive Website\assets\logo-concepts"; INK=r"C:\Program Files\Inkscape\bin\inkscape.exe"
OUT=os.path.dirname(os.path.abspath(__file__))
CX=CY=479.0; RO,RI=479.0,321.4                          # ring band: outer edge of the outer ring .. inner edge of the inner ring
CM={"orange":(0,.832,1,0),"teal":(.752,0,.1727,0),"blue":(1,.8356,.1151,.0342),"white":(0,0,0,0)}
RGB={"orange":"#f2501e","teal":"#1cb9dc","blue":"#213f95","white":"#ffffff"}
s=open(os.path.join(L,"thrieve-words-inner-circle-black.svg"),encoding="utf-8").read()
P={k:parse_path(re.search(r'<g id="%s"><path[^>]*?\sd="([^"]+)"'%k,s).group(1)) for k in ("text-top","text-left","text-right")}
# ---- emblem: union of the four filled parts (your gradient file) -> one outline
src=open(os.path.join(L,"thrieve-emblem-parts-filled.svg"),encoding="utf-8").read()
vb=re.search(r'viewBox="([^"]+)"',src).group(1)
ds=[re.search(r'<g\s+id="%s".*?<path[^>]*?\sd="([^"]+)"'%k,src,re.S).group(1) for k in ("t-top","t-bottom","left-edge-curve","arrow")]
tmp=os.path.join(OUT,"_u.svg"); tmo=os.path.join(OUT,"_u_o.svg")
open(tmp,"w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">'+"".join(f'<path d="{d}" fill="#000"/>' for d in ds)+'</svg>')
subprocess.run([INK,tmp,"--actions=select-all:all;path-union;export-filename:"+tmo+";export-plain-svg;export-do"],check=True,capture_output=True)
t=re.sub(r'<defs.*?</defs>','',open(tmo,encoding="utf-8").read(),flags=re.S); pp=re.findall(r'<path[^>]*?\sd="([^"]+)"',t); assert len(pp)==1,len(pp)
emblem=parse_path(pp[0]).continuous_subpaths(); os.remove(tmp); os.remove(tmo)
emblem_union=emblem
if os.environ.get("EMB")=="lines":      # hollow line-art emblem (the black master) instead of the filled one
    es=open(os.path.join(L,"thrieve-emblem-only-black.svg"),encoding="utf-8").read(); emblem=parse_path(re.search(r'<path[^>]*?\sd="([^"]+)"',es).group(1)).continuous_subpaths()
# ---- split THRIEVE into letters
subs=P["text-top"].continuous_subpaths()
bb=lambda p:p.bbox()
def inside(a,b): A,B=bb(a),bb(b); return B[0]<=A[0] and A[1]<=B[1] and B[2]<=A[2] and A[3]<=B[3]
outers=[p for p in subs if not any(q is not p and inside(p,q) for q in subs)]; holes=[p for p in subs if p not in outers]
ang=lambda p:(lambda b:math.atan2(-((b[2]+b[3])/2-CY),(b[0]+b[1])/2-CX))(bb(p)); outers.sort(key=ang,reverse=True); assert len(outers)==7
letters=[[o]+[h for h in holes if inside(h,o)] for o in outers]
names=["T","H","R","I","E","V","E2"]; role={"E":"orange","V":"teal"}
circle=lambda r:parse_path(f"M {CX-r} {CY} A {r} {r} 0 1 0 {CX+r} {CY} A {r} {r} 0 1 0 {CX-r} {CY} Z").continuous_subpaths()[0]
band=[circle(RO),circle(RI)]
layers=[("ring-band","blue",band,None)]
layers+=[(f"letter-{n}",role.get(n,"white"),ls,None) for n,ls in zip(names,letters)]
layers+=[("text-left","white",P["text-left"].continuous_subpaths(),None),("text-right","white",P["text-right"].continuous_subpaths(),None),
         ("emblem","white",emblem,"blue")]
if os.environ.get("EMB")=="lines": layers[-1:]=[("emblem-body","white",emblem_union,None),("emblem-lines","white",emblem,"blue")]                # (name, fill colour, subpaths, outline colour)
def arc_cubics(a):
    n=max(1,math.ceil(abs(a.delta)/90.0)); k=1/math.radians(a.delta); res=[]
    for i in range(n):
        t0,t1=i/n,(i+1)/n; al=4/3*math.tan(math.radians(a.delta)*(t1-t0)/4); P3=a.point(t1)
        res.append((a.point(t0)+al*a.derivative(t0)*k,P3-al*a.derivative(t1)*k,P3))
    return res
def segs(sp):
    for g in sp:
        if isinstance(g,Line): yield ("L",[g.end])
        elif isinstance(g,CubicBezier): yield ("C",[g.control1,g.control2,g.end])
        else:
            for c in arc_cubics(g): yield ("C",list(c))
def pdf_path(subpaths,S,H):
    f=lambda z:"%.4f %.4f"%(z.real*S,H-z.imag*S); o=[]
    for sp in subpaths:
        o.append(f(sp[0].start)+" m")
        for kd,pts in segs(sp): o.append(" ".join(f(p) for p in pts)+(" l" if kd=="L" else " c"))
        o.append("h")
    return "\n".join(o)
def svg_path(subpaths):
    out=[]
    for sp in subpaths:
        out.append("M %.4f %.4f "%(sp[0].start.real,sp[0].start.imag)+" ".join(kd+" "+" ".join("%.4f %.4f"%(p.real,p.imag) for p in pts) for kd,pts in segs(sp))+" Z")
    return " ".join(out)
def svg(pv=False):
    g=[]
    for n,c,sps,ol in layers:
        st=f' stroke="{RGB[ol]}" stroke-width="{OL}" stroke-linejoin="round"' if ol else ""
        g.append(f'  <g id="{n}"><path fill="{RGB[c]}" fill-rule="evenodd"{st} d="{svg_path(sps)}"/></g>')
    vbx="-30 -30 1018 1018" if pv else "0 0 958 958"; back='<rect x="-30" y="-30" width="1018" height="1018" fill="#ffffff"/>' if pv else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vbx}" width="{D}mm" height="{D}mm">\n{back}\n'+"\n".join(g)+"\n</svg>\n"
open(os.path.join(OUT,"thrieve-trunk-sticker-v2%s-editable.svg"%os.environ.get("EMB","")),"w",encoding="utf-8").write(svg())
W=D*72/25.4; S=W/958.0; H=W; kk=lambda c:"%.4f %.4f %.4f %.4f"%CM[c]; cs=[]
for n,c,sps,ol in layers:
    if ol: cs.append(f"{kk(c)} k\n{kk(ol)} K\n{OL*S:.4f} w 1 j\n"+pdf_path(sps,S,H)+"\nB*")      # fill + outline
    else: cs.append(f"{kk(c)} k\n"+pdf_path(sps,S,H)+"\nf*")
stream="\n".join(cs).encode()
objs=[b"<< /Type /Catalog /Pages 2 0 R >>", b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
      f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {W:.4f} {H:.4f}] /TrimBox [0 0 {W:.4f} {H:.4f}] /Contents 4 0 R /Resources << >> >>".encode(),
      b"<< /Length %d >>\nstream\n"%len(stream)+stream+b"\nendstream"]
out=bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"); off=[]
for i,o in enumerate(objs,1): off.append(len(out)); out+=f"{i} 0 obj\n".encode()+o+b"\nendobj\n"
x=len(out); out+=f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode()+"".join("%010d 00000 n \n"%o for o in off).encode()
out+=f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R /Info << /Title (ThriEVe trunk sticker v2) >> >>\nstartxref\n{x}\n%%EOF\n".encode()
open(os.path.join(OUT,f"thrieve-trunk-sticker-v2{os.environ.get('EMB','')}-{D:g}mm-white-vinyl-CMYK.pdf"),"wb").write(out)
t=os.path.join(OUT,"_p.svg"); open(t,"w",encoding="utf-8").write(svg(True)); subprocess.run([INK,t,"-o",os.path.join(OUT,"thrieve-trunk-sticker-v2%s-preview.png"%os.environ.get("EMB","")),"-w","1200"],check=True,capture_output=True); os.remove(t)
print("ok")
