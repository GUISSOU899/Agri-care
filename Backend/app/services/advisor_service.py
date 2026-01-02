import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from openai import AsyncOpenAI
from app.core.config import settings

logger = logging.getLogger(__name__)

# Default path relative to the app directory if not in settings
PROMPT_PATH_DEFAULT = "app/ml/prompts/advisor_prompt_fr.json"

class AdvisorService:
    _client: Optional[AsyncOpenAI] = None

    @classmethod
    def _get_client(cls) -> AsyncOpenAI:
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY manquante dans les settings")
        if cls._client is None:
            cls._client = AsyncOpenAI(api_key=api_key)
        return cls._client

    @staticmethod
    def _load_prompt_cfg() -> Dict[str, Any]:
        prompt_path = settings.ADVISOR_PROMPT_PATH or PROMPT_PATH_DEFAULT
        # If absolute path is needed, we could use Path(__file__).parent.parent / prompt_path
        # But if it's relative to CWD (usually the app root in Docker), this works.
        p = Path(prompt_path)
        if not p.is_absolute():
            # Try to resolve relative to the project root
            # In local dev CWD is Projet PFA/Agri-care/Backend
            # In Docker it might be /app
            pass
        return json.loads(p.read_text(encoding="utf-8"))

    @staticmethod
    def _render(template: str, data: Dict[str, Any]) -> str:
        # Avoid KeyError if a field is missing in data
        class SafeDict(dict):
            def __missing__(self, key):
                return f"{{{key}}}"
        
        # Normalize double backslashes for newlines if present in JSON string
        template = template.replace("\\n", "\n")
        return template.format_map(SafeDict(data))

    @classmethod
    async def get_recommendations(cls, context: Dict[str, Any]) -> str:
        try:
            cfg = cls._load_prompt_cfg()
            system_text = cfg.get("system", "")
            template = cfg.get("template", "")
            few_shots = cfg.get("few_shots", [])

            messages = [{"role": "system", "content": system_text}]

            # Flatten/Map context for the template
            # The template expects fields like region_name, rain_sum, etc.
            # We'll normalize the input context to match what the template expects.
            
            # Helper to extract from nested context
            def get_val(path, default="N/A"):
                keys = path.split(".")
                val = context
                for k in keys:
                    if isinstance(val, dict):
                        val = val.get(k)
                    else:
                        return default
                return val if val is not None else default

            # Prepare mapped context for the user prompt
            # Note: The context structure changed between step 1 and step 4.
            # I'll try to be flexible.
            
            mapped_context = {
                "region_name": get_val("region.name"),
                "region_id": get_val("region.id") or get_val("region.region_id"),
                "crop_name": get_val("crop.name"),
                "crop_id": get_val("crop.id") or get_val("crop.crop_id"),
                "window_days": 14,
                "rain_sum": get_val("forecast_14d_summary.rain_sum_mm") or get_val("forecast_14d.rain_sum_mm"),
                "rain_days": get_val("forecast_14d_summary.rain_days") or get_val("forecast_14d.rain_days"),
                "tmean_mean": get_val("forecast_14d_summary.tmean_mean_c") or get_val("forecast_14d.tmean_mean_c"),
                "tmax_p95": get_val("forecast_14d_summary.tmax_p95_c") or get_val("forecast_14d.tmax_p95_c"),
                "heat_days": get_val("forecast_14d_summary.heat_days_gt_32c") or get_val("forecast_14d.heat_days"),
                "cold_days": get_val("forecast_14d_summary.cold_days_lt_5c") or get_val("forecast_14d.cold_days"),
                "gdd_sum": get_val("derived_agro.gdd_sum") or 0.0,
                "ndvi_mean": get_val("ndvi.mean") or 0.0,
                "ndvi_max": get_val("ndvi.max") or 0.0,
                "ndvi_integral": get_val("ndvi.integral") or 0.0,
                "yield_t_ha": get_val("seasonal_yield.yield_t_ha") or get_val("seasonal_prediction.yield_t_ha") or 0.0,
                "confidence": get_val("seasonal_yield.confidence") or get_val("seasonal_prediction.confidence") or 0.0,
            }

            # Few-shots
            for ex in few_shots:
                ex_in = ex.get("input", {})
                ex_out = ex.get("output", "")
                messages.append({"role": "user", "content": cls._render(template, ex_in)})
                messages.append({"role": "assistant", "content": ex_out})

            # Actual User context
            messages.append({"role": "user", "content": cls._render(template, mapped_context)})

            model = settings.OPENAI_MODEL or "gpt-4o-mini"
            client = cls._get_client()
            
            # Using client.responses.create as requested
            resp = await client.responses.create(
                model=model,
                input=messages,
                temperature=0.3,
            )
            return (resp.output_text or "").strip()
            
        except Exception:
            logger.exception("Advisor OpenAI call failed")
            # Fallback to chat completions if responses API fails or is unavailable
            try:
                client = cls._get_client()
                resp = await client.chat.completions.create(
                    model=settings.OPENAI_MODEL or "gpt-4o-mini",
                    messages=messages,
                    temperature=0.3
                )
                return (resp.choices[0].message.content or "").strip()
            except Exception as e2:
                logger.error(f"Fallback also failed: {str(e2)}")
                return "⚠️ L’assistant IA est indisponible (vérifie OPENAI_API_KEY / OPENAI_MODEL)."
