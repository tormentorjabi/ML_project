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
# Установка окружения и зависимостей

## 0. Клонирование репозитория

```
git clone https://github.com/tormentorjabi/ML_project.git
```
## 1.  Инициализация uv и установка зависимостей

```bash 
uv install
```

## 2. Запуск pre-commit hook

```bash
uv run pre-commit install
```

## 3. Настройка MinIO (S3) для локального хранения данных
```
# добавляем alias для локального MinIO
mc alias set local http://localhost:9000 admin admin123

# создаём бакеты, если их ещё нет
mc mb local/raw
mc mb local/processed

# загружаем исходный CSV в raw
mc cp data/raw/taxi_trip_pricing.csv local/raw/
```

## 4. Запуск pipeline
```
uv run python -m src.run_pipeline --bucket raw --input-key taxi_trip_pricing.csv --output-key taxi_trip_pricing_processed.csv

> Параметры:
> - `--bucket` — бакет в S3  
> - `--input-key` — имя исходного файла  
> - `--output-key` — имя обработанного файла 

Или заменяем на ваш датасет

Файл taxi_trip_pricing_processed.csv будет сохранён обратно в S3 (бакет raw).
```
<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
