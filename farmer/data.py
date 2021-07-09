CROPS = ['Wheat', 'Corn', 'Sugar Beets']

SCENARIOS = ['Above', 'Average', 'Below']

ACREAGE = 500

PLANTING_COST = {
    # $/acre
    'Wheat':       150,
    'Corn':        230,
    'Sugar Beets': 260
}

SELLING_PRICE = {
    # $/ton
    # each tuple key below is the quantity range (tons) for which price applies
    # a value of None means there is no upper bound on the quantity range
    ('Wheat',          0, None): 170,
    ('Corn',           0, None): 150,
    ('Sugar Beets',    0, 6000):  36,
    ('Sugar Beets', 6000, None):  10
}

PURCHASE_PRICE = {
    # $/ton
    'Wheat':        328,
    'Corn':         210,
    'Sugar Beets': None
}

MIN_REQUIRED = {
    # tons
    'Wheat': 200,
    'Corn':  240,
    'Sugar Beets': 0
}

HARVEST = {
    # i.e., "YIELD" but yield is a reserved word in python
    # tons/acre
    'Above':   {'Wheat':        3.0,
                'Corn':         3.6,
                'Sugar Beets': 24.0},
    'Average': {'Wheat':        2.5,
                'Corn':         3.0,
                'Sugar Beets': 20.0},
    'Below':   {'Wheat':        2.0,
                'Corn':         2.4,
                'Sugar Beets': 16.0},
}

PROBABILITY = {
    'Above':   1 / 3,
    'Average': 1 / 3,
    'Below':   1 / 3
}
