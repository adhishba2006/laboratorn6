import logging
from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/items", tags=["items"])

fake_db = {1: {"name": "Foo", "price": 50.2, "is_offer": None}}


class Item(BaseModel):
    name: str = Field(..., title="Название", examples=["Телефон"])
    price: float = Field(..., gt=0, title="Цена", examples=[199.99])
    is_offer: bool | None = Field(None, title="Акционный товар")


@router.get("/{item_id}")
def read_item(
    item_id: int = Path(..., title="ID товара", ge=1),
    q: str | None = Query(None, title="Поисковый запрос", max_length=50),
):
    logger.info("Запрос товара с ID=%s (q=%s)", item_id, q)
    if item_id not in fake_db:
        logger.warning("Товар с ID=%s не найден", item_id)
        raise HTTPException(status_code=404, detail="Item not found")
    return {"item_id": item_id, "item": fake_db[item_id], "q": q}


@router.post("/")
def create_item(item: Item):
    logger.info("Попытка создания товара: %s", item.name)
    for existing_item in fake_db.values():
        if existing_item["name"].lower() == item.name.lower():
            logger.error("Конфликт уникальности: товар '%s' уже существует", item.name)
            raise HTTPException(
                status_code=400, detail="Item with this name already exists"
            )

    new_id = max(fake_db.keys(), default=0) + 1
    fake_db[new_id] = item.model_dump()
    logger.info("Товар '%s' успешно создан с ID=%s", item.name, new_id)
    return {"item_id": new_id, **fake_db[new_id]}


@router.put("/{item_id}")
def update_item(
    item: Item,
    item_id: int = Path(..., title="ID товара", ge=1),
):
    logger.info("Попытка обновления товара ID=%s", item_id)
    if item_id not in fake_db:
        logger.warning("Не удалось обновить: товар ID=%s не найден", item_id)
        raise HTTPException(status_code=404, detail="Item not found")

    for existing_id, existing_item in fake_db.items():
        if existing_id != item_id and existing_item["name"].lower() == item.name.lower():
            logger.error("Конфликт уникальности при обновлении ID=%s: имя '%s' занято", item_id, item.name)
            raise HTTPException(
                status_code=400, detail="Item with this name already exists"
            )

    fake_db[item_id] = item.model_dump()
    logger.info("Товар ID=%s успешно обновлён", item_id)
    return {"item_id": item_id, "item": fake_db[item_id]}