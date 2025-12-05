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

## Примечания
- Ссылка на датасет https://github.com/tormentorjabi/data/blob/main/taxi_trip_pricing.csv
- Образ для обучения: `docker build -t taxi-experiments .`
- Переменные S3/MLflow берутся из окружения, для локалки используются данные из docker-compose (endpoint minio, ключи admin/admin123).
<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
