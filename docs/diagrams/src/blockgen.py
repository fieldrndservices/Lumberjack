#!/usr/bin/env python3
"""Block/flow-diagram -> SVG generator for the Lumberjack design docs (topology, config)."""
import html, cairosvg, os

FONT = "DejaVu Sans, Arial, sans-serif"
ROLE = {
    "app":   ("#E8EEF7", "#2B5C8A"),
    "blue":  ("#DCE9F5", "#2B6CB0"),
    "grey":  ("#EEF0F2", "#6B7280"),
    "orange":("#FBEBD7", "#C0651A"),
    "green": ("#E3EFE7", "#2F7D4F"),
    "warn":  ("#FBEBD7", "#C0651A"),
    "error": ("#F7E4E4", "#B03A2E"),
}
C = dict(blue="#2B6CB0", orange="#C0651A", green="#2F7D4F", grey="#6B7280", red="#B03A2E")
def esc(s): return html.escape(str(s), quote=True)

class Block:
    def __init__(self, title, W, H):
        self.title=title; self.W=W; self.H=H; self.items=[]
    def box(self, key, x, y, w, h, title, subs=None, role="blue"):
        self.items.append(("box", dict(key=key,x=x,y=y,w=w,h=h,title=title,subs=subs or [],role=role)))
        return key
    def _b(self,key):
        for t,d in self.items:
            if t=="box" and d["key"]==key: return d
    def arrow(self, a, b, color="blue", dashed=False, label=None, lpos=0.5, ldy=-8, bend=None):
        self.items.append(("arrow", dict(a=a,b=b,color=color,dashed=dashed,label=label,lpos=lpos,ldy=ldy,bend=bend)))
    def legend(self, x, y, entries):
        self.items.append(("legend", dict(x=x,y=y,entries=entries)))
    def edge_point(self, d, side):
        x,y,w,h = d["x"],d["y"],d["w"],d["h"]
        return {"l":(x,y+h/2),"r":(x+w,y+h/2),"t":(x+w/2,y),"b":(x+w/2,y+h/2 if False else y+h),
                "c":(x+w/2,y+h/2)}[side]
    def render(self):
        s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.W}" height="{self.H}" viewBox="0 0 {self.W} {self.H}" font-family="{FONT}">',
           f'<rect width="{self.W}" height="{self.H}" fill="white"/>','<defs>']
        for n,col in C.items():
            s.append(f'<marker id="m_{n}" markerWidth="12" markerHeight="12" refX="8" refY="4" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L10,4 L0,8 Z" fill="{col}"/></marker>')
        s.append('</defs>')
        s.append(f'<text x="34" y="42" font-size="22" font-weight="bold" fill="#1F2937">{esc(self.title)}</text>')
        # arrows first (under boxes)
        for t,d in self.items:
            if t=="arrow": s.append(self._arrow(d))
        for t,d in self.items:
            if t=="box": s.append(self._box(d))
            elif t=="legend": s.append(self._legend(d))
        s.append('</svg>'); return "\n".join(s)
    def _box(self,d):
        fill,stroke = ROLE[d["role"]]
        cx=d["x"]+d["w"]/2
        out=[f'<rect x="{d["x"]}" y="{d["y"]}" width="{d["w"]}" height="{d["h"]}" rx="12" ry="12" fill="{fill}" stroke="{stroke}" stroke-width="2"/>']
        subs=d["subs"]; n=len(subs)
        ty = d["y"]+d["h"]/2 - (n*11)
        out.append(f'<text x="{cx}" y="{ty}" font-size="17" font-weight="bold" text-anchor="middle" fill="#1F2937">{esc(d["title"])}</text>')
        for i,ln in enumerate(subs):
            out.append(f'<text x="{cx}" y="{ty+24+i*22}" font-size="13.5" text-anchor="middle" fill="#5b6472">{esc(ln)}</text>')
        return "\n".join(out)
    def _endpoints(self,a,b):
        da,db=self._b(a[0]),self._b(b[0])
        return self.edge_point(da,a[1]), self.edge_point(db,b[1])
    def _arrow(self,d):
        (x1,y1),(x2,y2)=self._endpoints(d["a"],d["b"])
        col=C[d["color"]]; dash=' stroke-dasharray="8,6"' if d["dashed"] else ''
        line=f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="2.4"{dash} marker-end="url(#m_{d["color"]})"/>'
        out=[line]
        if d["label"]:
            lx=x1+(x2-x1)*d["lpos"]; ly=y1+(y2-y1)*d["lpos"]+d["ldy"]
            out.append(f'<text x="{lx}" y="{ly}" font-size="14" text-anchor="middle" fill="{col}">{esc(d["label"])}</text>')
        return "\n".join(out)
    def _legend(self,d):
        x,y=d["x"],d["y"]; out=[]
        for (style,col,text) in d["entries"]:
            dash=' stroke-dasharray="8,6"' if style=="dashed" else ''
            out.append(f'<line x1="{x}" y1="{y}" x2="{x+70}" y2="{y}" stroke="{C[col]}" stroke-width="2.6"{dash}/>')
            out.append(f'<text x="{x+84}" y="{y+5}" font-size="15" fill="#3a4250">{esc(text)}</text>')
            x+=430
        return "\n".join(out)

def save(bl,name,outdir):
    svg=bl.render()
    with open(os.path.join(outdir,name+".svg"),"w") as f: f.write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(outdir,name+".png"), scale=2.0, background_color="white")
    print("wrote",name)

if __name__=="__main__":
    OUT=os.path.dirname(os.path.abspath(__file__)); D=os.path.join(OUT,"diag_out"); os.makedirs(D,exist_ok=True)

    # ---- topology ----
    b=Block("Figure 1. Runtime topology: control plane and data plane", 1600, 960)
    b.box("app",60,395,340,180,"Application VIs",["hold Logger facade","(many call sites)"],"app")
    b.box("notif",600,150,390,160,"Notifier",["snapshot: threshold +","{id, enqueuer} entries"],"grey")
    b.box("mgr",1140,150,400,160,"Log Manager",["root actor (control plane)"],"orange")
    b.box("fa",1140,400,400,120,"File Appender",["own queue -> rolling files"],"blue")
    b.box("ca",1140,545,400,120,"Console Appender",["own queue -> console"],"blue")
    b.box("ra",1140,690,400,120,"Relay Appender",["own queue -> application"],"blue")
    b.arrow(("app","t"),("notif","l"),"blue",dashed=True,label="reads snapshot",lpos=0.5,ldy=-10)
    b.arrow(("mgr","l"),("notif","r"),"orange",label="posts snapshot",lpos=0.5,ldy=-10)
    b.arrow(("mgr","b"),("fa","t"),"orange",dashed=True,label="launch / stop",lpos=0.5,ldy=-8)
    b.arrow(("app","r"),("fa","l"),"blue",label="enqueue LogStatementMsg",lpos=0.5,ldy=-10)
    b.arrow(("app","r"),("ca","l"),"blue")
    b.arrow(("app","r"),("ra","l"),"blue")
    b.legend(70,895,[("solid","blue","data plane (log statements)"),("dashed","orange","control plane (manager posts / launches)")])
    save(b,"topology",D)

    # ---- config ----
    b=Block("Figure 3. Configuration: resolve, merge, validate (at launch)", 1820, 700)
    b.box("li",60,150,340,120,"Launch inputs",["baseline config"],"blue")
    b.box("json",60,320,340,120,"JSON config file",["(optional)"],"grey")
    b.box("merge",500,180,430,190,"Merge",["Unflatten From JSON,","baseline as default","(file overrides set keys)"],"blue")
    b.box("val",1040,205,320,130,"Validate",["ranges, enums;","default-file gated on","enableDefaultFile"],"grey")
    b.box("eff",1470,195,320,150,"Effective config",["global threshold +","default file appender"],"green")
    b.box("warn",500,500,430,120,"File missing: warn,",["continue on inputs"],"warn")
    b.box("inv",1040,500,320,120,"Invalid:",["fail launch (error)"],"error")
    b.arrow(("li","r"),("merge","l"),"grey",dashed=True,label="default value",lpos=0.5,ldy=-10)
    b.arrow(("json","r"),("merge","l"),"blue")
    b.arrow(("merge","r"),("val","l"),"blue")
    b.arrow(("val","r"),("eff","l"),"blue")
    b.arrow(("merge","b"),("warn","t"),"orange",dashed=True,label="path given, file absent",lpos=0.55,ldy=-8)
    b.arrow(("val","b"),("inv","t"),"red",label="unparseable / bad value",lpos=0.55,ldy=-8)
    save(b,"config",D)
    print("all done")
