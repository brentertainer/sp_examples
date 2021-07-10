CROPS = ['Wheat', 'Corn', 'Sugar Beets']

CROPS_BY_QUANTITY_RANGES = [
    ('Wheat',          0, None),
    ('Corn',           0, None),
    ('Sugar Beets',    0, 6000),
    ('Sugar Beets', 6000, None)
]

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
    ('Wheat', 'Above'):          3.0,
    ('Corn', 'Above'):           3.6,
    ('Sugar Beets', 'Above'):   24.0,
    ('Wheat', 'Average'):        2.5,
    ('Corn', 'Average'):         3.0,
    ('Sugar Beets', 'Average'): 20.0,
    ('Wheat', 'Below'):          2.0,
    ('Corn', 'Below'):           2.4,
    ('Sugar Beets', 'Below'):   16.0
}

PROBABILITY = {
    'Above':   1 / 3,
    'Average': 1 / 3,
    'Below':   1 / 3
}
