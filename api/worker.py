import json
import sys
from time import perf_counter
import pandas as pd
from singleRoster.solver import Solver
LABELS = ["装货", "去程", "服务", "返程", "卸货", "备货", "维修", "空闲"]
def solve(parameters):
    started = perf_counter()
    frame = pd.DataFrame(parameters.items(), columns=["参数名称", "参数值"])
    solver = Solver(0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, load_from_file=False, config_df=frame)
    solver.read_config(); solver.generate_car_schedule(); solver.generate_car_distribution()
    matrix = solver.output_df(); hours = [int(hour) for hour in matrix.index]
    vehicles = []; segments = []
    for vehicle_id, column in enumerate(matrix.columns, 1):
        states = [int(value) for value in matrix[column]]
        vehicles.append({"id": vehicle_id, "states": states, "work_hours": sum(state < 6 for state in states), "service_hours": states.count(2), "maintenance_hours": states.count(6)})
        begin = 0
        for offset in range(1, len(states) + 1):
            if offset == len(states) or states[offset] != states[begin]:
                segments.append({"vehicle": vehicle_id, "start": hours[begin], "end": hours[begin] + offset - begin, "state": states[begin], "activity": LABELS[states[begin]]}); begin = offset
    required = parameters["服务车辆"]
    coverage = [sum(vehicle["states"][offset] == 2 for vehicle in vehicles) for offset in range(len(hours))]
    shortage = sum(max(0, required - count) for count in coverage)
    work_values = [vehicle["work_hours"] for vehicle in vehicles]
    valid = bool(solver.check_validity4dist())
    warnings = []
    if shortage: warnings.append(f"计划包含启动准备期，存在 {shortage} 车·小时服务缺口。")
    if not valid: warnings.append("原算法连续服务检查未通过，请检查覆盖曲线。")
    return {"status": "completed", "algorithm": "Original factor-based vehicle rotation heuristic", "runtime_seconds": round(perf_counter() - started, 4), "parameters": parameters, "hours": hours, "vehicles": vehicles, "segments": segments, "coverage": coverage, "labels": LABELS, "kpis": {"vehicles": len(vehicles), "coverage_percent": round(100 * (1 - shortage / (len(hours) * required)), 2), "work_hours": sum(work_values), "shortage_vehicle_hours": shortage, "service_hours": sum(coverage), "maintenance_hours": sum(vehicle["maintenance_hours"] for vehicle in vehicles), "work_spread_hours": max(work_values) - min(work_values)}, "warnings": warnings, "continuous_service_valid": valid}
if __name__ == "__main__":
    try: print(json.dumps(solve(json.loads(sys.stdin.read())), ensure_ascii=False, allow_nan=False))
    except BaseException as error: print(json.dumps({"error": type(error).__name__}, ensure_ascii=False)); sys.exit(1)
