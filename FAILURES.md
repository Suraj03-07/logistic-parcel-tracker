# Failures and recovery log

Every bug, surprise and wrong turn, in the order they happened. Format: what happened, what I believed, what I did, what I learned.

## Data cleaning

### 1. The orders table showed 5,900 rows instead of 99,441
- **What happened:** `orders.shape` printed about 5,900 rows.
- **What I believed:** the uploaded file was cut short.
- **What I did:** counted the raw lines of the file (99,442, the header plus 99,441 orders), so the file was fine. A variable had been overwritten by an earlier cell. Reloaded the file.
- **Learned:** stale notebook variables look like data problems. When a number looks wrong, restart and use Runtime > Run all.

### 2. Wrong brackets in a drop-rows line
- **What happened:** my first attempt to drop rows missing two columns used `df['a', df['b']]`, which pandas reads as one odd key.
- **What I did:** used `dropna(subset=[...])` with a list of column names.
- **Learned:** `dropna` only sees empty cells, not impossible ones. Those need an explicit rule.

### 3. Missing values hiding as numbers
- **What happened:** 4 products had a weight of 0 g, and summing weights per order would have turned all-missing orders into a weight of 0.
- **What I believed:** a column with only 2 missing values was clean.
- **What I did:** set impossible zeros to missing, and summed with `min_count=1` so an order with no weights stays missing instead of becoming 0.
- **Learned:** ask whether a value can truly be 0.

### 4. Impossible dates passed through the first cleaning
- **What happened:** after dropping missing values, 23 orders still had carrier pickup after customer delivery and 165 had pickup before purchase.
- **What I believed:** the missing-value cleaning had already removed bad rows.
- **What I did:** dropped the 188 rows (0.2%).
- **Learned:** missing and impossible are different problems.

### 5. Joining items would have duplicated orders
- **What happened:** the items table has one row per item (up to 21 per order).
- **What I did:** collapsed it to one row per order before joining, and checked that the row count was the same before and after every join.
- **Learned:** row counts after a join are the cheapest bug detector.
- **Still unknown:** I never counted how many orders contain more than one seller.

### 6. An impossible distance of 8,677 km
- **What happened:** the largest straight-line distance was 8,677 km, which is impossible inside Brazil.
- **What I believed:** zip-code coordinates were reliable.
- **What I did:** the geolocation file has about 1M rows for 19,015 zip prefixes, some with wrong coordinates. Averaged per prefix, set distances above 4,500 km to missing, then filled the 482 affected orders with the median and added a `distance_missing` flag.
- **Learned:** even a reference table needs an audit.

## Modelling

### 7. More features did not help the linear model
- **What happened:** going from 6 to 11 features changed logistic regression PR-AUC from 0.306 to only 0.309.
- **What I believed:** more features would raise the score.
- **What I did:** switched to LightGBM, which can learn curved effects and feature combinations.
- **Learned:** the limit was the model type, not the information. I changed model and features together, so I cannot say exactly how much each contributed.

### 8. I looked at the test set before building a validation set
- **What happened:** I compared the baseline and LightGBM, and scanned thresholds, on the test months. Only then did I notice I had no validation period.
- **What I believed:** that was fine because I had not tuned anything yet.
- **What I did:** built a validation period (Dec 2017 to Feb 2018) inside the training months, retrained on the earlier months, tuned and chose the threshold there, and scored the test months once more at the end.
- **Learned:** decide the train, validation and test split before the first score. The first-pass and final test PR-AUC (0.391 and 0.384) are close, but the test set is no longer fully untouched.

### 9. The theoretical threshold was not the best one
- **What happened:** the cost argument says 0.2. On the data, 0.12 (test, first pass) and 0.15 (validation) saved more.
- **Why:** the late rate drifts. Validation months were 10.3% late and the training months 6.3%, so the model underestimates the risk.
- **Learned:** a threshold chosen on past months is only a starting point.

### 10. The validation score was much lower than the test score
- **What happened:** validation PR-AUC 0.28 to 0.30, test PR-AUC 0.38.
- **Why:** the validation months include the hard February 2018 spike, and the model had seen less data when it was scored there. The final model was also retrained on more recent months.
- **Learned:** scores from different periods are not comparable. Report each with its own late rate.

### 11. Hyperparameter tuning gave a small gain
- **What happened:** the best of 20 random combinations raised validation PR-AUC from 0.284 to 0.300.
- **What I did:** kept the search small on purpose, because validation holds only about 2,000 late parcels and a large search would overfit it.
- **Learned:** the gain is small and was selected on validation, so it is slightly optimistic.

### 12. The better model barely changed the money result
- **What happened:** at the same 3,086 flagged parcels, LightGBM caught 1,104 late parcels against 1,069 for the baseline, so a saving of 4,868 against 4,518 (+8%), although PR-AUC was 24% higher.
- **Learned:** the saving comes mostly from the threshold and the cost assumptions, not the model type. This is reported as it is.

## Business assumptions

### 13. "Every warning works" was too optimistic
- **What happened:** the 4,868 saving assumes every intervention prevents the delay.
- **What I found:** if only half work, the same plan loses about 652. It breaks even at about 56% success.
- **What I did:** reported the break-even rate for the whole plan and for each risk tier, and recommended a pilot to measure the real success rate.
- **Learned:** state the assumption next to the number every time.

### 14. The model missed the biggest spike
- **What happened:** March 2018 (21.4% late) accounts for about 45% of all missed late parcels. Quiet June lost money (-56).
- **Why:** the features describe one parcel at a time. Nothing tells the model that the system is overloaded.
- **Learned:** this needs features about current load. They are listed under "with more time" in the README.

### 15. Shifted inputs, but a working model
- **What happened:** PSI flagged `promised_days` (0.275) and `freight` (0.282) as shifted, although the model still performed well on test.
- **What I did:** reworded the alert rule: PSI above 0.25 means investigate, and retrain only if the real precision also drops.
- **Learned:** PSI shows that inputs changed, not that quality fell.

## Engineering

### 16. `NameError: pd is not defined` inside `explain.py`
- **What happened:** the notebook had pandas imported, but the error came from inside the module file.
- **What I did:** made sure the file starts with `import pandas as pd`, then reloaded the module with `importlib.reload`. Most likely Python had kept an older cached version of the module.
- **Learned:** after editing a file that a notebook has already imported, reload it or restart the session.

### 17. Moving files into the repo folder broke the paths
- **What happened:** after moving the scripts into `src/` and the model into `models/`, the default model paths and the test's file paths pointed to the wrong places.
- **What I did:** changed the default paths in `predict.py`, added `tests/conftest.py` so tests can import from `src/`, and made the test locate files from the repo root.
- **Learned:** run the tests and the script again after every restructuring.
