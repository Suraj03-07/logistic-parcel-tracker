# Decision memo: late-parcel warnings

**For:** the head of operations
**Based on:** 6 months of test data (March to August 2018), Olist dataset
**Important:** the money figures use cost numbers I assumed. They are not company data.

## What I recommend

Start a small pilot on the **medium-risk parcels only**: about 12 parcels a day where the model sees a 15% to 30% chance of a late delivery. Send these customers a message before the delay happens. Measure how often this prevents a complaint or a refund. Do not roll the model out to every parcel yet.

## Why

- Over the 6 test months, the model picked 3,086 parcels (about 17 a day). About 1 in 3 of them was really late. Picking at random, only about 1 in 11 would be.
- The model is most sure about a small group. Of the 381 parcels it rated "very high risk", 3 out of 4 were late.
- The medium group is the best place to start: 2,150 parcels, 27% of them late, and a message is cheap. It pays for itself if it prevents the lateness more than 37% of the time.

## Expected benefit and cost

I assumed that a late parcel costs 10 (refund, support, lost customer) and that acting on a flagged parcel costs between 1 (message) and 5 (shipping upgrade).

- If every warning prevented the delay, the model would have saved about **4,868** over 6 months.
- If a warning works only half the time, the same plan would have **lost about 652**.
- The plan across all flagged parcels pays off only if warnings prevent more than about **56%** of the lateness.
- Per group, the break-even is 37% for a message to medium-risk parcels, 72% for priority handling of high-risk parcels and 65% for a shipping upgrade of very-high-risk parcels. For the high-risk group, a cheaper action than priority handling would make more sense.
- A simple scoring method (the baseline) would have saved about 4,518 on the same parcels. The advanced model improves on that by only about 8%.

## What could go wrong

- **Most late parcels are not caught.** 68% of all late parcels were rated "low risk", so the model cannot help with them.
- **Sudden busy periods.** March 2018 had 21% late parcels, and the model caught only 30% of them. More than half of the total saving came from that one month.
- **Quiet months.** In June 2018 (1.4% late) the warnings cost more than they saved.
- **Weak regions.** In Rio Grande do Sul, Minas Gerais and Espirito Santo the model finds very few of the late parcels. In Pernambuco it raises too many false alarms and loses money.
- **The reasons given for each parcel are patterns, not proven causes.** "The customer is in Bahia" means parcels there were often late in the past, not that we know why.

## What I am unsure about

- How often a message, an upgrade or a reroute really prevents a late delivery. The data has no record of this, and the pilot is meant to answer it.
- Whether these patterns will hold in another year. The model learned from only 14 months, and the biggest spike (March 2018) happened once.
- The cost numbers are my own estimates. If a late parcel costs less than 10, the benefit shrinks.

## Next steps

1. Run the pilot for 4 to 6 weeks on the medium-risk group, with a comparison group that gets no message.
2. Check every week what share of the flagged parcels was really late. If it stays below 20% (with at least 50 flagged parcels), the warnings lose money: stop and investigate.
3. Watch whether the inputs change, for example if promised delivery times get shorter, as they did in the test months. This is a signal to investigate, not an automatic reason to retrain.
4. Add information on how busy the warehouses and each seller have been recently, to catch spikes like March 2018.
