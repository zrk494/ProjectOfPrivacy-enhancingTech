from __future__ import annotations

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def load_results(
    market_file: str,
    score_method: str = "additive",
) -> tuple[pd.DataFrame, pd.DataFrame, Path]:
    """
    Load bucket-level scores and event-level results for one market.
    """
    base = Path(__file__).resolve().parents[2]
    market_stem = Path(market_file).stem
    result_dir = base / "results" / "activity_pipeline" / market_stem

    bucket_path = result_dir / f"bucket_scores_{score_method}.csv"
    event_path = result_dir / f"stress_events_enriched_{score_method}.csv"

    if not bucket_path.exists():
        raise FileNotFoundError(f"Bucket score file not found: {bucket_path}")
    if not event_path.exists():
        raise FileNotFoundError(f"Event file not found: {event_path}")

    bucket_df = pd.read_csv(bucket_path)
    event_df = pd.read_csv(event_path)

    return bucket_df, event_df, result_dir


def prepare_data(
    bucket_df: pd.DataFrame,
    event_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Parse datetime columns and sort rows.
    """
    bucket_df = bucket_df.copy()
    event_df = event_df.copy()

    if "datetime" not in bucket_df.columns:
        raise ValueError("bucket_df must contain a 'datetime' column.")

    bucket_df["datetime"] = pd.to_datetime(bucket_df["datetime"])
    bucket_df = bucket_df.sort_values("datetime").reset_index(drop=True)

    if not event_df.empty:
        if "start_datetime" in event_df.columns:
            event_df["start_datetime"] = pd.to_datetime(event_df["start_datetime"])
        if "end_datetime" in event_df.columns:
            event_df["end_datetime"] = pd.to_datetime(event_df["end_datetime"])
        event_df = event_df.sort_values("start_datetime").reset_index(drop=True)

    return bucket_df, event_df


def plot_market_stress_diagnostics(
    market_file: str,
    score_method: str = "additive",
    top_k_events: int = 10,
    save_png: bool = True,
    show_plot: bool = True,
) -> None:
    """
    Plot stress score, midpoint, and spread for one market,
    with detected stress events highlighted as shaded regions.
    """
    bucket_df, event_df, result_dir = load_results(
        market_file=market_file,
        score_method=score_method,
    )
    bucket_df, event_df = prepare_data(bucket_df, event_df)

    # keep only top-k events by peak score for cleaner visualization
    if not event_df.empty and "peak_stress_score" in event_df.columns:
        event_df = (
            event_df.sort_values("peak_stress_score", ascending=False)
            .head(top_k_events)
            .sort_values("start_datetime")
            .reset_index(drop=True)
        )

    fig, axes = plt.subplots(
        3, 1, figsize=(14, 10), sharex=True, constrained_layout=True
    )

    # -------------------------------------------------
    # Panel 1: stress score
    # -------------------------------------------------
    axes[0].plot(
        bucket_df["datetime"],
        bucket_df["stress_score"],
        linewidth=1.2,
    )
    axes[0].set_ylabel("Stress score")
    axes[0].set_title(
        f"Market stress diagnostics: {market_file} ({score_method})"
    )

    # -------------------------------------------------
    # Panel 2: midpoint
    # -------------------------------------------------
    if "midpoint" in bucket_df.columns:
        axes[1].plot(
            bucket_df["datetime"],
            bucket_df["midpoint"],
            linewidth=1.2,
        )
    axes[1].set_ylabel("Midpoint")

    # -------------------------------------------------
    # Panel 3: spread
    # -------------------------------------------------
    if "spread" in bucket_df.columns:
        axes[2].plot(
            bucket_df["datetime"],
            bucket_df["spread"],
            linewidth=1.2,
        )
    axes[2].set_ylabel("Spread")
    axes[2].set_xlabel("Datetime")

    # -------------------------------------------------
    # Shade event windows
    # -------------------------------------------------
    for _, row in event_df.iterrows():
        start_dt = row["start_datetime"]
        end_dt = row["end_datetime"]

        # if event duration is zero/one bucket, extend slightly for visibility
        if pd.isna(start_dt) or pd.isna(end_dt):
            continue
        if start_dt == end_dt:
            end_dt = end_dt + pd.Timedelta(minutes=1)

        for ax in axes:
            ax.axvspan(start_dt, end_dt, alpha=0.2)

    # -------------------------------------------------
    # Format datetime axis
    # -------------------------------------------------
    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    axes[2].xaxis.set_major_locator(locator)
    axes[2].xaxis.set_major_formatter(formatter)

    # -------------------------------------------------
    # Save
    # -------------------------------------------------
    if save_png:
        out_path = result_dir / f"market_stress_diagnostics_{score_method}.png"
        fig.savefig(out_path, dpi=200, bbox_inches="tight")
        print("Saved figure:", out_path)

    if show_plot:
        plt.show()
    else:
        plt.close(fig)


def main():
    market_file = "572469_YES.csv"
    score_method = "additive"
    # score_method = "pca"

    plot_market_stress_diagnostics(
        market_file=market_file,
        score_method=score_method,
        top_k_events=12,
        save_png=True,
        show_plot=True,
    )


if __name__ == "__main__":
    main()