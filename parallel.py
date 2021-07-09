import mpi4py.MPI as mpi
import pyomo.environ as pe

from mpisppy.phbase import PHBase
from mpisppy.opt.ph import PH
from mpisppy.extensions.extension import MultiExtension
from mpisppy.extensions.cross_scen_extension import CrossScenarioExtension
from mpisppy.cylinders.lagrangian_bounder import LagrangianOuterBound
from mpisppy.cylinders.hub import PHHub
from mpisppy.cylinders.cross_scen_hub import CrossScenarioHub
from mpisppy.cylinders.cross_scen_spoke import CrossScenarioCutSpoke
from mpisppy.opt.lshaped import LShapedMethod
from mpisppy.utils.sputils import spin_the_wheel

import farmer
from data import *


# MPI setup
glob_comm = mpi.COMM_WORLD
glob_rank = glob_comm.Get_rank()


solve_progressive_hedging = True

# Progressive Hedging
if solve_progressive_hedging:

    hub_ph_options = {
        'solvername': 'ipopt',
        'PHIterLimit': 50,
        'defaultPHrho': 1.0,
        'convthresh': 0.0,
        'verbose': False,
        'display_progress': False,
        'display_timing': False,
        'iter0_solver_options': {},
        'iterk_solver_options': {},
        # more
        'bundes_per_rank': 0,
        'asynchronousPH': False,
        'subsolvedirectories': None,
        'tee-rank0-solves': False,
        'cross_scen_options': {'check_bound_improve_iterations': 2}
    }

    hub_dict = {
        'hub_class': CrossScenarioHub,
        'hub_kwargs': dict(),
        'opt_class': PH,
        'opt_kwargs': {
            'options': hub_ph_options,
            'all_scenario_names': SCENARIOS,
            'scenario_creator': farmer.scenario_creator,
            'rho_setter': None,
            'extensions': MultiExtension,
            'extension_kwargs': { 'ext_classes' : [CrossScenarioExtension] }
        }
    }


    ph = PH(hub_ph_options, SCENARIOS, farmer.scenario_creator)
    results = ph.ph_main()
    variables = ph.gather_var_values_to_rank0()
    for (scenario, variable) in variables:
        print(scenario, variable, variables[scenario, variable])


    scomm, opt = spin_the_wheel(hub_dict, [])
