#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
algo_lib.py
===========

一个可直接复制的 Python 算法与数据结构模板库（偏“刷题/面试/日常工具”）。
特点：
- 统一注释风格：每个模块说明用途、复杂度、注意点
- 每个算法/数据结构都有最小可用实现
- __main__ 内包含小测试用例（assert）用于自检

建议用法：
- 当“模板库”：复制相应函数/类到题解中
- 当“学习手册”：逐块阅读并运行 __main__ 的测试

Python 版本：3.10+（3.8+ 也通常没问题）
"""

from __future__ import annotations

from dataclasses import dataclass
from collections import deque, defaultdict
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple
import bisect
import heapq
import math


# ============================================================
# 1) 基础数据结构
# ============================================================

# ----------------------------
# 1.1 栈 / 队列
# ----------------------------
# Stack: list.append / list.pop
# Queue: collections.deque.append / deque.popleft


# ----------------------------
# 1.2 链表（手写）
# ----------------------------
@dataclass
class ListNode:
    """单链表节点。"""
    val: int
    nxt: Optional["ListNode"] = None


def build_linked_list(arr: Iterable[int]) -> Optional[ListNode]:
    """
    从可迭代序列构建单链表。
    时间 O(n)，空间 O(n)（节点本身）。
    """
    dummy = ListNode(0)
    cur = dummy
    for x in arr:
        cur.nxt = ListNode(x)
        cur = cur.nxt
    return dummy.nxt


def linked_list_to_list(head: Optional[ListNode]) -> List[int]:
    """链表转 Python list，便于测试。"""
    out: List[int] = []
    cur = head
    while cur:
        out.append(cur.val)
        cur = cur.nxt
    return out


def reverse_linked_list(head: Optional[ListNode]) -> Optional[ListNode]:
    """
    反转单链表（迭代版）。
    时间 O(n)，空间 O(1) 额外空间。
    """
    prev: Optional[ListNode] = None
    cur = head
    while cur:
        nxt = cur.nxt
        cur.nxt = prev
        prev = cur
        cur = nxt
    return prev


# ----------------------------
# 1.3 并查集 DSU / Union-Find
# ----------------------------
class DSU:
    """
    并查集：支持 find/union。
    - 路径压缩 + 按大小合并，均摊近似 O(1)。

    用途：
    - 动态连通性
    - Kruskal 最小生成树
    - 判断是否形成环
    """

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


# ----------------------------
# 1.4 Trie（前缀树）
# ----------------------------
class TrieNode:
    __slots__ = ("children", "end")

    def __init__(self):
        self.children: Dict[str, TrieNode] = {}
        self.end: bool = False


class Trie:
    """
    前缀树：insert / search / starts_with
    - 插入/查询：O(L)，L 为字符串长度
    """

    def __init__(self):
        self.root = TrieNode()

    def insert(self, w: str) -> None:
        cur = self.root
        for ch in w:
            if ch not in cur.children:
                cur.children[ch] = TrieNode()
            cur = cur.children[ch]
        cur.end = True

    def starts_with(self, p: str) -> bool:
        cur = self.root
        for ch in p:
            if ch not in cur.children:
                return False
            cur = cur.children[ch]
        return True

    def search(self, w: str) -> bool:
        cur = self.root
        for ch in w:
            if ch not in cur.children:
                return False
            cur = cur.children[ch]
        return cur.end


# ============================================================
# 2) 排序与二分
# ============================================================

def quicksort_inplace(a: List[int]) -> List[int]:
    """
    快速排序（原地版）。
    平均 O(n log n)，最坏 O(n^2)，空间 O(log n) 递归栈（平均）。
    注意：Python 内置 sort 更快更稳定；此处用于学习/模板。
    """

    def part(l: int, r: int) -> int:
        pivot = a[r]
        i = l
        for j in range(l, r):
            if a[j] <= pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[r] = a[r], a[i]
        return i

    def qs(l: int, r: int) -> None:
        if l >= r:
            return
        p = part(l, r)
        qs(l, p - 1)
        qs(p + 1, r)

    if a:
        qs(0, len(a) - 1)
    return a


def mergesort(a: List[int]) -> List[int]:
    """
    归并排序（稳定）。
    时间 O(n log n)，空间 O(n)。
    """
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    L = mergesort(a[:mid])
    R = mergesort(a[mid:])
    i = j = 0
    out: List[int] = []
    while i < len(L) and j < len(R):
        if L[i] <= R[j]:
            out.append(L[i]); i += 1
        else:
            out.append(R[j]); j += 1
    out.extend(L[i:])
    out.extend(R[j:])
    return out


def binary_search_leftmost_ge(a: Sequence[int], x: int) -> int:
    """
    返回第一个 >= x 的位置（lower_bound）。
    若全都 < x，则返回 len(a)。
    时间 O(log n)。
    """
    return bisect.bisect_left(a, x)


def binary_search_leftmost_gt(a: Sequence[int], x: int) -> int:
    """
    返回第一个 > x 的位置（upper_bound）。
    """
    return bisect.bisect_right(a, x)


# ============================================================
# 3) DFS / BFS / 回溯
# ============================================================

def dfs_reachable(g: Dict[Any, List[Any]], start: Any) -> set:
    """
    DFS：返回从 start 可达的节点集合。
    时间 O(V+E)。
    """
    seen = set()

    def go(u: Any) -> None:
        seen.add(u)
        for v in g.get(u, []):
            if v not in seen:
                go(v)

    go(start)
    return seen


def bfs_shortest_unweighted(g: Dict[Any, List[Any]], s: Any) -> Dict[Any, int]:
    """
    BFS：无权图最短路（从 s 出发到各点的最短边数）。
    时间 O(V+E)。
    """
    dist: Dict[Any, int] = {s: 0}
    q = deque([s])
    while q:
        u = q.popleft()
        for v in g.get(u, []):
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def permutations(nums: List[int]) -> List[List[int]]:
    """
    回溯：全排列。
    时间 O(n * n!)。
    """
    res: List[List[int]] = []
    used = [False] * len(nums)
    path: List[int] = []

    def bt() -> None:
        if len(path) == len(nums):
            res.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            bt()
            path.pop()
            used[i] = False

    bt()
    return res


# ============================================================
# 4) 图算法
# ============================================================

def dijkstra(g: Dict[Any, List[Tuple[Any, int]]], s: Any) -> Dict[Any, int]:
    """
    Dijkstra：非负权最短路。
    g[u] = [(v, w), ...]
    时间 O((V+E) log V)。
    """
    INF = 10**18
    dist: Dict[Any, int] = {s: 0}
    pq: List[Tuple[int, Any]] = [(0, s)]
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


def bellman_ford(n: int, edges: List[Tuple[int, int, int]], s: int) -> Optional[List[int]]:
    """
    Bellman-Ford：可处理负权；可检测负环。
    edges: (u, v, w)
    返回 dist 数组；若存在可达负环则返回 None。
    时间 O(VE)。
    """
    INF = 10**18
    dist = [INF] * n
    dist[s] = 0

    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:
            break

    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            return None
    return dist


def topo_sort(n: int, edges: List[Tuple[int, int]]) -> Optional[List[int]]:
    """
    拓扑排序（Kahn / BFS 入度法）。
    若有环返回 None。
    时间 O(V+E)。
    """
    g = defaultdict(list)
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


def kruskal_mst(n: int, edges: List[Tuple[int, int, int]]) -> Optional[int]:
    """
    Kruskal 最小生成树（无向图）。
    edges: (w, u, v)
    返回 MST 总权重；若图不连通返回 None。
    时间 O(E log E)。
    """
    edges = sorted(edges)
    dsu = DSU(n)
    total = 0
    used = 0
    for w, u, v in edges:
        if dsu.union(u, v):
            total += w
            used += 1
            if used == n - 1:
                break
    return total if used == n - 1 else None


# ============================================================
# 5) 动态规划 DP
# ============================================================

def knapsack_01(weights: List[int], values: List[int], cap: int) -> int:
    """
    0/1 背包：每件物品最多取一次，最大价值。
    dp[c] 表示容量 c 的最大价值。
    时间 O(n * cap)，空间 O(cap)。
    注意：容量必须从大到小枚举，避免一件物品被重复使用。
    """
    dp = [0] * (cap + 1)
    for w, val in zip(weights, values):
        for c in range(cap, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + val)
    return dp[cap]


def lis_length(nums: List[int]) -> int:
    """
    LIS（最长递增子序列）长度：O(n log n)。
    tails[k] 维护长度 k+1 的 LIS 的最小可能结尾值。
    """
    tails: List[int] = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)
        else:
            tails[i] = x
    return len(tails)


def edit_distance(a: str, b: str) -> int:
    """
    编辑距离（Levenshtein）。
    dp[i][j]：a[:i] 到 b[:j] 的最少操作次数。
    时间 O(nm)，空间 O(nm)（可优化到 O(min(n,m))）。
    """
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],     # 删除
                    dp[i][j - 1],     # 插入
                    dp[i - 1][j - 1], # 替换
                )
    return dp[n][m]


# ============================================================
# 6) 字符串算法
# ============================================================

def kmp_build(p: str) -> List[int]:
    """
    KMP 前缀函数（部分匹配表 pi）。
    pi[i]：p[:i+1] 的最长真前缀=真后缀长度。
    时间 O(m)。
    """
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
    """
    KMP 搜索：返回 p 在 s 中第一次出现的位置；不存在返回 -1。
    时间 O(n+m)。
    """
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


def rolling_hash_getter(s: str, base: int = 911382323, mod: int = 10**9 + 7) -> Callable[[int, int], int]:
    """
    Rolling Hash：预处理后 O(1) 取得子串 hash。
    get(l,r) 表示 s[l:r] 的 hash。
    说明：哈希存在碰撞可能，工程中可双模或与其他判定结合。
    """
    n = len(s)
    p = [1] * (n + 1)
    h = [0] * (n + 1)
    for i, ch in enumerate(s, 1):
        p[i] = (p[i - 1] * base) % mod
        h[i] = (h[i - 1] * base + ord(ch)) % mod

    def get(l: int, r: int) -> int:
        return (h[r] - h[l] * p[r - l]) % mod

    return get


# ============================================================
# 7) 区间 / 查询：前缀和、差分、线段树
# ============================================================

def prefix_sum_getter(a: Sequence[int]) -> Callable[[int, int], int]:
    """
    前缀和：O(1) 区间求和。
    range_sum(l,r) 返回 a[l:r] 的和。
    """
    ps = [0]
    for x in a:
        ps.append(ps[-1] + x)

    def range_sum(l: int, r: int) -> int:
        return ps[r] - ps[l]

    return range_sum


def difference_range_add(n: int, ops: List[Tuple[int, int, int]]) -> List[int]:
    """
    差分：对区间 [l, r]（闭区间）加 val。
    ops: (l, r, val)
    时间 O(n + len(ops))。
    """
    diff = [0] * (n + 1)
    for l, r, val in ops:
        diff[l] += val
        if r + 1 < n:
            diff[r + 1] -= val
    out = [0] * n
    cur = 0
    for i in range(n):
        cur += diff[i]
        out[i] = cur
    return out


class SegTreeSum:
    """
    线段树：区间和 + 单点更新。
    - build: O(n)
    - update: O(log n)
    - query: O(log n)
    """

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

        if not (0 <= pos < self.n):
            raise IndexError("pos out of range")
        go(1, 0, self.n - 1)

    def query(self, ql: int, qr: int) -> int:
        """
        查询闭区间 [ql, qr] 的区间和。
        """
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

        if not (0 <= ql <= qr < self.n):
            raise IndexError("query range out of bounds")
        return go(1, 0, self.n - 1)


# ============================================================
# 8) 常见技巧：双指针 / 滑动窗口 / 单调栈
# ============================================================

def two_sum_sorted(a: Sequence[int], target: int) -> Optional[Tuple[int, int]]:
    """
    双指针：在有序数组中找两数和为 target 的一对下标。
    时间 O(n)，空间 O(1)。
    """
    i, j = 0, len(a) - 1
    while i < j:
        s = a[i] + a[j]
        if s == target:
            return i, j
        if s < target:
            i += 1
        else:
            j -= 1
    return None


def longest_unique_substring(s: str) -> int:
    """
    滑动窗口：最长无重复子串长度。
    时间 O(n)，空间 O(字符集)。
    """
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
    """
    单调栈：每个位置的“下一个更大元素”，没有则 -1。
    时间 O(n)，空间 O(n)。
    """
    res = [-1] * len(nums)
    st: List[int] = []  # 存下标，保持栈内对应值单调递减
    for i, x in enumerate(nums):
        while st and nums[st[-1]] < x:
            res[st.pop()] = x
        st.append(i)
    return res


# ============================================================
# 9) 数论 / 数学
# ============================================================

def gcd(a: int, b: int) -> int:
    """最大公约数（欧几里得）。"""
    return math.gcd(a, b)


def lcm(a: int, b: int) -> int:
    """最小公倍数。"""
    return a // math.gcd(a, b) * b


def sieve(n: int) -> List[int]:
    """
    埃氏筛：返回 [0..n] 内所有素数。
    时间 O(n log log n)，空间 O(n)。
    """
    if n < 2:
        return []
    is_prime = [True] * (n + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(n**0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, n + 1, i):
                is_prime[j] = False
    return [i for i, ok in enumerate(is_prime) if ok]


def mod_pow(a: int, e: int, mod: int) -> int:
    """
    快速幂：计算 a^e mod mod。
    时间 O(log e)。
    """
    res = 1
    a %= mod
    while e > 0:
        if e & 1:
            res = (res * a) % mod
        a = (a * a) % mod
        e >>= 1
    return res


# ============================================================
# 10) 小测试与示例（自检入口）
# ============================================================

def _run_tests() -> None:
    # -------- 链表 --------
    head = build_linked_list([1, 2, 3])
    assert linked_list_to_list(head) == [1, 2, 3]
    rev = reverse_linked_list(head)
    assert linked_list_to_list(rev) == [3, 2, 1]

    # -------- DSU --------
    dsu = DSU(5)
    assert dsu.union(0, 1) is True
    assert dsu.union(1, 2) is True
    assert dsu.union(0, 2) is False
    assert dsu.find(2) == dsu.find(0)

    # -------- Trie --------
    tr = Trie()
    tr.insert("apple")
    assert tr.search("apple") is True
    assert tr.search("app") is False
    assert tr.starts_with("app") is True

    # -------- 排序 --------
    a1 = [3, 1, 4, 1, 5, 9, 2]
    assert quicksort_inplace(a1[:]) == sorted(a1)
    assert mergesort(a1[:]) == sorted(a1)

    # -------- 二分 --------
    a2 = [1, 2, 4, 4, 7]
    assert binary_search_leftmost_ge(a2, 4) == 2
    assert binary_search_leftmost_gt(a2, 4) == 4
    assert binary_search_leftmost_ge(a2, 8) == 5

    # -------- DFS/BFS --------
    g_simple = {
        1: [2, 3],
        2: [4],
        3: [],
        4: []
    }
    assert dfs_reachable(g_simple, 1) == {1, 2, 3, 4}
    dist = bfs_shortest_unweighted(g_simple, 1)
    assert dist[1] == 0 and dist[4] == 2

    # -------- 回溯：排列 --------
    perms = permutations([1, 2, 3])
    assert len(perms) == 6
    assert [1, 2, 3] in perms and [3, 2, 1] in perms

    # -------- Dijkstra --------
    g_w = {
        "A": [("B", 1), ("C", 4)],
        "B": [("C", 2), ("D", 5)],
        "C": [("D", 1)],
        "D": []
    }
    d = dijkstra(g_w, "A")
    assert d["D"] == 4  # A->B(1)->C(2)->D(1)

    # -------- Bellman-Ford --------
    # 例子：无负环
    edges = [
        (0, 1, 5),
        (1, 2, -2),
        (0, 2, 10),
    ]
    bf = bellman_ford(3, edges, 0)
    assert bf is not None
    assert bf[2] == 3

    # -------- Topo Sort --------
    order = topo_sort(4, [(0, 1), (0, 2), (1, 3), (2, 3)])
    assert order is not None
    # 只验证相对顺序约束：0 在 1/2 前，1/2 在 3 前
    pos = {x: i for i, x in enumerate(order)}
    assert pos[0] < pos[1] and pos[0] < pos[2]
    assert pos[1] < pos[3] and pos[2] < pos[3]

    # -------- Kruskal MST --------
    mst = kruskal_mst(
        4,
        [
            (1, 0, 1),
            (4, 0, 2),
            (2, 1, 2),
            (3, 1, 3),
            (5, 2, 3),
        ],
    )
    assert mst == 1 + 2 + 3  # 0-1, 1-2, 1-3

    # -------- DP：0/1 背包 --------
    w = [2, 1, 3]
    v = [4, 2, 3]
    assert knapsack_01(w, v, 4) == 6  # 2+1 价值 4+2

    # -------- DP：LIS --------
    assert lis_length([10, 9, 2, 5, 3, 7, 101, 18]) == 4  # 2,3,7,18

    # -------- DP：编辑距离 --------
    assert edit_distance("kitten", "sitting") == 3

    # -------- KMP --------
    assert kmp_search("abxabcabcaby", "abcaby") == 6
    assert kmp_search("aaaaa", "bba") == -1

    # -------- Rolling Hash --------
    get_hash = rolling_hash_getter("banana")
    assert get_hash(0, 3) == get_hash(0, 3)  # "ban" == "ban"
    assert get_hash(1, 3) != get_hash(0, 2)  # "an" != "ba" (通常不同)

    # -------- 前缀和 --------
    rs = prefix_sum_getter([1, 2, 3, 4])
    assert rs(0, 4) == 10
    assert rs(1, 3) == 5  # 2+3

    # -------- 差分 --------
    arr = difference_range_add(5, [(1, 3, 2), (0, 0, 7)])
    # 初始全 0
    # [0,0] +7 => [7,0,0,0,0]
    # [1,3] +2 => [7,2,2,2,0]
    assert arr == [7, 2, 2, 2, 0]

    # -------- 线段树 --------
    st = SegTreeSum([1, 3, 5, 7, 9, 11])
    assert st.query(1, 3) == 3 + 5 + 7
    st.update(1, 10)  # 3 -> 10
    assert st.query(1, 3) == 10 + 5 + 7

    # -------- 双指针 / 滑窗 / 单调栈 --------
    assert two_sum_sorted([1, 2, 4, 7, 11], 9) == (1, 3)  # 2+7
    assert longest_unique_substring("abcabcbb") == 3
    assert next_greater_element([2, 1, 2, 4, 3]) == [4, 2, 4, -1, -1]

    # -------- 数论 --------
    assert gcd(12, 18) == 6
    assert lcm(12, 18) == 36
    assert sieve(10) == [2, 3, 5, 7]
    assert mod_pow(2, 10, 1000) == 24

    print("✅ All tests passed!")


if __name__ == "__main__":
    _run_tests()
