"""Trunk sticker v2 (white vinyl, outlined style from the printer's reference): CMYK PDF + editable SVG.  usage: make_sticker2.py [diameter_mm=50] [outline_units=5]"""
import sys, os, re, math, subprocess
from svgpathtools import parse_path, Line, CubicBezier, Arc
D=float(sys.argv[1]) if len(sys.argv)>1 else 50.0
OW=float(sys.argv[2]) if len(sys.argv)>2 else 5.0          # outline width in artwork units (958 = ring diameter)
L=r"C:\Thrive Website\assets\logo-concepts"; INK=r"C:\Program Files\Inkscape\bin\inkscape.exe"
OUT=os.path.dirname(os.path.abspath(__file__))
EMB=os.environ.get("EMB","solid")          # solid = emblem lines filled dark blue; bold = white core + heavy dark blue outline
BOLD=float(os.environ.get("BOLDW",12))
TAG="" if EMB=="solid" else "-bold-outline"
s=open(os.path.join(L,"thrieve-words-inner-circle-black.svg"),encoding="utf-8").read()
P={k:parse_path(re.search(r'<g id="%s"><path[^>]*?\sd="([^"]+)"'%k,s).group(1)) for k in ("ring","ring-inner","emblem","text-top","text-left","text-right")}
CX=CY=479.0
CM={"orange":(0,.832,1,0),"teal":(.752,0,.1727,0),"blue":(1,.8356,.1151,.0342),"white":(0,0,0,0)}
RGB={"orange":"#f2501e","teal":"#1cb9dc","blue":"#213f95","white":"#ffffff"}
subs=P["text-top"].continuous_subpaths()
def bb(p): x0,x1,y0,y1=p.bbox(); return x0,x1,y0,y1
def inside(a,b): A,B=bb(a),bb(b); return B[0]<=A[0] and A[1]<=B[1] and B[2]<=A[2] and A[3]<=B[3]
outers=[p for p in subs if not any(q is not p and inside(p,q) for q in subs)]; holes=[p for p in subs if p not in outers]
ang=lambda p:(lambda b:math.atan2(-((b[2]+b[3])/2-CY),(b[0]+b[1])/2-CX))(bb(p))
outers.sort(key=ang,reverse=True); assert len(outers)==7
letters=[[o]+[h for h in holes if inside(h,o)] for o in outers]
names=["T","H","R","I","E","V","E2"]; fillc={"E":"orange","V":"teal"}
# (name, fill colour, stroke colour or None, subpaths)  bottom -> top
layers=[("ring","blue",None,P["ring"].continuous_subpaths()),("ring-inner","blue",None,P["ring-inner"].continuous_subpaths()),
        ("emblem","blue" if EMB=="solid" else "white","blue",P["emblem"].continuous_subpaths())]
WID={"emblem":BOLD} if EMB=="bold" else {}
layers+=[(f"letter-{n}",fillc.get(n,"white"),"blue",ls) for n,ls in zip(names,letters)]
layers+=[("text-left","white","blue",P["text-left"].continuous_subpaths()),("text-right","white","blue",P["text-right"].continuous_subpaths())]
def arc_cubics(a):
    n=max(1,math.ceil(abs(a.delta)/90.0)); res=[]
    for i in range(n):
        t0,t1=i/n,(i+1)/n; dth=math.radians(a.delta)*(t1-t0); al=4/3*math.tan(dth/4); k=1/math.radians(a.delta)
        P0,P3=a.point(t0),a.point(t1); d0,d1=a.derivative(t0)*k,a.derivative(t1)*k
        res.append((P0+al*d0,P3-al*d1,P3))
    return res
def fix_arcs(subpaths):
    out=[]
    for sp in subpaths:
        seg=["M %.4f %.4f"%(sp[0].start.real,sp[0].start.imag)]
        for g in sp:
            if isinstance(g,Line): seg.append("L %.4f %.4f"%(g.end.real,g.end.imag))
            elif isinstance(g,CubicBezier): seg.append("C %.4f %.4f %.4f %.4f %.4f %.4f"%(g.control1.real,g.control1.imag,g.control2.real,g.control2.imag,g.end.real,g.end.imag))
            else:
                for c1,c2,e in arc_cubics(g): seg.append("C %.4f %.4f %.4f %.4f %.4f %.4f"%(c1.real,c1.imag,c2.real,c2.imag,e.real,e.imag))
        out.append(" ".join(seg)+" Z")
    return " ".join(out)
def pdf_path(subpaths,S,H):
    f=lambda z:"%.4f %.4f"%(z.real*S,H-z.imag*S); o=[]
    for sp in subpaths:
        o.append(f(sp[0].start)+" m")
        for g in sp:
            if isinstance(g,Line): o.append(f(g.end)+" l")
            elif isinstance(g,CubicBezier): o.append(f(g.control1)+" "+f(g.control2)+" "+f(g.end)+" c")
            else:
                for c1,c2,e in arc_cubics(g): o.append(f(c1)+" "+f(c2)+" "+f(e)+" c")
        o.append("h")
    return "\n".join(o)
def svg(pv=None):
    g=[]
    for n,fc,sc,sps in layers:
        st=f' stroke="{RGB[sc]}" stroke-width="{WID.get(n,OW)}" stroke-linejoin="round"' if sc else ""
        g.append(f'  <g id="{n}"><path fill="{RGB[fc]}" fill-rule="evenodd"{st} d="{fix_arcs(sps)}"/></g>')
    vb="-30 -30 1018 1018" if pv else "0 0 958 958"
    back=f'<rect x="-30" y="-30" width="1018" height="1018" fill="{pv}"/>' if pv else ""
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" width="{D}mm" height="{D}mm">\n{back}\n'+"\n".join(g)+"\n</svg>\n"
open(os.path.join(OUT,f"thrieve-sticker-v3{TAG}-editable.svg"),"w",encoding="utf-8").write(svg())
def pdf(fn):
    W=D*72/25.4; S=W/958.0; H=W; f4=lambda c:"%.4f %.4f %.4f %.4f"%CM[c]; cs=["1 j 1 J"]
    for n,fc,sc,sps in layers:
        if sc: cs.append(f"{f4(fc)} k\n{f4(sc)} K\n{WID.get(n,OW)*S:.4f} w\n"+pdf_path(sps,S,H)+"\nB*")
        else:  cs.append(f"{f4(fc)} k\n"+pdf_path(sps,S,H)+"\nf*")
    stream="\n".join(cs).encode()
    objs=[b"<< /Type /Catalog /Pages 2 0 R >>",b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
          f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {W:.4f} {H:.4f}] /TrimBox [0 0 {W:.4f} {H:.4f}] /Contents 4 0 R /Resources << >> >>".encode(),
          b"<< /Length %d >>\nstream\n"%len(stream)+stream+b"\nendstream"]
    out=bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"); off=[]
    for i,o in enumerate(objs,1): off.append(len(out)); out+=f"{i} 0 obj\n".encode()+o+b"\nendobj\n"
    x=len(out); out+=f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode()+"".join("%010d 00000 n \n"%o for o in off).encode()
    out+=f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R /Info << /Title (ThriEVe trunk sticker v2) >> >>\nstartxref\n{x}\n%%EOF\n".encode()
    open(os.path.join(OUT,fn),"wb").write(out)
pdf(f"thrieve-sticker-v3{TAG}-{D:g}mm-white-vinyl-CMYK.pdf")
t=os.path.join(OUT,"_p.svg"); open(t,"w",encoding="utf-8").write(svg("#ffffff")); subprocess.run([INK,t,"-o",os.path.join(OUT,f"thrieve-sticker-v3{TAG}-preview.png"),"-w","1400"],check=True,capture_output=True); os.remove(t)
print("ok",D,OW)
