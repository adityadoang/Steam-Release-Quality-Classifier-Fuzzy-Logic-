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

# 3. Rules
# Extremely bad conditions -> Tunda
rule1 = ctrl.Rule(bug_density['rusak'] | fps['patah_patah'] | budget['kritis'], release_quality['tunda'])

# Excellent conditions -> Siap Rilis
rule2 = ctrl.Rule(bug_density['sangat_bersih'] & fps['lancar'] & wishlist['meledak'] & (budget['aman'] | budget['melimpah']), release_quality['siap_rilis'])

# Good conditions but with minor issues -> Akses Awal
rule3 = ctrl.Rule(bug_density['wajar'] & fps['stabil'] & (wishlist['menjanjikan'] | wishlist['meledak']), release_quality['akses_awal'])
rule4 = ctrl.Rule(bug_density['sangat_bersih'] & fps['lancar'] & wishlist['menjanjikan'], release_quality['akses_awal'])

# High potential but high bugs -> Akses Awal or Tunda (depending on budget)
rule5 = ctrl.Rule(bug_density['rusak'] & wishlist['meledak'] & budget['melimpah'], release_quality['akses_awal'])

# Mediocre games -> Tunda if wishlist is bad
rule6 = ctrl.Rule(bug_density['wajar'] & fps['stabil'] & wishlist['sedikit'], release_quality['tunda'])

# Missing combinations that fallback
rule7 = ctrl.Rule(bug_density['sangat_bersih'] & fps['stabil'] & wishlist['sedikit'] & budget['aman'], release_quality['akses_awal'])
rule8 = ctrl.Rule(bug_density['wajar'] & fps['lancar'] & budget['melimpah'], release_quality['akses_awal'])
rule9 = ctrl.Rule(wishlist['sedikit'] & budget['aman'], release_quality['tunda'])

# 4. Control System
quality_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9])
quality_sim = ctrl.ControlSystemSimulation(quality_ctrl)

def evaluate_quality(bugs: float, frames: float, wishes: int, budg: float) -> dict:
    """
    Evaluates the release quality using the Mamdani fuzzy logic engine.
    """
    quality_sim.input['bug_density'] = bugs
    quality_sim.input['fps'] = frames
    quality_sim.input['wishlist'] = wishes
    quality_sim.input['budget'] = budg
    
    try:
        quality_sim.compute()
        score = quality_sim.output['release_quality']
    except KeyError:
        # Fallback when the input combination does not trigger any rules
        # Calculate a rough estimation based on the inputs
        # Bugs: 0 (good) -> 15 (bad). FPS: 120 (good) -> 0 (bad)
        # Wishlist: 50000 (good) -> 0. Budget: 100 (good) -> 0
        norm_bug = max(0, 100 - (bugs / 15 * 100))
        norm_fps = min(100, (frames / 60 * 100))
        norm_wish = min(100, (wishes / 20000 * 100))
        norm_budg = budg
        
        score = (norm_bug * 0.3) + (norm_fps * 0.3) + (norm_wish * 0.2) + (norm_budg * 0.2)
    
    if score <= 40:
        status = "Tunda/Rombak Total"
    elif score <= 75:
        status = "Rilis Akses Awal"
    else:
        status = "Siap Rilis Penuh"
        
    return {
        "score": round(score, 2),
        "status": status
    }
