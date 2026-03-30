#!/usr/bin/env python3
"""
Sorting algorithm visualizer v4 or idk i cant keep track of versions - Pygame port (was Tkinter)
• 22 algorithms  •  Slightly devistating UI  •  Buttons and Sliders!  •  Useless extra info!  •  Sound
• Generator based 60 fps loop
smol note: some drawing code and helper parts were vibe coded for the pygame port
"""
import pygame, sys, math, struct, random, time
sys.setrecursionlimit(12000)

# ══════════════════════════════════════════════════════════════════════════════
#  SOUND
# ══════════════════════════════════════════════════════════════════════════════
# (was gonna rewrite this for better sounds but im too lazy and it kinda became normal after hundreds of listens)
_SND = False
try:
    pygame.mixer.pre_init(44100, -16, 2, 512)
    _SND = True
except Exception:
    pass

_PENTA = (0, 3, 5, 7, 10)
_ROOT  = 61.74
N_NOTES = 18

def _penta_freq(idx):
    return _ROOT * 2.0 ** (((idx // 5) * 12 + _PENTA[idx % 5]) / 12.0)

def _make_sound(freq, dur=0.055, vol=1.0):
    if not _SND: return None
    sr = 44100; n = int(sr * dur); buf = bytearray(n * 4)
    tau = 22.0; rd = int(sr * 0.013); rg = 0.22; p2 = math.pi * 2
    for i in range(n):
        t = i / sr; ev = math.exp(-t * tau)
        ph = (freq * t) % 1.0; tri = 1.0 - 4.0 * abs(ph - 0.5)
        w = 0.65 * tri + 0.35 * math.sin(p2 * freq * t)
        r = 0.0
        if i >= rd:
            td = (i - rd) / sr; ed = math.exp(-td * tau)
            phd = (freq * td) % 1.0; trd = 1.0 - 4.0 * abs(phd - 0.5)
            r = (0.65 * trd + 0.35 * math.sin(p2 * freq * td)) * ed * rg
        s = max(-32768, min(32767, int((w * ev + r) * 32767.0 * vol)))
        struct.pack_into("<hh", buf, i * 4, s, s)
    try:
        return pygame.mixer.Sound(buffer=bytes(buf))
    except Exception:
        return None

# ══════════════════════════════════════════════════════════════════════════════
#  PALETTE (nice and sexy)
# ══════════════════════════════════════════════════════════════════════════════
BG            = ( 13,  15,  20)
PANEL         = ( 19,  22,  30)
ACCENT        = (107,  92, 255)
ACCENT2       = (245, 194,  76)
ACCENT3       = (255, 107, 107)
SORTED_CLR    = ( 74, 222, 128)
PARTITION_CLR = (  0, 212, 255)
TEXT          = (232, 232, 240)
SUBTEXT       = (107, 109, 130)
BTN_BG        = ( 30,  33,  48)
BTN_HOVER     = ( 42,  45,  66)
BORDER        = ( 37,  40,  64)

def _glow(c, f=0.11):
    return tuple(min(255, int(v + (255 - v) * f)) for v in c)

GLOW = {c: _glow(c) for c in (ACCENT, ACCENT2, ACCENT3, SORTED_CLR, PARTITION_CLR)}

# ══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
SPEEDS = {
    "0.5x": dict(cmp_f=8, swp_f=25, is_max=False),
    "1x":   dict(cmp_f= 3, swp_f=8, is_max=False),
    "3x":   dict(cmp_f= 1, swp_f= 1, is_max=False),
    "max":  dict(cmp_f= 0, swp_f= 0, is_max=True ),
}
SPD_ORDER = ["0.5x", "1x", "3x", "max"]
SPD_TINT  = {
    "0.5x": (162, 155, 254),
    "1x":   SUBTEXT,
    "3x":   (255, 159,  67),
    "max":  ACCENT3,
}

ST_IDLE    = "idle"
ST_RUNNING = "running"
ST_PAUSED  = "paused"
ST_DONE    = "done"

STEP_PT = object()

ALGOS = [
    "Bubble Sort", "Insertion Sort", "Selection Sort", "Merge Sort",
    "Cocktail Shaker Sort", "Bucket Sort", "Shell Sort", "Radix Sort",
    "Quick Sort", "Gnome Sort", "Heap Sort", "Comb Sort",
    "Counting Sort", "Pancake Sort", "Tim Sort", "Cycle Sort",
    "Odd-Even Sort", "Bogosort", "Bitonic Sort", "Sleep Sort",
    "Stooge Sort", "Tree Sort", "e"
]

TOP_H      = 56
STRIP_H    = 26
BOT_H      = 58
PANEL_W    = 310
DD_VISIBLE = 6

SHUFFLE_MODES = ["RND", "REV", "ASC"]

# ══════════════════════════════════════════════════════════════════════════════
#  ALGORITHM INFO
# ══════════════════════════════════════════════════════════════════════════════
# thank you wikipedia
ALGO_INFO = {
    "Bubble Sort": dict(
        best="O(n)", avg="O(n^2)", worst="O(n^2)", space="O(1)", stable=True,
        approach="In-place  ·  Brute Force",
        snippet="for i in range(n):\n  for j in range(n-i-1):\n    if a[j] > a[j+1]:\n      swap(j, j+1)",
        fact="Named in 1962 by Kenneth Iverson; rarely used in production.",
    ),
    "Insertion Sort": dict(
        best="O(n)", avg="O(n^2)", worst="O(n^2)", space="O(1)", stable=True,
        approach="In-place  ·  Incremental",
        snippet="for i in range(1, n):\n  key = a[i]; j = i-1\n  while j>=0 and a[j]>key:\n    a[j+1]=a[j]; j-=1\n  a[j+1] = key",
        fact="Fastest known algorithm for nearly-sorted or very small (n<20) data.",
    ),
    "Selection Sort": dict(
        best="O(n^2)", avg="O(n^2)", worst="O(n^2)", space="O(1)", stable=False,
        approach="In-place  ·  Brute Force",
        snippet="for i in range(n):\n  mi = i\n  for j in range(i+1, n):\n    if a[j] < a[mi]: mi = j\n  swap(i, mi)",
        fact="Always makes exactly n-1 swaps — ideal when writes are costly.",
    ),
    "Merge Sort": dict(
        best="O(n log n)", avg="O(n log n)", worst="O(n log n)", space="O(n)", stable=True,
        approach="Out-of-place  ·  Divide & Conquer",
        snippet="def merge(a, l, m, r):\n  L=a[l:m+1]; R=a[m+1:r+1]\n  i=j=k=0\n  while i<len(L) and j<len(R):\n    pick smaller; a[k]=it; k+=1",
        fact="Invented by John von Neumann in 1945. Guarantees O(n log n) always.",
    ),
    "Cocktail Shaker Sort": dict(
        best="O(n)", avg="O(n^2)", worst="O(n^2)", space="O(1)", stable=True,
        approach="In-place  ·  Bidirectional Bubble",
        snippet="while lo < hi:\n  pass right -> hi -= 1\n  pass left  <- lo += 1",
        fact="Moves small 'turtle' values near the end faster than Bubble Sort.",
    ),
    "Bucket Sort": dict(
        best="O(n+k)", avg="O(n+k)", worst="O(n^2)", space="O(n+k)", stable=True,
        approach="Out-of-place  ·  Distribution",
        snippet="for v in arr:\n  buckets[idx(v)].append(v)\nfor b in buckets:\n  insertion_sort(b)\narr = flatten(buckets)",
        fact="Best when input is uniformly distributed over a known range.",
    ),
    "Shell Sort": dict(
        best="O(n log n)", avg="O(n log^2 n)", worst="O(n^2)", space="O(1)", stable=False,
        approach="In-place  ·  Gap Insertion",
        snippet="gap = n // 2\nwhile gap > 0:\n  for i in range(gap, n):\n    insert a[i] in gap sequence\n  gap //= 2",
        fact="Donald Shell, 1959 — first sort algorithm to beat O(n^2).",
    ),
    "Radix Sort": dict(
        best="O(nk)", avg="O(nk)", worst="O(nk)", space="O(n+k)", stable=True,
        approach="Out-of-place  ·  Non-Comparative",
        snippet="exp = 1\nwhile max(arr) // exp > 0:\n  counting_sort by (v//exp)%10\n  exp *= 10",
        fact="Used in electromechanical punch-card machines since 1887.",
    ),
    "Quick Sort": dict(
        best="O(n log n)", avg="O(n log n)", worst="O(n^2)", space="O(log n)", stable=False,
        approach="In-place  ·  Divide & Conquer",
        snippet="def partition(a, lo, hi):\n  piv=a[hi]; i=lo-1\n  for j in range(lo, hi):\n    if a[j]<=piv: i+=1; swap(i,j)\n  swap(i+1, hi)",
        fact="Tony Hoare, 1959 — fastest in practice for most real-world data.",
    ),
    "Gnome Sort": dict(
        best="O(n)", avg="O(n^2)", worst="O(n^2)", space="O(1)", stable=True,
        approach="In-place  ·  Brute Force",
        snippet="i = 1\nwhile i < n:\n  if a[i] >= a[i-1]: i += 1\n  else:\n    swap(i, i-1)\n    if i > 1: i -= 1",
        fact="Originally called 'Stupid Sort' by Hamid Sarbazi-Azad.",
    ),
    "Heap Sort": dict(
        best="O(n log n)", avg="O(n log n)", worst="O(n log n)", space="O(1)", stable=False,
        approach="In-place  ·  Selection + Heap",
        snippet="# Build max-heap\nfor i in range(n//2-1, -1, -1):\n  heapify(a, n, i)\n# Extract max repeatedly\nfor i in range(n-1, 0, -1):\n  swap(0, i); heapify(a, i, 0)",
        fact="Guaranteed O(n log n) worst case with O(1) extra memory — rare.",
    ),
    "Comb Sort": dict(
        best="O(n log n)", avg="O(n^2/2^p)", worst="O(n^2)", space="O(1)", stable=False,
        approach="In-place  ·  Gap Reduction",
        snippet="gap = n; shrink = 1.3\nwhile gap > 1 or swapped:\n  gap = max(1, int(gap/shrink))\n  for i in range(n-gap):\n    if a[i] > a[i+gap]: swap",
        fact="Improves Bubble Sort by eliminating 'turtles' with larger initial gaps.",
    ),
    "Counting Sort": dict(
        best="O(n+k)", avg="O(n+k)", worst="O(n+k)", space="O(n+k)", stable=True,
        approach="Out-of-place  ·  Non-Comparative",
        snippet="count = [0]*(max-min+1)\nfor v in arr: count[v-min]+=1\nfor i in range(1,k): count[i]+=count[i-1]\n# reconstruct from counts",
        fact="Linear time, but only works for integer keys in a bounded range.",
    ),
    "Pancake Sort": dict(
        best="O(n)", avg="O(n^2)", worst="O(n^2)", space="O(1)", stable=False,
        approach="In-place  ·  Prefix Reversal",
        snippet="for size in range(n, 1, -1):\n  mi = argmax(a[:size])\n  if mi != size-1:\n    flip(a, 0, mi)\n    flip(a, 0, size-1)",
        fact="Motivated by sorting pancakes with a spatula — each move flips a prefix.",
    ),
    "Tim Sort": dict(
        best="O(n)", avg="O(n log n)", worst="O(n log n)", space="O(n)", stable=True,
        approach="Hybrid  ·  Merge + Insertion",
        snippet="# Split into minRun-sized runs\nfor start in range(0, n, RUN):\n  insertion_sort(a, start, min(start+RUN,n))\n# Merge adjacent runs\nsize = RUN\nwhile size < n:\n  merge pairs; size *= 2",
        fact="Python's built-in sort since 2002; Java's Arrays.sort since Java 7.",
    ),
    "Cycle Sort": dict(
        best="O(n^2)", avg="O(n^2)", worst="O(n^2)", space="O(1)", stable=False,
        approach="In-place  ·  Minimum Writes",
        snippet="for cs in range(n-1):\n  item = a[cs]; pos = cs\n  count smaller -> pos\n  rotate cycle: a[pos]=item\n  item = displaced value",
        fact="Theoretically optimal for minimising writes to storage — O(n) writes total.",
    ),
    "Odd-Even Sort": dict(
        best="O(n)", avg="O(n^2)", worst="O(n^2)", space="O(1)", stable=True,
        approach="In-place  ·  Parallel Bubble",
        snippet="while not sorted:\n  for i in range(0,n-1,2): # even\n    if a[i]>a[i+1]: swap\n  for i in range(1,n-1,2): # odd\n    if a[i]>a[i+1]: swap",
        fact="Designed for parallel processors — even/odd passes can run simultaneously.",
    ),
    "Bogosort": dict(
        best="O(n)", avg="O((n+1)!)", worst="unbounded", space="O(1)", stable=False,
        approach="In-place  ·  Random Shuffle",
        snippet="while not is_sorted(a):\n  shuffle(a)  # random permutation",
        fact="Expected O((n+1)!) comparisons. Use n<=8 for any chance of finishing.",
    ),
    "Bitonic Sort": dict(
        best="O(n log^2 n)", avg="O(n log^2 n)", worst="O(n log^2 n)", space="O(log^2 n)", stable=False,
        approach="In-place  ·  Comparator Network",
        snippet="k = 2\nwhile k <= n:\n  j = k >> 1\n  while j > 0:\n    compare-swap (i, i^j)\n    j >>= 1\n  k <<= 1",
        fact="Highly parallelisable — all comparisons at the same depth are independent.",
    ),
    "Sleep Sort": dict(
        best="O(n+max)", avg="O(n+max)", worst="O(n+max)", space="O(n)", stable=True,
        approach="Out-of-place  ·  Delay-based",
        snippet="for v in arr:\n  spawn thread:\n    sleep(v * delay)\n    output(v)\nresult = collect outputs in order",
        fact="A real algorithm: each element's thread sleeps proportional to its value.",
    ),
    "Stooge Sort": dict(
        best="O(n^2.71)", avg="O(n^2.71)", worst="O(n^2.71)", space="O(n)", stable=False,
        approach="In-place  ·  Recursive Thirds",
        snippet="def stooge(a, lo, hi):\n  if a[lo]>a[hi]: swap(lo,hi)\n  if hi-lo+1 > 2:\n    t=(hi-lo+1)//3\n    stooge(a,lo,hi-t)\n    stooge(a,lo+t,hi)\n    stooge(a,lo,hi-t)",
        fact="Named after the Three Stooges — deliberately terrible at O(n^2.71).",
    ),
    "Tree Sort": dict(
        best="O(n log n)", avg="O(n log n)", worst="O(n^2)", space="O(n)", stable=True,
        approach="Out-of-place  ·  Binary Search Tree",
        snippet="root = None\nfor v in arr:\n  root = bst_insert(root, v)\nresult = []\ninorder_traverse(root, result)\narr[:] = result",
        fact="Worst case O(n^2) when input is already sorted (degenerate BST).",
    ),
}

# ══════════════════════════════════════════════════════════════════════════════
#  DRAW HELPERS
# ══════════════════════════════════════════════════════════════════════════════
def drect(surf, color, rect, radius=0, border=0, bc=None):
    r = pygame.Rect(rect)
    if radius and min(r.w, r.h) > radius * 2:
        pygame.draw.rect(surf, color, r, border_radius=radius)
        if border and bc: pygame.draw.rect(surf, bc, r, border, border_radius=radius)
    else:
        pygame.draw.rect(surf, color, r)
        if border and bc: pygame.draw.rect(surf, bc, r, border)

def dtxt(surf, text, pos, font, color, anchor="topleft"):
    s = font.render(str(text), True, color)
    r = s.get_rect(); setattr(r, anchor, pos)
    surf.blit(s, r); return r

def _make_fonts():
    F = {}
    preferred = [
        "JetBrainsMono NF", "JetBrainsMono", "jetbrainsmononf",
        "Cascadia Mono", "Cascadia Code", "Fira Code",
        "Consolas", "DejaVu Sans Mono", "Courier New", "monospace",
    ]
    sizes = [("xl",32,True),("lg",19,True),("md",15,True),
              ("sm",13,False),("xs",12,False),("xx",11,False)]
    for key, size, bold in sizes:
        placed = False
        for name in preferred:
            try:
                F[key] = pygame.font.SysFont(name, size, bold=bold)
                placed = True; break
            except Exception:
                continue
        if not placed:
            F[key] = pygame.font.Font(None, size + 4)
    return F

# ══════════════════════════════════════════════════════════════════════════════
#  SELECTION WINDOW
# ══════════════════════════════════════════════════════════════════════════════
class SelectionScreen:
    CW, CH = 420, 370

    def run(self):
        W, H   = self.CW + 60, self.CH + 60
        screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("Sort Visualizer")
        F = _make_fonts(); clock = pygame.time.Clock()
        algo = ALGOS[0]; count = 30; max_count = 500
        dd_open = False; dd_scroll = 0
        sl_drag = False; sb_drag = False
        ox, oy = 30, 30; cx = ox + self.CW // 2
        item_h = 26; dd_vis_h = DD_VISIBLE * item_h; sb_w = 10

        while True:
            mouse = pygame.mouse.get_pos()
            dd_r  = pygame.Rect(ox+30, oy+148, self.CW-60, 32)
            sl_r  = pygame.Rect(ox+30, oy+256, self.CW-60, 8)
            btn_r = pygame.Rect(cx-80, oy+318, 160, 40)
            dl_r  = pygame.Rect(dd_r.x, dd_r.bottom, dd_r.w, dd_vis_h)
            sb_track = pygame.Rect(dl_r.right-sb_w, dl_r.y, sb_w, dl_r.h)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:            return None
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:     return None
                    if e.key == pygame.K_RETURN:     return algo, count
                    if dd_open:
                        if e.key == pygame.K_DOWN:
                            dd_scroll = min(dd_scroll+1, len(ALGOS)-DD_VISIBLE)
                        if e.key == pygame.K_UP:
                            dd_scroll = max(dd_scroll-1, 0)
                if e.type == pygame.MOUSEWHEEL and dd_open and dl_r.collidepoint(mouse):
                    dd_scroll = max(0, min(len(ALGOS)-DD_VISIBLE, dd_scroll-e.y))
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if dd_open:
                        if sb_track.collidepoint(mouse):
                            sb_drag = True
                        else:
                            for vi in range(DD_VISIBLE):
                                ri = dd_scroll + vi
                                if ri >= len(ALGOS): break
                                ir = pygame.Rect(dl_r.x, dl_r.y+vi*item_h, dl_r.w-sb_w, item_h)
                                if ir.collidepoint(mouse):
                                    algo = ALGOS[ri]; dd_open = False; break
                            else:
                                if not dl_r.collidepoint(mouse): dd_open = False
                    else:
                        if   dd_r.collidepoint(mouse):              dd_open = True
                        elif btn_r.collidepoint(mouse):             return algo, count
                        elif sl_r.inflate(0,22).collidepoint(mouse): sl_drag = True
                if e.type == pygame.MOUSEBUTTONUP:
                    sl_drag = False; sb_drag = False
                if e.type == pygame.MOUSEMOTION:
                    if sl_drag:
                        frac = (mouse[0]-sl_r.x)/max(1, sl_r.w)
                        count = int(3 + max(0., min(1., frac))*(max_count-3))
                    if sb_drag:
                        rel = (mouse[1]-sb_track.y)/max(1, sb_track.h)
                        dd_scroll = int(max(0, min(len(ALGOS)-DD_VISIBLE, rel*len(ALGOS))))

            screen.fill(BG)
            drect(screen, PANEL, (ox,oy,self.CW,self.CH), radius=8, border=1, bc=BORDER)
            dtxt(screen, "SORT",       (cx, oy+36), F["xl"], ACCENT,  anchor="center")
            dtxt(screen, "VISUALIZER", (cx, oy+68), F["md"], TEXT,    anchor="center")
            pygame.draw.rect(screen, ACCENT, (cx-50, oy+88, 100, 2))
            dtxt(screen, "algorithm",  (cx, oy+116), F["xs"], SUBTEXT, anchor="center")

            dc = BTN_HOVER if dd_r.collidepoint(mouse) and not dd_open else BTN_BG
            drect(screen, dc, dd_r, radius=4, border=1, bc=BORDER)
            dtxt(screen, algo, (dd_r.x+10, dd_r.centery), F["sm"], TEXT, anchor="midleft")
            dtxt(screen, "v",  (dd_r.right-12, dd_r.centery), F["xs"], ACCENT, anchor="midright")

            dtxt(screen, "values", (cx, oy+228), F["xs"], SUBTEXT, anchor="center")
            dtxt(screen, str(count), (cx, oy+242), F["sm"], ACCENT, anchor="center")
            drect(screen, BTN_BG, sl_r, radius=3)
            fw = int(sl_r.w*(count-3)/(max_count-3))
            if fw > 0:
                pygame.draw.rect(screen, ACCENT, (sl_r.x,sl_r.y,fw,sl_r.h), border_radius=3)
            pygame.draw.circle(screen, ACCENT, (sl_r.x+fw, sl_r.centery), 6)
            dtxt(screen, "3",   (sl_r.x-8,sl_r.centery),  F["xs"], SUBTEXT, anchor="midright")
            dtxt(screen, str(max_count), (sl_r.right+8,sl_r.centery), F["xs"], SUBTEXT, anchor="midleft")

            bc2 = (130,110,255) if btn_r.collidepoint(mouse) else ACCENT
            drect(screen, bc2, btn_r, radius=6)
            dtxt(screen, "LAUNCH", (btn_r.centerx,btn_r.centery), F["md"], (255,255,255), anchor="center")

            if dd_open:
                pygame.draw.rect(screen, BTN_BG, dl_r)
                pygame.draw.rect(screen, BORDER, dl_r, 1)
                for vi in range(DD_VISIBLE):
                    ri = dd_scroll + vi
                    if ri >= len(ALGOS): break
                    name = ALGOS[ri]
                    ir   = pygame.Rect(dl_r.x, dl_r.y+vi*item_h, dl_r.w-sb_w, item_h)
                    sel  = name == algo; hov = ir.collidepoint(mouse)
                    pygame.draw.rect(screen, ACCENT if sel else (BTN_HOVER if hov else BTN_BG), ir)
                    dtxt(screen, name, (ir.x+10, ir.centery), F["sm"],
                         BG if sel else (TEXT if hov else SUBTEXT), anchor="midleft")
                n_over = max(1, len(ALGOS)-DD_VISIBLE)
                sb_h   = max(20, dl_r.h*DD_VISIBLE//len(ALGOS))
                sb_y   = sb_track.y + int(dd_scroll/n_over*(dl_r.h-sb_h))
                pygame.draw.rect(screen, BORDER, sb_track)
                drect(screen, BTN_HOVER, (sb_track.x+2, sb_y, sb_w-4, sb_h), radius=3)

            pygame.display.flip(); clock.tick(60)

# ══════════════════════════════════════════════════════════════════════════════
#  SORT VISUALIZER
# ══════════════════════════════════════════════════════════════════════════════
class SortVisualizer:
    def __init__(self, algo, num_values, speed="1x"):
        self.algo        = algo
        self.num_values  = num_values
        self.speed       = speed

        self.values          = []
        self.colors          = []
        self.x_offsets       = []
        self.compare_count   = 0
        self.swap_count      = 0
        self.partition_count = 0
        self._partition_set  = set()
        self._state          = ST_IDLE
        self._gen            = None
        self._piv            = 0

        self._step_mode    = False
        self._step_waiting = False

        self._elapsed_base  = 0.0
        self._segment_start = 0.0

        self._hud_visible    = True
        self._fullscreen     = False
        self._panel_open     = False
        self._panel_x        = float(-PANEL_W)
        self._panel_target   = float(-PANEL_W)

        self._sound_on    = True
        self._volume      = 0.85
        self._all_notes   = []
        self._sweep_notes = []
        self._note_map    = {}
        if _SND:
            pygame.mixer.set_num_channels(32)
            for i in range(N_NOTES):
                f = _penta_freq(i)
                self._all_notes.append(_make_sound(f, 0.055, 0.82))
                self._sweep_notes.append(_make_sound(f, 0.095, 0.92))

        self._phase = ""

        self._shuffle_mode = "RND"

        # FPS rolling average
        self._fps        = 0.0
        self._fps_acc    = 0.0
        self._fps_frames = 0


        self._legend_surf = None
        self._legend_w    = 0

        self._screen   = None
        self._F        = _make_fonts()
        self._rects    = {}
        self._vol_drag = False
        self._shuffle()

    # ── Main loop ─────────────────────────────────────────────────────────────
    def run(self):
        self._screen = pygame.display.set_mode(
            (1100, 640), pygame.RESIZABLE | pygame.DOUBLEBUF, vsync=1
        )
        pygame.display.set_caption(f"Sort Visualizer ... {self.algo}")
        clock = pygame.time.Clock()

        while True:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:   return "quit"
                if e.type == pygame.KEYDOWN:
                    r = self._key(e.key)
                    if r: return r
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    r = self._click(pygame.mouse.get_pos())
                    if r: return r
                if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                    self._vol_drag = False
                if e.type == pygame.MOUSEMOTION and self._vol_drag:
                    self._vol_from_mouse(pygame.mouse.get_pos())
                if e.type == pygame.VIDEORESIZE:
                    w = max(e.w, 640); h = max(e.h, 420)
                    self._screen = pygame.display.set_mode(
                        (w, h), pygame.RESIZABLE | pygame.DOUBLEBUF, vsync=1
                    ) if (w != e.w or h != e.h) else pygame.display.get_surface()
                    self._force_redraw()

            dt = clock.tick(60) / 1000.0
            self._fps_acc += 1.0/max(dt, 0.001); self._fps_frames += 1
            if self._fps_frames >= 30:
                self._fps = self._fps_acc/self._fps_frames
                self._fps_acc = 0.0; self._fps_frames = 0

            self._update(dt)
            self._draw()
            pygame.display.flip()

    # ── Input ─────────────────────────────────────────────────────────────────
    def _key(self, k):
        if k == pygame.K_ESCAPE:
            if self._fullscreen: self._toggle_fullscreen()
            else: return "back"
        elif k == pygame.K_SPACE:                                     self._on_action()
        elif k == pygame.K_r:                                         self._shuffle()
        elif k == pygame.K_h:                                         self._toggle_hud()
        elif k == pygame.K_i:                                         self._toggle_panel()
        elif k == pygame.K_m:                                         self._toggle_sound()
        elif k in (pygame.K_s, pygame.K_RIGHT):                       self._do_step()
        elif k in (pygame.K_PLUS,pygame.K_EQUALS,pygame.K_KP_PLUS):  self._cycle_speed(1)
        elif k in (pygame.K_MINUS, pygame.K_KP_MINUS):               self._cycle_speed(-1)
        elif k == pygame.K_F11:                                       self._toggle_fullscreen()
        return None

    def _click(self, pos):
        R = self._rects
        def hit(k): return R.get(k, pygame.Rect(0,0,0,0)).collidepoint(pos)
        if hit("x"):       return "back"
        if hit("action"):  self._on_action()
        if hit("step"):    self._do_step()
        if hit("restart"): self._shuffle()
        if hit("ptab"):    self._toggle_panel()
        if hit("sound"):   self._toggle_sound()
        if R.get("vol", pygame.Rect(0,0,0,0)).inflate(0,20).collidepoint(pos):
            self._vol_drag = True; self._vol_from_mouse(pos)
        for spd in SPD_ORDER:
            if hit(f"spd_{spd}"): self.speed = spd
        for mode in SHUFFLE_MODES:
            if hit(f"shuf_{mode}"): self._shuffle_mode = mode
        return None

    def _force_redraw(self):
        self._draw(); pygame.display.flip()

    # ── Update ────────────────────────────────────────────────────────────────
    def _update(self, dt):
        diff = self._panel_target - self._panel_x
        self._panel_x = self._panel_target if abs(diff) < 0.5 else \
                        self._panel_x + diff * min(1.0, 16.0*dt)

        if self._state != ST_RUNNING or self._gen is None or self._step_waiting:
            return
        sp = SPEEDS[self.speed]
        if sp["is_max"]:
            deadline = time.perf_counter() + 0.080
            while time.perf_counter() < deadline:
                try: next(self._gen)
                except StopIteration:
                    self._gen = None; self._on_sort_done(); return
            return
        try:
            tok = next(self._gen)
            self._force_redraw()
            if tok is STEP_PT and self._step_mode:
                self._step_waiting = True
        except StopIteration:
            self._gen = None; self._on_sort_done()

    # ══════════════════════════════════════════════════════════════════════════
    #  DRAW
    # ══════════════════════════════════════════════════════════════════════════
    def _draw(self):
        sc = self._screen; sw, sh = sc.get_size(); sc.fill(BG)
        if self._hud_visible:
            by = TOP_H + STRIP_H; bh = sh - by - BOT_H
        else:
            by = 0; bh = sh
        self._draw_bars(sc, sw, by, max(bh,1))
        if self._hud_visible:
            self._draw_top(sc, sw)
            self._draw_strip(sc, sw)
            self._draw_bottom(sc, sw, sh)
        self._draw_panel(sc, sh)
        self._draw_panel_tab(sc, sh)

    def _draw_bars(self, sc, sw, by, bh):
        n = len(self.values)
        if n == 0: return
        bw, gap, x0 = self._bar_dims(sw)
        mv = max(self.values); area = bh - 20
        hi_n = n > 400
        show_lbl  = (not hi_n) and bw >= 11
        draw_glow = (not hi_n) and n < 350
        for i in range(n):
            v  = self.values[i]; c = self.colors[i]
            ox = self.x_offsets[i] if i < len(self.x_offsets) else 0.0
            h  = max(1, int(v/mv*area))
            x  = int(x0 + i*(bw+gap) + ox); y = by+bh-h-10
            if draw_glow:
                gc = GLOW.get(c, c)
                pygame.draw.rect(sc, gc, (x-2, y-1, bw+4, h+1))
            if hi_n:
                pygame.draw.rect(sc, c, (x, y, bw, h))
            else:
                r = min(3, bw//2) if bw > 6 else 0
                pygame.draw.rect(sc, c, (x, y, bw, h), border_radius=r)
            if show_lbl:
                lbl = self._F["xx"].render(str(v), True, SUBTEXT)
                sc.blit(lbl, (x+bw//2-lbl.get_width()//2, y-13))
        if self._state == ST_PAUSED:
            ov = pygame.Surface((sw, bh), pygame.SRCALPHA)
            ov.fill((13,15,20,130)); sc.blit(ov, (0, by))
            dtxt(sc, "||  PAUSED", (sw//2, by+bh//2), self._F["lg"], TEXT, anchor="center")

    def _draw_top(self, sc, sw):
        F = self._F; mouse = pygame.mouse.get_pos()
        pygame.draw.rect(sc, PANEL, (0,0,sw,TOP_H))
        pygame.draw.rect(sc, BORDER, (0,TOP_H-1,sw,1))
        x = 20; cy = TOP_H//2
        r = dtxt(sc,"* SORT",(x,cy),F["lg"],ACCENT,anchor="midleft"); x+=r.w+12
        r = dtxt(sc,self.algo.upper(),(x,cy),F["md"],TEXT,anchor="midleft"); x+=r.w+10
        bw2 = F["xs"].size(f" {self.speed} ")[0]+10
        drect(sc, BTN_BG, (x,cy-10,bw2,20), radius=3)
        dtxt(sc, self.speed, (x+bw2//2,cy), F["xs"], SPD_TINT[self.speed], anchor="center")
        t_str  = f"{self._get_elapsed():.4f} s"
        fps_str = f"{self._fps:.0f} fps"
        dtxt(sc, t_str,   (sw-58,cy), F["md"], ACCENT2, anchor="midright")
        dtxt(sc, fps_str, (sw-58-F["md"].size(t_str)[0]-14,cy), F["xs"], SUBTEXT, anchor="midright")
        xr = pygame.Rect(sw-50,10,40,TOP_H-20)
        if xr.collidepoint(mouse): drect(sc,(60,20,20),xr,radius=4)
        dtxt(sc,"X",(xr.centerx,xr.centery),F["lg"],
             ACCENT3 if xr.collidepoint(mouse) else SUBTEXT,anchor="center")
        self._rects["x"] = xr

    def _draw_strip(self, sc, sw):
        F = self._F; y = TOP_H
        pygame.draw.rect(sc, PANEL, (0,y,sw,STRIP_H))
        pygame.draw.rect(sc, BORDER, (0,y+STRIP_H-1,sw,1))
        cy = y+STRIP_H//2; x = 20
        for text, color in [(f"comparisons  {self.compare_count:,}",ACCENT2),
                             (f"swaps  {self.swap_count:,}",ACCENT3),
                             (f"partitions  {self.partition_count:,}",PARTITION_CLR)]:
            r = dtxt(sc, text, (x,cy), F["xs"], color, anchor="midleft"); x += r.w+8
            if x < sw-340: dtxt(sc,"·",(x,cy),F["xs"],BORDER,anchor="midleft"); x+=10
        if self._phase and self._state == ST_RUNNING:
            dtxt(sc, f"phase: {self._phase}", (sw-8,cy), F["xs"], PARTITION_CLR, anchor="midright")
        else:
            dtxt(sc,"H=hud  M=mute  Space=pause  R=restart  S=step  +/-=speed  I=panel  F11=full",
                 (sw-8,cy), F["xs"], BORDER, anchor="midright")

    def _draw_bottom(self, sc, sw, sh):
        F = self._F; mouse = pygame.mouse.get_pos()
        by = sh-BOT_H
        pygame.draw.rect(sc, BORDER, (0,by,sw,1))
        pygame.draw.rect(sc, PANEL,  (0,by+1,sw,BOT_H))
        cy = by+BOT_H//2

        # Legend (cached)
        if self._legend_surf is None:
            items = [(ACCENT,"idle"),(ACCENT2,"compare"),(ACCENT3,"swap"),
                     (PARTITION_CLR,"partition"),(SORTED_CLR,"sorted")]
            lh=BOT_H-4; lw=0
            for col,lbl in items: lw += 10+4+F["xs"].size(lbl)[0]+12
            surf = pygame.Surface((lw,lh), pygame.SRCALPHA)
            lx=0; lcy=lh//2
            for col,lbl in items:
                pygame.draw.rect(surf,col,(lx,lcy-5,10,10)); lx+=14
                r2=dtxt(surf,lbl,(lx,lcy),F["xs"],SUBTEXT,anchor="midleft"); lx+=r2.w+12
            self._legend_surf=surf; self._legend_w=lx
        sc.blit(self._legend_surf, (12, by+2))
        x = 12+self._legend_w+4

        # Sound toggle
        snd_r = pygame.Rect(x, cy-12, 28, 24)
        drect(sc, BTN_HOVER if snd_r.collidepoint(mouse) else BTN_BG, snd_r, radius=4)
        dtxt(sc, ("S+" if self._sound_on else "S-"), (snd_r.centerx,snd_r.centery), F["xs"],
             TEXT if self._sound_on else SUBTEXT, anchor="center")
        self._rects["sound"] = snd_r; x += 32

        # Volume slider
        vol_r = pygame.Rect(x, cy-4, 68, 8)
        drect(sc, BTN_BG, vol_r, radius=4)
        fw = int(vol_r.w*self._volume)
        if fw>0: pygame.draw.rect(sc,ACCENT,(vol_r.x,vol_r.y,fw,vol_r.h),border_radius=4)
        hcol = ACCENT2 if vol_r.inflate(0,18).collidepoint(mouse) else ACCENT
        pygame.draw.circle(sc, hcol, (vol_r.x+fw, vol_r.centery), 6)
        self._rects["vol"] = vol_r; x += 76

        # Shuffle modes
        x += 6
        dtxt(sc, "mode:", (x, cy), F["xs"], SUBTEXT, anchor="midleft"); x += F["xs"].size("mode:")[0]+4
        for mode in SHUFFLE_MODES:
            mw = F["xs"].size(mode)[0]+14
            mr = pygame.Rect(x, cy-11, mw, 22)
            is_sel = mode == self._shuffle_mode
            is_hov = mr.collidepoint(mouse)
            drect(sc, ACCENT if is_sel else (BTN_HOVER if is_hov else BTN_BG), mr, radius=3)
            dtxt(sc, mode, (mr.centerx,mr.centery), F["xs"],
                 (255,255,255) if is_sel else SUBTEXT, anchor="center")
            self._rects[f"shuf_{mode}"] = mr; x += mw+3

        # Right side buttons
        rx = sw-8
        for key, label, mbg, mfg in [("restart","RESTART",BTN_BG,TEXT),
                                       ("step","STEP",BTN_BG,ACCENT2)]:
            bw3 = F["sm"].size(label)[0]+20
            r   = pygame.Rect(rx-bw3, cy-14, bw3, 28)
            drect(sc, BTN_HOVER if r.collidepoint(mouse) else mbg, r, radius=4)
            dtxt(sc, label, (r.centerx,r.centery), F["sm"],
                 ACCENT if (r.collidepoint(mouse) and mfg==TEXT) else mfg, anchor="center")
            self._rects[key]=r; rx -= bw3+4

        albl,abg,afg = self._action_info()
        aw = F["sm"].size(albl)[0]+24
        ar = pygame.Rect(rx-aw, cy-14, aw, 28)
        abghov = tuple(min(255,v+18) for v in abg) if ar.collidepoint(mouse) else abg
        drect(sc, abghov, ar, radius=4)
        dtxt(sc, albl, (ar.centerx,ar.centery), F["sm"], afg, anchor="center")
        self._rects["action"]=ar; rx -= aw+10

        pygame.draw.rect(sc,BORDER,(rx,cy-12,1,24)); rx -= 12

        for spd in reversed(SPD_ORDER):
            bw4 = F["xs"].size(spd)[0]+14
            r   = pygame.Rect(rx-bw4, cy-11, bw4, 22)
            is_act=spd==self.speed; is_hov=r.collidepoint(mouse)
            drect(sc, ACCENT if is_act else (BTN_HOVER if is_hov else BTN_BG), r, radius=3)
            dtxt(sc, spd, (r.centerx,r.centery), F["xs"],
                 (255,255,255) if is_act else SPD_TINT[spd], anchor="center")
            self._rects[f"spd_{spd}"]=r; rx -= bw4+3
        dtxt(sc,"speed:",(rx-4,cy),F["xs"],SUBTEXT,anchor="midright")

    def _draw_panel(self, sc, sh):
        px = int(self._panel_x)
        if px <= -PANEL_W: return
        old = sc.get_clip()
        sc.set_clip((max(0,px), 0, PANEL_W+min(0,px), sh))
        pygame.draw.rect(sc, PANEL, (px,0,PANEL_W,sh))
        pygame.draw.rect(sc, BORDER, (px+PANEL_W-1,0,1,sh))
        self._draw_panel_content(sc, px, sh)
        sc.set_clip(old)

    def _draw_panel_content(self, sc, px, sh):
        F = self._F; info = ALGO_INFO.get(self.algo, {})
        x = px+18; y = 18; wrap_w = PANEL_W-40

        def line(text, color, fk="xs", indent=0):
            nonlocal y
            words = str(text).split(); ln = ""
            for w in words:
                t2 = (ln+" "+w).strip()
                if F[fk].size(t2)[0] > wrap_w-indent:
                    if ln: dtxt(sc,ln,(x+indent,y),F[fk],color); y+=F[fk].get_height()+4
                    ln=w
                else: ln=t2
            if ln: dtxt(sc,ln,(x+indent,y),F[fk],color)
            y += F[fk].get_height()+8

        def section(label):
            nonlocal y
            dtxt(sc,label,(x,y),F["xs"],SUBTEXT); y+=F["xs"].get_height()+6

        def sep():
            nonlocal y; y+=6
            pygame.draw.rect(sc,BORDER,(x,y,wrap_w,1)); y+=14

        def kv(label, val, vc, lw=100):
            nonlocal y
            dtxt(sc,label,(x+4,y),F["xs"],SUBTEXT)
            dtxt(sc,str(val),(x+4+lw,y),F["xs"],vc)
            y += F["xs"].get_height()+7

        dtxt(sc,self.algo.upper(),(x,y),F["md"],ACCENT); y+=F["md"].get_height()+8
        sep()
        section("LIVE")
        kv("comparisons:",  self.compare_count,    ACCENT2)
        kv("swaps/writes:", self.swap_count,        ACCENT3)
        kv("partitions:",   self.partition_count,   PARTITION_CLR)
        if self._phase:
            kv("phase:", self._phase, PARTITION_CLR, lw=52)
        sep()
        section("COMPLEXITY")
        kv("Best:",    info.get("best","-"),  SORTED_CLR, lw=76)
        kv("Average:", info.get("avg","-"),   ACCENT2,    lw=76)
        kv("Worst:",   info.get("worst","-"), ACCENT3,    lw=76)
        kv("Space:",   info.get("space","-"), SUBTEXT,    lw=76)
        sep()
        stable = info.get("stable")
        if stable is not None:
            kv("Stability:", "Stable" if stable else "Unstable",
               SORTED_CLR if stable else ACCENT3, lw=88)
        ap = info.get("approach","")
        if ap:
            section("Approach:"); line(ap, TEXT, indent=8)
        sep()
        snippet = info.get("snippet","")
        if snippet and y < sh-170:
            section("CORE LOGIC")
            cl = snippet.split("\n"); lh=F["xx"].get_height()+3; ch=len(cl)*lh+14
            pygame.draw.rect(sc,BTN_BG,(x,y,wrap_w,ch),border_radius=4)
            cy2=y+7
            for ln in cl: dtxt(sc,ln,(x+8,cy2),F["xx"],ACCENT2); cy2+=lh
            y=cy2+10; sep()
        fact=info.get("fact","")
        if fact and y < sh-50:
            section("FUN FACT"); line(fact,SUBTEXT)

    def _draw_panel_tab(self, sc, sh):
        px=int(self._panel_x); tx=max(0,px+PANEL_W); ty=sh//2-26
        tab=pygame.Rect(tx,ty,18,52); mouse=pygame.mouse.get_pos()
        drect(sc, BTN_HOVER if tab.collidepoint(mouse) else BTN_BG, tab, radius=3)
        dtxt(sc,"<" if self._panel_open else ">",(tab.centerx,tab.centery),
             self._F["sm"],ACCENT if tab.collidepoint(mouse) else SUBTEXT,anchor="center")
        self._rects["ptab"]=tab

    # ── Geometry ──────────────────────────────────────────────────────────────
    def _bar_dims(self, sw=None):
        if sw is None: sw=self._screen.get_width()
        n=max(len(self.values),1)
        gap=max(0, min(4,(sw-n)//n//3))
        bw=max(1,(sw-gap*(n+1))//n)
        x0=(sw-(bw+gap)*n-gap)//2+gap
        return bw, gap, x0

    # ── UI helpers ────────────────────────────────────────────────────────────
    def _action_info(self):
        if self._state==ST_IDLE:    return "START",  SORTED_CLR, BG
        if self._state==ST_DONE:    return "SORTED", BTN_BG,     SORTED_CLR
        if self._state==ST_PAUSED:  return "RESUME", ACCENT,     (255,255,255)
        if self._step_waiting:      return "RESUME", ACCENT,     (255,255,255)
        return "PAUSE", ACCENT2, BG

    def _get_elapsed(self):
        if self._state!=ST_RUNNING: return self._elapsed_base
        return self._elapsed_base+(time.time()-self._segment_start)

    def _toggle_hud(self):    self._hud_visible  = not self._hud_visible
    def _toggle_panel(self):
        self._panel_open   = not self._panel_open
        self._panel_target = 0.0 if self._panel_open else float(-PANEL_W)
    def _toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        if self._fullscreen:
            self._screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        else:
            self._screen = pygame.display.set_mode(
                (920,640), pygame.RESIZABLE|pygame.DOUBLEBUF|pygame.HWSURFACE, vsync=1
            )
        self._force_redraw()
    def _toggle_sound(self):  self._sound_on = not self._sound_on
    def _vol_from_mouse(self, pos):
        vr=self._rects.get("vol")
        if vr: self._volume=max(0., min(1.,(pos[0]-vr.x)/max(1,vr.w)))
    def _cycle_speed(self, d):
        idx=SPD_ORDER.index(self.speed)
        self.speed=SPD_ORDER[max(0,min(len(SPD_ORDER)-1,idx+d))]

    # ── Lifecycle ─────────────────────────────────────────────────────────────
    def _shuffle(self):
        self._gen=None; self._state=ST_IDLE; self._phase=""
        n=self.num_values; hi=max(n*2,200)
        if self._shuffle_mode=="RND":
            self.values=random.sample(range(1,hi+1), min(n,hi))
        elif self._shuffle_mode=="REV":
            self.values=list(range(hi,hi-n,-1))
        else:  # ASC
            step=max(1,hi//n)
            self.values=[1+i*step for i in range(n)]
        self.x_offsets       = [0.0]*n
        self.colors          = [ACCENT]*n
        self.compare_count   = 0
        self.swap_count      = 0
        self.partition_count = 0
        self._partition_set.clear()
        self._elapsed_base   = 0.0
        self._segment_start  = 0.0
        self._step_mode      = False
        self._step_waiting   = False
        self._build_note_map()

    def _on_action(self):
        if self._step_waiting:
            self._step_mode=False; self._step_waiting=False; return
        if self._state==ST_IDLE:      self._do_start()
        elif self._state==ST_RUNNING: self._do_pause()
        elif self._state==ST_PAUSED:  self._do_resume()

    def _do_start(self):
        self._state=ST_RUNNING
        self.compare_count=0; self.swap_count=0; self.partition_count=0
        self.x_offsets=[0.0]*len(self.values)
        self.colors=[ACCENT]*len(self.values)
        self._elapsed_base=0.0; self._segment_start=time.time()
        self._gen=self._make_gen()

    def _do_pause(self):
        self._elapsed_base+=time.time()-self._segment_start
        self._state=ST_PAUSED

    def _do_resume(self):
        self._segment_start=time.time(); self._state=ST_RUNNING

    def _do_step(self):
        if self._state==ST_DONE: return
        if self._state==ST_IDLE:
            self._step_mode=True; self._do_start(); return
        if self._state==ST_PAUSED:
            self._step_mode=True; self._do_resume(); return
        if not self._step_mode:
            self._step_mode=True; return
        self._step_waiting=False

    def _on_sort_done(self):
        self._elapsed_base=self._get_elapsed(); self._phase=""
        self._state=ST_DONE; self._step_mode=False; self._step_waiting=False

    def _make_gen(self):
        return {
            "Bubble Sort":          self._bubble_gen,
            "Insertion Sort":       self._insertion_gen,
            "Selection Sort":       self._selection_gen,
            "Merge Sort":           self._merge_start_gen,
            "Cocktail Shaker Sort": self._cocktail_gen,
            "Bucket Sort":          self._bucket_gen,
            "Shell Sort":           self._shell_gen,
            "Radix Sort":           self._radix_gen,
            "Quick Sort":           self._quick_start_gen,
            "Gnome Sort":           self._gnome_gen,
            "Heap Sort":            self._heap_gen,
            "Comb Sort":            self._comb_gen,
            "Counting Sort":        self._counting_gen,
            "Pancake Sort":         self._pancake_gen,
            "Tim Sort":             self._tim_gen,
            "Cycle Sort":           self._cycle_gen,
            "Odd-Even Sort":        self._odd_even_gen,
            "Bogosort":             self._bogo_gen,
            "Bitonic Sort":         self._bitonic_gen,
            "Sleep Sort":           self._sleep_gen,
            "Stooge Sort":          self._stooge_start_gen,
            "Tree Sort":            self._tree_gen,
        }.get(self.algo, self._bubble_gen)()

    # ── Sound ─────────────────────────────────────────────────────────────────
    def _build_note_map(self):
        if not self.values: self._note_map={}; return
        sv=sorted(set(self.values)); nn=len(self._all_notes); nv=len(sv)
        self._note_map={v:int(r/max(nv-1,1)*(nn-1)) for r,v in enumerate(sv)}

    def _play_val(self, val, vol=0.65, notes=None):
        if not (_SND and self._sound_on and self.speed!="max"): return
        if self._state==ST_PAUSED: return
        idx=self._note_map.get(val)
        if idx is None: return
        src=notes if notes else self._all_notes
        snd=src[idx] if 0<=idx<len(src) else None
        if not snd: return
        try:
            ch=pygame.mixer.find_channel(True)
            if ch: ch.set_volume(min(1.0,vol*self._volume)); ch.play(snd)
        except Exception: pass

    # ── Generator primitives ──────────────────────────────────────────────────
    def _rc(self, i):
        """Restore color after highlight"""
        return PARTITION_CLR if i in self._partition_set else ACCENT

    def _eff_f(self, base):
        """Scale frame count for large arrays."""
        n=len(self.values)
        if n>300: return max(0,base//4)
        if n>150: return max(1,base//2)
        return base

    def _compare_gen(self, i, j):
        self.compare_count+=1
        cmp_f=self._eff_f(SPEEDS[self.speed]["cmp_f"])
        self._play_val(self.values[i], 0.13)
        if cmp_f>0:
            self.colors[i]=ACCENT2
            if i!=j: self.colors[j]=ACCENT2
            for _ in range(cmp_f): yield None
            if not self._step_mode:
                self.colors[i]=self._rc(i)
                if i!=j: self.colors[j]=self._rc(j)
        yield STEP_PT
        if self._step_mode:
            self.colors[i]=self._rc(i)
            if i!=j: self.colors[j]=self._rc(j)

    def _swap_gen(self, arr, i, j):
        self.swap_count+=1
        swp_f=self._eff_f(SPEEDS[self.speed]["swp_f"])
        self._play_val(arr[i],0.68); self._play_val(arr[j],0.68)
        if swp_f>0:
            bw,gap,_=self._bar_dims(self._screen.get_width())
            dist=(j-i)*(bw+gap)
            self.colors[i]=ACCENT3; self.colors[j]=ACCENT3
            for f in range(1,swp_f+1):
                t=f/swp_f; ease=t*t*(3-2*t)
                self.x_offsets[i]=dist*ease; self.x_offsets[j]=-dist*ease
                yield None
            self.x_offsets[i]=0.0; self.x_offsets[j]=0.0
        arr[i],arr[j]=arr[j],arr[i]
        self.colors[i]=self._rc(i); self.colors[j]=self._rc(j)
        yield STEP_PT

    def _write_gen(self, arr, k, val, color=None):
        self.swap_count+=1; arr[k]=val
        cmp_f=self._eff_f(SPEEDS[self.speed]["cmp_f"])
        self._play_val(val,0.55)
        if cmp_f>0:
            self.colors[k]=color if color else ACCENT3
            for _ in range(max(1,cmp_f*3//5)): yield None
            if not self._step_mode: self.colors[k]=self._rc(k)
        yield STEP_PT
        if self._step_mode: self.colors[k]=self._rc(k)

    def _finish_gen(self):
        self._phase="Sorted!"
        sp=SPEEDS[self.speed]
        delay=max(1,self._eff_f(sp["cmp_f"])//2) if not sp["is_max"] else 1
        for i in range(len(self.values)):
            self.colors[i]=SORTED_CLR
            self._play_val(self.values[i],0.88,notes=self._sweep_notes)
            for _ in range(delay): yield None

    # ══════════════════════════════════════════════════════════════════════════
    #  SORT GENERATORS
    # ══════════════════════════════════════════════════════════════════════════
    def _bubble_gen(self):
        arr=self.values; n=len(arr)
        for i in range(n):
            self._phase=f"Pass {i+1}/{n}"
            for j in range(n-i-1):
                yield from self._compare_gen(j,j+1)
                if arr[j]>arr[j+1]: yield from self._swap_gen(arr,j,j+1)
        yield from self._finish_gen()

    def _insertion_gen(self):
        arr=self.values; n=len(arr)
        for i in range(1,n):
            self._phase=f"Inserting {i}/{n-1}"
            key=arr[i]; j=i-1
            yield from self._compare_gen(i,max(0,j))
            while j>=0 and arr[j]>key:
                yield from self._write_gen(arr,j+1,arr[j],ACCENT3); j-=1
            yield from self._write_gen(arr,j+1,key,ACCENT2)
        yield from self._finish_gen()

    def _selection_gen(self):
        arr=self.values; n=len(arr)
        for i in range(n):
            self._phase=f"Finding min {i+1}/{n}"
            mi=i
            for j in range(i+1,n):
                yield from self._compare_gen(mi,j)
                if arr[j]<arr[mi]: mi=j
            if mi!=i: yield from self._swap_gen(arr,i,mi)
        yield from self._finish_gen()

    def _merge_start_gen(self):
        self._phase="Splitting"
        yield from self._merge_sort_gen(self.values,0,len(self.values)-1)
        yield from self._finish_gen()

    def _merge_sort_gen(self,arr,l,r):
        if l>=r: return
        m=(l+r)//2
        yield from self._merge_sort_gen(arr,l,m)
        yield from self._merge_sort_gen(arr,m+1,r)
        self._phase=f"Merging [{l}..{r}]"
        yield from self._merge_gen(arr,l,m,r)

    def _merge_gen(self,arr,l,m,r):
        L=arr[l:m+1]; R=arr[m+1:r+1]; i=j=0; k=l
        while i<len(L) and j<len(R):
            yield from self._compare_gen(l+i,m+1+j)
            if L[i]<=R[j]: yield from self._write_gen(arr,k,L[i]); i+=1
            else:           yield from self._write_gen(arr,k,R[j]); j+=1
            k+=1
        for v in L[i:]: yield from self._write_gen(arr,k,v); k+=1
        for v in R[j:]: yield from self._write_gen(arr,k,v); k+=1

    def _cocktail_gen(self):
        arr=self.values; n=len(arr); lo=0; hi=n-1
        while lo<hi:
            sw2=False
            self._phase=f"Forward pass"
            for i in range(lo,hi):
                yield from self._compare_gen(i,i+1)
                if arr[i]>arr[i+1]: yield from self._swap_gen(arr,i,i+1); sw2=True
            hi-=1
            if not sw2: break
            sw2=False
            self._phase=f"Backward pass"
            for i in range(hi,lo,-1):
                yield from self._compare_gen(i,i-1)
                if arr[i]<arr[i-1]: yield from self._swap_gen(arr,i-1,i); sw2=True
            lo+=1
            if not sw2: break
        yield from self._finish_gen()

    def _bucket_gen(self):
        arr=self.values; n=len(arr)
        mn,mx=min(arr),max(arr); bc=max(4,n//3); rng=mx-mn+1
        bkts=[[] for _ in range(bc)]
        self._phase="Distributing"
        for idx,v in enumerate(arr):
            bkts[min(int((v-mn)/rng*bc),bc-1)].append(v)
            yield from self._compare_gen(idx,idx)
        self._phase="Sorting buckets"
        out=0
        for bkt in bkts:
            for i in range(1,len(bkt)):
                key=bkt[i]; j=i-1
                while j>=0 and bkt[j]>key: bkt[j+1]=bkt[j]; j-=1
                bkt[j+1]=key
            for v in bkt: yield from self._write_gen(arr,out,v); out+=1
        yield from self._finish_gen()

    def _shell_gen(self):
        arr=self.values; n=len(arr); gap=n//2
        while gap>0:
            self._phase=f"Gap = {gap}"
            for i in range(gap,n):
                temp=arr[i]; j=i
                yield from self._compare_gen(j,j-gap)
                while j>=gap and arr[j-gap]>temp:
                    yield from self._write_gen(arr,j,arr[j-gap],ACCENT3); j-=gap
                yield from self._write_gen(arr,j,temp,ACCENT2)
            gap//=2
        yield from self._finish_gen()

    def _radix_gen(self):
        arr=self.values; n=len(arr); exp=1; pass_n=0
        while max(arr)//exp>0:
            pass_n+=1; self._phase=f"Digit pass {pass_n} (exp={exp})"
            out=[0]*n; cnt=[0]*10
            for i,v in enumerate(arr):
                cnt[(v//exp)%10]+=1; yield from self._compare_gen(i,i)
            for i in range(1,10): cnt[i]+=cnt[i-1]
            for i in range(n-1,-1,-1):
                d=(arr[i]//exp)%10; out[cnt[d]-1]=arr[i]; cnt[d]-=1
            for i in range(n): yield from self._write_gen(arr,i,out[i])
            exp*=10
        yield from self._finish_gen()

    def _quick_start_gen(self):
        yield from self._quick_gen(self.values,0,len(self.values)-1)
        yield from self._finish_gen()

    def _quick_gen(self,arr,lo,hi):
        if lo>=hi: return
        yield from self._partition_gen(arr,lo,hi)
        pi=self._piv
        yield from self._quick_gen(arr,lo,pi-1)
        yield from self._quick_gen(arr,pi+1,hi)

    def _partition_gen(self,arr,lo,hi):
        self.partition_count+=1
        self._phase=f"Partitioning [{lo}..{hi}]"
        pivot=arr[hi]; i=lo-1
        for k in range(lo,hi+1):
            if 0<=k<len(self.colors):
                self.colors[k]=PARTITION_CLR; self._partition_set.add(k)
        yield None
        for j in range(lo,hi):
            yield from self._compare_gen(j,hi)
            if arr[j]<=pivot: i+=1; yield from self._swap_gen(arr,i,j)
        yield from self._swap_gen(arr,i+1,hi)
        for k in range(lo,hi+1):
            self._partition_set.discard(k)
            if 0<=k<len(self.colors) and self.colors[k]!=SORTED_CLR:
                self.colors[k]=ACCENT
        # Pivot is in final position — use a distinct highlight, not SORTED_CLR
        pp=i+1
        if 0<=pp<len(self.colors): self.colors[pp]=ACCENT2
        self._piv=pp; yield STEP_PT
        if 0<=pp<len(self.colors): self.colors[pp]=ACCENT

    def _gnome_gen(self):
        arr=self.values; n=len(arr); i=1
        while i<n:
            yield from self._compare_gen(i,i-1)
            if arr[i]>=arr[i-1]: i+=1
            else:
                yield from self._swap_gen(arr,i-1,i)
                if i>1: i-=1
        yield from self._finish_gen()

    # ── Heap Sort ─────────────────────────────────────────────────────────────
    def _heap_gen(self):
        arr=self.values; n=len(arr)
        self._phase="Building max-heap"
        for i in range(n//2-1,-1,-1):
            yield from self._heapify_gen(arr,n,i)
        self._phase="Extracting elements"
        for i in range(n-1,0,-1):
            yield from self._swap_gen(arr,0,i)
            yield from self._heapify_gen(arr,i,0)
        yield from self._finish_gen()

    def _heapify_gen(self,arr,n,i):
        largest=i; l=2*i+1; r=2*i+2
        if l<n:
            yield from self._compare_gen(l,largest)
            if arr[l]>arr[largest]: largest=l
        if r<n:
            yield from self._compare_gen(r,largest)
            if arr[r]>arr[largest]: largest=r
        if largest!=i:
            yield from self._swap_gen(arr,i,largest)
            yield from self._heapify_gen(arr,n,largest)

    # ── Comb Sort ─────────────────────────────────────────────────────────────
    def _comb_gen(self):
        arr=self.values; n=len(arr); gap=n; shrink=1.3; sorted_=False
        while not sorted_:
            gap=max(1,int(gap/shrink))
            if gap==1: sorted_=True
            self._phase=f"Gap = {gap}"
            i=0
            while i+gap<n:
                yield from self._compare_gen(i,i+gap)
                if arr[i]>arr[i+gap]:
                    yield from self._swap_gen(arr,i,i+gap); sorted_=False
                i+=1
        yield from self._finish_gen()

    # ── Counting Sort ─────────────────────────────────────────────────────────
    def _counting_gen(self):
        arr=self.values; n=len(arr)
        mn,mx=min(arr),max(arr); k=mx-mn+1
        self._phase="Counting frequencies"
        cnt=[0]*k
        for i in range(n):
            cnt[arr[i]-mn]+=1
            yield from self._compare_gen(i,i)
        self._phase="Computing prefix sums"
        for i in range(1,k): cnt[i]+=cnt[i-1]
        out=[0]*n
        for i in range(n-1,-1,-1):
            out[cnt[arr[i]-mn]-1]=arr[i]; cnt[arr[i]-mn]-=1
        self._phase="Reconstructing array"
        for i in range(n): yield from self._write_gen(arr,i,out[i])
        yield from self._finish_gen()

    # ── Pancake Sort ──────────────────────────────────────────────────────────
    def _pancake_gen(self):
        arr=self.values; n=len(arr)
        for size in range(n,1,-1):
            self._phase=f"Finding max in [0..{size-1}]"
            mi=0
            for i in range(1,size):
                yield from self._compare_gen(i,mi)
                if arr[i]>arr[mi]: mi=i
            if mi==size-1: continue
            if mi!=0:
                self._phase=f"Flip 0..{mi}"
                yield from self._flip_gen(arr,0,mi)
            self._phase=f"Flip 0..{size-1}"
            yield from self._flip_gen(arr,0,size-1)
        yield from self._finish_gen()

    def _flip_gen(self,arr,l,r):
        while l<r:
            yield from self._swap_gen(arr,l,r); l+=1; r-=1

    # ── Tim Sort ──────────────────────────────────────────────────────────────
    def _tim_gen(self):
        arr=self.values; n=len(arr)
        RUN=max(8,min(32,n//8))
        self._phase=f"Sorting runs (size={RUN})"
        for start in range(0,n,RUN):
            end=min(start+RUN,n)
            yield from self._tim_insertion_gen(arr,start,end)
        self._phase="Merging runs"
        size=RUN
        while size<n:
            for start in range(0,n,size*2):
                mid=min(start+size,n)
                end=min(start+size*2,n)
                if mid<end:
                    yield from self._merge_gen(arr,start,mid-1,end-1)
            size*=2
        yield from self._finish_gen()

    def _tim_insertion_gen(self,arr,lo,hi):
        for i in range(lo+1,hi):
            key=arr[i]; j=i-1
            yield from self._compare_gen(i,max(lo,j))
            while j>=lo and arr[j]>key:
                yield from self._write_gen(arr,j+1,arr[j],ACCENT3); j-=1
            yield from self._write_gen(arr,j+1,key,ACCENT2)

    # ── Cycle Sort ────────────────────────────────────────────────────────────
    def _cycle_gen(self):
        arr=self.values; n=len(arr)
        for cs in range(n-1):
            self._phase=f"Cycle from {cs}"
            item=arr[cs]; pos=cs
            for i in range(cs+1,n):
                yield from self._compare_gen(cs,i)
                if arr[i]<item: pos+=1
            if pos==cs: continue
            while item==arr[pos]: pos+=1
            old=arr[pos]
            yield from self._write_gen(arr,pos,item)
            item=old
            while pos!=cs:
                pos=cs
                for i in range(cs+1,n):
                    yield from self._compare_gen(cs,i)
                    if arr[i]<item: pos+=1
                while item==arr[pos]: pos+=1
                old=arr[pos]
                yield from self._write_gen(arr,pos,item)
                item=old
        yield from self._finish_gen()

    # ── Odd-Even Sort ─────────────────────────────────────────────────────────
    def _odd_even_gen(self):
        arr=self.values; n=len(arr); sorted_=False
        while not sorted_:
            sorted_=True
            self._phase="Even phase"
            for i in range(0,n-1,2):
                yield from self._compare_gen(i,i+1)
                if arr[i]>arr[i+1]: yield from self._swap_gen(arr,i,i+1); sorted_=False
            self._phase="Odd phase"
            for i in range(1,n-1,2):
                yield from self._compare_gen(i,i+1)
                if arr[i]>arr[i+1]: yield from self._swap_gen(arr,i,i+1); sorted_=False
        yield from self._finish_gen()

    # ── Bogosort ──────────────────────────────────────────────────────────────
    def _bogo_gen(self):
        arr=self.values; n=len(arr); attempt=0
        while True:
            attempt+=1; self._phase=f"Check #{attempt}"
            ok=True
            for i in range(n-1):
                yield from self._compare_gen(i,i+1)
                if arr[i]>arr[i+1]: ok=False; break
            if ok: break
            self._phase=f"Shuffle #{attempt}"
            for i in range(n-1,0,-1):
                j=random.randint(0,i)
                yield from self._swap_gen(arr,i,j)
        yield from self._finish_gen()

    # ── Bitonic Sort ──────────────────────────────────────────────────────────
    def _bitonic_gen(self):
        arr=self.values; n=len(arr)
        # Next power of 2 >= n
        p=1
        while p<n: p<<=1
        self._phase="Building bitonic network"
        k=2
        while k<=p:
            j=k>>1
            self._phase=f"Network step k={k}"
            while j>0:
                for i in range(p):
                    ij=i^j
                    if ij>i and i<n and ij<n:
                        asc=(i&k)==0
                        yield from self._compare_gen(i,ij)
                        if (arr[i]>arr[ij])==asc:
                            yield from self._swap_gen(arr,i,ij)
                j>>=1
            k<<=1
        yield from self._finish_gen()

    # ── Sleep Sort ────────────────────────────────────────────────────────────
    def _sleep_gen(self):
        arr=self.values; n=len(arr); mx=max(arr)
        self._phase="All threads sleeping..."
        # Highlight all bars as "sleeping"
        for i in range(n): self.colors[i]=PARTITION_CLR
        yield None
        # Sort by value (smaller values "wake" first)
        events=sorted(range(n),key=lambda i:arr[i])
        prev_val=0; out_idx=0
        cmp_f=SPEEDS[self.speed]["cmp_f"]
        for orig_idx in events:
            val=arr[orig_idx]
            self._phase=f"Thread waking: val={val}"
            gap=val-prev_val
            delay=max(1,min(int(gap*max(1,cmp_f)/max(1,mx//8)),20))
            self.colors[orig_idx]=ACCENT2
            for _ in range(delay): yield None
            yield from self._write_gen(arr,out_idx,val)
            prev_val=val; out_idx+=1
        yield from self._finish_gen()

    # ── Stooge Sort ───────────────────────────────────────────────────────────
    def _stooge_start_gen(self):
        self._phase="Sorting in thirds"
        yield from self._stooge_gen(self.values,0,len(self.values)-1)
        yield from self._finish_gen()

    def _stooge_gen(self,arr,lo,hi):
        yield from self._compare_gen(lo,hi)
        if arr[lo]>arr[hi]: yield from self._swap_gen(arr,lo,hi)
        if hi-lo+1>2:
            t=(hi-lo+1)//3
            self._phase=f"First 2/3 [{lo}..{hi-t}]"
            yield from self._stooge_gen(arr,lo,hi-t)
            self._phase=f"Last 2/3 [{lo+t}..{hi}]"
            yield from self._stooge_gen(arr,lo+t,hi)
            self._phase=f"First 2/3 again [{lo}..{hi-t}]"
            yield from self._stooge_gen(arr,lo,hi-t)

    # ── Tree Sort ─────────────────────────────────────────────────────────────
    def _tree_gen(self):
        arr=self.values; n=len(arr)

        class Node:
            __slots__=("v","l","r")
            def __init__(self,v): self.v=v; self.l=self.r=None

        def insert(node,v):
            if node is None: return Node(v)
            if v<node.v: node.l=insert(node.l,v)
            else:        node.r=insert(node.r,v)
            return node

        def inorder(node,out):
            if node: inorder(node.l,out); out.append(node.v); inorder(node.r,out)

        self._phase="Building BST"
        root=None
        for i in range(n):
            root=insert(root,arr[i])
            yield from self._compare_gen(i,i)

        self._phase="In-order traversal"
        result=[]
        inorder(root,result)
        for i,val in enumerate(result):
            yield from self._write_gen(arr,i,val)
        yield from self._finish_gen()

# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def main():
    pygame.init()
    if _SND: pygame.mixer.init()
    while True:
        result=SelectionScreen().run()
        if result is None: break
        algo,count=result
        viz=SortVisualizer(algo,count)
        ret=viz.run()
        if ret=="quit": break
    pygame.quit(); sys.exit()

if __name__=="__main__":
    main()
