import pandas as pd

# (lower bound, tier, suggested action)
TIERS = [
    (0.50, 'very high', 'Upgrade shipping'),
    (0.30, 'high', 'Priority handling or reroute'),
    (0.15, 'medium', 'Send the customer a proactive message'),
    (0.00, 'low', 'No action'),
]

REASONS = {
    'promised_days': lambda v: f'the promised delivery time ({v:.0f} days) leaves little room',
    'handoff_days': lambda v: f'the seller took {v:.1f} days to hand the parcel to the carrier',
    'distance_km': lambda v: f'the parcel has to travel {v:.0f} km',
    'weight_g': lambda v: f'the parcel is heavy ({v / 1000:.1f} kg)',
    'volume_cm3': lambda v: 'the parcel is bulky',
    'freight': lambda v: f'the shipping cost is high ({v:.0f})',
    'n_items': lambda v: f'the order has {v:.0f} items',
    'n_sellers': lambda v: f'the order has items from {v:.0f} sellers',
    'category': lambda v: f'products in the category "{v}" were often late',
    'customer_state': lambda v: f'the customer is in {v}, where parcels were often late',
    'seller_state': lambda v: f'the seller is in {v}, where parcels were often late',
    'purchase_month': lambda v: f'month {v:.0f} was often a late period in the history',
    'purchase_dow': lambda v: 'the day of the week of the order',
}


def tier_and_action(p):
    for low, name, action in TIERS:
        if p >= low:
            return name, action


def top_reasons(row, contrib, n=3):
    # row: one parcel (features), contrib: its feature contributions
    order = sorted(range(len(contrib)), key=lambda k: contrib[k], reverse=True)
    parts = []
    for k in order[:n]:
        if contrib[k] <= 0:
            break
        name, value = row.index[k], row.iloc[k]
        if pd.isnull(value):
            parts.append('the location of the parcel is unknown')
        elif name in REASONS:
            parts.append(REASONS[name](value))
        else:
            parts.append(f'{name} = {value}')
    return '; '.join(parts) if parts else 'no single strong reason'
