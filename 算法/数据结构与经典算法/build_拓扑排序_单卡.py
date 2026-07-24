"""Standalone: 拓扑排序 Kahn 模板单卡片 APKG."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SKILL_DIR = REPO_ROOT / '.claude' / 'skills' / 'anki-apkg-generator'
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_deck, add_basic, code, build

d = make_deck(1747302700, '算法::数据结构与经典算法::图论::拓扑排序')

add_basic(d, '拓扑排序 | 拓扑排序 Java 模板怎么写？',
    '模板：<br>'
    + code(
'''import java.util.*;

public class Kahn {
    // 拓扑排序，返回拓扑序列；若有环返回空列表
    public List<Integer> topoSort(int n, int[][] edges) {
        // 1. 构建邻接表
        List<List<Integer>> graph = new ArrayList<>();
        int[] inDegree = new int[n]; // 入度数组

        for (int i = 0; i < n; i++) {
            graph.add(new ArrayList<>());
        }
        for (int[] e : edges) {
            int from = e[0], to = e[1];
            graph.get(from).add(to);
            inDegree[to]++;
        }

        // 2. 队列：存入度为0的节点
        Queue<Integer> queue = new LinkedList<>();
        for (int i = 0; i < n; i++) {
            if (inDegree[i] == 0) {
                queue.offer(i);
            }
        }

        List<Integer> res = new ArrayList<>();
        // 3. BFS 遍历
        while (!queue.isEmpty()) {
            int cur = queue.poll();
            res.add(cur);

            // 遍历后继节点
            for (int next : graph.get(cur)) {
                inDegree[next]--;
                if (inDegree[next] == 0) {
                    queue.offer(next);
                }
            }
        }

        // 长度不等 → 存在环
        return res.size() == n ? res : new ArrayList<>();
    }

    public static void main(String[] args) {
        Kahn kahn = new Kahn();
        // 示例：3个节点，边 [0→1, 1→2, 0→2]
        int n = 3;
        int[][] edges = {{0,1},{1,2},{0,2}};
        List<Integer> topo = kahn.topoSort(n, edges);
        System.out.println(topo); // [0,1,2]
    }
}''')
    + '含完整 main 方法可直接运行验证。'
    + '<br><br><hr><small>Tags: 算法 数据结构经典算法 图论 拓扑排序 模板<br>'
    + 'Source: 图论-拓扑排序<br>Difficulty: Hard</small>')

OUTPUT = REPO_ROOT / '牌组' / '算法' / '拓扑排序_Kahn模板.apkg'
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
print(build(str(OUTPUT)))
