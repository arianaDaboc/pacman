"""US2.8: compare the ghosts' search algorithms on fixed start/target pairs. No pygame here.

Run it with:  uv run python -m pacman.experiments.search_comparison
It writes results/search_comparison.csv (one row per pair and algorithm) and
results/search_comparison.tex (the summary table used in section 5.1 of the documentation).
"""

import csv
import random
import statistics
import time
from contextlib import contextmanager

from pacman import config
from pacman.model.maze import Maze, Tile
from pacman.search import astar
from pacman.search.astar import AStar
from pacman.search.bfs import BFS
from pacman.search.dfs import DFS
from pacman.search.greedy import GreedyBestFirst
from pacman.search.path_finder import corridors

PAIR_COUNT = 30  # the description asks for at least 20
SEED = 2026  # fixed, so every run (and every algorithm) uses the same pairs
REPEATS = 50  # each search is timed this many times; the median is kept
RESULTS_DIR = config.ROOT_DIR / "results"

# Pairs chosen by hand because the shortest path goes through the warp tunnel (row 14 of classic.txt).
TUNNEL_PAIRS: list[tuple[Tile, Tile]] = [((3, 14), (24, 14)), ((6, 11), (21, 17)), ((1, 8), (26, 20))]


class AStarPlainManhattan(AStar):
    """A* with the plain Manhattan distance, which does not know about the warp tunnel.

    Only used in this experiment, to answer the question of US2.3: what does the tunnel do to A*?
    The game uses AStar, whose heuristic also measures the way round through the tunnel.
    """

    name = "A* (plain)"

    def find_path(self, maze: Maze, start: Tile, goal: Tile, banned: set[Tile]):
        """Run AStar.find_path with the tunnel ignored by the heuristic."""
        with plain_manhattan():
            return super().find_path(maze, start, goal, banned)


@contextmanager
def plain_manhattan():
    """While active, astar.manhattan ignores the width of the maze, so the tunnel is not counted."""
    original = astar.manhattan
    astar.manhattan = lambda a, b, width=None: original(a, b)
    try:
        yield
    finally:
        astar.manhattan = original


def make_pairs(maze: Maze) -> list[tuple[Tile, Tile]]:
    """Return the fixed start/target pairs: the tunnel pairs, then random corridor pairs."""
    rng = random.Random(SEED)
    tiles = list(corridors(maze))
    pairs = list(TUNNEL_PAIRS)
    while len(pairs) < PAIR_COUNT:
        start, goal = rng.sample(tiles, 2)
        pairs.append((start, goal))
    return pairs


def run_time(finder, maze: Maze, start: Tile, goal: Tile) -> float:
    """Median run time of one search, in milliseconds."""
    times = []
    for _ in range(REPEATS):
        begin = time.perf_counter()
        finder.find_path(maze, start, goal, set())
        times.append((time.perf_counter() - begin) * 1000)
    return statistics.median(times)


def main() -> None:
    """Run every algorithm on every pair, save the raw rows and the summary table, and print the summary."""
    maze = Maze.load(config.MAP_PATH)
    finders = [DFS(), BFS(), AStar(), AStarPlainManhattan(), GreedyBestFirst()]
    pairs = make_pairs(maze)
    rows = []
    for number, (start, goal) in enumerate(pairs, start=1):
        for finder in finders:
            path, expanded = finder.find_path(maze, start, goal, set())
            rows.append(
                {
                    "pair": number,
                    "start": start,
                    "goal": goal,
                    "algorithm": finder.name,
                    "length": len(path),
                    "expanded": expanded,
                    "time_ms": round(run_time(finder, maze, start, goal), 4),
                }
            )

    RESULTS_DIR.mkdir(exist_ok=True)
    with open(RESULTS_DIR / "search_comparison.csv", "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    shortest = {row["pair"]: row["length"] for row in rows if row["algorithm"] == "BFS"}
    lines = [
        r"\begin{tabular}{lrrrr}",
        r"\toprule",
        r"Algorithm & Avg.\ path length & Shortest paths & Avg.\ expanded nodes & Avg.\ time (ms) \\",
        r"\midrule",
    ]
    print(f"{len(pairs)} pairs on {config.MAP_PATH.name}")
    print(f"{'algorithm':10s} {'length':>8s} {'shortest':>9s} {'expanded':>9s} {'time ms':>9s}")
    for finder in finders:
        mine = [row for row in rows if row["algorithm"] == finder.name]
        length = statistics.mean(row["length"] for row in mine)
        optimal = sum(row["length"] == shortest[row["pair"]] for row in mine)
        expanded = statistics.mean(row["expanded"] for row in mine)
        ms = statistics.mean(row["time_ms"] for row in mine)
        print(f"{finder.name:10s} {length:8.1f} {optimal:4d}/{len(pairs):<4d} {expanded:9.1f} {ms:9.3f}")
        name = finder.name.replace("*", r"$^*$").replace("GREEDY", "Greedy best-first")
        name = name.replace("(plain)", "(plain Manhattan)")
        lines.append(f"{name} & {length:.1f} & {optimal}/{len(pairs)} & {expanded:.1f} & {ms:.3f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}"]
    (RESULTS_DIR / "search_comparison.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("\nTunnel pairs (BFS, A*, A* with the plain Manhattan distance):")
    for number, (start, goal) in enumerate(TUNNEL_PAIRS, start=1):
        found = {r["algorithm"]: r for r in rows if r["pair"] == number}
        print(
            f"  {start} -> {goal}: BFS {found['BFS']['length']}, A* {found['A*']['length']}, "
            f"plain {found['A* (plain)']['length']} tiles"
        )


if __name__ == "__main__":
    main()
