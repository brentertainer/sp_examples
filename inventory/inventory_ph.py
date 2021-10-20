from functools import reduce
from itertools import product
from operator import mul

import mpi4py.MPI as mpi
import mpisppy.utils.sputils as sputils
from mpisppy.utils import baseparsers, vanilla

import inventory
#import data.balanced_3stage as data
import data.balanced_4stage as data
#import data.balanced_6stage as data
#import data.unbalanced_4stage as data


# MPI setup
glob_comm = mpi.COMM_WORLD
glob_rank = glob_comm.Get_rank()

# argument parsing
parser = baseparsers.make_multistage_parser()
parser = baseparsers.two_sided_args(parser)
parser = baseparsers.xhatlooper_args(parser)
parser = baseparsers.xhatshuffle_args(parser)
parser = baseparsers.lagrangian_args(parser)
cli_args = parser.parse_args()


# scenario parameters
all_nodenames = data.all_nodenames
scenario_names = data.scenarios
scenario_creator = inventory.scenario_creator
scenario_denouement = None
scenario_creator_kwargs = {
    # scenario tree data
    'nodes': data.nodes,
    'parent': data.parent,
    'node_prob': data.node_prob,
    'scen_prob': data.scen_prob,
    # scenario instance data
    'num_days': data.num_days,
    'cost': data.cost,
    'revenue': data.revenue,
    'demand': data.demand
}

args = [cli_args,
        scenario_creator,
        scenario_denouement,
        scenario_names]
kwargs = {'scenario_creator_kwargs': scenario_creator_kwargs,
          'all_nodenames': all_nodenames}

# hub setup
hub_dict = vanilla.ph_hub(*args, **kwargs)

# spoke setup
spoke_dicts = list()

# primal spokes
if cli_args.with_xhatlooper:
    spoke_dicts.append(vanilla.xhatlooper_spoke(*args, **kwargs))

if cli_args.with_xhatshuffle:
    spoke_dicts.append(vanilla.xhatshuffle_spoke(*args, **kwargs))

# dual spokes
if cli_args.with_lagrangian:
    spoke_dicts.append(vanilla.lagrangian_spoke(*args, **kwargs))

# solve
spcomm, opt_dict = sputils.spin_the_wheel(hub_dict, spoke_dicts)
sputils.write_spin_the_wheel_first_stage_solution(spcomm, opt_dict, 'solution.csv')
sputils.write_spin_the_wheel_tree_solution(spcomm, opt_dict, 'solution')

