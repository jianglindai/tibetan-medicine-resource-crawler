"""藏药材数据模型"""

from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass
class MedicineImage:
    """药材图片"""

    url: str
    alt: str = ""
    local_path: str = ""


@dataclasses.dataclass
class MedicineRecord:
    """藏药材数据记录"""

    scientific_name: str = ""
    latin_name: str = ""
    aliases: list[str] = dataclasses.field(default_factory=list)
    medicine_name: str = ""
    medicinal_parts: list[str] = dataclasses.field(default_factory=list)

    functions_and_indications: str = ""
    morphological_characteristics: str = ""
    distribution: str = ""

    images: list[MedicineImage] = dataclasses.field(default_factory=list)
    notes: str = ""

    source_url: str = ""
    crawled_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        result = dataclasses.asdict(self)
        result["images"] = [img.__dict__ if dataclasses.is_dataclass(img) else img for img in self.images]
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> MedicineRecord:
        images_data = data.pop("images", [])
        images = [MedicineImage(**img) if isinstance(img, dict) else img for img in images_data]
        return cls(**data, images=images)
