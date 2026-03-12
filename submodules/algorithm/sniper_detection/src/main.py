"""
Main entry point for sniper detection module
"""

import os
import sys

# 添加模块路径（如果需要在独立运行时使用）
current_dir = os.path.dirname(__file__)
module_root = os.path.dirname(current_dir)
if module_root not in sys.path:
    sys.path.insert(0, module_root)


def main():
    """示例：调用 SniperDetector 进行检测"""
    try:
        from detector import SniperDetector

        print("=" * 50)
        print("Sniper Detection Module - Example Usage")
        print("=" * 50)

        # 初始化检测器
        detector = SniperDetector()

        # 获取预计算的案例
        print("\n📊 获取验证案例...")
        cases = detector.get_case_summary()
        for rank, case in cases.items():
            print(f"  Rank {rank}: {case['duration']}s, ${case['buy_amount']:.0f} → ${case['sell_amount']:.0f}")

        # 查找狙击手候选
        print("\n🔍 查找狙击手候选...")
        snipers = detector.find_snipers(use_precomputed=True)
        if isinstance(snipers, dict):
            print(f"  使用预计算案例: {len(snipers)} 个")
        else:
            print(f"  找到 {len(snipers)} 个候选")

        print("\n✅ 示例运行完成")

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保在正确的环境中运行")


if __name__ == '__main__':
    main()