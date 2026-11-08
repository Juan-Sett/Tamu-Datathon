import json
import time
from dataclasses import dataclass

import requests


class SnowflakeError(Exception):
    pass


@dataclass
class SnowflakeConfig:
    account: str
    host: str
    api_key: str
    role: str = "PUBLIC"
    warehouse: str = "COMPUTE_WH"
    database: str = "AGGIE_DECISION_DESK"
    schema: str = "PUBLIC"


class SnowflakeClient:
    def __init__(self, config):
        self.config = config
        self.base_url = f"https://{config.host.rstrip('/')}/api/v2"
        self.headers = {
            "Authorization": f"Bearer {config.api_key}",
            "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method, path, **kwargs):
        url = path if path.startswith("http") else f"{self.base_url}{path}"
        try:
            response = requests.request(method, url, headers=self.headers, timeout=30, **kwargs)
        except requests.RequestException as exc:
            raise SnowflakeError(f"Could not reach Snowflake: {exc}") from exc
        if response.status_code >= 400:
            raise SnowflakeError(f"Snowflake returned {response.status_code}: {response.text[:300]}")
        return response.json() if response.content else {}

    def execute_sql(self, statement):
        payload = {
            "statement": statement,
            "timeout": 30,
            "warehouse": self.config.warehouse,
            "role": self.config.role,
            "database": self.config.database,
            "schema": self.config.schema,
            "resultSetMetaData": {"format": "jsonv2"},
        }
        result = self._request("POST", "/statements", json=payload)
        status = result.get("statementStatusUrl")
        if status:
            for _ in range(20):
                time.sleep(0.5)
                polled = self._request("GET", status if status.startswith("http") else status if status.startswith("/") else f"/statements/{result.get('statementHandle')}")
                if polled.get("statementStatusUrl") is None and polled.get("code") not in ("333333", "6410"):
                    result = polled
                    break
                if polled.get("message") and "still running" not in polled.get("message", "").lower():
                    raise SnowflakeError(polled["message"])
        return result

    def fetch_campus_facts(self):
        result = self.execute_sql("SELECT ID, CATEGORY, NAME, DESCRIPTION, LOCATION, PRICE, OPEN_TIME, CLOSE_TIME, TAGS, SOURCE_URL, UPDATED_AT FROM CAMPUS_FACTS LIMIT 200")
        rows = result.get("data", [])
        columns = ["id", "category", "name", "description", "location", "price", "open_time", "close_time", "tags", "source_url", "updated_at"]
        return [dict(zip(columns, row)) for row in rows]

    def generate_decision(self, question, records):
        context = json.dumps(records, indent=2)
        prompt = f"""You are Aggie Decision Desk, a concise campus planning copilot.\n\nStudent question:\n{question}\n\nCampus records retrieved from Snowflake:\n{context}\n\nReturn ONLY valid JSON with these keys: recommendation (string), steps (array of strings), why (string), tradeoff (string). Use only the provided records. Do not invent hours, prices, routes, or availability."""
        result = self._request("POST", "/cortex/inference:complete", json={
            "model": "llama3.1-70b",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "max_tokens": 700,
        })
        choice = result.get("choices", [{}])[0]
        content = choice.get("messages") or choice.get("message", {}).get("content", "")
        if isinstance(content, list):
            content = "".join(
                item.get("text", item.get("content", ""))
                for item in content
                if isinstance(item, dict)
            )
        if isinstance(content, dict):
            content = content.get("text", content.get("content", ""))
        try:
            return json.loads(content)
        except (TypeError, json.JSONDecodeError) as exc:
            raise SnowflakeError("Cortex returned an unexpected response format") from exc
