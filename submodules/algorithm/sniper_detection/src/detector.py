"""
Unified interface for sniper detection
"""
import pandas as pd
import os
from .plot_attack_windows import plot_attack_window as plot_window
from .train_model import load_data, train_detector


class SniperDetector:
    def __init__(self):
        self.results = None
        self.sniper_candidates = None
        # 获取当前文件所在目录
        self.current_dir = os.path.dirname(__file__)
        # 往上一级到 sniper_detection/
        self.module_root = os.path.dirname(self.current_dir)

    def find_snipers(self, df=None, use_precomputed=True):
        """
        找狙击手候选

        Args:
            df: 原始订单数据（如果为None，用预计算结果）
            use_precomputed: 是否用预计算结果

        Returns:
            DataFrame with sniper candidates
        """
        if use_precomputed:
            # 返回预计算的37个候选
            candidates_path = os.path.join(self.module_root, 'results', 'strict_sniper_candidates.csv')
            if os.path.exists(candidates_path):
                self.sniper_candidates = pd.read_csv(candidates_path)
            else:
                # 返回3个验证案例作为示例
                return self.get_case_summary()
        else:
            # 运行完整pipeline（需要df）
            if df is None:
                raise ValueError("df is required when use_precomputed=False")
            # 这里放你的完整训练逻辑
            pass

        return self.sniper_candidates

    def plot_attack_window(self, session_id, save_path=None):
        """
        画攻击窗口图

        Args:
            session_id: 会话ID
            save_path: 保存路径（None则自动生成）
        """
        # 调用已有的 plot_attack_windows.py
        return plot_window(session_id, save_path)

    def get_case_summary(self):
        """返回3个验证案例的摘要"""
        cases = {
            2: {
                'session_id': '0x28d47763e7a53ef2c1e0d6fabfc59d9dfff3ba55_1',
                'duration': 74,
                'buy_amount': 17894.13,
                'sell_amount': 17876.22,
                'profit': -17.91,
                'anomaly_score': -0.4933,
                'buy_tx': '0x733305afcdfd53e4331fd2164fd36fc6796e2df96134782100df23dda926ff69',
                'sell_tx': '0x6addf209ed9f4a3ec8d21cf76dde171aef1947adca47d6da947a213de23f6cca'
            },
            3: {
                'session_id': '0x63b81ddc36a228f7431a534d67eb058b7cc0f906_1',
                'duration': 76,
                'buy_amount': 17754.11,
                'sell_amount': 17736.34,
                'profit': -17.77,
                'anomaly_score': -0.4870,
                'buy_tx': '0xe48675a9c5422d604956472b17d0f2785e7c8b13c6f2047a74004a53f1786b93',
                'sell_tx': '0xa58078148acb1371bdc0044fe9eabc6e7c2c7a032ff3a0056170e20134f328e0'
            },
            4: {
                'session_id': '0x6a4aaf27bb285af2744c7def8ec447937fb07f69_1',
                'duration': 72,
                'buy_amount': 17787.85,
                'sell_amount': 17770.04,
                'profit': -17.81,
                'anomaly_score': -0.4847,
                'buy_tx': '0x4f133897f46bed815a1c7c6a95f04d4ab76eb688db3ec97b4af56ebbdae0190e',
                'sell_tx': '0x48ce73b8d175c579ea70269d35695259ebddb4e729066c70597049578481cd79'
            }
        }
        return cases