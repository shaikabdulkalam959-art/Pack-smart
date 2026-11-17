#!/usr/bin/env python3
"""Pack Smart: 0/1 Knapsack solved five ways, plus a pickup-trip distance on a 10 km x 7 km map.

Run:  python pack_smart.py          (interactive menu)
      python pack_smart.py --demo   (sample data, no typing)
Optional: pip install matplotlib to also save a map image (pickup_map.png).
"""
import math
import random
import sys
import time
from bisect import bisect_right

MAX_ITEMS, MAX_NUM, MAX_CAP = 15, 999, 1000
DEPOT = (5.0, 3.5)  # km, middle of the 10 x 7 map


# ---------------------------------------------------------------- data
class Item:
    def __init__(self, name, weight, value, x=None, y=None):
        self.name, self.weight, self.value = name, weight, value
        self.x = x if x is not None else random.uniform(0.8, 9.2)
        self.y = y if y is not None else random.uniform(0.8, 6.2)

    @property
    def ratio(self):
        return self.value / self.weight


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def total(items, ids):
    return sum(items[i].weight for i in ids), sum(items[i].value for i in ids)


# ---------------------------------------------------------------- validation
def read_int(text, lo, hi, label):
    """Return (number, None) or (None, error message)."""
    text = text.strip()
    if not text.isdigit():
        return None, f"{label} must be a whole number from {lo} to {hi}."
    n = int(text)
    if not lo <= n <= hi:
        return None, f"{label} must be a whole number from {lo} to {hi}."
    return n, None


def validate_item(items, name, w_text, v_text):
    name = name.strip()
    if not name:
        return None, "Item name cannot be empty."
    if any(i.name.lower() == name.lower() for i in items):
        return None, f"'{name}' is already in the list. Use a different name."
    w, err = read_int(w_text, 1, MAX_NUM, "Weight")
    if err:
        return None, err
    v, err = read_int(v_text, 1, MAX_NUM, "Value")
    if err:
        return None, err
    if len(items) >= MAX_ITEMS:
        return None, f"Maximum is {MAX_ITEMS} items."
    return Item(name[:20], w, v), None


# ---------------------------------------------------------------- 1 brute force  O(2^n * n)
def brute_force(items, cap):
    n, best, best_mask = len(items), -1, 0
    for mask in range(1 << n):                       # every subset
        w = v = 0
        for i in range(n):
            if mask >> i & 1:
                w += items[i].weight
                v += items[i].value
        if w <= cap and v > best:
            best, best_mask = v, mask
    ids = [i for i in range(n) if best_mask >> i & 1]
    return ids, f"{1 << n} combinations checked"


# ---------------------------------------------------------------- 2 greedy  O(n log n)
def greedy(items, cap):
    order = sorted(range(len(items)), key=lambda i: items[i].ratio, reverse=True)
    w, ids = 0, []
    for i in order:                                  # best value per weight first
        if w + items[i].weight <= cap:
            w += items[i].weight
            ids.append(i)
    return sorted(ids), f"{len(items)} items considered"


# ---------------------------------------------------------------- 3 dynamic programming  O(n*W)
def dynamic_programming(items, cap):
    n = len(items)
    T = [[0] * (cap + 1) for _ in range(n + 1)]      # T[i][c] = best value, first i items, capacity c
    for i in range(1, n + 1):
        it = items[i - 1]
        for c in range(cap + 1):
            T[i][c] = T[i - 1][c]                    # skip item
            if it.weight <= c:                       # or take it
                T[i][c] = max(T[i][c], T[i - 1][c - it.weight] + it.value)
    ids, c = [], cap
    for i in range(n, 0, -1):                        # walk back to find chosen items
        if T[i][c] != T[i - 1][c]:
            ids.append(i - 1)
            c -= items[i - 1].weight
    return sorted(ids), f"{n * cap} table cells filled"


# ---------------------------------------------------------------- 4 backtracking + bound  O(2^n) worst
def backtracking(items, cap):
    order = sorted(range(len(items)), key=lambda i: items[i].ratio, reverse=True)
    n = len(order)
    best, best_set, nodes, pruned = 0, [], 0, 0

    def bound(k, w, v):                              # optimistic estimate using fractions
        room, b = cap - w, v
        for j in range(k, n):
            it = items[order[j]]
            if it.weight <= room:
                room -= it.weight
                b += it.value
            else:
                return b + it.value * room / it.weight
        return b

    def go(k, w, v, chosen):
        nonlocal best, best_set, nodes, pruned
        nodes += 1
        if v > best:
            best, best_set = v, chosen[:]
        if k == n:
            return
        if bound(k, w, v) <= best:                   # cannot beat best: prune
            pruned += 1
            return
        it = items[order[k]]
        if w + it.weight <= cap:                     # take
            chosen.append(order[k])
            go(k + 1, w + it.weight, v + it.value, chosen)
            chosen.pop()
        go(k + 1, w, v, chosen)                      # skip

    go(0, 0, 0, [])
    return sorted(best_set), f"{nodes} nodes visited, {pruned} branches pruned"


# ---------------------------------------------------------------- 5 divide and conquer  O(2^(n/2) * n)
def divide_and_conquer(items, cap):
    n = len(items)
    h = n // 2

    def subsets(lo, hi):                             # conquer: all subsets of one half
        out = []
        for m in range(1 << (hi - lo)):
            w = sum(items[lo + i].weight for i in range(hi - lo) if m >> i & 1)
            v = sum(items[lo + i].value for i in range(hi - lo) if m >> i & 1)
            out.append((w, v, m))
        return out

    left, right = subsets(0, h), subsets(h, n)       # divide into two halves
    right.sort()                                     # by weight
    weights = [r[0] for r in right]
    best_idx, run = [], 0
    for i, r in enumerate(right):                    # running best value so far
        if r[1] > right[run][1]:
            run = i
        best_idx.append(run)

    best, pair = -1, None
    for lw, lv, lm in left:                          # merge step
        if lw > cap:
            continue
        pos = bisect_right(weights, cap - lw) - 1    # heaviest right subset that still fits
        r = right[best_idx[pos]]
        if lv + r[1] > best:
            best, pair = lv + r[1], (lm, r[2])
    lm, rm = pair
    ids = [i for i in range(h) if lm >> i & 1] + [h + i for i in range(n - h) if rm >> i & 1]
    return ids, f"{len(left) + len(right)} half-subsets built, {len(left)} merge lookups"


ALGOS = {
    "1": ("Brute force", "O(2^n * n)", "O(n)", True, brute_force,
          ["List every subset of items.", "Reject subsets heavier than the capacity.",
           "Keep the highest-value subset seen.", "Return it."]),
    "2": ("Greedy", "O(n log n)", "O(n)", False, greedy,
          ["Compute value / weight for each item.", "Sort best ratio first.",
           "Take each item if it still fits.", "Stop at the end of the list."]),
    "3": ("Dynamic programming", "O(n * W)", "O(n * W)", True, dynamic_programming,
          ["Table[i][c] = best value using first i items with capacity c.",
           "Each cell = max(skip item, take item + cell above at c - weight).",
           "Bottom-right cell is the best value.", "Walk back up to see which items were taken."]),
    "4": ("Backtracking + bound", "O(2^n) worst", "O(n)", True, backtracking,
          ["Sort by value / weight.", "Branch on take / skip for each item.",
           "Estimate the best reachable value with fractions of remaining items.",
           "Prune the branch if the estimate cannot beat the best bag."]),
    "5": ("Divide and conquer", "O(2^(n/2) * n)", "O(2^(n/2))", True, divide_and_conquer,
          ["Divide items into a left half and a right half.", "Conquer: list all subsets of each half.",
           "Sort right subsets by weight, track the best value so far.",
           "Merge: for each left subset, binary-search the heaviest right subset that fits."]),
}


# ---------------------------------------------------------------- map distance
def pickup_trip(items, ids):
    """Nearest-neighbour trip: depot -> every packed item -> depot. Returns (order, km)."""
    left, cur, order, km = list(ids), DEPOT, [], 0.0
    while left:
        nxt = min(left, key=lambda i: dist(cur, (items[i].x, items[i].y)))
        km += dist(cur, (items[nxt].x, items[nxt].y))
        cur = (items[nxt].x, items[nxt].y)
        left.remove(nxt)
        order.append(nxt)
    return order, km + (dist(cur, DEPOT) if order else 0.0)


def ascii_map(items, ids):
    cols, rows = 50, 14
    grid = [["." for _ in range(cols)] for _ in range(rows)]
    def put(p, ch):
        c = min(cols - 1, int(p[0] / 10 * cols)); r = min(rows - 1, int(p[1] / 7 * rows))
        grid[r][c] = ch
    for i, it in enumerate(items):
        put((it.x, it.y), chr(65 + i) if i in ids else chr(97 + i))
    put(DEPOT, "D")
    print("\n  Map 10 km x 7 km   D = depot, CAPITAL = packed, lower-case = left behind")
    for row in grid:
        print("  " + "".join(row))


def save_png(items, ids, order):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    fig, ax = plt.subplots(figsize=(8, 5.6))
    path = [DEPOT] + [(items[i].x, items[i].y) for i in order] + [DEPOT]
    for a, b in zip(path, path[1:]):
        ax.plot([a[0], b[0]], [a[1], b[1]], color="#c2410c")
        ax.text((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, f"{dist(a, b):.1f} km", fontsize=8)
    for i, it in enumerate(items):
        ax.scatter(it.x, it.y, color="#c2410c" if i in ids else "grey", s=90, zorder=3)
        ax.annotate(it.name, (it.x, it.y), textcoords="offset points", xytext=(0, 9), ha="center", fontsize=8)
    ax.scatter(*DEPOT, marker="s", color="black", s=110, zorder=3)
    ax.set_xlim(0, 10); ax.set_ylim(7, 0); ax.grid(True, alpha=.3); ax.set_title("Pickup map (km)")
    fig.savefig("pickup_map.png", dpi=120, bbox_inches="tight")
    print("  Map image saved to pickup_map.png")


# ---------------------------------------------------------------- run + report
def run(key, items, cap, best_value=None):
    name, tm, sp, exact, fn, steps = ALGOS[key]
    t0 = time.perf_counter()
    ids, work = fn(items, cap)
    ms = (time.perf_counter() - t0) * 1000
    w, v = total(items, ids)
    return dict(key=key, name=name, time=tm, space=sp, exact=exact, steps=steps,
                ids=ids, w=w, v=v, work=work, ms=ms)


def show(r, items, cap, best):
    print(f"\n=== {r['name']} ===")
    print(f"Time: {r['time']}   Space: {r['space']}   {'Always optimal' if r['exact'] else 'Not always optimal'}")
    print("How it works:")
    for i, s in enumerate(r["steps"], 1):
        print(f"  {i}. {s}")
    print("Result:")
    for i in r["ids"]:
        print(f"  - {items[i].name} (weight {items[i].weight}, value {items[i].value})")
    print(f"  Total value {r['v']}, weight {r['w']}/{cap}")
    print("  " + ("Matches the best value found." if r["v"] == best else f"{best - r['v']} short of the best ({best})."))
    order, km = pickup_trip(items, r["ids"])
    if order:
        route = " -> ".join(["Depot"] + [items[i].name for i in order] + ["Depot"])
        print(f"  Pickup trip: {km:.2f} km  ({route})")
    print(f"  Work: {r['work']}.  Run time: {r['ms']:.3f} ms")


def compare(items, cap):
    results = [run(k, items, cap) for k in ALGOS]
    best = max(r["v"] for r in results)
    print(f"\n{'Approach':<22}{'Time':<18}{'Value':<8}{'Weight':<10}{'Trip km':<10}{'Run ms'}")
    for r in results:
        km = pickup_trip(items, r["ids"])[1]
        print(f"{r['name']:<22}{r['time']:<18}{str(r['v']) + (' *' if r['v'] == best else ''):<8}"
              f"{str(r['w']) + '/' + str(cap):<10}{km:<10.2f}{r['ms']:.3f}")
    print("* = best value. The four exact methods must agree; greedy may fall short.")
    return results, best


SAMPLE = [("Laptop", 5, 12), ("Camera", 3, 8), ("Water bottle", 2, 3), ("Jacket", 4, 6),
          ("Book", 1, 2), ("Snacks", 2, 4), ("Tripod", 6, 7), ("Speaker", 3, 9)]


def load_sample():
    return [Item(n, w, v) for n, w, v in SAMPLE]


def print_intro():
    print("PACK SMART - 0/1 Knapsack, five algorithms")
    print("Problem : choose items that fit a weight limit and give the highest total value.")
    print("Why     : loading vans, budgeting ads, choosing projects, cargo planning.")
    print("Computes: chosen items, weight, value, pickup distance on a map, and work done per algorithm.\n")


def show_items(items, cap):
    print(f"\nCapacity: {cap}")
    if not items:
        print("  (no items yet)")
    for i, it in enumerate(items, 1):
        d = dist(DEPOT, (it.x, it.y))
        print(f"  {i:>2}. {it.name:<20} weight {it.weight:<4} value {it.value:<4} {d:.1f} km from depot")


def main():
    print_intro()
    items, cap = load_sample(), 15
    if "--demo" in sys.argv:
        results, best = compare(items, cap)
        for r in results:
            show(r, items, cap, best)
        ascii_map(items, set(results[4]["ids"]))
        return
    while True:
        show_items(items, cap)
        print("\n[a] add item  [r] remove item  [c] set capacity  [s] sample  [x] random 8  [z] clear")
        print("[1-5] show one algorithm  [t] compare all + map  [q] quit")
        ch = input("> ").strip().lower()
        if ch == "q":
            break
        elif ch == "a":
            it, err = validate_item(items, input("Name: "), input("Weight: "), input("Value: "))
            if err:
                print("  ! " + err)
            else:
                items.append(it)
        elif ch == "r":
            n, err = read_int(input("Item number to remove: "), 1, max(len(items), 1), "Item number")
            if err or not items:
                print("  ! " + (err or "Nothing to remove."))
            else:
                items.pop(n - 1)
        elif ch == "c":
            n, err = read_int(input("Capacity: "), 1, MAX_CAP, "Capacity")
            if err:
                print("  ! " + err)
            else:
                cap = n
        elif ch == "s":
            items, cap = load_sample(), 15
        elif ch == "x":
            names = ["Tent", "Stove", "Lamp", "Rope", "Radio", "Map", "Pot", "Boots"]
            items = [Item(nm, random.randint(1, 9), random.randint(1, 20)) for nm in names]
            cap = 20
        elif ch == "z":
            items = []
        elif ch in ALGOS or ch == "t":
            if not items:
                print("  ! Add at least one item first.")
                continue
            results, best = compare(items, cap) if ch == "t" else ([run(k, items, cap) for k in ALGOS], None)
            best = max(r["v"] for r in results)
            if ch == "t":
                dc = results[4]
                ascii_map(items, set(dc["ids"]))
                save_png(items, set(dc["ids"]), pickup_trip(items, dc["ids"])[0])
            else:
                r = next(x for x in results if x["key"] == ch)
                show(r, items, cap, best)
                ascii_map(items, set(r["ids"]))
        else:
            print("  ! Unknown choice.")


if __name__ == "__main__":
    main()
