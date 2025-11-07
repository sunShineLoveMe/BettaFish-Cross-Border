"""Black Friday trend aggregation utilities for QueryEngine agents."""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List, Optional


@dataclass
class BlackFridayTrendRecord:
    """Structured representation of a Black Friday trend sample."""

    product_name: str
    platform: str
    category: str
    historical_peak_years: List[int]
    target_audience: List[str]
    price_range: Dict[str, Any]
    traction_signals: Dict[str, Any]
    source_url: str
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the record into a dictionary with sorted years."""

        payload = asdict(self)
        payload["historical_peak_years"] = sorted(set(self.historical_peak_years))
        return payload


class _BaseTrendClient:
    """Base class for platform specific clients."""

    platform: str
    _dataset: List[BlackFridayTrendRecord]

    def fetch(self, *, category: Optional[str] = None, limit: Optional[int] = None) -> List[BlackFridayTrendRecord]:
        """Return curated trend records for the platform."""

        records: Iterable[BlackFridayTrendRecord] = self._dataset
        if category:
            category_lower = category.lower()
            records = [
                record
                for record in records
                if record.category.lower() == category_lower
            ]
        if limit is None or limit >= len(records):
            return list(records)
        return list(records)[: max(limit, 0)]


class AmazonTrendClient(_BaseTrendClient):
    """Simulated client wrapping Amazon trend endpoints."""

    platform = "amazon"

    def __init__(self) -> None:
        self._dataset = [
            BlackFridayTrendRecord(
                product_name="Echo Dot (5th Gen)",
                platform=self.platform,
                category="smart home",
                historical_peak_years=[2019, 2021, 2022],
                target_audience=["家庭用户", "智能家居入门", "语音助手重度用户"],
                price_range={"currency": "USD", "min": 24.99, "max": 49.99},
                traction_signals={
                    "best_seller_rank": "Top 5 Smart Speakers",
                    "deal_badge": True,
                    "average_rating": 4.7,
                },
                source_url="https://www.amazon.com/dp/B09B8V2B4T",
                notes="连续三年黑五进入智能家居榜单前五，Prime Day 预热带动搜索需求。",
            ),
            BlackFridayTrendRecord(
                product_name="Instant Pot Duo 7-in-1",
                platform=self.platform,
                category="kitchen",
                historical_peak_years=[2018, 2020, 2023],
                target_audience=["家庭厨师", "健康餐备餐", "学生宿舍"],
                price_range={"currency": "USD", "min": 69.99, "max": 129.99},
                traction_signals={
                    "wishlist_mentions": 42000,
                    "coupon_clip_rate": 0.64,
                    "review_volume": 180000,
                },
                source_url="https://www.amazon.com/dp/B08PQ2KWHS",
                notes="常年占据厨房电器爆款榜，组合装在黑五期转化率显著提升。",
            ),
            BlackFridayTrendRecord(
                product_name="Fire TV Stick 4K",
                platform=self.platform,
                category="entertainment",
                historical_peak_years=[2020, 2021, 2022],
                target_audience=["流媒体重度用户", "家庭影音升级", "礼品采购"],
                price_range={"currency": "USD", "min": 29.99, "max": 54.99},
                traction_signals={
                    "bundle_uplift": 0.32,
                    "ad_click_share": 0.18,
                    "review_volume": 250000,
                },
                source_url="https://www.amazon.com/dp/B09R6FJWWS",
                notes="黑五常见捆绑 Echo 设备销售，低价拉新效果显著。",
            ),
        ]


class TikTokTrendClient(_BaseTrendClient):
    """Simulated client wrapping TikTok commerce trend signals."""

    platform = "tiktok"

    def __init__(self) -> None:
        self._dataset = [
            BlackFridayTrendRecord(
                product_name="LED Strip Lights",
                platform=self.platform,
                category="home decor",
                historical_peak_years=[2021, 2022, 2023],
                target_audience=["Z 世代租房", "直播间氛围改造", "短视频创作者"],
                price_range={"currency": "USD", "min": 15.99, "max": 39.99},
                traction_signals={
                    "hashtag_views": 2.3e9,
                    "affiliate_conversion_rate": 0.045,
                    "creator_mentions": 1350,
                },
                source_url="https://www.tiktok.com/tag/ledstriplights",
                notes="达人改造内容在黑五前两周集中爆发，搭配团购券拉动 GMV。",
            ),
            BlackFridayTrendRecord(
                product_name="Portable Blender",
                platform=self.platform,
                category="kitchen",
                historical_peak_years=[2020, 2022],
                target_audience=["健身与代餐人群", "办公室白领", "宿舍学生"],
                price_range={"currency": "USD", "min": 24.99, "max": 59.99},
                traction_signals={
                    "gmv_24h_peak": 430000,
                    "ugc_growth_rate": 0.58,
                    "ads_ctr": 0.074,
                },
                source_url="https://www.tiktok.com/tag/portableblender",
                notes="黑五直播带货搭配奶昔食谱，平价入门款动销最佳。",
            ),
            BlackFridayTrendRecord(
                product_name="Thermal Fleece Leggings",
                platform=self.platform,
                category="apparel",
                historical_peak_years=[2019, 2021, 2023],
                target_audience=["北美女性职场人", "御寒穿搭博主粉丝", "轻户外兴趣"],
                price_range={"currency": "USD", "min": 19.99, "max": 49.99},
                traction_signals={
                    "hashtag_views": 1.1e9,
                    "live_sell_through": 0.37,
                    "repeat_purchase_rate": 0.22,
                },
                source_url="https://www.tiktok.com/tag/winterleggings",
                notes="达人穿搭清单结合优惠券，黑五周搜索热度翻倍。",
            ),
        ]


class BlackFridaySourcesTool:
    """Aggregate Black Friday trend data from multiple platforms."""

    def __init__(self) -> None:
        self._clients: Dict[str, _BaseTrendClient] = {
            "amazon": AmazonTrendClient(),
            "tiktok": TikTokTrendClient(),
        }

    @property
    def supported_platforms(self) -> List[str]:
        """List platforms that have dedicated clients."""

        return list(self._clients.keys())

    def fetch_trends(
        self,
        *,
        platform: Optional[str] = None,
        category: Optional[str] = None,
        limit: Optional[int] = None,
        include_platform_field: bool = True,
    ) -> List[Dict[str, Any]]:
        """Collect curated trend dictionaries suitable for LLM prompts."""

        platforms: List[str]
        if platform:
            platform_key = platform.lower()
            if platform_key not in self._clients:
                raise ValueError(f"Unsupported platform: {platform}")
            platforms = [platform_key]
        else:
            platforms = self.supported_platforms

        records: List[BlackFridayTrendRecord] = []
        for platform_key in platforms:
            client = self._clients[platform_key]
            platform_records = client.fetch(category=category, limit=limit)
            records.extend(platform_records)

        serialised = [record.to_dict() for record in records]

        if not include_platform_field:
            for payload in serialised:
                payload.pop("platform", None)

        if limit is not None and limit >= 0:
            serialised = serialised[:limit]

        return serialised

