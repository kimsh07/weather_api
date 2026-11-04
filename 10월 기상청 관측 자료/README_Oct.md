# 10월 기상청 관측 자료

## 관측 정보

- 관측소: 서울 (지점번호 `108`)
- 조회 기간: 2025-10-01 00:00부터 2025-10-07 23:00까지 (KST)
- 출처: [기상청 API허브 - 지상관측](https://apihub.kma.go.kr/apiList.do?seqApi=2)
- 시간자료 API: [kma_sfctm3.php](https://apihub.kma.go.kr/api/typ01/url/kma_sfctm3.php)

## 폴더 내용

- `kma_sfctm3.py`: 기상청 시간자료를 요청하고 CSV와 원본 응답을 저장합니다.
- `weather.csv`: TM, TA, HM, WS 관측값을 필요한 열로 정리한 CSV입니다.
- `weather_response.txt`: API에서 받은 원본 응답입니다.
- `plot_weather.py`: `weather.csv`를 읽어 기온 그래프를 만듭니다. API를 다시 호출하지 않습니다.
- `temperature.png`: 생성된 시간별 기온 그래프입니다.

CSV의 열은 `datetime` (관측시각, KST), `temperature_C` (기온, °C),
`humidity_pct` (상대습도, %), `wind_speed_ms` (풍속, m/s) 순서입니다.

## 실행 방법

PowerShell에서 이 폴더로 이동해 필요한 라이브러리를 설치합니다.

```powershell
python -m pip install requests pandas matplotlib
```

수집 스크립트를 실행하면 API 인증키를 입력하라는 메시지가 표시됩니다.
인증키는 화면에 표시되지 않습니다.

```powershell
python .\kma_sfctm3.py
```

이미 저장된 `weather.csv`로 그래프만 다시 만들려면 다음을 실행합니다.

```powershell
python .\plot_weather.py
```

그래프 스크립트는 시간 자료를 정렬하고 1시간 간격의 누락 시각을 확인합니다.
누락 시각이나 기온 결측 구간은 선이 끊겨 표시됩니다.
