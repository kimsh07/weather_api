"""Plot September hourly temperatures from Sep_weather.CSV."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DATA_PATH = Path(__file__).resolve().with_name("Sep_weather.CSV")
PLOT_PATH = Path(__file__).resolve().with_name("Sep_weather.png")


def load_hourly_temperatures(csv_path: Path) -> tuple[pd.Series, list[pd.Timestamp]]:
    """Load, sort, and reindex September temperatures to every hour."""
    frame = pd.read_csv(csv_path, parse_dates=["datetime"])
    required_columns = {"datetime", "temperature_C"}
    missing_columns = required_columns.difference(frame.columns)
    if missing_columns:
        raise ValueError(
            f"CSV에 필요한 열이 없습니다: {', '.join(sorted(missing_columns))}"
        )
    if frame.empty:
        raise ValueError("CSV에 관측 데이터가 없습니다.")

    frame["temperature_C"] = pd.to_numeric(frame["temperature_C"], errors="raise")
    frame = frame.sort_values("datetime").set_index("datetime")
    if frame.index.has_duplicates:
        raise ValueError("CSV에 중복 관측 시각이 있습니다.")

    hourly_index = pd.date_range(
        start=frame.index.min(),
        end=frame.index.max(),
        freq="h",
        name="datetime",
    )
    temperatures = frame["temperature_C"].reindex(hourly_index)
    missing_times = temperatures.index[temperatures.isna()].tolist()
    return temperatures, missing_times


def plot_temperatures(temperatures: pd.Series) -> None:
    """Save and display the September chart without modifying other plots."""
    figure, axis = plt.subplots(figsize=(12, 6))
    axis.plot(temperatures.index, temperatures, linewidth=2)
    axis.set_title("Temperature over time")
    axis.set_xlabel("Time (KST)")
    axis.set_ylabel("Temperature (°C)")
    axis.grid(True, alpha=0.3)
    figure.autofmt_xdate()
    figure.tight_layout()
    figure.savefig(PLOT_PATH, dpi=150)
    print(f"그래프 저장 위치: {PLOT_PATH}")
    plt.show()


def main() -> None:
    """Read only Sep_weather.CSV and render its temperature plot."""
    temperatures, missing_times = load_hourly_temperatures(DATA_PATH)
    if missing_times:
        print(f"누락된 시각 ({len(missing_times)}개):")
        for timestamp in missing_times:
            print(timestamp.strftime("%Y-%m-%d %H:%M:%S"))
    else:
        print("누락된 시각이 없습니다.")
    plot_temperatures(temperatures)


if __name__ == "__main__":
    main()
