import os
import joblib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import pandas as pd
from labels import make_label
from explain import tier_and_action

FORBIDDEN = ['order_delivered_customer_date', 'is_late', 'order_status',
             'order_id', 'customer_id', 'seller_id']


def test_label_late_and_on_time():
    est = pd.Series(pd.to_datetime(['2018-01-10', '2018-01-10']))
    got = pd.Series(pd.to_datetime(['2018-01-12', '2018-01-08']))
    assert list(make_label(got, est)) == [True, False]


def test_label_exactly_on_promise_is_not_late():
    est = pd.Series(pd.to_datetime(['2018-01-10 00:00:00']))
    assert not make_label(est, est).iloc[0]


def test_no_leaky_columns_in_features():
    features = joblib.load(os.path.join(ROOT, 'models', 'model_meta.joblib'))['features']
    leaked = [c for c in FORBIDDEN if c in features]
    assert leaked == []


def test_tier_boundaries():
    assert tier_and_action(0.149)[0] == 'low'
    assert tier_and_action(0.15)[0] == 'medium'
    assert tier_and_action(0.30)[0] == 'high'
    assert tier_and_action(0.50)[0] == 'very high'
