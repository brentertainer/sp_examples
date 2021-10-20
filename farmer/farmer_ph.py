import mpi4py.MPI as mpi
import pyomo.environ as pe

import mpisppy.utils.sputils as sputils
from mpisppy.utils import baseparsers, vanilla

import farmer
from data import *


# MPI setup
glob_comm = mpi.COMM_WORLD
glob_rank = glob_comm.Get_rank()

# argument parsing
parser = baseparsers.make_parser()
parser = baseparsers.two_sided_args(parser)
parser = baseparsers.aph_args(parser)
parser = baseparsers.xhatlooper_args(parser)
parser = baseparsers.fwph_args(parser)
parser = baseparsers.lagrangian_args(parser)
parser = baseparsers.xhatshuffle_args(parser)
parser.add_argument('--risk-measure',
                    choices=['expectation', 'cvar', 'robust'],
                    help='risk measure to employ in the objective function',
                    default='expectation',
                    required=False)
parser.add_argument('--cvar-epsilon',
                    help='proportion of tail over which to optimize using CVaR',
                    type=float,
                    default=1,
                    required=False)
cli_args = parser.parse_args()

# scenario parameters
scenario_creator = farmer.scenario_creator
scenario_denouement = None
scenario_names = ['Scen1', 'Scen2', 'Scen3']

args = [cli_args,
        scenario_creator,
        scenario_denouement,
        scenario_names]

# hub setup
hub_setup = vanilla.ph_hub
hub_dict = hub_setup(*args)

# spoke setup
spoke_dicts = list()

# primal spokes
if cli_args.with_xhatlooper:
    spoke_dicts.append(vanilla.xhatlooper_spoke(*args))

if cli_args.with_xhatshuffle:
    spoke_dicts.append(vanilla.xhatshuffle_spoke(*args))

# dual spokes
if cli_args.with_fwph:
    spoke_dicts.append(vanilla.fwph_spoke(*args))

if cli_args.with_lagrangian:
    spoke_dicts.append(vanilla.lagrangian_spoke(*args))

# solve
spcomm, opt_dict = sputils.spin_the_wheel(hub_dict, spoke_dicts)
sputils.write_spin_the_wheel_first_stage_solution(spcomm, opt_dict, 'solution.csv')
sputils.write_spin_the_wheel_tree_solution(spcomm, opt_dict, 'solution')

