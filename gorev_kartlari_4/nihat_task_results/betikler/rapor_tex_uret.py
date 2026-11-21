"""[Nihat, gorev kartlari 4] Nihat_Gorev_Karti_4_Rapor.md -> Nihat_Gorev_Karti_4_Rapor.tex
Yalnizca Python standart kutuphanesi kullanilir. Formuller elle yazilmis LaTeX karsiliklariyla (SUBS, DISPLAY) degistirilir.
Calistirma (nihat_task_results klasorunde):
    python3 betikler/rapor_tex_uret.py                                            # kisa rapor
    python3 betikler/rapor_tex_uret.py Nihat_Gorev_Karti_4_Rapor_ayrintili.md --icindekiler   # ayrintili rapor
Derleme (iki kez; icindekiler icin):
    pdflatex Nihat_Gorev_Karti_4_Rapor.tex && pdflatex Nihat_Gorev_Karti_4_Rapor.tex
    (xelatex, lualatex ya da tectonic ile de derlenir)
"""
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
KOK = os.path.join(HERE, "..")
SRC = os.path.join(KOK, "Nihat_Gorev_Karti_4_Rapor.md")
OUT = os.path.join(KOK, "Nihat_Gorev_Karti_4_Rapor.tex")
TOC = False          # --icindekiler: icindekiler sayfasi ve BOLUM basliklarinda yeni sayfa (ayrintili rapor icin)

# ------------------------------------------------------------------ formuller
# (md parcasi, LaTeX) -- uzun/ozel olanlar once
SUBS = [
    ("N_info > 3824 olduğunda nicemleme yapılır ve TBS = 8·C·⌈(N′_info + 24)/(8·C)⌉ − 24 hesaplanır.",
     r"$N_{\mathrm{info}} > 3824$ olduğunda nicemleme yapılır ve taşıma bloğu boyutu şöyle hesaplanır: "
     r"\[ \mathrm{TBS} = 8C\left\lceil \frac{N'_{\mathrm{info}} + 24}{8C} \right\rceil - 24 . \]"),
    ("t = (slot_ofset + o·T_PRS_slot)·14·T_sym + (sembol_ofset + j)·T_sym",
     r"$t = (\text{slot\_ofset} + o\,T_{\mathrm{PRS,slot}})\cdot 14\,T_{\mathrm{sym}} + (\text{sembol\_ofset} + j)\,T_{\mathrm{sym}}$"),
    ("N′_RE = 12·N_sembol − N_DMRS − N_oh",
     r"$N'_{\mathrm{RE}} = 12\,N_{\text{sembol}} - N_{\mathrm{DMRS}} - N_{\mathrm{oh}}$"),
    ("N_RE = min(156, N′_RE)·n_PRB", r"$N_{\mathrm{RE}} = \min(156,\, N'_{\mathrm{RE}})\cdot n_{\mathrm{PRB}}$"),
    ("N_info = N_RE·R·Q_m·υ", r"$N_{\mathrm{info}} = N_{\mathrm{RE}}\cdot R\cdot Q_m\cdot \upsilon$"),
    ("N_RE = N_RE,başlangıç − N_PRS,veri", r"$N_{\mathrm{RE}} = N_{\text{RE,başlangıç}} - N_{\text{PRS,veri}}$"),
    ("N_info ≤ 3824", r"$N_{\mathrm{info}} \le 3824$"),
    ("N_info ≈ 182 000 bit", r"$N_{\mathrm{info}} \approx 182\,000$ bit"),
    ("G = 10·log10(Σ|a_i|²)", r"$G = 10\log_{10}\!\bigl(\sum_i |a_i|^2\bigr)$"),
    ("(λ/4πd)²", r"$(\lambda/4\pi d)^2$"),
    ("20·log10(4,9/3,5)", r"$20\log_{10}(4{,}9/3{,}5)$"),
    ("10·log10(3276/1024)", r"$10\log_{10}(3276/1024)$"),
    ("8 + 10·log10(64)", r"$8 + 10\log_{10}64$"),
    ("T_s = (1/SCS)·(1 + 7/64)", r"$T_s = (1/\mathrm{SCS})\cdot(1 + 7/64)$"),
    ("W = N·SCS", r"$W = N\cdot\mathrm{SCS}$"),
    ("(c / f_c)", r"($c/f_{\mathrm{c}}$)"),
    ("ΔR = c/(2B)", r"$\Delta R = c/(2B)$"),
    ("c/(2W)", r"$c/(2W)$"),
    ("c/(2B)", r"$c/(2B)$"),
    ("10⁻³", r"$10^{-3}$"),
    ("±λ/(4·T_PRS)", r"$\pm\lambda/(4T_{\mathrm{PRS}})$"),
    ("λ/(4·T_PRS)", r"$\lambda/(4T_{\mathrm{PRS}})$"),
    ("λ/(2·0,16 s)", r"$\lambda/(2\cdot 0{,}16\,\mathrm{s})$"),
    ("λ/(2·M·T_s)", r"$\lambda/(2MT_s)$"),
    ("λ/(4·50)", r"$\lambda/(4\cdot 50)$"),
    ("λ/(4·TS)", r"$\lambda/(4T_S)$"),
    ("λ/(2·M·TS)", r"$\lambda/(2MT_S)$"),
    ("m·TS", r"$m\,T_S$"),
    ("modulo 2·v_max", r"modulo $2v_{\max}$"),
    ("α_PRS = PRS RE / toplam RE", r"$\alpha_{\mathrm{PRS}} = \text{PRS RE}/\text{toplam RE}$"),
    ("α = M/140", r"$\alpha = M/140$"),
    ("0,5·Δr … 1,5·Δr", r"$0{,}5\,\Delta r \ldots 1{,}5\,\Delta r$"),
    ("v·t", r"$v\,t$"),
    ("1/T_gözlem", r"$1/T_{\text{gözlem}}$"),
    ("→ Q_m = 6, R = 948/1024", r"$\rightarrow Q_m = 6,\ R = 948/1024$"),
    ("λ²", r"$\lambda^2$"),
    ("işlem kazancı N·M", r"işlem kazancı $N\cdot M$"),
]
TOKENS = {"X_SI": r"X_{\mathrm{SI}}", "f_c": r"f_{\mathrm{c}}", "T_PRS": r"T_{\mathrm{PRS}}", "P_FA": r"P_{\mathrm{FA}}",
          "T_s": r"T_s", "α_PRS": r"\alpha_{\mathrm{PRS}}", "v_max": r"v_{\max}", "Q_m": r"Q_m",
          "N_info": r"N_{\mathrm{info}}", "N_RE": r"N_{\mathrm{RE}}", "a_i": r"a_i"}
TOKEN_RE = re.compile(r"(?<![\w/\\])(" + "|".join(sorted(map(re.escape, TOKENS), key=len, reverse=True)) + r")(?!\w)")

# 2 bosluk girintili denklem satirlari -> numarali denklem
DISPLAY = {
    "P_r = ": r"P_r = \frac{P_t\, G^2 \lambda^2 \sigma}{(4\pi)^3 R^4}, \qquad "
              r"\mathrm{SNR}_{\text{örnek}} = \frac{P_r}{k T_0\, N\, \mathrm{SCS}\, F\, X_{\mathrm{SI}}}",
    "SNR_tepe": r"\mathrm{SNR}_{\text{tepe}} = \mathrm{SNR}_{\text{örnek}}\cdot N M "
                r"= \frac{P_t\, G^2 \lambda^2 \sigma\, M}{(4\pi)^3 R^4\, k T_0\, \mathrm{SCS}\, F\, X_{\mathrm{SI}}}",
    "Y(k,t)": r"Y(k,t) = a\, X(k,t)\, e^{-j2\pi f_k \tau_0}\, e^{\,j2\pi f_D t}\, e^{\,j2\pi f_k f_D t / f_{\mathrm{c}}} + n(k,t), "
              r"\qquad f_D = -\frac{2 v_r}{\lambda}",
}

# ------------------------------------------------------------------ satir ici donusum
CHARMAP = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
           "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", "<": r"\textless{}", ">": r"\textgreater{}", "|": r"\textbar{}"}

def esc(s):
    return "".join(CHARMAP.get(c, c) for c in s)

def code_tex(s):
    t = esc(s).replace(r"\_", r"\_\allowbreak{}").replace("/", r"/\allowbreak{}")
    return r"\texttt{" + t + "}"

def inline(text):
    """Satir ici: baglanti -> metin, `kod`, formuller, **kalin**, tirnaklar, LaTeX kacislari."""
    keep = []
    def ph(latex):
        keep.append(latex)
        return f"\x00{len(keep) - 1}\x00"
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)
    text = re.sub(r"`([^`]+)`", lambda m: ph(code_tex(m.group(1))), text)
    for a, b in SUBS:
        if a in text:
            text = text.replace(a, ph(b))
    text = TOKEN_RE.sub(lambda m: ph("$" + TOKENS[m.group(1)] + "$"), text)
    text = re.sub(r'"([^"\x00]+)"', lambda m: "\x01" + m.group(1) + "\x02", text)
    out = esc(text).replace("\x01", "``").replace("\x02", "''")
    out = re.sub(r"(\d) (\d{3})(?![\d,])", r"\1\\,\2", out)
    parts = out.split("**")
    out = "".join(p if k % 2 == 0 else r"\textbf{" + p + "}" for k, p in enumerate(parts))
    return re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], out)

def plain(t):
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", t)
    return t.replace("**", "").replace("`", "")

def pdfstr(t):
    t = plain(t).replace("→", "->").replace("—", "-").replace("–", "-").replace("_", " ")
    return esc(t)

# ------------------------------------------------------------------ tablo
def split_row(line):
    s = line.strip()
    s = s[1:] if s.startswith("|") else s
    s = s[:-1] if s.endswith("|") else s
    cells, cur, code = [], "", False
    for ch in s:
        if ch == "`":
            code = not code
        if ch == "|" and not code:
            cells.append(cur.strip()); cur = ""
        else:
            cur += ch
    cells.append(cur.strip())
    return cells

def table(rows):
    head, body = rows[0], rows[2:]
    n = len(head)
    body = [(r + [""] * n)[:n] for r in body]
    size = r"\scriptsize" if n >= 10 else r"\footnotesize" if n >= 7 else r"\small"
    k = {r"\scriptsize": 0.86, r"\footnotesize": 0.96, r"\small": 1.05}[size]   # karakter basina satir genisligi yuzdesi
    nb = lambda t: re.sub(r"(\d) (\d{3})\b", r"\1~\2", plain(t))                  # binlik ayirac bolunmez
    words = lambda t: max((len(w) for w in re.split(r"[\s/]+", nb(t))), default=0)
    mn, want = [], []
    for c in range(n):
        mw = words(head[c]) * 1.3; ww = min(len(plain(head[c])), 16) * 0.55
        for r in body:
            mw = max(mw, words(r[c])); ww = max(ww, min(len(plain(r[c])), 46))
        mn.append(max(mw, 2) * k + 2.6); want.append(max(ww, mw, 2) * k + 2.6)
    S = 100.0
    if sum(want) <= S:
        w = [x * S / sum(want) for x in want]
    elif sum(mn) >= S:
        w = [x * S / sum(mn) for x in mn]
    else:
        f = (S - sum(mn)) / (sum(want) - sum(mn)); w = [m + f * (want[c] - m) for c, m in enumerate(mn)]
    center = [c > 0 and all(len(plain(r[c])) <= 18 for r in body) for c in range(n)]
    spec = "".join(
        (r">{\centering\arraybackslash}" if center[c] else r">{\raggedright\arraybackslash}")
        + r"p{\dimexpr %.4f\linewidth-2\tabcolsep\relax}" % (w[c] / S) for c in range(n))
    L = [r"\begin{center}", r"\begingroup" + size, r"\begin{tabular}{@{}" + spec + "@{}}", r"\toprule"]
    L.append(" & ".join(r"\textbf{" + inline(h) + "}" for h in head) + r" \\")
    L.append(r"\midrule")
    for r in body:
        L.append(" & ".join(inline(x) for x in r) + r" \\")
    L += [r"\bottomrule", r"\end{tabular}\endgroup", r"\end{center}"]
    return L

# ------------------------------------------------------------------ bloklar
LIST_RE = re.compile(r"^(\s*)([-*]|\d+\.)\s+(.*)$")

def convert(lines):
    out, i, title_done, toc_done = [], 0, False, False
    while i < len(lines):
        line = lines[i]
        if not line.strip() or re.match(r"^---+\s*$", line):
            i += 1; continue
        if line.startswith("```"):
            code = []; i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code.append(lines[i]); i += 1
            i += 1
            out += [r"\begin{kod}", r"\begin{Verbatim}[breaklines,breakanywhere,fontsize=\footnotesize]"] + code + [r"\end{Verbatim}", r"\end{kod}", ""]
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            lvl, txt = len(m.group(1)), m.group(2)
            if lvl == 1 and not title_done:
                title_done = True
                out += [r"\begin{center}", r"{\sffamily\bfseries\LARGE\color{acc} " + inline(txt) + "}", r"\end{center}", r"\vspace{2mm}", ""]
            else:
                if lvl == 2 and not toc_done and TOC:
                    toc_done = True
                    out += [r"\clearpage", r"\tableofcontents", r"\clearpage", ""]
                cmd = {1: "section", 2: "subsection", 3: "subsubsection", 4: "paragraph"}[lvl]
                pre = ([r"\clearpage"] if TOC else [r"\bigskip"]) if lvl == 1 else []
                t = r"\texorpdfstring{" + inline(txt) + "}{" + pdfstr(txt) + "}"
                out += pre + [r"\phantomsection", "\\" + cmd + "*{" + t + "}"]
                if lvl <= 2:
                    out.append(r"\addcontentsline{toc}{" + cmd + "}{" + t + "}")
                out.append("")
            i += 1; continue
        if line.strip().startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i])); i += 1
            out += table(rows) + [""]
            continue
        m = re.match(r"^!\[[^\]]*\]\(([^)]+)\)\s*$", line)
        if m:
            path = m.group(1); cap = ""
            j = i + 1
            while j < len(lines) and not lines[j].strip(): j += 1
            if j < len(lines) and lines[j].strip().startswith("*Şekil"):
                cap = lines[j].strip().strip("*"); i = j
            out += [r"\begin{figure}[H]", r"\centering",
                    r"\includegraphics[width=\linewidth,height=0.45\textheight,keepaspectratio]{" + path + "}",
                    r"\par\smallskip", r"{\small\itshape " + inline(cap) + "}", r"\end{figure}", ""]
            i += 1; continue
        if line.startswith(">"):
            paras, cur = [], []
            while i < len(lines) and lines[i].startswith(">"):
                t = re.sub(r"^>\s?", "", lines[i])
                if not t.strip():
                    if cur: paras.append(" ".join(cur)); cur = []
                else:
                    cur.append(t)
                i += 1
            if cur: paras.append(" ".join(cur))
            out += [r"\begin{ozet}"] + [inline(p) + "\n" for p in paras] + [r"\end{ozet}", ""]
            continue
        if LIST_RE.match(line):
            stack = []                                     # [(env, level)]
            while i < len(lines):
                l = lines[i]
                if not l.strip():
                    j = i + 1
                    while j < len(lines) and not lines[j].strip(): j += 1
                    if j < len(lines) and (LIST_RE.match(lines[j]) or re.match(r"^\s{3,}\S", lines[j])):
                        i = j; continue
                    break
                mm = LIST_RE.match(l)
                if mm:
                    lvl = 1 if len(mm.group(1)) >= 2 else 0
                    env = "enumerate" if re.match(r"\d+\.", mm.group(2)) else "itemize"
                    while stack and stack[-1][1] > lvl:
                        out.append(r"\end{" + stack.pop()[0] + "}")
                    if stack and stack[-1][1] == lvl and stack[-1][0] != env:
                        out.append(r"\end{" + stack.pop()[0] + "}")
                    if not stack or stack[-1][1] < lvl:
                        out.append(r"\begin{" + env + "}"); stack.append((env, lvl))
                    out.append(r"\item " + inline(mm.group(3)))
                elif re.match(r"^\s{2,}\S", l):
                    while stack and stack[-1][1] > 0:
                        out.append(r"\end{" + stack.pop()[0] + "}")
                    out.append(r"\par\smallskip " + inline(l.strip()))
                else:
                    break
                i += 1
            while stack:
                out.append(r"\end{" + stack.pop()[0] + "}")
            out.append("")
            continue
        if re.match(r"^ {2}\S", line):
            key = next((k for k in DISPLAY if line.strip().startswith(k)), None)
            if key is None:
                raise SystemExit("tanimsiz denklem satiri: " + line)
            out += [r"\begin{equation}", DISPLAY[key], r"\end{equation}", ""]
            i += 1; continue
        out += [inline(line.strip()), ""]
        i += 1
    return out

PREAMBLE = r"""% Otomatik uretildi: betikler/rapor_tex_uret.py (kaynak: Nihat_Gorev_Karti_4_Rapor.md). Elle degistirmeyin; .md'yi degistirip yeniden uretin.
\documentclass[11pt,a4paper]{article}
\usepackage{iftex}
\ifPDFTeX
  \usepackage[T1]{fontenc}
  \usepackage[utf8]{inputenc}
  \usepackage{lmodern}
  \usepackage{textcomp}
\else
  \usepackage{fontspec}
\fi
\usepackage[turkish,shorthands=off]{babel}
\usepackage[a4paper,left=2.2cm,right=2.2cm,top=2.2cm,bottom=2.2cm,headheight=14pt]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{graphicx,float,array,booktabs}
\usepackage[table]{xcolor}
\usepackage{enumitem,fancyhdr,titlesec}
\usepackage{fvextra}
\usepackage[most]{tcolorbox}
\usepackage{newunicodechar}
\usepackage[hidelinks]{hyperref}

\definecolor{acc}{HTML}{1F4E79}\definecolor{accl}{HTML}{EEF2F7}\definecolor{codebg}{HTML}{F3F4F6}\definecolor{muted}{HTML}{6B7280}

% metin icindeki Unicode simgeler -> matematik
\newunicodechar{λ}{\ensuremath{\lambda}}
\newunicodechar{α}{\ensuremath{\alpha}}
\newunicodechar{σ}{\ensuremath{\sigma}}
\newunicodechar{Δ}{\ensuremath{\Delta}}
\newunicodechar{τ}{\ensuremath{\tau}}
\newunicodechar{π}{\ensuremath{\pi}}
\newunicodechar{Σ}{\ensuremath{\Sigma}}
\newunicodechar{υ}{\ensuremath{\upsilon}}
\newunicodechar{≥}{\ensuremath{\geq}}
\newunicodechar{≤}{\ensuremath{\leq}}
\newunicodechar{≈}{\ensuremath{\approx}}
\newunicodechar{→}{\ensuremath{\rightarrow}}
\newunicodechar{×}{\ensuremath{\times}}
\newunicodechar{·}{\ensuremath{\cdot}}
\newunicodechar{−}{\ensuremath{-}}
\newunicodechar{±}{\ensuremath{\pm}}
\newunicodechar{∈}{\ensuremath{\in}}
\newunicodechar{′}{\ensuremath{'}}
\newunicodechar{⌈}{\ensuremath{\lceil}}
\newunicodechar{⌉}{\ensuremath{\rceil}}
\newunicodechar{²}{\textsuperscript{2}}
\newunicodechar{³}{\textsuperscript{3}}
\newunicodechar{⁴}{\textsuperscript{4}}
\newunicodechar{⁻}{\textsuperscript{\ensuremath{-}}}
\newunicodechar{₀}{\textsubscript{0}}
\newunicodechar{µ}{\ensuremath{\mu}}
\newunicodechar{…}{\ldots}

\setlength{\parindent}{0pt}\setlength{\parskip}{5pt plus 1pt}\setlength{\emergencystretch}{3em}
\renewcommand{\arraystretch}{1.18}
\setlist{itemsep=3pt,topsep=3pt,parsep=0pt}
\setcounter{tocdepth}{2}
\titleformat{\section}{\sffamily\bfseries\LARGE\color{acc}}{}{0pt}{}
\titleformat{\subsection}{\sffamily\bfseries\Large\color{acc}}{}{0pt}{}
\titleformat{\subsubsection}{\sffamily\bfseries\large}{}{0pt}{}
\titlespacing*{\subsection}{0pt}{14pt}{6pt}
\titlespacing*{\subsubsection}{0pt}{10pt}{4pt}
\pagestyle{fancy}\fancyhf{}
\renewcommand{\headrulewidth}{0.3pt}
\fancyhead[L]{\sffamily\footnotesize\color{muted} Nihat -- Görev Kartı 4}
\fancyhead[R]{\sffamily\footnotesize\color{muted} n78, 3,5 GHz, 30 kHz, 100 MHz}
\fancyfoot[C]{\sffamily\footnotesize\color{muted} Sayfa \thepage}
\newtcolorbox{ozet}{enhanced,breakable,colback=accl,colframe=acc,boxrule=0pt,leftrule=2.5pt,arc=0pt,left=8pt,right=8pt,top=6pt,bottom=6pt}
\newtcolorbox{kod}{enhanced,breakable,colback=codebg,colframe=codebg!60!black,boxrule=0.3pt,arc=1pt,left=4pt,right=4pt,top=2pt,bottom=2pt}
\title{Nihat -- Görev Kartı 4 Uygulama ve Sonuç Raporu}
\author{Nihat}
\date{21 Kasım 2026}

\begin{document}
\thispagestyle{fancy}
"""

def main():
    global SRC, OUT, TOC
    import sys
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    TOC = "--icindekiler" in sys.argv
    if args:
        SRC = os.path.abspath(args[0]); OUT = os.path.splitext(SRC)[0] + ".tex"
    lines = open(SRC, encoding="utf-8").read().replace("\r", "").split("\n")
    body = convert(lines)
    tex = PREAMBLE + "\n".join(body) + "\n\\end{document}\n"
    open(OUT, "w", encoding="utf-8").write(tex)
    # denetim: tanimsiz Unicode karakterler, { } ve $ dengesi
    izinli = set("ıİğĞşŞçÇöÖüÜâÂîÎûÛéÉèàá°§–—“”’") | set("λασΔτπΣυ≥≤≈→×·−±∈′⌈⌉²³⁴⁻₀µ…")
    kotu = sorted({c for c in tex if ord(c) > 127 and c not in izinli})
    dengesiz = 0
    for n, l in enumerate(tex.split("\n"), 1):
        s = re.sub(r"\\[{}$]", "", l)
        if s.count("{") != s.count("}") or s.count("$") % 2:
            if not l.startswith(("\\begin{Verbatim}", "[", " ", "~")) and "\\[" not in l:
                dengesiz += 1
                print(f"  denetim: satir {n} dengesiz: {l[:120]}")
    print("yazildi:", os.path.relpath(OUT), "| satir:", tex.count("\n"), "| tanimsiz karakter:", kotu, "| dengesiz satir:", dengesiz)

if __name__ == "__main__":
    main()
