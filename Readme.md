# Pack Smart: Knapsack Algorithm Explorer

A small website (plus a Python version) that solves one real-world problem, the **0/1 Knapsack Problem**, with five different algorithms and compares them on the user's own input.

**Live site:** https://YOUR-USERNAME.github.io/pack-smart/
**Source code:** https://github.com/YOUR-USERNAME/pack-smart

## The problem

You have a bag with a weight limit and a list of items. Each item has a weight and a value. Choose the items that fit in the bag and give the highest total value. Each item is taken whole or left behind.

## Why it matters

Loading delivery vans, choosing ads for a budget, picking projects for limited hours and cutting cargo for a flight are all knapsack problems.

## What the program computes

For the items and capacity you enter, it finds the chosen items, total weight and total value, shows how much work each algorithm did, and checks every result against the best value found. A map shows the pickup trip distance (depot to every packed item and back).

## Algorithms

| Approach | Time | Space | Always optimal? |
|---|---|---|---|
| Brute force | O(2^n · n) | O(n) | Yes |
| Greedy (best value per weight) | O(n log n) | O(n) | No |
| Dynamic programming | O(n · W) | O(n · W) | Yes |
| Backtracking with a bound | O(2^n) worst case | O(n) | Yes |
| Divide and conquer (split in halves, merge) | O(2^(n/2) · n) | O(2^(n/2)) | Yes |

`n` = number of items, `W` = bag capacity.

## How each one works

- **Brute force:** try all 2^n subsets, drop the ones that are too heavy, keep the highest value.
- **Greedy:** sort by value ÷ weight and take each item if it still fits. Fast, but it never reconsiders, so it can miss the best bag.
- **Dynamic programming:** fill a table where cell (i, c) is the best value using the first i items with capacity c. Each cell is the larger of "skip item i" and "take item i plus the cell above at c − weight". Walk back up the table to find the chosen items.
- **Backtracking with a bound:** search take/skip choices item by item. At each step estimate the best value still reachable using fractions of the remaining items. If the estimate cannot beat the best bag so far, prune that branch.
- **Divide and conquer:** split the items into two halves and list every subset of each half. Sort the right subsets by weight and keep a running best value. For each left subset, binary-search the heaviest right subset that still fits and combine the two.

## Input and validation

- Item name: required, unique, up to 20 characters.
- Weight and value: whole numbers from 1 to 999.
- Capacity: a whole number from 1 to 1000.
- Maximum 15 items.
- Any invalid input shows a clear message and is not added.

## Map and distance

Each item gets a location on a 10 km × 7 km map with the depot in the middle. The trip visits every packed item by always driving to the nearest unvisited one, then returns to the depot. This is a nearest-neighbour heuristic, so it is not guaranteed to be the shortest possible trip. On the website you can drag pins to see the distance change.

## Run it

**Website:** open `index.html` in any browser. No install needed.

**Python:**

```bash
python pack_smart.py          # interactive menu
python pack_smart.py --demo   # sample data, no typing
```

Optional: `pip install matplotlib` to also save `pickup_map.png`.

## Files

- `pack_smart.py`: the same algorithms in Python
- `README.md`: this file

## Team

| Name | Contribution |
|---|---|
| Member 1 |Shaik Abdulkalam |
| Member 2 |Shaik Anas hussain|
| Member 3 |Naveed khan |
