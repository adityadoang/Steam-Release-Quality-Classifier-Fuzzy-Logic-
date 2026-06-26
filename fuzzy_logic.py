import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# 1. New Antecedents/Consequents
bug_density = ctrl.Antecedent(np.arange(0, 16, 0.1), 'bug_density')
fps = ctrl.Antecedent(np.arange(0, 121, 1), 'fps')
wishlist = ctrl.Antecedent(np.arange(0, 50001, 100), 'wishlist')
budget = ctrl.Antecedent(np.arange(0, 101, 1), 'budget')

release_quality = ctrl.Consequent(np.arange(0, 101, 1), 'release_quality')

# 2. Membership functions
# Bug Density: Sangat Bersih (0-2), Wajar (3-7), Rusak (>8)
bug_density['sangat_bersih'] = fuzz.trapmf(bug_density.universe, [0, 0, 1, 3])
bug_density['wajar'] = fuzz.trapmf(bug_density.universe, [2, 4, 6, 8])
bug_density['rusak'] = fuzz.trapmf(bug_density.universe, [7, 9, 15, 15])

# FPS: Patah-patah (0-25), Stabil 30fps (25-50), Lancar 60fps+ (>50)
fps['patah_patah'] = fuzz.trapmf(fps.universe, [0, 0, 20, 30])
fps['stabil'] = fuzz.trapmf(fps.universe, [20, 30, 45, 55])
fps['lancar'] = fuzz.trapmf(fps.universe, [45, 60, 120, 120])

# Wishlist Count: Sedikit (0-5000), Menjanjikan (5000-20000), Meledak (>20000)
wishlist['sedikit'] = fuzz.trapmf(wishlist.universe, [0, 0, 4000, 6000])
wishlist['menjanjikan'] = fuzz.trapmf(wishlist.universe, [4000, 10000, 15000, 22000])
wishlist['meledak'] = fuzz.trapmf(wishlist.universe, [18000, 25000, 50000, 50000])

# Production Cost / Remaining Budget (%): Kritis (0-10), Aman (10-40), Melimpah (>40)
budget['kritis'] = fuzz.trapmf(budget.universe, [0, 0, 8, 12])
budget['aman'] = fuzz.trapmf(budget.universe, [8, 15, 35, 45])
budget['melimpah'] = fuzz.trapmf(budget.universe, [35, 45, 100, 100])

# Output: Status Kelayakan Rilis (0-100)
release_quality['tunda'] = fuzz.trapmf(release_quality.universe, [0, 0, 35, 45])
release_quality['akses_awal'] = fuzz.trapmf(release_quality.universe, [35, 50, 65, 80])
release_quality['siap_rilis'] = fuzz.trapmf(release_quality.universe, [70, 85, 100, 100])

# 3. Rules (Mamdani Murni Komprehensif)
2
# -- Pengaruh Bug Density --
rule_bug_1 = ctrl.Rule(bug_density['rusak'], release_quality['tunda'])
rule_bug_2 = ctrl.Rule(bug_density['wajar'], release_quality['akses_awal'])
rule_bug_3 = ctrl.Rule(bug_density['sangat_bersih'], release_quality['siap_rilis'])

# -- Pengaruh FPS --
rule_fps_1 = ctrl.Rule(fps['patah_patah'], release_quality['tunda'])
rule_fps_2 = ctrl.Rule(fps['stabil'], release_quality['akses_awal'])
rule_fps_3 = ctrl.Rule(fps['lancar'], release_quality['siap_rilis'])

# -- Pengaruh Wishlist --
rule_wish_1 = ctrl.Rule(wishlist['sedikit'], release_quality['tunda'])
rule_wish_2 = ctrl.Rule(wishlist['menjanjikan'], release_quality['akses_awal'])
rule_wish_3 = ctrl.Rule(wishlist['meledak'], release_quality['siap_rilis'])

# -- Pengaruh Budget --
rule_budg_1 = ctrl.Rule(budget['kritis'], release_quality['tunda'])
rule_budg_2 = ctrl.Rule(budget['aman'], release_quality['akses_awal'])
rule_budg_3 = ctrl.Rule(budget['melimpah'], release_quality['siap_rilis'])

# 4. Control System
quality_ctrl = ctrl.ControlSystem([
    rule_bug_1, rule_bug_2, rule_bug_3,
    rule_fps_1, rule_fps_2, rule_fps_3,
    rule_wish_1, rule_wish_2, rule_wish_3,
    rule_budg_1, rule_budg_2, rule_budg_3
])
quality_sim = ctrl.ControlSystemSimulation(quality_ctrl)

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
    Evaluates the release quality using the pure Mamdani fuzzy logic engine.
    """
    quality_sim.input['bug_density'] = bugs
    quality_sim.input['fps'] = frames
    quality_sim.input['wishlist'] = wishes
    quality_sim.input['budget'] = budg
    
    # 100% Mamdani Murni, tidak perlu diakali menggunakan blok try-except
    quality_sim.compute()
    score = quality_sim.output['release_quality']
    
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
