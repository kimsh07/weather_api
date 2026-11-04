# 9월 기상청 관측 자료

## 관측 정보 및 출처

- 관측소: 서울 (지점번호 `108`)
- 조회 기간: 2025-09-01 00:00부터 2025-09-07 23:00까지 (KST)
- 자료 출처: [기상청 API허브 - 지상관측](https://apihub.kma.go.kr/apiList.do?seqApi=2)
- 사용 API: [기상청 시간자료 API](https://apihub.kma.go.kr/api/typ01/url/kma_sfctm3.php)

## 폴더 파일

- `kma_sfctm2.py`: 9월 기간의 시간자료를 요청하고 CSV 및 원본 응답을 저장합니다.
- `Sep_weather.CSV`: 관측시각, 기온, 상대습도, 풍속을 정리한 CSV입니다.
- `Sep_weather_response.txt`: API에서 받은 원본 응답입니다.
- `plot_sep_weather.py`: 저장된 CSV만 읽어 기온 그래프를 만듭니다. API를 호출하지 않습니다.
- `Sep_weather.png`: 생성된 9월 시간별 기온 그래프입니다.
- `requirements-kma-api.txt`: Python 의존성 목록입니다.

CSV 열 순서는 `datetime` (관측시각, KST), `temperature_C` (기온, °C),
`humidity_pct` (상대습도, %), `wind_speed_ms` (풍속, m/s)입니다.

## 설치 및 실행

PowerShell에서 이 폴더로 이동해 의존성을 설치합니다.

```powershell
python -m pip install -r .\requirements-kma-api.txt
```

수집 코드를 실행하면 터미널에서 기상청 API 인증키를 입력하라는 메시지가 표시됩니다. 입력한 키는 화면에 표시되지 않습니다.

```powershell
python .\kma_sfctm2.py
```

이미 저장된 `Sep_weather.CSV`로 그래프만 다시 만들려면 다음 명령을 실행합니다.

```powershell
python .\plot_sep_weather.py
```

그래프 코드는 시간순으로 정렬하고 1시간 간격의 누락 시각을 확인합니다. 누락 시각이나 기온 결측 구간은 그래프에서 선이 끊겨 표시됩니다.
