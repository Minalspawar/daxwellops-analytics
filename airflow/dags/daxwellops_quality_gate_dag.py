from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from airflow import DAG
from airflow.decorators import task
from airflow.exceptions import AirflowFailException


DAG_ID = "daxwellops_dbt_quality_gate"
DBT_DIR = "/opt/airflow/dbt/daxwellops"

DEFAULT_ARGS = {
    "owner": "daxwellops",
    "retries": 3,
    "retry_delay": timedelta(minutes=2),
    "retry_exponential_backoff": True,
    "max_retry_delay": timedelta(minutes=15),
}

def jlog(event: str, **fields: Any) -> None:
    """Structured JSON log line (great for production debugging)."""
    payload: Dict[str, Any] = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "event": event,
        "dag_id": DAG_ID,
        **fields,
    }
    print(json.dumps(payload, ensure_ascii=False))

def run_cmd(cmd: str, step: str) -> None:
    start = datetime.now(timezone.utc)
    jlog("cmd_start", step=step, cmd=cmd)

    p = subprocess.run(
        ["bash", "-lc", cmd],
        capture_output=True,
        text=True
    )

    end = datetime.now(timezone.utc)
    duration_s = (end - start).total_seconds()

    # Emit stdout/stderr as structured fields (truncate to keep logs readable)
    jlog(
        "cmd_result",
        step=step,
        returncode=p.returncode,
        duration_s=duration_s,
        stdout_tail=p.stdout[-2000:],
        stderr_tail=p.stderr[-2000:],
    )

    if p.returncode != 0:
        raise AirflowFailException(f"[{step}] Command failed: {cmd}")

def discord_notify(message: str) -> None:
    """Optional: send a Discord alert if DISCORD_WEBHOOK_URL is set."""
    url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not url:
        jlog("discord_skip", reason="DISCORD_WEBHOOK_URL not set")
        return

    try:
        import requests  # type: ignore
        resp = requests.post(url, json={"content": message}, timeout=10)
        jlog("discord_sent", status_code=resp.status_code)
    except Exception as e:
        jlog("discord_error", error=str(e))

def on_failure_callback(context: dict) -> None:
    ti = context.get("task_instance")
    dag = context.get("dag")
    msg = (
        f"?? Airflow failure: DAG `{dag.dag_id if dag else DAG_ID}` "
        f"Task `{ti.task_id if ti else 'unknown'}` "
        f"Run `{context.get('run_id','')}`"
    )
    discord_notify(msg)

with DAG(
    dag_id=DAG_ID,
    start_date=datetime(2026, 2, 1),
    schedule=None,  # manual trigger for demo
    catchup=False,
    default_args=DEFAULT_ARGS,
    on_failure_callback=on_failure_callback,
    tags=["daxwellops", "dbt", "quality", "reliability"],
) as dag:

    @task(retries=3, retry_delay=timedelta(minutes=1))
    def dbt_run():
        run_cmd(f"cd {DBT_DIR} && dbt run --profiles-dir .", step="dbt_run")

    @task(retries=2, retry_delay=timedelta(minutes=1))
    def dbt_test():
        run_cmd(f"cd {DBT_DIR} && dbt test --profiles-dir .", step="dbt_test")

    dbt_run() >> dbt_test()