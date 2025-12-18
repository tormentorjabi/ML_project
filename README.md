ML_project
==============================

My ML project

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io


--------
# Окружение и запуск (Windows / PowerShell)

## 1. Установка зависимостей
```powershell
uv install
uv run pre-commit install
```

## 2. Поднять инфраструктуру (MinIO + MLflow)
```powershell
docker compose up -d
```
- MinIO web: http://localhost:9001  
- MLflow UI: http://localhost:5000

## 3. Загрузить датасет в MinIO (пример для taxi_trip_pricing.csv)
```powershell
docker compose cp .\taxi_trip_pricing.csv minio-mc:/tmp/taxi_trip_pricing.csv
docker compose exec minio-mc mc cp /tmp/taxi_trip_pricing.csv local/raw/
```
После загрузки в конфиге указывайте `bucket: raw`, `key: taxi_trip_pricing.csv`.

## 4. Запуск одиночного эксперимента
Отредактируйте `configs/experiment.yaml` при необходимости и выполните:
```powershell
docker run --rm --network ml_project_default `
  -e S3_ENDPOINT_URL=http://minio:9000 `
  -e S3_ACCESS_KEY=admin `
  -e S3_SECRET_KEY=admin123 `
  -e MLFLOW_S3_ENDPOINT_URL=http://minio:9000 `
  -v "${PWD}\models:/app/models" `
  -v "${PWD}\configs\experiment.yaml:/app/configs/active.yaml:ro" `
  taxi-experiments `
  python -m src.experiments.run_experiment --config configs/active.yaml
```
Результат:
- run и метрики в MLflow (`taxi-pricing-rf`),
- модель и метрики сохраняются в S3 бакет `experiments/<experiment>/<run>/`,
- локально — в `models/<experiment>/<run>.joblib` и `.metrics.json`.

## 5. Запуск перебора гиперпараметров
Опишите сетку в `configs/grid.yaml` и запустите:
```powershell
docker run --rm --network ml_project_default `
  -e S3_ENDPOINT_URL=http://minio:9000 `
  -e S3_ACCESS_KEY=admin `
  -e S3_SECRET_KEY=admin123 `
  -e MLFLOW_S3_ENDPOINT_URL=http://minio:9000 `
  -v "${PWD}\models:/app/models" `
  -v "${PWD}\configs\grid.yaml:/app/configs/grid_active.yaml:ro" `
  taxi-experiments `
  python -m src.experiments.run_grid --config configs/grid_active.yaml
```
Все комбинации попадут в MLflow эксперимент `taxi-pricing-grid` и в S3 бакет `experiments`.

## 6. REST-сервис для инференса модели

### 6.1. Локальный запуск (без Docker)
```powershell
uv run uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```
По умолчанию сервис ищет модель по пути:
- `models/taxi-pricing-rf/taxi-pricing-rf-max_depth=12-max_features=sqrt-n_estimators=300-20251205-102201.joblib`

Путь к модели можно переопределить:
```powershell
$env:MODEL_PATH="models\taxi-pricing-rf\taxi-pricing-rf-max_depth=12-max_features=sqrt-n_estimators=300-20251205-102201.joblib"
uv run uvicorn src.api.app:app --host 0.0.0.0 --port 8000
```

Проверка работоспособности:
```powershell
curl http://localhost:8000/health
```

Пример запроса к `/predict`:
```powershell
curl -X POST "http://localhost:8000/predict" `
  -H "Content-Type: application/json" `
  -d '{"instances":[{"Trip_Distance_km":10.5,"Time_of_Day":"Morning","Day_of_Week":"Weekday","Passenger_Count":2,"Traffic_Conditions":"Medium","Weather":"Clear","Base_Fare":3.0,"Per_Km_Rate":1.2,"Per_Minute_Rate":0.3,"Trip_Duration_Minutes":25.0}]}'
```

### 6.2. Запуск сервиса в Docker

Собрать образ:
```powershell
docker build -f Dockerfile.api -t taxi-api .
```

Запустить контейнер (модель монтируется из локальной папки `models`):
```powershell
docker run --rm -p 8000:8000 `
  -v "${PWD}\models:/app/models" `
  taxi-api
```

Или явно указать путь к модели:
```powershell
docker run --rm -p 8000:8000 `
  -v "${PWD}\models:/app/models" `
  -e MODEL_PATH="models/taxi-pricing-rf/taxi-pricing-rf-max_depth=12-max_features=sqrt-n_estimators=300-n_estimators=300-20251205-102201.joblib" `
  taxi-api
```

После запуска:
- Swagger UI: http://localhost:8000/docs  
- `/predict`: POST http://localhost:8000/predict

## 7. Нагрузочное тестирование

Для нагрузочного теста используется скрипт `scripts/load_test.py`, который шлёт запросы к `/predict`
в N параллельных соединений и выводит статистику по латенциям.

### 7.1. Запуск
```powershell
uv run python .\scripts\load_test.py `
  --url "http://localhost:8000/predict" `
  --total-requests 500 `
  --concurrency 1 2 5 10 20 50
```

Вывод будет вида:
```text
N   avg_ms  q25_ms  q50_ms  q90_ms  q95_ms  q99_ms  ok_requests
1   ...     ...     ...     ...     ...     ...     500
2   ...
...
```

### 7.2. Таблица для README

| N  | avg, ms | q25, ms | q50, ms | q90, ms | q95, ms | q99, ms |
|----|---------|---------|---------|---------|---------|---------|
| 1  | 65.55   | 64.06   | 65.12   | 68.27   | 70.09   | 84.20   |
| 2  | 120.05  | 109.88  | 119.55  | 142.06  | 147.55  | 159.79  |
| 5  | 303.60  | 283.01  | 303.96  | 343.86  | 361.95  | 387.49  |
| 10 | 616.06  | 577.88  | 617.29  | 697.99  | 726.87  | 783.25  |
| 20 | 1236.77 | 1166.08 | 1256.73 | 1403.63 | 1450.72 | 1527.98 |
| 50 | 3056.78 | 2919.68 | 3127.21 | 3444.49 | 3519.55 | 3643.66 |

### Характеристики железа

- CPU: AMD Ryzen 5 5600 6-Core Processor, 6 cores / 12 threads
- GPU: не использовался, инференс только на CPU

## Примечания
- Ссылка на датасет https://github.com/tormentorjabi/data/blob/main/taxi_trip_pricing.csv
- Образ для обучения: `docker build -t taxi-experiments .`
- Переменные S3/MLflow берутся из окружения, для локалки используются данные из docker-compose (endpoint minio, ключи admin/admin123).
<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
