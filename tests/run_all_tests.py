#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""运行所有测试脚本"""

import sys
import os
import subprocess
import io

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def run_test(test_file):
    """运行单个测试文件"""
    print("\n" + "="*70)
    print(f"Running: {test_file}")
    print("="*70)
    
    test_path = os.path.join(os.path.dirname(__file__), test_file)
    result = subprocess.run(
        [sys.executable, test_path],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        capture_output=False
    )
    
    return result.returncode == 0

def main():
    """运行所有测试"""
    print("="*70)
    print("URL2VIDEO - Test Suite")
    print("="*70)
    
    # 测试文件列表（按顺序）
    tests = [
        "test_env.py",           # 环境检查
        "test_scraper.py",       # 网页抓取
        "test_ai_director.py",   # AI脚本生成
        "test_video_engine.py"   # 视频生成
    ]
    
    results = {}
    
    for test in tests:
        success = run_test(test)
        results[test] = success
        if not success:
            print(f"\n[FAILED] {test}")
            print("Stopping test suite due to failure.")
            break
        else:
            print(f"\n[PASSED] {test}")
    
    # 总结
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, success in results.items():
        status = "PASS" if success else "FAIL"
        print(f"  {status:4s} - {test}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print(f"\n[FAILURE] {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())