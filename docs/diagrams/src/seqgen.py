#!/usr/bin/env python3
"""Sequence-diagram -> SVG generator for the Lumberjack design docs.
Unified clean style; rendered to PNG with cairosvg (offline, no browser)."""
import html, cairosvg, os, textwrap

FONT = "DejaVu Sans, Arial, sans-serif"
ROLE = {
    "app":      ("#E8EEF7", "#2B5C8A"),
    "logger":   ("#DCE9F5", "#2B6CB0"),
    "notifier": ("#EEF0F2", "#6B7280"),
    "manager":  ("#FBEBD7", "#C0651A"),
    "appender": ("#E3EFE7", "#2F7D4F"),
    "store":    ("#FBEBD7", "#C0651A"),
}
C_BLUE, C_ORANGE, C_GREEN, C_GREY, C_RED = "#2B6CB0", "#C0651A", "#2F7D4F", "#6B7280", "#B03A2E"

def esc(s): return html.escape(str(s), quote=True)
def wrap(t, w): return textwrap.wrap(t, w) or [""]

class Seq:
    def __init__(self, title, participants, col_w=250):
        self.title = title
        self.parts = participants
        self.keys = [p[0] for p in participants]
        self.col_w = col_w
        self.LEFT = 90
        self.BOX_Y = 64
        self.BOX_H = 56
        self.BOX_W = 190
        self.row0 = self.BOX_Y + self.BOX_H + 48
        self.events = []
        self.y = self.row0
    def x(self, key):
        i = self.keys.index(key)
        return self.LEFT + i * self.col_w + self.BOX_W/2
    def msg(self, a, b, text, kind="sync", color=None):
        self.events.append(dict(t="msg", a=a, b=b, text=text, kind=kind, color=color, y=self.y))
        self.y += 58
    def selfmsg(self, a, text, color=C_GREEN):
        lines = wrap(text, 44)
        self.events.append(dict(t="self", a=a, lines=lines, color=color, y=self.y))
        self.y += 30 + len(lines)*16 + 18
    def note(self, text, x=None, style="info", align="middle", w=82):
        lines = wrap(text, w)
        self.events.append(dict(t="note", lines=lines, x=x, style=style, y=self.y, align=align))
        self.y += 16 + len(lines)*16
    def divider(self, label, color=C_GREEN):
        self.y += 8
        self.events.append(dict(t="div", label=label, color=color, y=self.y))
        self.y += 30
    def gap(self, h=18): self.y += h

    def render(self):
        W = self.LEFT*2 + (len(self.parts)-1)*self.col_w + self.BOX_W
        H = self.y + 40
        s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="{FONT}">']
        s.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="white"/>')
        s.append('<defs>')
        for name,col in [("blue",C_BLUE),("orange",C_ORANGE),("green",C_GREEN),("grey",C_GREY),("red",C_RED)]:
            s.append(f'<marker id="ah_{name}" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L9,3 L0,6 Z" fill="{col}"/></marker>')
            s.append(f'<marker id="oah_{name}" markerWidth="12" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L9,3 L0,6" fill="none" stroke="{col}" stroke-width="1.3"/></marker>')
        s.append('</defs>')
        s.append(f'<text x="30" y="36" font-size="20" font-weight="bold" fill="#1F2937">{esc(self.title)}</text>')
        life_top = self.BOX_Y + self.BOX_H
        life_bot = H - 26
        for p in self.parts:
            x = self.x(p[0])
            s.append(f'<line x1="{x}" y1="{life_top}" x2="{x}" y2="{life_bot}" stroke="#B7BEC7" stroke-width="1.4" stroke-dasharray="3,4"/>')
        for e in self.events:
            s.append(self._ev(e))
        for p in self.parts:
            key,ttl,sub,role = p
            fill,stroke = ROLE.get(role, ("#EEF0F2","#6B7280"))
            x = self.x(key) - self.BOX_W/2
            s.append(f'<rect x="{x}" y="{self.BOX_Y}" width="{self.BOX_W}" height="{self.BOX_H}" rx="9" ry="9" fill="{fill}" stroke="{stroke}" stroke-width="1.8"/>')
            cx = self.x(key)
            if sub:
                s.append(f'<text x="{cx}" y="{self.BOX_Y+24}" font-size="14" font-weight="bold" text-anchor="middle" fill="#1F2937">{esc(ttl)}</text>')
                s.append(f'<text x="{cx}" y="{self.BOX_Y+42}" font-size="11" text-anchor="middle" fill="#6B7280">{esc(sub)}</text>')
            else:
                s.append(f'<text x="{cx}" y="{self.BOX_Y+34}" font-size="14" font-weight="bold" text-anchor="middle" fill="#1F2937">{esc(ttl)}</text>')
        s.append('</svg>')
        return "\n".join(s)

    def _ev(self, e):
        cnm = {C_BLUE:"blue",C_ORANGE:"orange",C_GREEN:"green",C_GREY:"grey",C_RED:"red"}
        if e["t"] == "msg":
            xa, xb = self.x(e["a"]), self.x(e["b"]); y = e["y"]
            color = e["color"] or (C_BLUE if xa < xb else C_ORANGE)
            cn = cnm.get(color,"blue")
            dash = ' stroke-dasharray="6,5"' if e["kind"]=="return" else ''
            marker = f'oah_{cn}' if e["kind"]=="return" else f'ah_{cn}'
            tx = (xa+xb)/2
            out = [f'<text x="{tx}" y="{y-8}" font-size="13" text-anchor="middle" fill="#1F2937">{esc(e["text"])}</text>',
                   f'<line x1="{xa}" y1="{y}" x2="{xb}" y2="{y}" stroke="{color}" stroke-width="1.8"{dash} marker-end="url(#{marker})"/>']
            return "\n".join(out)
        if e["t"] == "self":
            x = self.x(e["a"]); y = e["y"]; color=e["color"]; cn=cnm.get(color,"green")
            lines = e["lines"]; n=len(lines)
            out=[]
            # labels centered above the loop, so leftmost columns never clip
            for i,ln in enumerate(lines):
                out.append(f'<text x="{x}" y="{y + i*16 + 11}" font-size="13" text-anchor="middle" fill="#1F2937">{esc(ln)}</text>')
            loop_top = y + n*16 + 8
            out.append(f'<path d="M{x},{loop_top} h26 v18 h-26" fill="none" stroke="{color}" stroke-width="1.8" marker-end="url(#ah_{cn})"/>')
            return "\n".join(out)
        if e["t"] == "note":
            y=e["y"]; x = e["x"] if e["x"] is not None else (self.LEFT + ((len(self.parts)-1)*self.col_w+self.BOX_W)/2)
            fill = C_RED if e["style"]=="constraint" else "#6B7280"
            out=[]
            for i,ln in enumerate(e["lines"]):
                out.append(f'<text x="{x}" y="{y+i*16}" font-size="12.5" font-style="italic" text-anchor="{e["align"]}" fill="{fill}">{esc(ln)}</text>')
            return "\n".join(out)
        if e["t"] == "div":
            y=e["y"]; W = self.LEFT*2 + (len(self.parts)-1)*self.col_w + self.BOX_W
            return (f'<line x1="30" y1="{y-4}" x2="{W-30}" y2="{y-4}" stroke="#D7DCE2" stroke-width="1.2"/>'
                    f'<text x="40" y="{y+14}" font-size="14" font-weight="bold" fill="{e["color"]}">{esc(e["label"])}</text>')
        return ""

def save(seq, name, outdir):
    svg = seq.render()
    with open(os.path.join(outdir, name+".svg"),"w") as f: f.write(svg)
    cairosvg.svg2png(bytestring=svg.encode(), write_to=os.path.join(outdir, name+".png"), scale=2.0, background_color="white")
    print("wrote", name)

# ----------------------------------------------------------------------------
if __name__ == "__main__":
    OUT = os.path.dirname(os.path.abspath(__file__))
    D = os.path.join(OUT, "diag_out"); os.makedirs(D, exist_ok=True)

    # ---- launch ----
    d = Seq("Figure 7. Initialization / launch sequence",
            [("app","Application","caller","app"),
             ("init","Logger.Initialize","","logger"),
             ("mgr","LogManager","root actor","manager"),
             ("fa","FileAppender","nested actor","appender")], col_w=300)
    d.msg("app","init","Initialize(threshold, fileCfg, paths, enableDefaultFile)")
    d.note("PRE-LAUNCH: obtain snapshotNotifier + stoppedNotifier (unnamed)", x=d.x("init"), style="constraint", align="start", w=52)
    d.selfmsg("init","construct LogManager; SetLaunchInputs (both notifiers)", color=C_BLUE)
    d.msg("init","mgr","Launch Root Actor(manager)", color=C_GREEN)
    d.msg("mgr","init","manager enqueuer", kind="return", color=C_GREY)
    d.note("Actor Core begins (async)", x=d.x("mgr"), style="info", align="start")
    d.selfmsg("mgr","ResolveConfig (baseline / file merge, §4.2)", color=C_ORANGE)
    d.msg("mgr","fa","Launch Nested Actor(FileAppender) [if enableDefaultFile]", color=C_ORANGE)
    d.msg("fa","mgr","appender enqueuer + caller-actor-out", kind="return", color=C_GREY)
    d.selfmsg("mgr","append RegistryEntry{id, enqueuer}", color=C_ORANGE)
    d.msg("mgr","init","PostSnapshot: Send Notification{threshold, {id,enqueuer}[]}", color=C_ORANGE)
    d.note("snapshot carries {id, enqueuer} entries (§2.1); posted before the loop", x=d.x("mgr"), style="constraint", align="middle", w=60)
    d.selfmsg("mgr","Call Parent Method (enter message loop)", color=C_ORANGE)
    d.gap(8)
    d.selfmsg("init","WaitForSnapshot(AnySnapshot): readiness barrier (§5.11)", color=C_BLUE)
    d.note("blocks until initial snapshot; manager dies on entry -> error 5030 (loud)", x=d.x("init"), style="constraint", align="start", w=56)
    d.msg("init","app","return ready Logger (+ non-fatal config warning on error wire)", kind="return", color=C_GREY)
    save(d, "launch", D)

    # ---- register / unregister ----
    d = Seq("Figure 5. Register and unregister an appender at runtime",
            [("app","Application","via Logger","app"),
             ("mgr","LogManager","root actor","manager"),
             ("note","snapshotNotifier","","notifier"),
             ("ap","Appender","nested actor","appender")], col_w=300)
    d.divider("Register", C_GREEN)
    d.msg("app","mgr","RegisterAppender -> RegisterAppenderMsg(configured Appender)", color=C_BLUE)
    d.msg("mgr","ap","Launch Nested Actor", color=C_ORANGE)
    d.msg("ap","mgr","appender enqueuer", kind="return", color=C_GREY)
    d.selfmsg("mgr","append RegistryEntry{id, enqueuer}", color=C_ORANGE)
    d.msg("mgr","note","PostSnapshot (+ {id, enqueuer})", color=C_ORANGE)
    d.msg("app","note","WaitForSnapshot(IDPresent, id)", color=C_BLUE)
    d.msg("note","app","id present -> appender is live", kind="return", color=C_GREY)
    d.note("returns only once the id appears; next Log reaches it (§5.11)", x=d.x("app"), style="info", align="start", w=60)
    d.gap(10)
    d.divider("Unregister", C_RED)
    d.msg("app","mgr","UnregisterAppender -> UnregisterAppenderMsg(id)", color=C_BLUE)
    d.selfmsg("mgr","remove RegistryEntry(id)", color=C_ORANGE)
    d.msg("mgr","note","PostSnapshot (- id)", color=C_ORANGE)
    d.msg("mgr","ap","Stop (framework)", color=C_ORANGE)
    d.selfmsg("ap","flush + close sink", color=C_GREEN)
    d.msg("app","note","WaitForSnapshot(IDAbsent, id)", color=C_BLUE)
    d.msg("note","app","id absent -> unregistered", kind="return", color=C_GREY)
    d.note("unknown id: already absent -> returns immediately (benign no-op)", x=d.x("app"), style="constraint", align="start", w=60)
    save(d, "register", D)

    # ---- shutdown ----
    d = Seq("Figure 6. Shutdown: synchronous stop and teardown",
            [("app","Application","caller","app"),
             ("mgr","LogManager","root actor","manager"),
             ("ap","Appender","each nested","appender"),
             ("sn","stoppedNotifier","error cluster","notifier")], col_w=300)
    d.msg("app","mgr","Logger.Shutdown -> framework Stop", color=C_BLUE)
    d.note("runs even if error in is set (SRS-LMBR-004)", x=d.x("mgr"), style="info", align="start", w=46)
    d.msg("mgr","ap","Stop (to each nested appender)", color=C_ORANGE)
    d.selfmsg("ap","drain queued statements", color=C_GREEN)
    d.selfmsg("ap","CloseSink (flush + close)", color=C_GREEN)
    d.msg("ap","mgr","stopped", kind="return", color=C_GREY)
    d.note("Call Parent Method returns only after ALL nested actors have stopped", x=d.x("mgr"), style="constraint", align="middle", w=64)
    d.selfmsg("mgr","Actor Core exit: Send Notification(exitError)", color=C_ORANGE)
    d.msg("mgr","sn","stoppedNotifier <- exitError", color=C_ORANGE)
    d.msg("app","sn","Wait on Notification (bounded)", color=C_BLUE)
    d.msg("sn","app","exitError (fired once)", kind="return", color=C_GREY)
    d.note("not stopped within timeout -> error 5032", x=d.x("app"), style="constraint", align="start", w=48)
    d.selfmsg("app","force-destroy application-owned relay queues", color=C_BLUE)
    d.note("safe only after confirmed stop: no writer can hit a destroyed queue (§5.6, §5.10)", x=d.x("app"), style="info", align="start", w=64)
    save(d, "shutdown", D)

    # ---- barriers (new, §5.11) ----
    d = Seq("Figure 8. Synchronous confirmation barriers (§5.11)",
            [("cal","Caller / Test","","logger"),
             ("mgr","LogManager","root actor","manager"),
             ("sp","snapshotNotifier","Snapshot","notifier"),
             ("st","stoppedNotifier","error cluster","notifier")], col_w=300)
    d.divider("Snapshot barrier  -  WaitForSnapshot", C_BLUE)
    d.msg("mgr","sp","PostSnapshot on every control-plane change", color=C_ORANGE)
    d.selfmsg("cal","WaitForSnapshot(mode, targetID) - deadline loop", color=C_BLUE)
    d.msg("cal","sp","read (Wait on Notification, remaining time)", color=C_BLUE)
    d.msg("sp","cal","snapshot -> test predicate", kind="return", color=C_GREY)
    d.note("AnySnapshot = readiness  ·  IDPresent = register  ·  IDAbsent = unregister", x=d.x("cal"), style="info", align="start", w=66)
    d.note("id is the signal, not a count; bounded deadline, timeout -> error 5030", x=d.x("cal"), style="constraint", align="start", w=66)
    d.gap(12)
    d.divider("Stopped barrier  -  Logger.Shutdown", C_RED)
    d.msg("mgr","st","Actor Core exit: Send Notification(exitError)", color=C_ORANGE)
    d.note("fired once, only after all nested appenders stopped", x=d.x("mgr"), style="info", align="middle", w=56)
    d.msg("cal","st","Wait on Notification (bounded, single wait)", color=C_BLUE)
    d.msg("st","cal","exitError", kind="return", color=C_GREY)
    d.note("fires exactly once (no predicate loop); timeout -> error 5032", x=d.x("cal"), style="constraint", align="start", w=62)
    save(d, "barriers", D)

    print("all done")
