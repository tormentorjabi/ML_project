from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.models.predict_model import load_model, predict


class TaxiTrip(BaseModel):  # type: ignore[misc]
    Trip_Distance_km: Optional[float] = Field(
        default=None,
        description="Расстояние поездки, км",
    )
    Time_of_Day: Optional[str] = Field(
        default=None,
        description="Время суток (Morning, Afternoon, Evening, Night)",
    )
    Day_of_Week: Optional[str] = Field(
        default=None,
        description="День недели (Weekday, Weekend)",
    )
    Passenger_Count: Optional[float] = Field(
        default=None,
        description="Количество пассажиров",
    )
    Traffic_Conditions: Optional[str] = Field(
        default=None,
        description="Уровень трафика (Low, Medium, High)",
    )
    Weather: Optional[str] = Field(
        default=None,
        description="Погода (Clear, Rain, etc.)",
    )
    Base_Fare: Optional[float] = Field(
        default=None,
        description="Базовый тариф",
    )
    Per_Km_Rate: Optional[float] = Field(
        default=None,
        description="Стоимость за км",
    )
    Per_Minute_Rate: Optional[float] = Field(
        default=None,
        description="Стоимость за минуту",
    )
    Trip_Duration_Minutes: Optional[float] = Field(
        default=None,
        description="Длительность поездки в минутах",
    )


class PredictRequest(BaseModel):  # type: ignore[misc]
    instances: List[TaxiTrip] = Field(
        description="Список поездок, для которых нужно сделать предсказание цены"
    )


class PredictResponse(BaseModel):  # type: ignore[misc]
    predictions: List[float]


def _get_model_path() -> Path:
    """
    Получить путь до модели из переменной окружения MODEL_PATH.
    Если переменная не задана, используем разумный дефолт.
    """
    env_path = os.getenv("MODEL_PATH")
    if env_path:
        return Path(env_path)

    # Дефолт: один из уже обученных RF в каталоге models/taxi-pricing-rf
    default = (
        Path("models")
        / "taxi-pricing-rf"
        / "taxi-pricing-rf-max_depth=12-max_features=sqrt-n_estimators=300-20251205-102201.joblib"
    )
    return default


app = FastAPI(
    title="Taxi Pricing Model API",
    description="REST сервис для инференса модели прогнозирования стоимости поездки на такси",
    version="0.1.0",
)

_model = None


@app.on_event("startup")  # type: ignore[misc]
def load_model_on_startup() -> None:
    global _model
    model_path = _get_model_path()
    try:
        _model = load_model(model_path)
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"Не удалось загрузить модель по пути {model_path}. "
            "Убедитесь, что смонтировали каталог models в контейнер "
            "или задали переменную MODEL_PATH."
        ) from exc


@app.get("/health")  # type: ignore[misc]
def health() -> dict[str, str]:
    if _model is None:
        return {"status": "error", "detail": "model_not_loaded"}
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)  # type: ignore[misc]
def make_prediction(request: PredictRequest) -> PredictResponse:
    if _model is None:
        raise HTTPException(status_code=500, detail="Модель не загружена")

    if not request.instances:
        raise HTTPException(status_code=400, detail="Список instances пуст")

    # Преобразуем список Pydantic-моделей в DataFrame
    data_dicts = [item.dict() for item in request.instances]
    data_frame = pd.DataFrame(data_dicts)

    try:
        preds = predict(_model, data_frame)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Ошибка во время инференса: {exc}") from exc

    # Приводим к list[float] для сериализации
    preds_list = [float(x) for x in preds]
    return PredictResponse(predictions=preds_list)
