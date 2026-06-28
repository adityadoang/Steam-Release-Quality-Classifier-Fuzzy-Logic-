import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# 1. New Antecedents/Consequents
bug_density = ctrl.Antecedent(np.arange(0, 101, 1),       'bug_density')   # 0-100 bug per 1000 lines
fps         = ctrl.Antecedent(np.arange(0, 121, 1),       'fps')           # 0-120 FPS
wishlist    = ctrl.Antecedent(np.arange(0, 2000001, 1000), 'wishlist')      # 0-2,000,000 wishlists
budget      = ctrl.Antecedent(np.arange(0, 101, 1),       'budget')        # 0-100 % sisa budget

release_quality = ctrl.Consequent(np.arange(0, 101, 1), 'release_quality')

# 2. Membership functions
# Bug Density (per 1000 lines of code): Sangat Bersih (0-5), Wajar (5-30), Rusak (>25)
bug_density['sangat_bersih'] = fuzz.trapmf(bug_density.universe, [0,  0,  5, 15])
bug_density['wajar']         = fuzz.trapmf(bug_density.universe, [10, 20, 35, 50])
bug_density['rusak']         = fuzz.trapmf(bug_density.universe, [40, 60, 100, 100])

# FPS: Patah-patah (0-25), Stabil 30fps (25-50), Lancar 60fps+ (>50)
fps['patah_patah'] = fuzz.trapmf(fps.universe, [0,  0,  20, 30])
fps['stabil']      = fuzz.trapmf(fps.universe, [20, 30, 45, 55])
fps['lancar']      = fuzz.trapmf(fps.universe, [45, 60, 120, 120])

# Wishlist Count: Sedikit (<50K), Menjanjikan (50K-500K), Meledak (>400K)
wishlist['sedikit']     = fuzz.trapmf(wishlist.universe, [0,       0,      50000,  150000])
wishlist['menjanjikan'] = fuzz.trapmf(wishlist.universe, [100000,  250000, 500000, 700000])
wishlist['meledak']     = fuzz.trapmf(wishlist.universe, [500000,  800000, 2000000, 2000000])

# Production Cost / Remaining Budget (%): Kritis (0-10), Aman (10-40), Melimpah (>40)
budget['kritis'] = fuzz.trapmf(budget.universe, [0, 0, 8, 12])
budget['aman'] = fuzz.trapmf(budget.universe, [8, 15, 35, 45])
budget['melimpah'] = fuzz.trapmf(budget.universe, [35, 45, 100, 100])

# Output: Status Kelayakan Rilis (0-100)
release_quality['tunda'] = fuzz.trapmf(release_quality.universe, [0, 0, 35, 45])
release_quality['akses_awal'] = fuzz.trapmf(release_quality.universe, [35, 50, 65, 80])
release_quality['siap_rilis'] = fuzz.trapmf(release_quality.universe, [70, 85, 100, 100])

# 3. Rules — 81 Kombinasi Lengkap (Mamdani Manual Inference)
# Format: (bug, fps, wishlist, budget) → output
# Logika skor: rusak/patah_patah/sedikit/kritis=0, wajar/stabil/menjanjikan/aman=1, bersih/lancar/meledak/melimpah=2
# Total skor 0-2 → tunda | 3-5 → akses_awal | 6-8 → siap_rilis

RULES_TABLE = {
    # ── GROUP 1: Bug = RUSAK ──────────────────────────────────────────────────────────────────────
    # FPS = patah_patah
    ('rusak', 'patah_patah', 'sedikit',     'kritis'):   'tunda',       # R1  skor 0
    ('rusak', 'patah_patah', 'sedikit',     'aman'):     'tunda',       # R2  skor 1
    ('rusak', 'patah_patah', 'sedikit',     'melimpah'): 'tunda',       # R3  skor 2
    ('rusak', 'patah_patah', 'menjanjikan', 'kritis'):   'tunda',       # R4  skor 1
    ('rusak', 'patah_patah', 'menjanjikan', 'aman'):     'tunda',       # R5  skor 2
    ('rusak', 'patah_patah', 'menjanjikan', 'melimpah'): 'akses_awal',  # R6  skor 3
    ('rusak', 'patah_patah', 'meledak',     'kritis'):   'tunda',       # R7  skor 2
    ('rusak', 'patah_patah', 'meledak',     'aman'):     'akses_awal',  # R8  skor 3
    ('rusak', 'patah_patah', 'meledak',     'melimpah'): 'akses_awal',  # R9  skor 4
    # FPS = stabil
    ('rusak', 'stabil', 'sedikit',     'kritis'):   'tunda',       # R10 skor 1
    ('rusak', 'stabil', 'sedikit',     'aman'):     'tunda',       # R11 skor 2
    ('rusak', 'stabil', 'sedikit',     'melimpah'): 'akses_awal',  # R12 skor 3
    ('rusak', 'stabil', 'menjanjikan', 'kritis'):   'tunda',       # R13 skor 2
    ('rusak', 'stabil', 'menjanjikan', 'aman'):     'akses_awal',  # R14 skor 3
    ('rusak', 'stabil', 'menjanjikan', 'melimpah'): 'akses_awal',  # R15 skor 4
    ('rusak', 'stabil', 'meledak',     'kritis'):   'akses_awal',  # R16 skor 3
    ('rusak', 'stabil', 'meledak',     'aman'):     'akses_awal',  # R17 skor 4
    ('rusak', 'stabil', 'meledak',     'melimpah'): 'akses_awal',  # R18 skor 5
    # FPS = lancar
    ('rusak', 'lancar', 'sedikit',     'kritis'):   'tunda',       # R19 skor 2
    ('rusak', 'lancar', 'sedikit',     'aman'):     'akses_awal',  # R20 skor 3
    ('rusak', 'lancar', 'sedikit',     'melimpah'): 'akses_awal',  # R21 skor 4
    ('rusak', 'lancar', 'menjanjikan', 'kritis'):   'akses_awal',  # R22 skor 3
    ('rusak', 'lancar', 'menjanjikan', 'aman'):     'akses_awal',  # R23 skor 4
    ('rusak', 'lancar', 'menjanjikan', 'melimpah'): 'akses_awal',  # R24 skor 5
    ('rusak', 'lancar', 'meledak',     'kritis'):   'akses_awal',  # R25 skor 4
    ('rusak', 'lancar', 'meledak',     'aman'):     'akses_awal',  # R26 skor 5
    ('rusak', 'lancar', 'meledak',     'melimpah'): 'siap_rilis',  # R27 skor 6

    # ── GROUP 2: Bug = WAJAR ──────────────────────────────────────────────────────────────────────
    # FPS = patah_patah
    ('wajar', 'patah_patah', 'sedikit',     'kritis'):   'tunda',       # R28 skor 1
    ('wajar', 'patah_patah', 'sedikit',     'aman'):     'tunda',       # R29 skor 2
    ('wajar', 'patah_patah', 'sedikit',     'melimpah'): 'akses_awal',  # R30 skor 3
    ('wajar', 'patah_patah', 'menjanjikan', 'kritis'):   'tunda',       # R31 skor 2
    ('wajar', 'patah_patah', 'menjanjikan', 'aman'):     'akses_awal',  # R32 skor 3
    ('wajar', 'patah_patah', 'menjanjikan', 'melimpah'): 'akses_awal',  # R33 skor 4
    ('wajar', 'patah_patah', 'meledak',     'kritis'):   'akses_awal',  # R34 skor 3
    ('wajar', 'patah_patah', 'meledak',     'aman'):     'akses_awal',  # R35 skor 4
    ('wajar', 'patah_patah', 'meledak',     'melimpah'): 'akses_awal',  # R36 skor 5
    # FPS = stabil
    ('wajar', 'stabil', 'sedikit',     'kritis'):   'tunda',       # R37 skor 2
    ('wajar', 'stabil', 'sedikit',     'aman'):     'akses_awal',  # R38 skor 3
    ('wajar', 'stabil', 'sedikit',     'melimpah'): 'akses_awal',  # R39 skor 4
    ('wajar', 'stabil', 'menjanjikan', 'kritis'):   'akses_awal',  # R40 skor 3
    ('wajar', 'stabil', 'menjanjikan', 'aman'):     'akses_awal',  # R41 skor 4
    ('wajar', 'stabil', 'menjanjikan', 'melimpah'): 'akses_awal',  # R42 skor 5
    ('wajar', 'stabil', 'meledak',     'kritis'):   'akses_awal',  # R43 skor 4
    ('wajar', 'stabil', 'meledak',     'aman'):     'akses_awal',  # R44 skor 5
    ('wajar', 'stabil', 'meledak',     'melimpah'): 'siap_rilis',  # R45 skor 6
    # FPS = lancar
    ('wajar', 'lancar', 'sedikit',     'kritis'):   'akses_awal',  # R46 skor 3
    ('wajar', 'lancar', 'sedikit',     'aman'):     'akses_awal',  # R47 skor 4
    ('wajar', 'lancar', 'sedikit',     'melimpah'): 'akses_awal',  # R48 skor 5
    ('wajar', 'lancar', 'menjanjikan', 'kritis'):   'akses_awal',  # R49 skor 4
    ('wajar', 'lancar', 'menjanjikan', 'aman'):     'akses_awal',  # R50 skor 5
    ('wajar', 'lancar', 'menjanjikan', 'melimpah'): 'siap_rilis',  # R51 skor 6
    ('wajar', 'lancar', 'meledak',     'kritis'):   'akses_awal',  # R52 skor 5
    ('wajar', 'lancar', 'meledak',     'aman'):     'siap_rilis',  # R53 skor 6
    ('wajar', 'lancar', 'meledak',     'melimpah'): 'siap_rilis',  # R54 skor 7

    # ── GROUP 3: Bug = SANGAT_BERSIH ─────────────────────────────────────────────────────────────
    # FPS = patah_patah
    ('sangat_bersih', 'patah_patah', 'sedikit',     'kritis'):   'tunda',       # R55 skor 2
    ('sangat_bersih', 'patah_patah', 'sedikit',     'aman'):     'akses_awal',  # R56 skor 3
    ('sangat_bersih', 'patah_patah', 'sedikit',     'melimpah'): 'akses_awal',  # R57 skor 4
    ('sangat_bersih', 'patah_patah', 'menjanjikan', 'kritis'):   'akses_awal',  # R58 skor 3
    ('sangat_bersih', 'patah_patah', 'menjanjikan', 'aman'):     'akses_awal',  # R59 skor 4
    ('sangat_bersih', 'patah_patah', 'menjanjikan', 'melimpah'): 'akses_awal',  # R60 skor 5
    ('sangat_bersih', 'patah_patah', 'meledak',     'kritis'):   'akses_awal',  # R61 skor 4
    ('sangat_bersih', 'patah_patah', 'meledak',     'aman'):     'akses_awal',  # R62 skor 5
    ('sangat_bersih', 'patah_patah', 'meledak',     'melimpah'): 'siap_rilis',  # R63 skor 6
    # FPS = stabil
    ('sangat_bersih', 'stabil', 'sedikit',     'kritis'):   'akses_awal',  # R64 skor 3
    ('sangat_bersih', 'stabil', 'sedikit',     'aman'):     'akses_awal',  # R65 skor 4
    ('sangat_bersih', 'stabil', 'sedikit',     'melimpah'): 'akses_awal',  # R66 skor 5
    ('sangat_bersih', 'stabil', 'menjanjikan', 'kritis'):   'akses_awal',  # R67 skor 4
    ('sangat_bersih', 'stabil', 'menjanjikan', 'aman'):     'akses_awal',  # R68 skor 5
    ('sangat_bersih', 'stabil', 'menjanjikan', 'melimpah'): 'siap_rilis',  # R69 skor 6
    ('sangat_bersih', 'stabil', 'meledak',     'kritis'):   'akses_awal',  # R70 skor 5
    ('sangat_bersih', 'stabil', 'meledak',     'aman'):     'siap_rilis',  # R71 skor 6
    ('sangat_bersih', 'stabil', 'meledak',     'melimpah'): 'siap_rilis',  # R72 skor 7
    # FPS = lancar
    ('sangat_bersih', 'lancar', 'sedikit',     'kritis'):   'akses_awal',  # R73 skor 4
    ('sangat_bersih', 'lancar', 'sedikit',     'aman'):     'akses_awal',  # R74 skor 5
    ('sangat_bersih', 'lancar', 'sedikit',     'melimpah'): 'siap_rilis',  # R75 skor 6
    ('sangat_bersih', 'lancar', 'menjanjikan', 'kritis'):   'akses_awal',  # R76 skor 5
    ('sangat_bersih', 'lancar', 'menjanjikan', 'aman'):     'siap_rilis',  # R77 skor 6
    ('sangat_bersih', 'lancar', 'menjanjikan', 'melimpah'): 'siap_rilis',  # R78 skor 7
    ('sangat_bersih', 'lancar', 'meledak',     'kritis'):   'siap_rilis',  # R79 skor 6
    ('sangat_bersih', 'lancar', 'meledak',     'aman'):     'siap_rilis',  # R80 skor 7
    ('sangat_bersih', 'lancar', 'meledak',     'melimpah'): 'siap_rilis',  # R81 skor 8
}



def get_membership_degrees(bugs: float, frames: float, wishes: int, budg: float, score: float = None) -> dict:
    """
    Calculates membership degrees (mu) for all variables.
    """
    mu_bug_sangat_bersih = float(fuzz.interp_membership(bug_density.universe, bug_density['sangat_bersih'].mf, bugs))
    mu_bug_wajar = float(fuzz.interp_membership(bug_density.universe, bug_density['wajar'].mf, bugs))
    mu_bug_rusak = float(fuzz.interp_membership(bug_density.universe, bug_density['rusak'].mf, bugs))

    mu_fps_patah_patah = float(fuzz.interp_membership(fps.universe, fps['patah_patah'].mf, frames))
    mu_fps_stabil = float(fuzz.interp_membership(fps.universe, fps['stabil'].mf, frames))
    mu_fps_lancar = float(fuzz.interp_membership(fps.universe, fps['lancar'].mf, frames))

    mu_wishlist_sedikit = float(fuzz.interp_membership(wishlist.universe, wishlist['sedikit'].mf, wishes))
    mu_wishlist_menjanjikan = float(fuzz.interp_membership(wishlist.universe, wishlist['menjanjikan'].mf, wishes))
    mu_wishlist_meledak = float(fuzz.interp_membership(wishlist.universe, wishlist['meledak'].mf, wishes))

    mu_budget_kritis = float(fuzz.interp_membership(budget.universe, budget['kritis'].mf, budg))
    mu_budget_aman = float(fuzz.interp_membership(budget.universe, budget['aman'].mf, budg))
    mu_budget_melimpah = float(fuzz.interp_membership(budget.universe, budget['melimpah'].mf, budg))

    if score is not None:
        mu_quality_tunda = float(fuzz.interp_membership(release_quality.universe, release_quality['tunda'].mf, score))
        mu_quality_akses_awal = float(fuzz.interp_membership(release_quality.universe, release_quality['akses_awal'].mf, score))
        mu_quality_siap_rilis = float(fuzz.interp_membership(release_quality.universe, release_quality['siap_rilis'].mf, score))
    else:
        mu_quality_tunda = 0.0
        mu_quality_akses_awal = 0.0
        mu_quality_siap_rilis = 0.0

    return {
        "mu_bug_sangat_bersih": round(mu_bug_sangat_bersih, 4),
        "mu_bug_wajar": round(mu_bug_wajar, 4),
        "mu_bug_rusak": round(mu_bug_rusak, 4),
        "mu_fps_patah_patah": round(mu_fps_patah_patah, 4),
        "mu_fps_stabil": round(mu_fps_stabil, 4),
        "mu_fps_lancar": round(mu_fps_lancar, 4),
        "mu_wishlist_sedikit": round(mu_wishlist_sedikit, 4),
        "mu_wishlist_menjanjikan": round(mu_wishlist_menjanjikan, 4),
        "mu_wishlist_meledak": round(mu_wishlist_meledak, 4),
        "mu_budget_kritis": round(mu_budget_kritis, 4),
        "mu_budget_aman": round(mu_budget_aman, 4),
        "mu_budget_melimpah": round(mu_budget_melimpah, 4),
        "mu_quality_tunda": round(mu_quality_tunda, 4),
        "mu_quality_akses_awal": round(mu_quality_akses_awal, 4),
        "mu_quality_siap_rilis": round(mu_quality_siap_rilis, 4)
    }

def evaluate_quality(bugs: float, frames: float, wishes: int, budg: float) -> dict:
    """
    Evaluates the release quality using MANUAL Mamdani fuzzy inference.
    Langkah:
      1. Fuzzifikasi  : hitung µ tiap variabel input
      2. Inferensi    : firing strength tiap rule = MIN(µ antecedents)  [AND = MIN]
      3. Agregasi     : per output term ambil MAX dari semua rules yang firing
      4. Clip & gabung: potong MF output sesuai strength, gabung dengan MAX
      5. Defuzzifikasi: centroid dari area gabungan
    """
    # Step 1 — Fuzzifikasi
    mu_bug = {
        'rusak':         float(fuzz.interp_membership(bug_density.universe, bug_density['rusak'].mf,         bugs)),
        'wajar':         float(fuzz.interp_membership(bug_density.universe, bug_density['wajar'].mf,         bugs)),
        'sangat_bersih': float(fuzz.interp_membership(bug_density.universe, bug_density['sangat_bersih'].mf, bugs)),
    }
    mu_fps = {
        'patah_patah': float(fuzz.interp_membership(fps.universe, fps['patah_patah'].mf, frames)),
        'stabil':      float(fuzz.interp_membership(fps.universe, fps['stabil'].mf,      frames)),
        'lancar':      float(fuzz.interp_membership(fps.universe, fps['lancar'].mf,      frames)),
    }
    mu_wish = {
        'sedikit':     float(fuzz.interp_membership(wishlist.universe, wishlist['sedikit'].mf,     wishes)),
        'menjanjikan': float(fuzz.interp_membership(wishlist.universe, wishlist['menjanjikan'].mf, wishes)),
        'meledak':     float(fuzz.interp_membership(wishlist.universe, wishlist['meledak'].mf,     wishes)),
    }
    mu_budg = {
        'kritis':   float(fuzz.interp_membership(budget.universe, budget['kritis'].mf,   budg)),
        'aman':     float(fuzz.interp_membership(budget.universe, budget['aman'].mf,     budg)),
        'melimpah': float(fuzz.interp_membership(budget.universe, budget['melimpah'].mf, budg)),
    }

    # Step 2 & 3 — Inferensi + Agregasi (per output term, ambil MAX firing strength)
    agg_strength = {'tunda': 0.0, 'akses_awal': 0.0, 'siap_rilis': 0.0}
    for (b, f, w, d), output_term in RULES_TABLE.items():
        strength = min(mu_bug[b], mu_fps[f], mu_wish[w], mu_budg[d])  # AND = MIN
        if strength > agg_strength[output_term]:
            agg_strength[output_term] = strength

    # Step 4 — Clip output MF & gabung dengan MAX (Mamdani)
    x = release_quality.universe
    aggregated = np.zeros_like(x, dtype=float)
    for term, strength in agg_strength.items():
        if strength > 0:
            clipped = np.fmin(strength, release_quality[term].mf)
            aggregated = np.fmax(aggregated, clipped)

    # Step 5 — Defuzzifikasi Centroid
    if aggregated.sum() == 0:
        score = 50.0  # fallback netral jika tidak ada rule yang firing
    else:
        score = float(fuzz.defuzz(x, aggregated, 'centroid'))

    if score <= 40:
        status = "Tunda/Rombak Total"
    elif score <= 75:
        status = "Rilis Akses Awal"
    else:
        status = "Siap Rilis Penuh"
        
    memberships = get_membership_degrees(bugs, frames, wishes, budg, score)
    return {
        "score": round(score, 2),
        "status": status,
        "memberships": memberships
    }
