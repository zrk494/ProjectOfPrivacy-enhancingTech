import pandas as pd


def merge_boolean_runs(df: pd.DataFrame, flag_col: str, time_col: str = "bucket"):
    """
    把连续为 True 的时间点合并为一个事件（start, end）
    """
    events = []
    in_event = False
    start = None

    for _, row in df.iterrows():
        t = int(row[time_col])
        is_on = bool(row[flag_col])

        if is_on and not in_event:
            in_event = True
            start = t
            end = t

        elif is_on and in_event:
            end = t

        elif (not is_on) and in_event:
            events.append({"start": start, "end": end})
            in_event = False

    # 如果最后一个还在事件里
    if in_event:
        events.append({"start": start, "end": end})

    return pd.DataFrame(events)
