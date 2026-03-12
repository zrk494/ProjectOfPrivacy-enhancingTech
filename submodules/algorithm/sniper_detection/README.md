# Sniper Attack Detection Module

## 🎯 Purpose
Detect sniper attacks on Polymarket prediction markets.  
Sniper definition: **Large trade + Buy then sell + Ultra-short holding + 2 trades**

## 📊 Key Results
| Metric | Value |
|--------|-------|
| Total Orders | 54,582 |
| Total Sessions | 27,188 |
| Anomalous Sessions (5%) | 1,360 |
| Strict Sniper Candidates | 37 |
| Verified Cases | 3 |

### Verified Cases
| Rank | Duration | Buy Amount | Sell Amount | Profit/Loss |
|------|----------|------------|-------------|-------------|
| 2 | 74s | $17,894.13 | $17,876.22 | -$17.91 |
| 3 | 76s | $17,754.11 | $17,736.34 | -$17.77 |
| 4 | 72s | $17,787.85 | $17,770.04 | -$17.81 |

## 🚀 Quick Start

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run the full pipeline
```python
from src.detector import SniperDetector

# Initialize detector
detector = SniperDetector()

# Get verified cases
cases = detector.get_case_summary()
print(cases[2])  # Rank 2 case

# Find all sniper candidates
snipers = detector.find_snipers(use_precomputed=True)

# Plot attack window for a specific case
detector.plot_attack_window('0x28d47763e7a53ef2c1e0d6fabfc59d9dfff3ba55_1')
```

## 📁 Module Structure
```
sniper_detection/
├── src/               # Source code
├── results/           # Example outputs
├── models/            # Pre-trained model
├── data/              # Data format docs
├── config.py          # Configuration
├── README.md          # This file
└── requirements.txt   # Dependencies
```

## 📧 Contact
FAN Penghui - Algorithm Lead