import asyncio
import csv
import json
import logging
import sys
from pathlib import Path
import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, StrictInt, model_validator

ROOT = Path(__file__).resolve().parent.parent
PARAMETERS = ["计划开始时刻", "计划结束时刻", "服务车辆", "装货时间", "卸货时间", "备货时间", "去程时间", "返程时间", "服务时间", "维修时间", "最大工作时间"]
app = FastAPI(title="Rostering · 车辆轮转优化 API", version="1.0.0")
gate = asyncio.Semaphore(1)
logger = logging.getLogger(__name__)

@app.middleware("http")
async def refresh_frontend_assets(request: Request, call_next):
    response = await call_next(request)
    if not request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-cache, must-revalidate"
    return response

class SolveRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    parameters: dict[str, StrictInt]
    @model_validator(mode="after")
    def validate_parameters(self):
        values = self.parameters
        if set(values) != set(PARAMETERS):
            raise ValueError("必须且只能提供示例中的全部 11 个参数")
        if any(value < 0 or value > 10000 for value in values.values()):
            raise ValueError("参数须为 0–10000 的整数小时")
        horizon = values["计划结束时刻"] - values["计划开始时刻"]
        if not 1 <= horizon <= 1440 or not 1 <= values["服务车辆"] <= 12:
            raise ValueError("计划跨度限制为 1–1440 小时，服务车辆限制为 1–12")
        if not 1 <= values["服务时间"] <= 48:
            raise ValueError("服务时间须为 1–48 小时")
        round_hours = sum(values[key] for key in ["装货时间", "卸货时间", "备货时间", "去程时间", "返程时间", "服务时间"])
        if values["最大工作时间"] < round_hours:
            raise ValueError("不可行：最大工作时间小于完整任务周期")
        if round_hours > 168 or values["维修时间"] > 336:
            raise ValueError("完整任务周期不得超过 168 小时，维修不得超过 336 小时")
        estimate = values["服务车辆"] * (round_hours + values["维修时间"] + values["服务时间"])
        if estimate > 2000:
            raise ValueError("场景规模过大，请减少服务车辆或任务周期")
        return self

@app.get("/api/health")
def health():
    return {"status": "ok", "solver": "singleRoster", "max_concurrent_solves": 1, "timeout_seconds": 20}

@app.get("/api/example")
def example():
    with (ROOT / "data/data.csv").open(encoding="utf-8-sig", newline="") as source:
        parameters = {row["参数名称"]: int(row["参数值"]) for row in csv.DictReader(source)}
    start = parameters["计划开始时刻"]
    end = parameters["计划结束时刻"]
    task_hours = sum(parameters[key] for key in ["装货时间", "去程时间", "服务时间", "返程时间", "卸货时间", "备货时间"])
    slots = end - start + 1
    return {
        "parameters": parameters,
        "scenario": {
            "planning_span_hours": end - start,
            "hourly_slots": slots,
            "required_service_vehicles": parameters["服务车辆"],
            "required_service_vehicle_hours": slots * parameters["服务车辆"],
            "task_cycle_hours": task_hours,
            "maintenance_hours": parameters["维修时间"],
            "max_work_hours": parameters["最大工作时间"],
            "input_parameters": len(parameters),
            "activity_states": 8,
        },
    }

async def run_solver(payload):
    try:
        await asyncio.wait_for(gate.acquire(), timeout=0.1)
    except TimeoutError:
        raise HTTPException(429, "求解器正忙，请稍后重试")
    process = None
    try:
        process = await asyncio.create_subprocess_exec(sys.executable, "-m", "api.worker", cwd=ROOT, stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
        output, errors = await asyncio.wait_for(process.communicate(json.dumps(payload.parameters).encode()), timeout=20)
        if process.returncode:
            logger.error("Solver failed: %s", errors.decode(errors="replace")[-1000:])
            raise HTTPException(422, "算法无法为当前参数生成排班，请调整周期和维护参数")
        return json.loads(output)
    except TimeoutError:
        raise HTTPException(504, "求解超过 20 秒，已终止，请缩小计划范围")
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected solver error")
        raise HTTPException(500, "求解内部异常，请稍后重试")
    finally:
        if process is not None and process.returncode is None:
            process.kill()
            await process.wait()
        gate.release()

@app.post("/api/solve")
async def solve(payload: SolveRequest):
    return await run_solver(payload)

app.mount("/", StaticFiles(directory=ROOT / "frontend", html=True), name="frontend")






