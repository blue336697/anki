"""Standalone: 接雨水 DP 单卡片 APKG."""
import sys
from pathlib import Path

TOPIC_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOPIC_DIR.parent.parent
SKILL_DIR = REPO_ROOT / '.claude' / 'skills' / 'anki-apkg-generator'
sys.path.insert(0, str(SKILL_DIR / 'scripts'))
from apkg_builder import make_deck, add_basic, add_cloze, code, build

d = make_deck(1747300190, '算法::动态规划::接雨水(DP修复)')

add_basic(d, '接雨水 | DP解法',
    'dp_left[i] 记录 i 及左边最高柱（含自身），dp_right[i] 记录 i 及右边最高柱（含自身）。<br>'
    'len &lt;= 2 直接 return 0。<br>'
    '每个位置接水量 = min(左最高, 右最高) - 当前高度。<br><br>'
    + code(
'''class Solution {
    public int trap(int[] height) {
        int sum = 0;
        int len = height.length;
        if (len <= 2) return 0;

        int[] dp_left = new int[len];
        int[] dp_right = new int[len];
        // 初始化：第0个位置左边没有柱子，左边最大高度为height[0]
        dp_left[0] = height[0];
        for (int i = 1; i < len; i++) {
            dp_left[i] = Math.max(dp_left[i - 1], height[i]);
        }
        // 初始化最后一个位置右边最大高度
        dp_right[len - 1] = height[len - 1];
        for (int i = len - 2; i >= 0; i--) {
            dp_right[i] = Math.max(dp_right[i + 1], height[i]);
        }
        // 计算每个位置接水量：左右两侧最大高度的较小值，减去当前柱子高度
        for (int i = 1; i < len - 1; i++) {
            int min = Math.min(dp_left[i], dp_right[i]);
            sum += min - height[i];
        }
        return sum;
    }
}'''))

OUTPUT = REPO_ROOT / '牌组' / '算法' / '接雨水_DP修复.apkg'
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
print(build(str(OUTPUT)))
