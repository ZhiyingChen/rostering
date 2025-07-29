# 中英字典
APP_LANG = {
    "中文": {
        "page_title": "📦 车辆轮转算法平台",
        "welcome_message": "欢迎使用！请通过左侧导航栏选择功能页面：",
        "navigation_guide": """
### 📘 页面导航说明：
- **项目背景**：了解问题背景
- **执行算法**：了解输入输出文件格式，编辑输入文件，运行算法并查看结果
"""
    },
    "English": {
        "page_title": "📦 Vehicle Rotation Algorithm Platform",
        "welcome_message": "Welcome! Please select a feature page via the left navigation bar:",
        "navigation_guide": """
### 📘 Page Navigation Guide:
- **Project Background**: Understand the problem background
- **Execute Algorithm**: Learn about input/output file formats, edit input files, run the algorithm, and view results
"""
    }
}

# 中英字典
PROJECT_DOC_LANG = {
    "中文": {
        "page_title": "📦 汽车轮转与维修调度优化系统 - 项目文档",
        "project_background_header": "🧩 项目背景简介",
        "project_background_text": """
在某大型服务单位的后勤保障系统中，存在若干辆运维车辆需要按小时级排班，在服务区域内全天值守。
每辆车有工作时间、维修时间等复杂的轮转规则，如何最小化所需车辆总数，成为关键优化任务。
本项目基于真实业务需求建立车辆轮换排班模型，并提出创新性的“菱形算法”实现高效调度，最终减少运维成本与车辆投入需求。
""",
        "problem_description_subheader": "📋 问题描述",
        "problem_description_image_caption": "问题描述图",
        "problem_description_details": """
- 每小时必须有至少一辆车在服务区值守
- 每辆车单次连续工作时间不得超过 6 小时
- 每辆车累计服务时间达到 100 小时后必须维修 48 小时，其中包含 8 小时备货时间（可计入维修）
- 服务时间计划为连续 30 天（720 小时）
- 目标：最小化所需车辆数量，并排出每辆车的任务甘特图
"""
    },
    "English": {
        "page_title": "📦 Vehicle Rotation and Maintenance Scheduling Optimization System - Project Documentation",
        "project_background_header": "🧩 Project Background Overview",
        "project_background_text": """
In the logistics support system of a large service unit, several maintenance vehicles need to be scheduled hourly to provide round-the-clock coverage in the service area.
Each vehicle has complex rotation rules involving working hours and maintenance times. Minimizing the total number of required vehicles is the key optimization task.
This project establishes a vehicle rotation scheduling model based on real business needs and proposes an innovative “Diamond Algorithm” for efficient scheduling, ultimately reducing operational costs and vehicle requirements.
""",
        "problem_description_subheader": "📋 Problem Description",
        "problem_description_image_caption": "Problem Description Image",
        "problem_description_details": """
- At least one vehicle must be on duty in the service area every hour
- Each vehicle cannot work continuously for more than 6 hours at a time
- Each vehicle must undergo maintenance for 48 hours after accumulating 100 service hours, including 8 hours of restocking time (which can be counted towards maintenance)
- The service period is planned for continuous 30 days (720 hours)
- Objective: Minimize the number of required vehicles and generate Gantt charts for each vehicle's tasks
"""
    }
}

# 中英字典
EXECUTE_ALGORITHM_LANG = {
    "中文": {
        "page_title": "⚙️ 汽车轮转与维修调度算法",
        "description": """
请在“执行算法”页面将示例输入文件改成你需要的数据。
""",
        "input_interface_header": "📥 输入接口文档",
        "global_params_expander": "📥 输入文件说明：全局参数.csv",
        "global_params_field": ["字段名称", "类型", "描述"],
        "global_params_table": [
            ["参数名称", "str", "各类参数的名称"],
            ["参数值", "double", "参数值"]
        ],
        "global_params_description": """
**参数枚举说明：**
以下是各个参数的定义和含义：

- **t_pack**：装货时间，车辆在装货点需要花费的时间。
- **t_unpack**：卸货时间，车辆在卸货点需要花费的时间。
- **t_pre**：备货时间，车辆在维修点进行备货的时间，这部分时间可以计入维修时间。
- **t_go**：去程时间，车辆从起点出发到达服务区域的时间。
- **t_back**：返程时间，车辆从服务区域返回起点的时间。
- **t_serve**：单次服务时间（小时），车辆在服务区域内一次连续提供服务的时间。
- **t_rest**：维修时间（小时），车辆进行维修所需的时间。
- **t_work**：每辆车的最大累计工作时间（小时），车辆在进行服务和维修之前可以累计的最大工作时间。
- **t0 / t1**：起始时间 / 结束时间，服务时间的开始和结束的具体时间点。
- **t_gap**：错峰时间间隔（小时），在排班时需要考虑的时间间隔，以避免车辆在同一时间段集中出发或返回。
""",
        "output_interface_header": "📥 输出接口文档",
        "vehicle_result_expander": "📥 输出文件说明：车辆和执行结果.csv",
        "vehicle_result_details": """
每一行代表时间（小时），每一列代表每辆车，内容值含义如下：
- 装货： 0
- 出发： 1
- 服务： 2
- 返回： 3
- 卸货： 4
- 备货： 5
- 维修： 6
- 空闲： 7
""",
        "example_data_header": "📄 示例输入数据（可编辑）",
        "edit_global_params": "📝 编辑全局参数",
        "download_global_params": "📥 下载编辑后的 全局参数.csv",
        "run_algorithm": "🚀 运行算法",
        "running_algorithm": "算法运行中，请稍候...",
        "algorithm_success": "✅ 算法运行完成！耗时{}秒",
        "algorithm_error": "❌ 算法运行出错：{}",
        "output_results": "📊 输出结果: 至少需要{}辆车",
        "vehicle_execution_results": "📄 车辆和执行结果",
        "download_vehicle_results": "📥 下载 车辆和执行结果.csv",
        "drawing_gantt_chart": "正在绘制甘特图..."
    },
    "English": {
        "page_title": "⚙️ Vehicle Rotation and Maintenance Scheduling Algorithm",
        "description": """
Please modify the example input files on the "Execute Algorithm" page to your required data.
""",
        "input_interface_header": "📥 Input Interface Documentation",
        "global_params_expander": "📥 Input File Description: global_params.csv",
        "global_params_field": ["Parameter", "Type", "Description"],
        "global_params_table": [
            ["Parameter Name", "str", "Names of various parameters"],
            ["Parameter Value", "double", "Values of parameters"]
        ],
        "global_params_description": """
**Parameter Enumeration Explanation:**
Below are the definitions and meanings of each parameter:

- **t_pack**: Loading time, the time the vehicle spends at the loading point.
- **t_unpack**: Unloading time, the time the vehicle spends at the unloading point.
- **t_pre**: Preparation time, the time the vehicle spends preparing at the maintenance point, which can be counted towards maintenance time.
- **t_go**: Travel time to service area, the time the vehicle takes to travel from the starting point to the service area.
- **t_back**: Return time, the time the vehicle takes to return from the service area to the starting point.
- **t_serve**: Single service duration (hours), the continuous service time the vehicle provides in the service area.
- **t_rest**: Maintenance time (hours), the time the vehicle requires for maintenance.
- **t_work**: Maximum cumulative working time per vehicle (hours), the maximum working time a vehicle can accumulate before service and maintenance.
- **t0 / t1**: Start time / End time, specific start and end times for the service period.
- **t_gap**: Off-peak interval (hours), the time intervals to consider during scheduling to avoid concentrated departures or returns of vehicles.
""",
        "output_interface_header": "📥 Output Interface Documentation",
        "vehicle_result_expander": "📥 Output File Description: vehicle_and_execution_results.csv",
        "vehicle_result_details": """
Each row represents an hour, each column represents a vehicle, and the content values represent:
- Loading: 0
- Departure: 1
- Service: 2
- Return: 3
- Unloading: 4
- Preparation: 5
- Maintenance: 6
- Idle: 7
""",
        "example_data_header": "📄 Example Input Data (Editable)",
        "edit_global_params": "📝 Edit Global Parameters",
        "download_global_params": "📥 Download Edited global_params.csv",
        "run_algorithm": "🚀 Run Algorithm",
        "running_algorithm": "Algorithm running, please wait...",
        "algorithm_success": "✅ Algorithm run successfully! Took {} seconds",
        "algorithm_error": "❌ Algorithm error: {}",
        "output_results": "📊 Output Results: At least {} vehicles needed",
        "vehicle_execution_results": "📄 Vehicle and Execution Results",
        "download_vehicle_results": "📥 Download vehicle_and_execution_results.csv",
        "drawing_gantt_chart": "Drawing Gantt chart..."
    }
}