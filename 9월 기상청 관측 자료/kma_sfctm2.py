"""Fetch KMA hourly observations for September and save a separate CSV."""

import getpass
from pathlib import Path

import pandas as pd
import requests


API_URL = "https://apihub.kma.go.kr/api/typ01/url/kma_sfctm3.php"
TIMEOUT_SECONDS = 30
HEADER_POSITIONS = {"TM": 1, "WS": 4, "TA": 12, "HM": 14}
OUTPUT_COLUMNS = ["datetime", "temperature_C", "humidity_pct", "wind_speed_ms"]
MISSING_VALUES = {
    "", "-9", "-9.0", "-9.9", "-99", "-99.0", "-99.9",
    "-999", "-999.0", "-999.9", "-9999",
}
TEMPERATURE_MISSING_VALUES = {
    "", "-99", "-99.0", "-99.9", "-999", "-999.0", "-999.9", "-9999",
}


def decode_response(response: requests.Response) -> str:
    """Decode the response using its declared or detected character set."""
    content_type = response.headers.get("Content-Type", "")
    if "charset=" not in content_type.lower():
        response.encoding = response.apparent_encoding or response.encoding or "utf-8"
    return response.text


def get_header_positions(lines: list[str]) -> dict[str, int]:
    """Find the commented field header and verify official 1-based positions."""
    aliases = {"TM", "YYMMDDHHMI"}
    for line in lines:
        if not line.lstrip().startswith("#"):
            continue
        fields = line.lstrip()[1:].split()
        if not fields or fields[0].upper() not in aliases:
            continue
        normalized = [
            "TM" if field.upper() in aliases else field.upper()
            for field in fields
        ]
        positions = {
            field: normalized.index(field) + 1
            for field in HEADER_POSITIONS
            if field in normalized
        }
        if positions != HEADER_POSITIONS:
            raise ValueError(f"응답 헤더 위치가 예상과 다릅니다: {positions}")
        return positions
    raise ValueError("응답에서 자료 필드 헤더를 찾을 수 없습니다.")


def parse_observations(body: str, positions: dict[str, int]) -> pd.DataFrame:
    """Parse whitespace-separated response rows into sorted hourly observations."""
    records: list[dict[str, str]] = []
    for line in body.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        fields = line.split()
        if len(fields) < max(positions.values()):
            raise ValueError(f"필드 수가 부족한 자료 행입니다: {line}")
        records.append(
            {
                "datetime": fields[positions["TM"] - 1],
                "wind_speed_ms": fields[positions["WS"] - 1],
                "temperature_C": fields[positions["TA"] - 1],
                "humidity_pct": fields[positions["HM"] - 1],
            }
        )

    if not records:
        raise ValueError("응답에 처리할 실제 자료 행이 없습니다.")

    frame = pd.DataFrame.from_records(records, columns=OUTPUT_COLUMNS)
    frame["datetime"] = pd.to_datetime(
        frame["datetime"], format="%Y%m%d%H%M", errors="raise"
    )
    for column in OUTPUT_COLUMNS[1:]:
        values = frame[column].str.strip()
        missing_values = (
            TEMPERATURE_MISSING_VALUES if column == "temperature_C" else MISSING_VALUES
        )
        frame[column] = pd.to_numeric(
            values.mask(values.isin(missing_values)), errors="raise"
        )

    frame = frame.sort_values("datetime").reset_index(drop=True)
    if frame["datetime"].duplicated().any():
        raise ValueError("중복 관측 시각이 있어 CSV 저장을 중단합니다.")
    return frame


def main() -> None:
    """Fetch September data and save the raw response and separate CSV."""
    auth_key = getpass.getpass("기상청 API 인증키: ").strip()
    if not auth_key:
        print("인증키가 비어 있어 요청을 중단합니다.")
        raise SystemExit(1)

    params = {
        "tm1": "202509010000",
        "tm2": "202509072300",
        "stn": "108",
        "help": "1",
        "authKey": auth_key,
    }
    try:
        response = requests.get(API_URL, params=params, timeout=TIMEOUT_SECONDS)
    except requests.RequestException:
        print("HTTP 상태: 확인 불가")
        print("기상청 API 요청에 실패했습니다. 네트워크 연결과 요청 설정을 확인하세요.")
        raise SystemExit(1) from None

    print(f"HTTP 상태: {response.status_code}")
    body = decode_response(response).replace(auth_key, "[인증키 숨김]")
    if not response.ok:
        print("요청에 실패했습니다. 응답 메시지:")
        print(body)
        raise SystemExit(1)

    output_dir = Path(__file__).resolve().parent
    raw_path = output_dir / "Sep_weather_response.txt"
    csv_path = output_dir / "Sep_weather.CSV"
    raw_path.write_bytes(response.content)
    print(f"원본 응답 저장 위치: {raw_path}")

    lines = body.splitlines()
    print("\n본문 앞 15줄:")
    print("\n".join(lines[:15]))
    data_rows = [
        line for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    ]
    print("\n실제 데이터 행 3개:")
    print("\n".join(data_rows[:3]) if data_rows else "응답에 실제 데이터 행이 없습니다.")

    try:
        positions = get_header_positions(lines)
        print(
            "\n헤더 위치 확인: "
            + ", ".join(f"{field}({position})" for field, position in positions.items())
        )
        frame = parse_observations(body, positions)
    except (ValueError, KeyError) as error:
        print(f"응답 자료 처리 중 오류: {error}")
        raise SystemExit(1) from None

    frame.to_csv(csv_path, index=False, encoding="utf-8-sig", na_rep="")
    print(f"\n행 수: {len(frame)}")
    print("변환된 표 앞 3행:")
    print(frame.head(3).to_string(index=False))
    print("열별 결측 수:")
    print(frame.isna().sum().to_string())
    print(f"첫 시각: {frame['datetime'].iloc[0]}")
    print(f"마지막 시각: {frame['datetime'].iloc[-1]}")
    print(f"CSV 저장 위치: {csv_path}")


if __name__ == "__main__":
    main()
