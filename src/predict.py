import sys
import argparse
import joblib
from explain import tier_and_action, top_reasons
import pandas as pd

CAT_COLS = ['category', 'seller_state', 'customer_state']
OPTIONAL_EMPTY = ['seller_lat', 'seller_lng', 'customer_lat', 'customer_lng']

# allowed ranges (min, max) for numeric columns
RANGES = {
    'promised_days': (1, 200), 'handoff_days': (0, 150),
    'distance_km': (0, 4500), 'weight_g': (1, 500000),
    'freight': (0, 5000), 'price': (0, 50000),
    'n_items': (1, 100), 'volume_cm3': (1, 5000000),
    'purchase_month': (1, 12), 'purchase_dow': (0, 6),
    'n_sellers': (1, 20),
    'seller_lat': (-35, 6), 'seller_lng': (-75, -30),
    'customer_lat': (-35, 6), 'customer_lng': (-75, -30),
}


def fail(msg):
    print('ERROR:', msg)
    sys.exit(1)


def validate(df, features, categories):
    missing = [c for c in ['order_id'] + features if c not in df.columns]
    if missing:
        fail(f'missing columns: {missing}')

    for c in features:
        if c not in OPTIONAL_EMPTY and df[c].isnull().any():
            fail(f'column {c} has {df[c].isnull().sum()} empty values')

    for c, (lo, hi) in RANGES.items():
        if not pd.api.types.is_numeric_dtype(df[c]):
            fail(f'column {c} must be numeric')
        bad = df[c].notnull() & ((df[c] < lo) | (df[c] > hi))
        if bad.any():
            fail(f'column {c} has {bad.sum()} values outside {lo} to {hi} '
                 f'(first bad order_id: {df.loc[bad, "order_id"].iloc[0]})')

    if df['distance_missing'].dtype != bool:
        fail('column distance_missing must be True/False')

    for c in CAT_COLS:
        unknown = set(df[c].dropna()) - set(categories[c])
        if unknown:
            fail(f'column {c} has labels the model has never seen: {sorted(unknown)[:5]}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', required=True)
    p.add_argument('--output', default='predictions.csv')
    p.add_argument('--model', default='models/logistic_tracker.joblib')
    p.add_argument('--meta', default='models/model_meta.joblib')
    a = p.parse_args()

    model = joblib.load(a.model)
    meta = joblib.load(a.meta)
    features = meta['features']

    df = pd.read_csv(a.input)
    if len(df) == 0:
        fail('input file has no rows')

    validate(df, features, meta['categories'])

    X = df[features].copy()
    for c in CAT_COLS:
        X[c] = pd.Categorical(X[c], categories=meta['categories'][c])

    prob = model.predict_proba(X)[:, 1]
    contrib = model.predict(X, pred_contrib=True)[:, :-1]
    out = df[['order_id']].copy()
    out['late_probability'] = prob.round(4)
    out['flagged'] = prob >= meta['threshold']
    out['risk_tier'] = [tier_and_action(p)[0] for p in prob]
    out['suggested_action'] = [tier_and_action(p)[1] for p in prob]
    out['reasons'] = [top_reasons(X.iloc[k], contrib[k]) if prob[k] >= meta['threshold'] else ''
                      for k in range(len(X))]

    out.to_csv(a.output, index=False)
    print(f'OK: {len(out)} parcels scored, {out["flagged"].sum()} flagged '
          f'(threshold {meta["threshold"]}). Saved to {a.output}')


if __name__ == '__main__':
    main()
