#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LeetCode Template (single file)
===============================

Usage:
- In LeetCode editor: paste everything (or remove __main__ part).
- Implement the required method(s) in class Solution.

Notes:
- Turn DEBUG = False before submitting (or keep, it won't print unless called).
"""

from __future__ import annotations

from dataclasses import dataclass
from collections import deque, defaultdict, Counter
from typing import (
    Any,
    Callable,
    DefaultDict,
    Deque,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    TypeVar,
)
import bisect
import heapq
import math

T = TypeVar("T")

# ----------------------------
# Global toggles / constants
# ----------------------------
DEBUG: bool = False
INF: int = 10**18

# 4-dir / 8-dir for grid problems
DIR4: Tuple[Tuple[int, int], ...] = ((1, 0), (-1, 0), (0, 1), (0, -1))
DIR8: Tuple[Tuple[int, int], ...] = (
    (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (1, -1), (-1, 1), (-1, -1),
)

def dbg(*args: Any) -> None:
    """Debug print (safe to leave in code; controlled by DEBUG)."""
    if DEBUG:
        print(*args)


# ============================================================
# Common LeetCode data structures (ListNode / TreeNode)
# ============================================================

@dataclass
class ListNode:
    val: int = 0
    next: Optional["ListNode"] = None


@dataclass
class TreeNode:
    val: int = 0
    left: Optional["TreeNode"] = None
    right: Optional["TreeNode"] = None


# ============================================================
# Useful DS / helpers
# ============================================================

class DSU:
    """Disjoint Set Union (Union-Find) with path compression + union by size."""
    def __init__(self, n: int):
        self.p = list(range(n))
        self.sz = [1] * n

    def find(self, x: int) -> int:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.sz[ra] < self.sz[rb]:
            ra, rb = rb, ra
        self.p[rb] = ra
        self.sz[ra] += self.sz[rb]
        return True


class Fenwick:
    """
    Fenwick Tree (BIT): prefix sums.
    - add(i, delta): O(log n)
    - sum(i): sum of [0..i], O(log n)
    - range_sum(l,r): sum of [l..r], O(log n)
    """
    def __init__(self, n: int):
        self.n = n
        self.bit = [0] * (n + 1)

    def add(self, i: int, delta: int) -> None:
        i += 1
        while i <= self.n:
            self.bit[i] += delta
            i += i & -i

    def sum(self, i: int) -> int:
        i += 1
        s = 0
        while i > 0:
            s += self.bit[i]
            i -= i & -i
        return s

    def range_sum(self, l: int, r: int) -> int:
        if l > r:
            return 0
        return self.sum(r) - (self.sum(l - 1) if l > 0 else 0)


class SegTreeSum:
    """Segment Tree: range sum + point update."""
    def __init__(self, a: List[int]):
        if not a:
            raise ValueError("SegTreeSum requires non-empty array")
        self.n = len(a)
        self.seg = [0] * (4 * self.n)
        self._build(1, 0, self.n - 1, a)

    def _build(self, idx: int, l: int, r: int, a: List[int]) -> None:
        if l == r:
            self.seg[idx] = a[l]
            return
        m = (l + r) // 2
        self._build(idx * 2, l, m, a)
        self._build(idx * 2 + 1, m + 1, r, a)
        self.seg[idx] = self.seg[idx * 2] + self.seg[idx * 2 + 1]

    def update(self, pos: int, val: int) -> None:
        def go(idx: int, l: int, r: int) -> None:
            if l == r:
                self.seg[idx] = val
                return
            m = (l + r) // 2
            if pos <= m:
                go(idx * 2, l, m)
            else:
                go(idx * 2 + 1, m + 1, r)
            self.seg[idx] = self.seg[idx * 2] + self.seg[idx * 2 + 1]
        go(1, 0, self.n - 1)

    def query(self, ql: int, qr: int) -> int:
        def go(idx: int, l: int, r: int) -> int:
            if ql <= l and r <= qr:
                return self.seg[idx]
            m = (l + r) // 2
            res = 0
            if ql <= m:
                res += go(idx * 2, l, m)
            if qr > m:
                res += go(idx * 2 + 1, m + 1, r)
            return res
        return go(1, 0, self.n - 1)


class TrieNode:
    __slots__ = ("ch", "end")
    def __init__(self):
        self.ch: Dict[str, TrieNode] = {}
        self.end: bool = False


class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, w: str) -> None:
        cur = self.root
        for c in w:
            if c not in cur.ch:
                cur.ch[c] = TrieNode()
            cur = cur.ch[c]
        cur.end = True

    def search(self, w: str) -> bool:
        cur = self.root
        for c in w:
            if c not in cur.ch:
                return False
            cur = cur.ch[c]
        return cur.end

    def starts_with(self, p: str) -> bool:
        cur = self.root
        for c in p:
            if c not in cur.ch:
                return False
            cur = cur.ch[c]
        return True


# ============================================================
# Algorithm templates
# ============================================================

def bfs_grid_shortest(
    grid: List[List[int]],
    sr: int, sc: int,
    passable: Callable[[int, int], bool],
) -> List[List[int]]:
    """
    Grid BFS shortest path distance map.
    grid: any shape, use passable(r,c) to check cells you can step on.
    returns dist[][] with -1 = unreachable.
    """
    R, C = len(grid), len(grid[0]) if grid else 0
    dist = [[-1] * C for _ in range(R)]
    q: Deque[Tuple[int, int]] = deque()
    if 0 <= sr < R and 0 <= sc < C and passable(sr, sc):
        dist[sr][sc] = 0
        q.append((sr, sc))

    while q:
        r, c = q.popleft()
        for dr, dc in DIR4:
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C and dist[nr][nc] == -1 and passable(nr, nc):
                dist[nr][nc] = dist[r][c] + 1
                q.append((nr, nc))
    return dist


def dijkstra(
    g: Dict[int, List[Tuple[int, int]]],
    s: int
) -> Dict[int, int]:
    """Dijkstra for non-negative weighted graph. g[u] = [(v,w), ...]."""
    dist: Dict[int, int] = {s: 0}
    pq: List[Tuple[int, int]] = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist.get(u, INF):
            continue
        for v, w in g.get(u, []):
            nd = d + w
            if nd < dist.get(v, INF):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


def topo_sort(n: int, edges: List[Tuple[int, int]]) -> Optional[List[int]]:
    """Kahn topo sort. Returns order or None if has cycle."""
    g: DefaultDict[int, List[int]] = defaultdict(list)
    indeg = [0] * n
    for u, v in edges:
        g[u].append(v)
        indeg[v] += 1
    q = deque([i for i in range(n) if indeg[i] == 0])
    order: List[int] = []
    while q:
        u = q.popleft()
        order.append(u)
        for v in g[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    return order if len(order) == n else None


def lis_length(nums: Sequence[int]) -> int:
    """LIS length in O(n log n)."""
    tails: List[int] = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def knapsack_01(weights: Sequence[int], values: Sequence[int], cap: int) -> int:
    """0/1 knapsack, O(n*cap) time, O(cap) space."""
    dp = [0] * (cap + 1)
    for w, val in zip(weights, values):
        for c in range(cap, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + val)
    return dp[cap]


def kmp_build(p: str) -> List[int]:
    """KMP prefix function."""
    pi = [0] * len(p)
    j = 0
    for i in range(1, len(p)):
        while j > 0 and p[i] != p[j]:
            j = pi[j - 1]
        if p[i] == p[j]:
            j += 1
            pi[i] = j
    return pi


def kmp_search(s: str, p: str) -> int:
    """Return first index of p in s, else -1."""
    if p == "":
        return 0
    pi = kmp_build(p)
    j = 0
    for i, ch in enumerate(s):
        while j > 0 and ch != p[j]:
            j = pi[j - 1]
        if ch == p[j]:
            j += 1
            if j == len(p):
                return i - len(p) + 1
    return -1


def longest_unique_substring(s: str) -> int:
    """Sliding window: longest substring without repeating chars."""
    last: Dict[str, int] = {}
    l = 0
    ans = 0
    for r, ch in enumerate(s):
        if ch in last and last[ch] >= l:
            l = last[ch] + 1
        last[ch] = r
        ans = max(ans, r - l + 1)
    return ans


def next_greater_element(nums: Sequence[int]) -> List[int]:
    """Monotonic stack: next greater element (value), -1 if none."""
    res = [-1] * len(nums)
    st: List[int] = []
    for i, x in enumerate(nums):
        while st and nums[st[-1]] < x:
            res[st.pop()] = x
        st.append(i)
    return res


# ============================================================
# LeetCode Solution skeleton
# ============================================================

class Solution:
    """
    把题目要求的方法写在这里。
    下面给一些常见题型的“占位”方法，你做题时保留需要的，删掉不需要的即可。
    """

    # ---- 数组/哈希 ----
    def twoSum(self, nums: List[int], target: int) -> List[int]:
        """Example: Two Sum (hash map)."""
        mp: Dict[int, int] = {}
        for i, x in enumerate(nums):
            y = target - x
            if y in mp:
                return [mp[y], i]
            mp[x] = i
        return []

    # ---- 二分 ----
    def lowerBound(self, nums: List[int], x: int) -> int:
        """Return first index i with nums[i] >= x."""
        return bisect.bisect_left(nums, x)

    # ---- 图：无权 BFS (示例) ----
    def shortestPathBinaryMatrix(self, grid: List[List[int]]) -> int:
        """
        Example: shortest path in binary matrix (8 directions).
        这里只是示意骨架，具体按题意修改。
        """
        if not grid or not grid[0]:
            return -1
        n = len(grid)
        if grid[0][0] != 0 or grid[n - 1][n - 1] != 0:
            return -1

        q = deque([(0, 0)])
        dist = [[-1] * n for _ in range(n)]
        dist[0][0] = 1
        while q:
            r, c = q.popleft()
            if r == n - 1 and c == n - 1:
                return dist[r][c]
            for dr, dc in DIR8:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0 and dist[nr][nc] == -1:
                    dist[nr][nc] = dist[r][c] + 1
                    q.append((nr, nc))
        return -1


# ============================================================
# Local quick tests (not used by LeetCode)
# ============================================================

def _self_test() -> None:
    global DEBUG
    DEBUG = False

    # Solution.twoSum
    sol = Solution()
    assert sol.twoSum([2, 7, 11, 15], 9) == [0, 1]

    # KMP
    assert kmp_search("abxabcabcaby", "abcaby") == 6
    assert kmp_search("aaaaa", "bba") == -1

    # LIS
    assert lis_length([10, 9, 2, 5, 3, 7, 101, 18]) == 4

    # Knapsack
    assert knapsack_01([2, 1, 3], [4, 2, 3], 4) == 6

    # Monotonic stack
    assert next_greater_element([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]

    # Sliding window
    assert longest_unique_substring("abcabcbb") == 3

    # DSU
    dsu = DSU(4)
    assert dsu.union(0, 1) is True
    assert dsu.union(1, 2) is True
    assert dsu.union(0, 2) is False

    # BIT
    bit = Fenwick(5)
    bit.add(0, 5)
    bit.add(3, 2)
    assert bit.range_sum(0, 3) == 7
    assert bit.range_sum(1, 2) == 0

    # Segment tree
    st = SegTreeSum([1, 3, 5, 7, 9, 11])
    assert st.query(1, 3) == 15
    st.update(1, 10)
    assert st.query(1, 3) == 22

    print("✅ lc_template self-test passed!")


if __name__ == "__main__":
    _self_test()
