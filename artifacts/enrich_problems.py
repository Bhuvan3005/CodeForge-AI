import json
import os
from pathlib import Path

# Paths
WORKSPACE_DIR = Path(r"c:\Users\bhuvam\OneDrive\Desktop\CodeForge_copy")
PROBLEMS_FILE = WORKSPACE_DIR / "backend" / "problems.json"

ENRICHMENT = {
    "Find Duplicate in Array": {
        "function_name": "findDuplicate",
        "function_signature": "int findDuplicate(vector<int>& nums)",
        "return_type": "int",
        "parameter_types": ["vector<int>"],
        "constraints": ["2 <= nums.size() <= 10^5", "1 <= nums[i] < nums.size()"]
    },
    "Rotate Array by K Steps": {
        "function_name": "rotate",
        "function_signature": "vector<int> rotate(vector<int>& nums, int k)",
        "return_type": "vector<int>",
        "parameter_types": ["vector<int>", "int"],
        "constraints": ["1 <= nums.size() <= 10^5", "0 <= k <= 10^5"]
    },
    "Maximum Product Subarray": {
        "function_name": "maxProduct",
        "function_signature": "int maxProduct(vector<int>& nums)",
        "return_type": "int",
        "parameter_types": ["vector<int>"],
        "constraints": ["1 <= nums.size() <= 2 * 10^4", "-10 <= nums[i] <= 10"]
    },
    "Two Sum with HashMap": {
        "function_name": "twoSum",
        "function_signature": "vector<int> twoSum(vector<int>& nums, int target)",
        "return_type": "vector<int>",
        "parameter_types": ["vector<int>", "int"],
        "constraints": ["2 <= nums.size() <= 10^4", "-10^9 <= nums[i] <= 10^9"]
    },
    "Group Anagrams Together": {
        "function_name": "groupAnagrams",
        "function_signature": "vector<vector<string>> groupAnagrams(vector<string>& words)",
        "return_type": "vector<vector<string>>",
        "parameter_types": ["vector<string>"],
        "constraints": ["1 <= words.size() <= 10^4", "0 <= words[i].length() <= 100"]
    },
    "Longest Consecutive Sequence": {
        "function_name": "longestConsecutive",
        "function_signature": "int longestConsecutive(vector<int>& nums)",
        "return_type": "int",
        "parameter_types": ["vector<int>"],
        "constraints": ["0 <= nums.size() <= 10^5", "-10^9 <= nums[i] <= 10^9"]
    },
    "Maximum Average Subarray": {
        "function_name": "findMaxAverage",
        "function_signature": "double findMaxAverage(vector<int>& nums, int k)",
        "return_type": "double",
        "parameter_types": ["vector<int>", "int"],
        "constraints": ["1 <= k <= nums.size() <= 10^5", "-10^4 <= nums[i] <= 10^4"]
    },
    "Longest Substring Without Repeating Characters": {
        "function_name": "lengthOfLongestSubstring",
        "function_signature": "int lengthOfLongestSubstring(string s)",
        "return_type": "int",
        "parameter_types": ["string"],
        "constraints": ["0 <= s.length() <= 5 * 10^4"]
    },
    "Minimum Window Containing All Characters": {
        "function_name": "minWindow",
        "function_signature": "string minWindow(string s, string t)",
        "return_type": "string",
        "parameter_types": ["string", "string"],
        "constraints": ["1 <= s.length(), t.length() <= 10^5"]
    },
    "Pair Sum Equals Target": {
        "function_name": "hasPairWithSum",
        "function_signature": "bool hasPairWithSum(vector<int>& nums, int target)",
        "return_type": "bool",
        "parameter_types": ["vector<int>", "int"],
        "constraints": ["2 <= nums.size() <= 10^5", "nums is sorted"]
    },
    "Remove Duplicates from Sorted Array": {
        "function_name": "removeDuplicates",
        "function_signature": "int removeDuplicates(vector<int>& nums)",
        "return_type": "int",
        "parameter_types": ["vector<int>"],
        "constraints": ["1 <= nums.size() <= 3 * 10^4", "nums is sorted"]
    },
    "Trapping Rain Water": {
        "function_name": "trap",
        "function_signature": "int trap(vector<int>& height)",
        "return_type": "int",
        "parameter_types": ["vector<int>"],
        "constraints": ["n == height.size()", "1 <= n <= 2 * 10^4"]
    },
    "Valid Parentheses Checker": {
        "function_name": "isValid",
        "function_signature": "bool isValid(string s)",
        "return_type": "bool",
        "parameter_types": ["string"],
        "constraints": ["1 <= s.length() <= 10^4"]
    },
    "Evaluate Reverse Polish Notation": {
        "function_name": "evalRPN",
        "function_signature": "int evalRPN(vector<string>& tokens)",
        "return_type": "int",
        "parameter_types": ["vector<string>"],
        "constraints": ["1 <= tokens.length <= 10^4", "tokens[i] is operator or integer"]
    },
    "Largest Rectangle in Histogram": {
        "function_name": "largestRectangleArea",
        "function_signature": "int largestRectangleArea(vector<int>& heights)",
        "return_type": "int",
        "parameter_types": ["vector<int>"],
        "constraints": ["1 <= heights.size() <= 10^5", "0 <= heights[i] <= 10^4"]
    },
    "First Non-Repeating Character in Stream": {
        "function_name": "firstNonRepeating",
        "function_signature": "vector<string> firstNonRepeating(string stream)",
        "return_type": "vector<string>",
        "parameter_types": ["string"],
        "constraints": ["1 <= stream.length() <= 10^4"]
    },
    "Sliding Window Maximum": {
        "function_name": "maxSlidingWindow",
        "function_signature": "vector<int> maxSlidingWindow(vector<int>& nums, int k)",
        "return_type": "vector<int>",
        "parameter_types": ["vector<int>", "int"],
        "constraints": ["1 <= nums.size() <= 10^5", "1 <= k <= nums.size()"]
    },
    "Task Scheduler with Cooldown": {
        "function_name": "leastInterval",
        "function_signature": "int leastInterval(vector<string>& tasks, int n)",
        "return_type": "int",
        "parameter_types": ["vector<string>", "int"],
        "constraints": ["1 <= tasks.length <= 10^4", "0 <= n <= 100"]
    },
    "Reverse a Linked List": {
        "function_name": "reverseList",
        "function_signature": "vector<int> reverseList(vector<int>& head)",
        "return_type": "vector<int>",
        "parameter_types": ["vector<int>"],
        "constraints": ["0 <= head.size() <= 5000"]
    },
    "Detect Cycle in Linked List": {
        "function_name": "hasCycle",
        "function_signature": "bool hasCycle(vector<int>& head, int pos)",
        "return_type": "bool",
        "parameter_types": ["vector<int>", "int"],
        "constraints": ["0 <= head.size() <= 10^4"]
    },
    "Merge K Sorted Linked Lists": {
        "function_name": "mergeKLists",
        "function_signature": "vector<int> mergeKLists(vector<vector<int>>& lists)",
        "return_type": "vector<int>",
        "parameter_types": ["vector<vector<int>>"],
        "constraints": ["k == lists.size()", "0 <= k <= 10^4"]
    },
    "Invert Binary Tree": {
        "function_name": "invertTree",
        "function_signature": "vector<int> invertTree(vector<int>& root)",
        "return_type": "vector<int>",
        "parameter_types": ["vector<int>"],
        "constraints": ["0 <= root.size() <= 100"]
    },
    "Level Order Traversal of Binary Tree": {
        "function_name": "levelOrder",
        "function_signature": "vector<vector<int>> levelOrder(vector<int>& root)",
        "return_type": "vector<vector<int>>",
        "parameter_types": ["vector<int>"],
        "constraints": ["0 <= root.size() <= 2000"]
    },
    "Serialize and Deserialize Binary Tree": {
        "function_name": "serializeAndDeserialize",
        "function_signature": "vector<int> serializeAndDeserialize(vector<int>& root)",
        "return_type": "vector<int>",
        "parameter_types": ["vector<int>"],
        "constraints": ["0 <= root.size() <= 10^4"]
    },
    "Number of Islands": {
        "function_name": "numIslands",
        "function_signature": "int numIslands(vector<vector<string>>& grid)",
        "return_type": "int",
        "parameter_types": ["vector<vector<string>>"],
        "constraints": ["m == grid.size()", "n == grid[i].size()", "1 <= m, n <= 300"]
    },
    "Course Schedule Feasibility": {
        "function_name": "canFinish",
        "function_signature": "bool canFinish(int numCourses, vector<vector<int>>& prerequisites)",
        "return_type": "bool",
        "parameter_types": ["int", "vector<vector<int>>"],
        "constraints": ["1 <= numCourses <= 2000", "0 <= prerequisites.size() <= 5000"]
    },
    "Shortest Path in Weighted Graph": {
        "function_name": "shortestPath",
        "function_signature": "vector<int> shortestPath(int n, vector<vector<int>>& edges, int src)",
        "return_type": "vector<int>",
        "parameter_types": ["int", "vector<vector<int>>", "int"],
        "constraints": ["1 <= n <= 500", "0 <= src < n"]
    },
    "Climbing Stairs": {
        "function_name": "climbStairs",
        "function_signature": "int climbStairs(int n)",
        "return_type": "int",
        "parameter_types": ["int"],
        "constraints": ["1 <= n <= 45"]
    },
    "0/1 Knapsack Problem": {
        "function_name": "knapsack",
        "function_signature": "int knapsack(vector<int>& weights, vector<int>& values, int W)",
        "return_type": "int",
        "parameter_types": ["vector<int>", "vector<int>", "int"],
        "constraints": ["1 <= weights.size() <= 1000", "0 <= W <= 1000"]
    },
    "Edit Distance Between Two Strings": {
        "function_name": "minDistance",
        "function_signature": "int minDistance(string word1, string word2)",
        "return_type": "int",
        "parameter_types": ["string", "string"],
        "constraints": ["0 <= word1.length, word2.length <= 500"]
    },
    "Assign Cookies to Children": {
        "function_name": "findContentChildren",
        "function_signature": "int findContentChildren(vector<int>& g, vector<int>& s)",
        "return_type": "int",
        "parameter_types": ["vector<int>", "vector<int>"],
        "constraints": ["0 <= g.size(), s.size() <= 3 * 10^4"]
    },
    "Jump Game Reachability": {
        "function_name": "canJump",
        "function_signature": "bool canJump(vector<int>& nums)",
        "return_type": "bool",
        "parameter_types": ["vector<int>"],
        "constraints": ["1 <= nums.size() <= 10^4", "0 <= nums[i] <= 10^5"]
    },
    "Minimum Number of Platforms": {
        "function_name": "findPlatform",
        "function_signature": "int findPlatform(vector<int>& arrival, vector<int>& departure)",
        "return_type": "int",
        "parameter_types": ["vector<int>", "vector<int>"],
        "constraints": ["1 <= arrival.size() <= 50000"]
    },
    "Generate All Subsets": {
        "function_name": "subsets",
        "function_signature": "vector<vector<int>> subsets(vector<int>& nums)",
        "return_type": "vector<vector<int>>",
        "parameter_types": ["vector<int>"],
        "constraints": ["1 <= nums.size() <= 10", "-10 <= nums[i] <= 10"]
    },
    "Permutations of Unique Elements": {
        "function_name": "permute",
        "function_signature": "vector<vector<int>> permute(vector<int>& nums)",
        "return_type": "vector<vector<int>>",
        "parameter_types": ["vector<int>"],
        "constraints": ["1 <= nums.size() <= 8", "-10 <= nums[i] <= 10"]
    },
    "Sudoku Solver": {
        "function_name": "solveSudoku",
        "function_signature": "vector<vector<string>> solveSudoku(vector<vector<string>>& board)",
        "return_type": "vector<vector<string>>",
        "parameter_types": ["vector<vector<string>>"],
        "constraints": ["board.size() == 9", "board[i].size() == 9"]
    },
    "Square Root via Binary Search": {
        "function_name": "mySqrt",
        "function_signature": "int mySqrt(int x)",
        "return_type": "int",
        "parameter_types": ["int"],
        "constraints": ["0 <= x <= 2^31 - 1"]
    },
    "Search in Rotated Sorted Array": {
        "function_name": "search",
        "function_signature": "int search(vector<int>& nums, int target)",
        "return_type": "int",
        "parameter_types": ["vector<int>", "int"],
        "constraints": ["1 <= nums.size() <= 5000", "-10^4 <= nums[i] <= 10^4"]
    },
    "Median of Two Sorted Arrays": {
        "function_name": "findMedianSortedArrays",
        "function_signature": "double findMedianSortedArrays(vector<int>& nums1, vector<int>& nums2)",
        "return_type": "double",
        "parameter_types": ["vector<int>", "vector<int>"],
        "constraints": ["nums1.size() == m", "nums2.size() == n", "0 <= m, n <= 1000"]
    },
    "Find K Closest Elements": {
        "function_name": "findClosestElements",
        "function_signature": "vector<int> findClosestElements(vector<int>& arr, int k, int x)",
        "return_type": "vector<int>",
        "parameter_types": ["vector<int>", "int", "int"],
        "constraints": ["1 <= k <= arr.size() <= 10^4", "arr is sorted"]
    },
    "Top K Frequent Elements": {
        "function_name": "topKFrequent",
        "function_signature": "vector<int> topKFrequent(vector<int>& nums, int k)",
        "return_type": "vector<int>",
        "parameter_types": ["vector<int>", "int"],
        "constraints": ["1 <= nums.size() <= 10^5", "k is in range [1, unique elements]"]
    },
    "Find Median from Data Stream": {
        "function_name": "medianStream",
        "function_signature": "vector<double> medianStream(vector<vector<string>>& operations)",
        "return_type": "vector<double>",
        "parameter_types": ["vector<vector<string>>"],
        "constraints": ["1 <= operations.size() <= 5 * 10^4"]
    },
    "Count Set Bits": {
        "function_name": "hammingWeight",
        "function_signature": "int hammingWeight(int n)",
        "return_type": "int",
        "parameter_types": ["int"],
        "constraints": ["0 <= n <= 2^31 - 1"]
    },
    "Single Number in Array": {
        "function_name": "singleNumber",
        "function_signature": "int singleNumber(vector<int>& nums)",
        "return_type": "int",
        "parameter_types": ["vector<int>"],
        "constraints": ["1 <= nums.size() <= 3 * 10^4", "every element appears 3 times except one"]
    },
    "Reverse Bits of an Integer": {
        "function_name": "reverseBits",
        "function_signature": "long reverseBits(long n)",
        "return_type": "long",
        "parameter_types": ["long"],
        "constraints": ["0 <= n <= 2^32 - 1"]
    }
}

def main():
    if not PROBLEMS_FILE.exists():
        print(f"File not found: {PROBLEMS_FILE}")
        return
    
    with open(PROBLEMS_FILE, "r", encoding="utf-8") as f:
        problems = json.load(f)
        
    updated = []
    for p in problems:
        title = p["title"]
        info = ENRICHMENT.get(title, {})
        
        p["function_name"] = info.get("function_name", "solve")
        p["function_signature"] = info.get("function_signature", "void solve()")
        p["return_type"] = info.get("return_type", "void")
        p["parameter_types"] = info.get("parameter_types", [])
        
        # Merge constraints
        existing_constraints = p.get("constraints", [])
        if not existing_constraints:
            existing_constraints = info.get("constraints", [])
        elif isinstance(existing_constraints, str):
            existing_constraints = [existing_constraints]
        p["constraints"] = existing_constraints
        
        p["expected_pattern"] = info.get("function_name", "solve") # simple fallback
        p["expected_time_complexity"] = "O(N)" # fallback
        p["expected_space_complexity"] = "O(1)" # fallback
        
        updated.append(p)
        
    with open(PROBLEMS_FILE, "w", encoding="utf-8") as f:
        json.dump(updated, f, indent=2)
        
    print(f"Successfully enriched {len(updated)} problems in {PROBLEMS_FILE}")

if __name__ == "__main__":
    main()
