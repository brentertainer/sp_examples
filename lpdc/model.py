import math

import mpisppy.utils.sputils as sputils
import yaml
from pyomo.environ import *


### FIRST STAGE OBJECTIVE -- EXPECTED VALUE OPTIMIZATION ###

def block_fs_obj_ev(block):
    root = block.model()
    # objective
    root.expr_fs_obj = Expression(expr=0)
    root.expr_ss_obj = Expression(expr=root.gamma)
    root.obj_min_expected_shed = Objective(sense=minimize, expr=root.expr_fs_obj + root.expr_ss_obj)


### FIRST STAGE OBJECTIVE -- ROBUST OPTIMIZATION ###

def con_def_gamma_max(base):
    return base.gamma_max >= base.gamma

def block_fs_obj_ro(block):
    root = block.model()
    # variables
    root.gamma_max = Var(domain=Reals)
    # constraints
    root.con_def_gamma_max = Constraint(rule=con_def_gamma_max)
    # objective
    root.expr_fs_obj = Expression(expr=root.gamma_max)
    root.expr_ss_obj = Expression(expr=0)
    root.obj_min_max_shed = Objective(sense=minimize, expr=root.expr_fs_obj + root.expr_ss_obj)


### FIRST STAGE OBJECTIVE -- CVaR OPTIMIZATION ###

def con_def_gamma_plus(base):
    return base.gamma_plus >= base.gamma - base.cvar_scale

def block_fs_obj_cvar(block):
    root = block.model()
    # parameters
    root.epsilon = Param(initialize=root._specs['epsilon'])
    # variables
    root.gamma_plus = Var(domain=NonNegativeReals)
    root.cvar_scale = Var(domain=Reals)
    # constraints
    root.con_def_gamma_plus = Constraint(rule=con_def_gamma_plus)
    # objective
    root.expr_fs_obj = Expression(expr=root.cvar_scale)
    root.expr_ss_obj = Expression(expr=root.gamma_plus / (1 - root.epsilon))
    root.obj_min_cvar_shed = Objective(sense=minimize, expr=root.expr_fs_obj + root.expr_ss_obj)


### FIRST STAGE CONSTRAINTS ###

def con_resource_hi(base):
    return sum(base.c[k, r] * base.x[k, r] for k, r in base.KxR) <= base.f

def con_inexorable_flooding(base, k):
    return base.x[k, base.r_hat[k]] == 0

def con_incremental(base, k, r):
    if r == base.r_hat[k]:
        return Constraint.Skip
    else:
        return base.x[k, r+1] <= base.x[k, r]

def block_fs_con(block):
    root = block.model()
    # sets
    root.K = Set(initialize=sorted(root._specs['K']))
    root.R = Set(root.K, initialize=root._specs['R'])
    root.KxR = Set(initialize=[(k, r) for k in root.R for r in root.R[k]])
    # parameters
    root.c = Param(root.KxR, initialize=root._specs['c'], default=0)
    root.f = Param(initialize=root._specs['f'], mutable=True)
    root.r_hat = Param(root.K, initialize=root._specs['r_hat'])
    # variables
    root.x = Var(root.KxR, domain=Binary)
    # constraints
    root.con_resource_hi = Constraint(rule=con_resource_hi)
    root.con_inexorable_flooding = Constraint(root.K, rule=con_inexorable_flooding)
    root.con_incremental = Constraint(root.KxR, rule=con_incremental)


### LPNF ###

def con_gen_dispatch(base, n, g):
    return base.zeta[n, g] == base.alpha[n]

def con_p_net_flow(base, n):
    flow_out = sum(base.p_tilde[l]
               for m in base.delta_neg[n]
               for l in base.L_nm[m, n])
    flow_in = sum(base.p_tilde[l]
               for m in base.delta_pos[n]
               for l in base.L_nm[n, m])
    return base.p[n] == flow_out - flow_in

def con_p_net_injection(base, n):
    net_generation = sum(base.p_hat[g] for g in base.G_n[n])
    net_load = sum(base.p_load_hi[d] * base.z[d] for d in base.D_n[n])
    return base.p[n] == net_generation - net_load

def con_p_gen_lo(base, n, g):
    return base.p_gen_lo[g] * base.zeta[n, g] <= base.p_hat[g]

def con_p_gen_hi(base, n, g):
    return base.p_hat[g] <= base.p_gen_hi[g] * base.zeta[n, g]

def con_p_flow_lo(base, n, m, l):
    return -base.s_flow_hi[l] * base.beta[n, m] <= base.p_tilde[l]

def con_p_flow_hi(base, n, m, l):
    return base.p_tilde[l] <= base.s_flow_hi[l] * base.beta[n, m]

def con_def_alpha_gt(base, n):
    k = base.k_of_n[n]
    sum1 = sum(1 - base.xi[k, r] * (1 - base.x[k, r]) for r in base.R[k])
    return base.alpha[n] >= sum1 - len(base.R[k]) + 1

def con_def_alpha_lt(base, n, r):
    k = base.k_of_n[n]
    return base.alpha[n] <= 1 - base.xi[k, r] * (1 - base.x[k, r])

def con_def_beta_gt(base, n, m):
    return base.beta[n, m] >= base.alpha[n] + base.alpha[m] - 1

def con_def_beta_lt_f(base, n, m):
    return base.beta[n, m] <= base.alpha[n]

def con_def_beta_lt_t(base, n, m):
    return base.beta[n, m] <= base.alpha[m]

def con_def_gamma(base):
    return base.gamma == sum(base.p_load_hi[d] * (1 - base.z[d]) for d in base.D)


def block_lpnf(block):

    root = block.model()
    # sets
    root.N = Set(initialize=sorted(root._specs['N']))
    root.N_G = Set(initialize=sorted(root._specs['N_G']))
    root.N_D = Set(initialize=sorted(root._specs['N_D']))
    root.G = Set(initialize=sorted(root._specs['G']))
    root.D = Set(initialize=sorted(root._specs['D']))
    root.E = Set(initialize=sorted(root._specs['E']))
    EA = {(n, m) for (n, m) in root._specs['E']} | {(m, n) for (n, m) in root._specs['E']}
    root.EA = Set(initialize=sorted(EA))
    root.L = Set(initialize=sorted(root._specs['L']))
    root.NxG = Set(within=root.N * root.G, initialize=sorted(root._specs['NxG']))
    root.NxD = Set(within=root.N * root.D, initialize=sorted(root._specs['NxD']))
    root.ExL = Set(within=root.E * root.L, initialize=sorted(root._specs['ExL']))
    root.G_n = Param(root.N, initialize=root._specs['G_n'], default=set(), within=Any)
    root.D_n = Param(root.N, initialize=root._specs['D_n'], default=set(), within=Any)
    root.L_nm = Param(root.E, initialize=root._specs['L_nm'], default=set(), within=Any)
    root.delta_neg = Param(root.N, initialize=root._specs['delta_neg'], default=set(), within=Any)
    root.delta_pos = Param(root.N, initialize=root._specs['delta_pos'], default=set(), within=Any)
    root.k_of_n = Param(root.N, initialize=root._specs['k_of_n'])
    root.NxR = Set(initialize=[(n, r) for n in root.N for r in root.R[root.k_of_n[n]]])
    # parameters
    root.p_gen_lo = Param(root.G, initialize=root._specs['p_gen_lo'])
    root.p_gen_hi = Param(root.G, initialize=root._specs['p_gen_hi'])
    root.p_load_hi = Param(root.D, initialize=root._specs['p_load_hi'])
    root.s_flow_hi = Param(root.L, initialize=root._specs['s_flow_hi'])
    xi = {(k, r): v for (k, r, omega), v in root._specs['xi'].items() if omega == root._omega}
    root.xi = Param(root.KxR, initialize=xi, default=0)
    # variables
    root.p = Var(root.N, domain=Reals)
    root.p_hat = Var(root.G, domain=Reals)
    root.p_tilde = Var(root.L, domain=Reals)
    root.z = Var(root.D, bounds=(0, 1))
    root.zeta = Var(root.NxG, bounds=(0, 1))
    root.alpha = Var(root.N, bounds=(0, 1))
    root.beta = Var(root.EA, bounds=(0, 1))
    root.gamma = Var(domain=NonNegativeReals)
    # constraints
    root.con_gen_dispatch = Constraint(root.NxG, rule=con_gen_dispatch)
    root.con_p_net_flow = Constraint(root.N, rule=con_p_net_flow)
    root.con_p_net_injection = Constraint(root.N, rule=con_p_net_injection)
    root.con_p_gen_lo = Constraint(root.NxG, rule=con_p_gen_lo)
    root.con_p_gen_hi = Constraint(root.NxG, rule=con_p_gen_hi)
    root.con_p_flow_lo = Constraint(root.ExL, rule=con_p_flow_lo)
    root.con_p_flow_hi = Constraint(root.ExL, rule=con_p_flow_hi)
    root.con_def_alpha_gt = Constraint(root.N, rule=con_def_alpha_gt)
    root.con_def_alpha_lt = Constraint(root.NxR, rule=con_def_alpha_lt)
    root.con_def_beta_gt = Constraint(root.EA, rule=con_def_beta_gt)
    root.con_def_beta_lt_f = Constraint(root.EA, rule=con_def_beta_lt_f)
    root.con_def_beta_lt_t = Constraint(root.EA, rule=con_def_beta_lt_t)
    root.con_def_gamma = Constraint(rule=con_def_gamma)


def con_ohms_law_gt(base, n, m, l):
    bigM = 2 * math.pi * -base.b[l]
    rhs = (base.theta[n] - base.theta[m]) * -base.b[l]
    lhs = base.p_tilde[l]
    return rhs >= lhs - bigM * (1 - base.beta[n, m])

def con_ohms_law_lt(base, n, m, l):
    bigM = 2 * math.pi * -base.b[l]
    rhs = (base.theta[n] - base.theta[m]) * -base.b[l]
    lhs = base.p_tilde[l]
    return rhs <= lhs + bigM * (1 - base.beta[n, m])

def con_ref_phase_angle(base):
    return base.theta[base.n_ref] == 0


def block_lpdc(block):

    root = block.model()
    root.lpnf = Block(rule=block_lpnf)
    # sets
    root.n_ref = Param(initialize=root._specs['n_ref'])
    # parameters
    root.b = Param(root.L, initialize=root._specs['b'])
    # variables
    root.theta = Var(root.N, bounds=(-math.pi, math.pi))
    # constraints
    root.con_ohms_law_gt = Constraint(root.ExL, rule=con_ohms_law_gt)
    root.con_ohms_law_lt = Constraint(root.ExL, rule=con_ohms_law_lt)
    root.con_ref_phase_angle = Constraint(rule=con_ref_phase_angle)


def scenario_creator_lpdc_ev(omega, **specs):
    root = ConcreteModel('root')
    root._omega = int(omega)
    root._specs = specs
    root._mpisppy_probability = root._specs['probability'][root._omega]
    root.fs_con = Block(rule=block_fs_con)
    root.pf = Block(rule=block_lpdc)
    root.fs_obj = Block(rule=block_fs_obj_ev)
    del root._specs
    sputils.attach_root_node(root, root.expr_fs_obj, [root.x])
    return root


def scenario_creator_lpdc_ro(omega, **specs):
    root = ConcreteModel('root')
    root._omega = int(omega)
    root._specs = specs
    root._mpisppy_probability = root._specs['probability'][root._omega]
    root.fs_con = Block(rule=block_fs_con)
    root.pf = Block(rule=block_lpdc)
    root.fs_obj = Block(rule=block_fs_obj_ro)
    del root._specs
    sputils.attach_root_node(root, root.expr_fs_obj, [root.x, root.gamma_max])
    return root


def scenario_creator_lpdc_cvar(omega, **specs):
    root = ConcreteModel('root')
    root._omega = int(omega)
    root._specs = specs
    root._mpisppy_probability = root._specs['probability'][root._omega]
    root.fs_con = Block(rule=block_fs_con)
    root.pf = Block(rule=block_lpdc)
    root.fs_obj = Block(rule=block_fs_obj_cvar)
    del root._specs
    sputils.attach_root_node(root, root.expr_fs_obj, [root.x, root.cvar_scale])
    return root

