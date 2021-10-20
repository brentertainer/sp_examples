CROPS = ['Wheat', 'Corn', 'Sugar Beets']

CROPS_BY_QUANTITY_RANGES = [
    ('Wheat',          0, None),
    ('Corn',           0, None),
    ('Sugar Beets',    0, 6000),
    ('Sugar Beets', 6000, None)
]

SCENARIOS = ['Scen1', 'Scen2', 'Scen3']

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
    ('Wheat', 'Scen1'):          3.0,
    ('Corn', 'Scen1'):           3.6,
    ('Sugar Beets', 'Scen1'):   24.0,
    ('Wheat', 'Scen2'):        2.5,
    ('Corn', 'Scen2'):         3.0,
    ('Sugar Beets', 'Scen2'): 20.0,
    ('Wheat', 'Scen3'):          2.0,
    ('Corn', 'Scen3'):           2.4,
    ('Sugar Beets', 'Scen3'):   16.0
}

PROBABILITY = {
    'Scen1':   1 / 3,
    'Scen2': 1 / 3,
    'Scen3':   1 / 3
}
