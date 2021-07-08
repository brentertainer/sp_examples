import mpi4py.MPI as mpi
import pyomo.environ as pe
from mpi.extensions.extension import MultiExtension
#from mpi.extensions.cross_scen_extension import CrossScenarioExtension
from mpisppy.phbase import PHBase
from mpisppy.opt.ph import PH

import farmer


comm = mpi.COMM_WORLD
rank = comm.Get_rank()


solve_progressive_hedging = True

# Progressive Hedging
if solve_progressive_hedging:

    hub_ph_options = {
        'solvername': 'gurobi',
        'PHIterLimit': 50,
        'defaultPHrho': 1.0,
        'convthresh': 0.0,
        'verbose': False,
        'display_progress': False,
        'display_timing': False,
        'iter0_solver_options': {},
        'iterk_solver_options': {}
        # more
        'bundes_per_rank': 0,
        'asynchronousPH': False
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
            'rho_setter': rho_setter,
            'extensions': MultiExtension,
            'extension_kwargs': multi_ext
        }


    ph = PH(options, SCENARIOS, farmer.scenario_creator)
    results = ph.ph_main()
    variables = ph.gather_var_values_to_rank0()
    for (scenario, variable) in variables:
        print(scenario, variable, variables[scenario, variable])


    scomm, opt = spin_the_wheel({}, [])
