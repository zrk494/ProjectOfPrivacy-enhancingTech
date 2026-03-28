from src.detector import SniperDetector

def main():
    print('=== Sniper Detection Module ===')
    
    # 初始化检测器
    detector = SniperDetector()
    
    # 获取验证案例
    print('\n📊 验证案例:')
    cases = detector.get_case_summary()
    for rank, case in cases.items():
        print(f'  Rank {rank}: {case["duration"]}s, ${case["buy_amount"]:.2f} → ${case["sell_amount"]:.2f} (Profit: ${case["profit"]:.2f})')
    
    # 查找狙击手候选
    print('\n🔍 查找狙击手候选...')
    snipers = detector.find_snipers(use_precomputed=True)
    print(f'  找到 {len(snipers)} 个狙击手候选')
    
    # 绘制攻击窗口图
    print('\n📈 绘制攻击窗口图...')
    for rank, case in cases.items():
        try:
            detector.plot_attack_window(case["session_id"])
            print(f'  已绘制 Rank {rank} 的攻击窗口图')
        except Exception as e:
            print(f'  绘制 Rank {rank} 的攻击窗口图失败: {e}')
    
    print('\n✅ 运行完成')

if __name__ == '__main__':
    main()