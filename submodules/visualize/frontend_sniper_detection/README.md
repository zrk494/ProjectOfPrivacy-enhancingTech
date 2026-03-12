# Frontend Data for Polymarket Sniper Detection

## 📁 Files
- `detailed_cases.json` - 3 verified cases (most important!)
- `stats/all_cases.json` - All 37 sniper candidates
- `images/` - Attack window plots and statistics

## 🔑 Key File: `detailed_cases.json`

```json
[
  {
    "rank": 2,
    "session_id": "0x28d47763e7a53ef2c1e0d6fabfc59d9dfff3ba55_1",
    "duration_seconds": 74,
    "anomaly_score": -0.4933,
    "buy": {
      "amount": 17894.13,
      "price": 0.9990,
      "time": "20:57:50",
      "date": "2026-02-18",
      "tx_hash": "0x733305afcdfd53e4331fd2164fd36fc6796e2df96134782100df23dda926ff69",
      "polygonscan_url": "https://polygonscan.com/tx/0x733305afcdfd53e4331fd2164fd36fc6796e2df96134782100df23dda926ff69"
    },
    "sell": {
      "amount": 17876.22,
      "price": 0.9980,
      "time": "20:59:04",
      "date": "2026-02-18",
      "tx_hash": "0x6addf209ed9f4a3ec8d21cf76dde171aef1947adca47d6da947a213de23f6cca",
      "polygonscan_url": "https://polygonscan.com/tx/0x6addf209ed9f4a3ec8d21cf76dde171aef1947adca47d6da947a213de23f6cca"
    },
    "profit": -17.91,
    "image": "images/sniper_rank2_74seconds.png"
  },
  {
    "rank": 3,
    "session_id": "0x63b81ddc36a228f7431a534d67eb058b7cc0f906_1",
    "duration_seconds": 76,
    "anomaly_score": -0.4870,
    "buy": {
      "amount": 17754.11,
      "price": 0.9990,
      "time": "00:50:08",
      "date": "2026-02-19",
      "tx_hash": "0xe48675a9c5422d604956472b17d0f2785e7c8b13c6f2047a74004a53f1786b93",
      "polygonscan_url": "https://polygonscan.com/tx/0xe48675a9c5422d604956472b17d0f2785e7c8b13c6f2047a74004a53f1786b93"
    },
    "sell": {
      "amount": 17736.34,
      "price": 0.9980,
      "time": "00:51:24",
      "date": "2026-02-19",
      "tx_hash": "0xa58078148acb1371bdc0044fe9eabc6e7c2c7a032ff3a0056170e20134f328e0",
      "polygonscan_url": "https://polygonscan.com/tx/0xa58078148acb1371bdc0044fe9eabc6e7c2c7a032ff3a0056170e20134f328e0"
    },
    "profit": -17.77,
    "image": "images/sniper_rank3_76seconds.png"
  },
  {
    "rank": 4,
    "session_id": "0x6a4aaf27bb285af2744c7def8ec447937fb07f69_1",
    "duration_seconds": 72,
    "anomaly_score": -0.4847,
    "buy": {
      "amount": 17787.85,
      "price": 0.9990,
      "time": "18:05:36",
      "date": "2026-02-18",
      "tx_hash": "0x4f133897f46bed815a1c7c6a95f04d4ab76eb688db3ec97b4af56ebbdae0190e",
      "polygonscan_url": "https://polygonscan.com/tx/0x4f133897f46bed815a1c7c6a95f04d4ab76eb688db3ec97b4af56ebbdae0190e"
    },
    "sell": {
      "amount": 17770.04,
      "price": 0.9980,
      "time": "18:06:48",
      "date": "2026-02-18",
      "tx_hash": "0x48ce73b8d175c579ea70269d35695259ebddb4e729066c70597049578481cd79",
      "polygonscan_url": "https://polygonscan.com/tx/0x48ce73b8d175c579ea70269d35695259ebddb4e729066c70597049578481cd79"
    },
    "profit": -17.81,
    "image": "images/sniper_rank4_72seconds.png"
  }
]

