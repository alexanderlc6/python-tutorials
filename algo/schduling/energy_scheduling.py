"""
    测试服能量调度
"""
import copy
import logging

import psycopg2
import requests
import jsonpath
import logging
from datetime import datetime

from psycopg2.extras import execute_values, Json

from common.Signnature import APISignature
from datetime import date, timedelta, datetime
from time import time
from common.read_utils import load_plants_from_csv
import pandas as pd
import truststore
import json
import numpy as np
from typing import List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict

account = {}

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("foxess_sync")

base_url = "https://test.maitian-yun.com"

# 数据库
DB_CONFIG = {
    'host': '212.64.73.96',  # 数据库服务器地址（如 '127.0.0.1' 或远程 IP）
    'port': 5432,  # PostgreSQL 默认端口是 5432
    'database': 'metabase',  # 你的数据库名
    'user': 'postgres',  # 登录用户名
    'password': 'Xwj981226.'  # 密码
}


# ===== 工具函数 =====
# 日志打印
def log_request_response(method, url, headers, json_body, response):
    """统一打印请求和响应日志（用于调试）"""
    logger.debug("---------- API REQUEST ----------")
    logger.debug(f"METHOD: {method}")
    logger.debug(f"URL: {url}")
    logger.debug("HEADERS:")
    for k, v in headers.items():
        logger.debug(f"  {k}: {v}")
    logger.debug("JSON BODY:")
    logger.debug(json.dumps(json_body, indent=2, ensure_ascii=False))
    logger.debug("---------- API RESPONSE ----------")
    logger.debug(f"STATUS: {response.status_code}")
    try:
        resp_json = response.json()
        logger.debug("RESPONSE JSON:")
        logger.debug(json.dumps(resp_json, indent=2, ensure_ascii=False))
    except Exception as e:
        logger.debug(f"RESPONSE TEXT (non-JSON): {response.text}")
    logger.debug("---------- END ----------\n")


# 获取当前日期
def get_current_date():
    today = date.today()
    return {
        "year": today.year,
        "month": today.month,
        "day": today.day
    }


# 获取昨日日期
def get_yesterday_date():
    yesterday = date.today() - timedelta(days=1)
    return {
        "year": yesterday.year,
        "month": yesterday.month,
        "day": yesterday.day
    }


# 工作模式转码
def encode_work_mode(mode_str: str) -> int:
    """将 workMode 字符串转为数值编码"""
    if not mode_str:
        return None
    mode_str = mode_str.strip()
    if mode_str == "SelfUse":
        return 0
    elif mode_str.startswith("ForceCharge"):
        return 1
    elif mode_str.startswith("ForceDischarge"):
        return -1
    else:
        return 2  # Backup / Feedin / 其他


# 处理敏感字段
def sanitize_dict(data: dict) -> dict:
    """脱敏敏感字段"""
    if not data:
        return {}
    data = copy.deepcopy(data)
    sensitive_keys = {"token", "password", "signature", "sid", "captcha"}
    for key in list(data.keys()):
        if key.lower() in sensitive_keys:
            data[key] = "***REDACTED***"
    return data


# 将API调用记录安全写入数据库
def log_api_call_to_db(
        plant_id: str = None,
        device_id: str = None,
        endpoint: str = None,
        method: str = "POST",
        request_params: dict = None,
        request_headers: dict = None,
        request_body: dict = None,
        status_code: int = None,
        response_body: dict = None,
        success: bool = False,
        error_message: str = None,
        duration_ms: int = 0
):
    """将API调用记录安全写入数据库"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO api_call_logs (
                plant_id, device_id, endpoint, method,
                request_params, request_headers, request_body,
                status_code, response_body,
                success, error_message, duration_ms
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            plant_id,
            device_id,
            endpoint,
            method,
            Json(sanitize_dict(request_params)) if request_params else None,
            Json(sanitize_dict(request_headers)) if request_headers else None,
            Json(sanitize_dict(request_body)) if request_body else None,
            status_code,
            Json(response_body) if response_body else None,
            success,
            error_message,
            duration_ms
        ))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        logger.error(f"[DB Log Error] Failed to save API log: {e}")


# ===== 统一安全调用器 =====
def safe_api_call(func_name: str, callable_func):
    """基础安全调用，不记录到数据库"""
    start = time()
    try:
        result = callable_func()
        duration = int((time() - start) * 1000)
        logger.info(f"{func_name} 成功 | 耗时: {duration}ms")
        return True, result
    except Exception as e:
        duration = int((time() - start) * 1000)
        logger.error(f"❌ {func_name} 失败 | 耗时: {duration}ms | 错误: {str(e)}", exc_info=True)
        return False, None


def logged_api_call(
        func_name: str,
        callable_func,
        plant_id: str = None,
        device_id: str = None,
        endpoint: str = None,
        method: str = "POST",
        request_params: dict = None,
        request_headers: dict = None,
        request_body: dict = None
):
    """
    安全API调用并记录到数据库（除了登录接口）
    返回: (success: bool, response: requests.Response or data)
    """
    start = time()
    resp = None  # 保存 Response 对象

    try:
        resp = callable_func()  # 必须返回 Response 对象！
        duration = int((time() - start) * 1000)

        # 提取响应信息
        status_code = resp.status_code  # 使用保存的 Response 对象
        try:
            resp_json = resp.json()
        except:
            resp_json = {"raw_text": resp.text[:500]}

        # 判断是否成功（HTTP 2xx 且 errno=0）
        http_success = 200 <= status_code < 300
        api_success = False
        if http_success and isinstance(resp_json, dict):
            api_success = resp_json.get("errno") == 0

        success = http_success and api_success

        # 记录到数据库（除了登录接口）
        if endpoint != "/basic/v1/user/login":
            log_api_call_to_db(
                plant_id=plant_id,
                device_id=device_id,
                endpoint=endpoint,
                method=method,
                request_params=request_params,
                request_headers=request_headers,
                request_body=request_body,
                status_code=status_code,
                response_body=resp_json,
                success=success,
                error_message=None if success else f"HTTP: {status_code}, API: {resp_json.get('msg', 'Unknown error')}",
                duration_ms=duration
            )

        # 原有日志
        if success:
            logger.info(f"✅ {func_name} 成功 | 耗时: {duration}ms")
        else:
            error_msg = resp_json.get('msg', f"HTTP {status_code}")
            logger.error(f"❌ {func_name} 失败 | 耗时: {duration}ms | 错误: {error_msg}")

        return success, resp

    except Exception as e:
        duration = int((time() - start) * 1000)
        error_msg = str(e)
        logger.error(f"❌ {func_name} 失败 | 耗时: {duration}ms | 错误: {error_msg}", exc_info=True)

        # 记录到数据库（除了登录接口）
        if endpoint != "/basic/v1/user/login":
            log_api_call_to_db(
                plant_id=plant_id,
                device_id=device_id,
                endpoint=endpoint,
                method=method,
                request_params=request_params,
                request_headers=request_headers,
                request_body=request_body,
                status_code=None,
                response_body=None,
                success=False,
                error_message=error_msg,
                duration_ms=duration
            )
        return False, None


# ===== API 调用封装 =====
# 登录  拿到token和sid值（不记录到数据库）
def login():
    def _call():
        resp = requests.post(
            url=base_url + "/basic/v1/user/login",
            headers={
                "lang": "en",
                "signature": "be867234c2887bd0023f35c9a4f87dee.1370579500",
                "timestamp": "1766140625420",
                "timezone": "Asia/Shanghai",
                "Content-Type": "application/json",
                "platform": "android",
                "token": ""
            },
            json={
                "type": 1,
                "verification": 1,
                "user": "a124",
                "password": "670b14728ad9902aecba32e22fa4f6bd",
                "captcha": "1",
                "registrationID": "160a3797c814275e934"
            },
            verify=False,
            timeout=30
        )
        log_request_response("POST", resp.url, resp.request.headers,
                             resp.request.body and json.loads(resp.request.body), resp)
        resp.raise_for_status()
        data = resp.json()
        if data.get("errno") != 0:
            raise Exception(f"Login failed: {data.get('msg')}")
        token = jsonpath.jsonpath(data, "$.result.token")
        if not token:
            raise ValueError("Token not found in login response")
        account["token"] = token[0]
        account["salt"] = resp.headers.get("sid")
        return data

    success, _ = safe_api_call("login", _call)
    return success


# 按日（查昨日）查询可以获取昨日实际买卖电价、实际收益total revenue=Solar Savings+Feed-in-Revenue 、Solar Savings、Feed-in-Revenue，这边数据是15分钟的间隔
def call_earning_curve(plant_id: str, target_date: dict):
    """获取收益曲线数据"""
    test = signer.debug_signature(
        salt=account.get("salt"),
        timestamp=signer.get_current_timestamp(),
        lang="en",
        token=account.get("token"),
        url_path="/dew/v0/earning/curve"
    )
    sign = test["signature"]
    headers = {
        "lang": "en",
        "signature": sign,
        "timestamp": test["timestamp"],
        "timezone": "Asia/Shanghai",
        "Content-Type": "application/json",
        "platform": "android",
        "token": account["token"]
    }
    json_body = {
        "date": {**target_date, "week": 0},
        "plantId": plant_id,
        "dimension": "DAY"
    }

    def _call():
        url = base_url + "/dew/v0/earning/curve"
        resp = requests.post(url, headers=headers, json=json_body, verify=False, timeout=30)
        log_request_response("POST", url, headers, json_body, resp)
        resp.raise_for_status()
        return resp

    # 使用 logged_api_call 包装
    success, result = logged_api_call(
        func_name=f"earning_curve({plant_id})",
        callable_func=_call,
        plant_id=plant_id,
        endpoint="/dew/v0/earning/curve",
        method="POST",
        request_headers=headers,
        request_body=json_body
    )
    if success:
        # 解析响应数据
        data = result.json()
        if data.get("errno") != 0:
            raise Exception(f"API error: {data.get('msg')}")
        return data
    else:
        raise Exception(f"call_earning_curve failed for plant {plant_id}")


# 获取实际模式
def call_scheduler_mode(device_id: str, shard_id: Optional[int] = None):
    """获取调度器模式"""
    url_path = "/dew/v0/device/mode/scheduler/get"
    test = signer.debug_signature(
        salt=account["salt"],
        timestamp=signer.get_current_timestamp(),
        lang="en",
        token=account["token"],
        url_path=url_path
    )
    sign = test["signature"]
    headers = {
        "Content-Type": "application/json",
        "platform": "android",
        "lang": "en",
        "timezone": "Asia/Shanghai",
        "token": account["token"],
        "timestamp": test["timestamp"],
        "signature": sign
    }
    json_body = {"type": 3, "deviceID": device_id}
    if shard_id is not None:
        json_body["shardID"] = shard_id

    def _call():
        url = base_url + url_path
        resp = requests.post(url, headers=headers, json=json_body, verify=False, timeout=30)
        log_request_response("POST", url, headers, json_body, resp)
        resp.raise_for_status()
        return resp

    # 使用 logged_api_call 包装
    success, result = logged_api_call(
        func_name=f"scheduler_mode({device_id})",
        callable_func=_call,
        device_id=device_id,
        endpoint="/dew/v0/device/mode/scheduler/get",
        method="POST",
        request_headers=headers,
        request_body=json_body
    )
    if success:
        # 解析响应数据
        data = result.json()
        if data.get("errno") != 0:
            raise Exception(f"API error: {data.get('msg')}")
        return data
    else:
        raise Exception(f"call_scheduler_mode failed for device {device_id}")


# 预测发电和用电接口
def call_forecast_curve(plant_id: str):
    """获取预测曲线数据"""
    test = signer.debug_signature(
        salt=account["salt"],
        timestamp=signer.get_current_timestamp(),
        lang="en",
        token=account["token"],
        url_path="/dew/v0/earning/forecastCurve"
    )
    sign = test["signature"]
    headers = {
        "Content-Type": "application/json",
        "platform": "android",
        "lang": "en",
        "timezone": "Asia/Shanghai",
        "token": account["token"],
        "timestamp": test["timestamp"],
        "signature": sign
    }
    json_body = {"plantId": plant_id}

    def _call():
        url = base_url + "/dew/v0/earning/forecastCurve"
        resp = requests.post(url, headers=headers, json=json_body, verify=False, timeout=30)
        log_request_response("POST", url, headers, json_body, resp)
        resp.raise_for_status()
        return resp

    # 使用 logged_api_call 包装
    success, result = logged_api_call(
        func_name=f"forecast_curve({plant_id})",
        callable_func=_call,
        plant_id=plant_id,
        endpoint="/dew/v0/earning/forecastCurve",
        method="POST",
        request_headers=headers,
        request_body=json_body
    )
    if success:
        # 解析响应数据
        data = result.json()
        if data.get("errno") != 0:
            raise Exception(f"API error: {data.get('msg')}")
        return data
    else:
        raise Exception(f"call_forecast_curve failed for plant {plant_id}")


# 查询 当日实际发电用电
def call_earning_raw(plant_id: str, target_date: dict):
    """获取原始收益数据"""
    test = signer.debug_signature(
        salt=account["salt"],
        timestamp=signer.get_current_timestamp(),
        lang="en",
        token=account["token"],
        url_path="/dew/v0/earning/internal/earningRaw"
    )
    sign = test["signature"]
    headers = {
        "Content-Type": "application/json",
        "platform": "android",
        "lang": "en",
        "timezone": "Asia/Shanghai",
        "token": account["token"],
        "timestamp": test["timestamp"],
        "signature": sign
    }
    json_body = {
        "plantId": plant_id,
        "dimension": "DAY",
        "date": target_date
    }

    def _call():
        url = base_url + "/dew/v0/earning/internal/earningRaw"
        resp = requests.post(url, headers=headers, json=json_body, verify=False, timeout=30)
        log_request_response("POST", url, headers, json_body, resp)
        resp.raise_for_status()
        return resp

    # 使用 logged_api_call 包装
    success, result = logged_api_call(
        func_name=f"earning_raw({plant_id})",
        callable_func=_call,
        plant_id=plant_id,
        endpoint="/dew/v0/earning/internal/earningRaw",
        method="POST",
        request_headers=headers,
        request_body=json_body
    )
    if success:
        # 解析响应数据
        data = result.json()
        if data.get("errno") != 0:
            raise Exception(f"API error: {data.get('msg')}")
        return data
    else:
        raise Exception(f"call_earning_raw failed for plant {plant_id}")


# 查7天实际的用电和发电
def call_plant_history_report(plant_id: str, year: int, month: int):
    """用于 fetch_actual_daily_data_cross_month 的接口，带完整监控"""
    json_body = {
        "date": {"year": year, "month": month, "day": 1},
        "variables": ["input", "loads", "feedin", "gridConsumption"],
        "custom": False,
        "plantID": plant_id,
        "dimension": "month"
    }
    url = base_url + "/dew/v1/plant/history/report"
    test = signer.debug_signature("POST", url, json_body)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"DEW {test}",
        "User-Agent": "Mozilla/5.0"
    }

    def _call():
        resp = requests.post(url, headers=headers, json=json_body, verify=False, timeout=10)
        log_request_response("POST", url, headers, json_body, resp)
        resp.raise_for_status()
        return resp

    # 使用 logged_api_call 包装
    success, result = logged_api_call(
        func_name=f"plant_history_report({plant_id}, {year}-{month})",
        callable_func=_call,
        plant_id=plant_id,
        endpoint="/dew/v1/plant/history/report",
        method="POST",
        request_headers=headers,
        request_body=json_body
    )
    if success:
        # 解析响应数据
        data = result.json()
        if data.get("errno") != 0:
            raise Exception(f"Plant history report error: {data.get('msg')}")
        return data.get("result", {}).get("data", [])
    else:
        raise Exception(f"call_plant_history_report failed for plant {plant_id}")


# ===== 数据提取与转换 =====
def extract_curve(response_data):
    result = response_data.get("result", {})
    extract_data = {}
    for item in result.get("data", []):
        name = item.get("name")
        if name not in ["Solar Savings", "Feed-in-Revenue", "Predicted Earning"]:
            continue
        points = item.get("points", [])
        time_value_map = {}
        for pt in points:
            if not isinstance(pt, dict):
                logger.warning(f"跳过非字典类型的 point: {pt}")
                continue
            t = pt.get("index")
            v = pt.get("value")
            if t is not None and v is not None:
                try:
                    time_value_map[t] = float(v)
                except (ValueError, TypeError):
                    logger.warning(f"无法解析数值: value={v} at time={t}")
                    time_value_map[t] = None
            else:
                logger.debug(f"point 缺少 index 或 value: {pt}")
        extract_data[name] = time_value_map

    for item in result.get("other", []):
        name = item.get("name")
        if name not in ["Selling Price", "Buying Price"]:
            continue
        points = item.get("points", [])
        time_value_map = {}
        for pt in points:
            if not isinstance(pt, dict):
                logger.warning(f"跳过非字典类型的 point: {pt}")
                continue
            t = pt.get("index")
            v = pt.get("value")
            if t is not None and v is not None:
                try:
                    time_value_map[t] = float(v)
                except (ValueError, TypeError):
                    logger.warning(f"无法解析数值: value={v} at time={t}")
                    time_value_map[t] = None
            else:
                logger.debug(f"point 缺少 index 或 value: {pt}")
        extract_data[name] = time_value_map

    logger.debug(f"📊 extract_curve 结果: {json.dumps(extract_data, indent=2)}")
    return extract_data


# 处理实际模式的数据
def scheduler_to_15min_actual(scheduler_list, target_date=None):
    """
    将 schedulerList 转换为 96 个 15 分钟点的实际工作模式序列（仅覆盖配置时间段）
    未配置的时间保持 None。
    """
    from datetime import datetime, timedelta
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")

    # 初始化 96 个 None
    actual_modes = [None] * 96

    for sched in scheduler_list:
        if not sched.get("enable", True):
            continue

        start_min = sched["startHour"] * 60 + sched["startMinute"]
        end_min = sched["endHour"] * 60 + sched["endMinute"]
        work_mode = sched["workMode"]

        # 处理 end=(0,0) → 视为 24:00 (1440)
        if end_min == 0:
            end_min = 1440
        if end_min <= start_min:
            continue  # 跳过无效区间

        encoded_mode = encode_work_mode(work_mode)

        # 遍历 96 个时间点
        for i in range(96):
            point_min = i * 15  # 0, 15, 30, ..., 1425 (23:45)
            if start_min <= point_min < end_min:
                actual_modes[i] = encoded_mode

    return actual_modes


# 将 实际发用电的96 个 15 分钟粒度的数据点聚合为 24 个小时粒度的数据
def aggregate_96_to_24(data_96: list) -> list:
    if not data_96 or len(data_96) != 96:
        return [None] * 24
    hourly = []
    for i in range(24):
        chunk = data_96[i * 4:(i + 1) * 4]
        if all(x is not None for x in chunk):
            hourly.append(sum(chunk))
        else:
            hourly.append(None)
    return hourly


# 预测模式是24条数据，需要转换成对应15分钟的
def expand_predicted_mode_to_15min(dispatch_temp_look: dict) -> list:
    """
    输入: dispatchTempLook 字典，如 {"0": "SelfUse", "1": "ForceCharge", ...}
    输出: 长度为96的列表，按规则编码，缺失小时为 None
    """
    if not dispatch_temp_look:
        return [None] * 96

    # 构建24小时模式列表
    hourly_modes = []
    for h in range(24):
        mode_val = dispatch_temp_look.get(str(h)) or dispatch_temp_look.get(h)
        if mode_val is not None:
            hourly_modes.append(encode_work_mode(mode_val))
        else:
            hourly_modes.append(None)

    # 扩展为96点
    points_96 = []
    for mode in hourly_modes:
        points_96.extend([mode] * 4)
    return points_96


# 循环调用shard_id
def fetch_all_scheduler_list(device_id: str):
    """
    循环调用 scheduler 接口，直到获取完整 schedulerList
    返回合并后的完整列表
    """
    all_schedulers = []
    shard_id = None  # 第一次不传 shardID

    while True:
        resp = call_scheduler_mode(device_id, shard_id=shard_id)
        result = resp.get("result", {})
        sched_list = result.get("schedulerList", [])
        all_schedulers.extend(sched_list)

        has_next = result.get("hasNext", False)
        if not has_next:
            break
        # 下一页的 shardID 来自响应
        shard_id = result.get("shardID")
        if shard_id is None:
            break  # 安全兜底

    return all_schedulers


# 通用函数拆分日期范围到所属月份，并合并结果。
def get_months_between(start_date: str, end_date: str):
    """返回 [start_month, ..., end_month] 的列表，每个元素是 (year, month)"""
    start = datetime.fromisoformat(start_date).date()
    end = datetime.fromisoformat(end_date).date()
    months = []
    current = start.replace(day=1)
    while current <= end.replace(day=1):
        months.append((current.year, current.month))
        if current.month == 12:
            current = current.replace(year=current.year + 1, month=1)
        else:
            current = current.replace(month=current.month + 1)
    return months


# 拿到实际发电/用电--实际收益没做，需要加上
def fetch_actual_daily_data_cross_month(plant_id: str, start_date: str, end_date: str):
    """获取 [start_date, end_date] 的实际日数据（支持跨月）"""
    all_data = defaultdict(lambda: {"gen": 0.0, "load": 0.0})
    months = get_months_between(start_date, end_date)

    for year, month in months:
        json_body = {
            "date": {"year": year, "month": month, "day": 1},
            "variables": ["input", "loads", "feedin", "gridConsumption"],
            "custom": False,
            "plantID": plant_id,
            "dimension": "month"
        }
        url = base_url + "/dew/v1/plant/history/report"
        test = signer.debug_signature("POST", url, json_body)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"DEW {test}",
            "User-Agent": "Mozilla/5.0"
        }
        try:
            resp = requests.post(url, headers=headers, json=json_body, verify=False, timeout=10)
            if resp.status_code != 200:
                continue
            data = resp.json().get("result", {}).get("data", [])
        except Exception as e:
            logger.error(f"Fetch actual data failed for {year}-{month}: {e}")
            continue

        solar_points = {}
        load_points = {}
        for item in data:
            if item.get("name") == "Solar":
                solar_points = {pt["index"]: float(pt["value"]) for pt in item.get("points", [])}
            elif item.get("name") == "Load":
                load_points = {pt["index"]: float(pt["value"]) for pt in item.get("points", [])}

        for day_str, gen_val in solar_points.items():
            try:
                day = int(day_str)
                date_key = f"{year}-{month:02d}-{day:02d}"
                if start_date <= date_key <= end_date:
                    all_data[date_key]["gen"] = gen_val
            except:
                continue
        for day_str, load_val in load_points.items():
            try:
                day = int(day_str)
                date_key = f"{year}-{month:02d}-{day:02d}"
                if start_date <= date_key <= end_date:
                    all_data[date_key]["load"] = load_val
            except:
                continue

    return dict(all_data)


# ============================== 新增：7天预测所需表是存在相关函数 ==============================
def ensure_7day_tables_exist():
    """确保7天预测所需表存在"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS forecast_7day_history (
        plant_id TEXT NOT NULL,
        run_date DATE NOT NULL,
        target_date DATE NOT NULL,
        predicted_generation_kwh NUMERIC,
        predicted_consumption_kwh NUMERIC,
        predicted_earning_eur NUMERIC,
        created_at TIMESTAMP DEFAULT NOW(),
        PRIMARY KEY (plant_id, run_date, target_date)
    );
    CREATE TABLE IF NOT EXISTS prediction_metrics_7day (
        plant_id TEXT NOT NULL,
        run_date DATE NOT NULL,
        metric_type TEXT NOT NULL,
        rmse NUMERIC,
        mae NUMERIC,
        nrmse NUMERIC,
        nmae NUMERIC,
        mape NUMERIC,
        r2_score NUMERIC,
        evaluated_at TIMESTAMP DEFAULT NOW(),
        PRIMARY KEY (plant_id, run_date, metric_type)
    );
    """)
    conn.commit()
    cur.close()
    conn.close()


# ===== 保存函数 =====
def save_15min_data(plant_id, target_date, actual_curve, pred_earning, actual_mode_15min, pred_mode_96):
    """
    注意：现在 pred_mode_96 是长度为96的列表（对应00:00–23:45）
    actual_mode_15min 是长度为97的列表，我们只取前96个点
    """
    date_str = f"{target_date['year']}-{target_date['month']:02d}-{target_date['day']:02d}"
    rows = []
    for i in range(96):  # 只处理96个15分钟区间（00:00 到 23:45）
        t = f"{i // 4:02d}:{(i % 4) * 15:02d}"
        minutes = i * 15

        solar = actual_curve.get("Solar Savings", {}).get(t)
        feedin = actual_curve.get("Feed-in-Revenue", {}).get(t)
        sell = actual_curve.get("Selling Price", {}).get(t)
        buy = actual_curve.get("Buying Price", {}).get(t)
        actual_income = (solar or 0) + (feedin or 0) if solar is not None or feedin is not None else None

        pred_val = pred_earning.get(t)
        actual_mode = actual_mode_15min[i]  # 取前96个
        pred_mode = pred_mode_96[i]  # 直接索引

        rows.append((
            plant_id, date_str, t, minutes,
            pred_val, actual_income, solar, feedin, sell, buy,
            actual_mode, pred_mode
        ))

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    execute_values(cur, """
        INSERT INTO income_comparison_table 
        (plant_id, date, "time", time_minutes, predictedearning, actualincome, solarsaving, feedinrevenue, sell, buy, actual_mode, predicted_mode)
        VALUES %s
        ON CONFLICT (plant_id, date, "time") DO UPDATE SET
            predictedearning = EXCLUDED.predictedearning,
            actualincome = EXCLUDED.actualincome,
            solarsaving = EXCLUDED.solarsaving,
            feedinrevenue = EXCLUDED.feedinrevenue,
            sell = EXCLUDED.sell,
            buy = EXCLUDED.buy,
            actual_mode = EXCLUDED.actual_mode,
            predicted_mode = EXCLUDED.predicted_mode;
    """, rows)
    conn.commit()
    cur.close()
    conn.close()


def save_15min_data_without_actual_mode(plant_id, target_date, actual_curve, pred_earning, pred_mode_96):
    """
    保存15分钟数据，但排除actual_mode字段（不更新实际模式）
    用于历史日期，避免用今天的配置覆盖历史配置
    """
    date_str = f"{target_date['year']}-{target_date['month']:02d}-{target_date['day']:02d}"
    rows = []
    for i in range(96):  # 只处理96个15分钟区间（00:00 到 23:45）
        t = f"{i // 4:02d}:{(i % 4) * 15:02d}"
        minutes = i * 15

        solar = actual_curve.get("Solar Savings", {}).get(t)
        feedin = actual_curve.get("Feed-in-Revenue", {}).get(t)
        sell = actual_curve.get("Selling Price", {}).get(t)
        buy = actual_curve.get("Buying Price", {}).get(t)
        actual_income = (solar or 0) + (feedin or 0) if solar is not None or feedin is not None else None

        pred_val = pred_earning.get(t)
        # 不获取实际模式
        pred_mode = pred_mode_96[i]  # 直接索引

        rows.append((
            plant_id, date_str, t, minutes,
            pred_val, actual_income, solar, feedin, sell, buy,
            None, pred_mode  # actual_mode 设为 None，但数据库中有冲突时不更新
        ))

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    execute_values(cur, """
        INSERT INTO income_comparison_table 
        (plant_id, date, "time", time_minutes, predictedearning, actualincome, solarsaving, feedinrevenue, sell, buy, actual_mode, predicted_mode)
        VALUES %s
        ON CONFLICT (plant_id, date, "time") DO UPDATE SET
            predictedearning = EXCLUDED.predictedearning,
            actualincome = EXCLUDED.actualincome,
            solarsaving = EXCLUDED.solarsaving,
            feedinrevenue = EXCLUDED.feedinrevenue,
            sell = EXCLUDED.sell,
            buy = EXCLUDED.buy,
            predicted_mode = EXCLUDED.predicted_mode;
            -- 注意：actual_mode 不在 UPDATE SET 中，保持原值
    """, rows)
    conn.commit()
    cur.close()
    conn.close()


def save_hourly_data(plant_id, target_date, actual_gen, actual_feedin, pred_gen, pred_load):
    date_str = f"{target_date['year']}-{target_date['month']:02d}-{target_date['day']:02d}"
    rows = []
    for hour in range(24):
        ag = actual_gen[hour] if hour < len(actual_gen) else None
        af = actual_feedin[hour] if hour < len(actual_feedin) else None
        pg = pred_gen[hour] if hour < len(pred_gen) else None
        pl = pred_load[hour] if hour < len(pred_load) else None
        ac = ag - af if ag is not None and af is not None else None
        rows.append((plant_id, date_str, hour, ag, af, ac, pg, pl))

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    execute_values(cur, """
        INSERT INTO generation_load_hourly 
        (plant_id, date, hour, actual_generation_kwh, actual_feedin_kwh, actual_consumption_kwh, predicted_generation_kwh, predicted_consumption_kwh)
        VALUES %s
        ON CONFLICT (plant_id, date, hour) DO UPDATE SET
            actual_generation_kwh = EXCLUDED.actual_generation_kwh,
            actual_feedin_kwh = EXCLUDED.actual_feedin_kwh,
            actual_consumption_kwh = EXCLUDED.actual_consumption_kwh,
            predicted_generation_kwh = EXCLUDED.predicted_generation_kwh,
            predicted_consumption_kwh = EXCLUDED.predicted_consumption_kwh;
    """, rows)
    conn.commit()
    cur.close()
    conn.close()


# 保存7天预测
def save_7day_forecast(plant_id: str, run_date_dict: dict, forecast_resp: dict):
    """保存7天日粒度预测"""
    run_date = datetime(run_date_dict["year"], run_date_dict["month"], run_date_dict["day"]).date()
    result = forecast_resp.get("result", {})

    # 合并 data 和 other
    all_items = result.get("data", []) + result.get("other", [])

    production = consumption = earnings = None
    for item in all_items:
        name = item.get("name", "")
        points = item.get("points", [])
        values = []
        for pt in points:
            try:
                values.append(float(pt.get("value", "0")))
            except (ValueError, TypeError):
                values.append(0.0)

        if name == "Production":
            production = values
        elif name == "Consumption":
            consumption = values
        elif name == "Forecasted Earnings":
            earnings = values

    if not (production and consumption and earnings):
        logger.warning(f"[7D Forecast] plant {plant_id} 缺少完整7天预测数据")
        return

    rows = []
    for i in range(7):
        target_date = run_date + timedelta(days=i)
        pg = production[i] if i < len(production) else None
        pc = consumption[i] if i < len(consumption) else None
        pe = earnings[i] if i < len(earnings) else None
        rows.append((plant_id, run_date.isoformat(), target_date.isoformat(), pg, pc, pe))

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    execute_values(cur, """
        INSERT INTO forecast_7day_history 
        (plant_id, run_date, target_date, predicted_generation_kwh, predicted_consumption_kwh, predicted_earning_eur)
        VALUES %s
        ON CONFLICT (plant_id, run_date, target_date) DO UPDATE SET
        predicted_generation_kwh = EXCLUDED.predicted_generation_kwh,
        predicted_consumption_kwh = EXCLUDED.predicted_consumption_kwh,
        predicted_earning_eur = EXCLUDED.predicted_earning_eur;
    """, rows)
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"[7D Forecast] Saved 7-day forecast for run_date={run_date}")


# ==============================预测指标计算与存储==============================
def calculate_prediction_metrics(
        true_values: List[float],
        pred_values: List[float],
        data_type: str = "generation"
) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float], Optional[float], Optional[float]]:
    """
    返回: (rmse, mae, nrmse, nmae, mape, r2)
    """
    # Step 1: 过滤有效配对
    paired = [(t, p) for t, p in zip(true_values, pred_values) if t is not None and p is not None]
    if not paired:
        logger.warning(f"{data_type}: 无有效配对数据点")
        return None, None, None, None, None, None

    y_true = np.array([float(t) for t, _ in paired])
    y_pred = np.array([float(p) for _, p in paired])

    # 基础指标
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    mae = float(np.mean(np.abs(y_true - y_pred)))

    # 判断全零
    true_all_zero = np.allclose(y_true, 0.0)
    pred_all_zero = np.allclose(y_pred, 0.0)

    # 情况：两者都全为0 → 跳过所有指标
    if true_all_zero and pred_all_zero:
        logger.info(f"{data_type}: 实际与预测均全为0，跳过所有指标")
        return None, None, None, None, None, None

    # 情况：实际全0，预测非全0 → 只保留 RMSE/MAE
    if true_all_zero and not pred_all_zero:
        logger.info(f"{data_type}: 实际全0，预测非全0 → 仅返回 RMSE/MAE")
        return rmse, mae, None, None, None, None

    # 正常情况：计算全部指标
    y_max, y_min = np.max(y_true), np.min(y_true)
    if y_max != y_min:
        nrmse = float(rmse / (y_max - y_min))
        nmae = float(mae / (y_max - y_min))
    else:
        nrmse = None
        nmae = None

    # MAPE: only where y_true > 0
    valid_mask = y_true > 0
    if np.sum(valid_mask) > 0:
        mape = float(np.mean(np.abs((y_true[valid_mask] - y_pred[valid_mask]) / y_true[valid_mask])) * 100)
    else:
        mape = None

    # R²
    mean_true = np.mean(y_true)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - mean_true) ** 2)
    r2 = float(1 - (ss_res / ss_tot)) if ss_tot != 0 else None

    return rmse, mae, nrmse, nmae, mape, r2


def fetch_actual_and_predicted_data(plant_id: str, target_date: str, data_type: str) -> Tuple[List[float], List[float]]:
    if data_type == "consumption":
        data_type = "load"  # 兼容别名
    if data_type not in ("generation", "load"):
        raise ValueError("data_type 必须是 'generation' 或 'load'")

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    if data_type == "generation":
        sql = """
        SELECT actual_generation_kwh, predicted_generation_kwh 
        FROM generation_load_hourly 
        WHERE plant_id = %s AND date = %s 
        ORDER BY hour;
        """
    elif data_type == "load":
        sql = """
        SELECT actual_consumption_kwh, predicted_consumption_kwh 
        FROM generation_load_hourly 
        WHERE plant_id = %s AND date = %s 
        ORDER BY hour;
        """
    else:
        raise ValueError("data_type 必须是 'generation' 或 'load'")
    cur.execute(sql, (plant_id, target_date))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    actual_list = [row[0] for row in rows]
    pred_list = [row[1] for row in rows]
    return actual_list, pred_list


# 保存用电发电测试指标函数
def save_prediction_metric(
        plant_id: str,
        target_date: str,
        data_type: str,
        rmse: Optional[float],
        mae: Optional[float],
        nrmse: Optional[float],
        nmae: Optional[float],
        mape: Optional[float],
        r2: Optional[float]
):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    insert_sql = """
    INSERT INTO prediction_metrics 
        (plant_id, target_date, data_type, rmse, mae, nrmse, nmae, mape, r2)
    VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (plant_id, target_date, data_type) DO UPDATE SET
        rmse = EXCLUDED.rmse,
        mae = EXCLUDED.mae,
        nrmse = EXCLUDED.nrmse,
        nmae = EXCLUDED.nmae,
        mape = EXCLUDED.mape,
        r2 = EXCLUDED.r2;
    """
    cur.execute(insert_sql, (plant_id, target_date, data_type, rmse, mae, nrmse, nmae, mape, r2))
    conn.commit()
    cur.close()
    conn.close()


# 计算指标并保存--7天版
def save_prediction_metric_7day(plant_id: str, run_date: str, metric_type: str, rmse, mae, nrmse, nmae, mape, r2):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO prediction_metrics_7day 
        (plant_id, run_date, metric_type, rmse, mae, nrmse, nmae, mape, r2_score)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (plant_id, run_date, metric_type) DO UPDATE SET
            rmse = EXCLUDED.rmse,
            mae = EXCLUDED.mae,
            nrmse = EXCLUDED.nrmse,
            nmae = EXCLUDED.nmae,
            mape = EXCLUDED.mape,
            r2_score = EXCLUDED.r2_score,
            evaluated_at = NOW();
    """, (plant_id, run_date, metric_type, rmse, mae, nrmse, nmae, mape, r2))
    conn.commit()
    cur.close()
    conn.close()


# 评估7天预测
def evaluate_7day_forecast_for_run_date(plant_id: str, run_date: str):
    rd = datetime.fromisoformat(run_date).date()
    end_target = rd + timedelta(days=6)
    today = datetime.today().date()

    if today < end_target:
        return

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT target_date, predicted_generation_kwh, predicted_consumption_kwh
        FROM forecast_7day_history
        WHERE plant_id = %s AND run_date = %s
        ORDER BY target_date
    """, (plant_id, run_date))
    pred_rows = cur.fetchall()
    cur.close()
    conn.close()

    if not pred_rows:
        return

    target_dates = [r[0] for r in pred_rows]
    start_actual = target_dates[0]
    end_actual = target_dates[-1]

    actual_dict = fetch_actual_daily_data_cross_month(plant_id, start_actual, end_actual)

    pred_gen = [r[1] for r in pred_rows]
    pred_load = [r[2] for r in pred_rows]
    actual_gen = [actual_dict.get(d, {}).get("gen", None) for d in target_dates]
    actual_load = [actual_dict.get(d, {}).get("load", None) for d in target_dates]

    def filter_valid(true_list, pred_list):
        pairs = [(t, p) for t, p in zip(true_list, pred_list) if t is not None and p is not None]
        return [t for t, _ in pairs], [p for _, p in pairs]

    true_gen, pred_gen_clean = filter_valid(actual_gen, pred_gen)
    true_load, pred_load_clean = filter_valid(actual_load, pred_load)

    if len(true_gen) > 1:
        rmse, mae, nrmse, nmae, mape, r2 = calculate_prediction_metrics(true_gen, pred_gen_clean, "generation_7d")
        save_prediction_metric_7day(plant_id, run_date, "generation", rmse, mae, nrmse, nmae, mape, r2)

    if len(true_load) > 1:
        rmse, mae, nrmse, nmae, mape, r2 = calculate_prediction_metrics(true_load, pred_load_clean, "load_7d")
        save_prediction_metric_7day(plant_id, run_date, "load", rmse, mae, nrmse, nmae, mape, r2)

    logger.info(f"[7D Eval] Evaluated run_date={run_date} with {len(true_gen)} gen days, {len(true_load)} load days")


# ===== 新增：只保存实际数据（不更新预测字段） =====
def save_actual_hourly_data(plant_id, target_date, actual_gen, actual_feedin):
    """
    只保存实际数据，不更新预测字段
    用于保存历史/昨日的实际发电和用电
    """
    date_str = f"{target_date['year']}-{target_date['month']:02d}-{target_date['day']:02d}"
    rows = []
    for hour in range(24):
        ag = actual_gen[hour] if hour < len(actual_gen) else None
        af = actual_feedin[hour] if hour < len(actual_feedin) else None
        ac = ag - af if ag is not None and af is not None else None
        # 预测字段传入None，但在UPDATE SET中不包含它们
        rows.append((plant_id, date_str, hour, ag, af, ac, None, None))

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    execute_values(cur, """
        INSERT INTO generation_load_hourly 
        (plant_id, date, hour, actual_generation_kwh, actual_feedin_kwh, actual_consumption_kwh, predicted_generation_kwh, predicted_consumption_kwh)
        VALUES %s
        ON CONFLICT (plant_id, date, hour) DO UPDATE SET
            actual_generation_kwh = EXCLUDED.actual_generation_kwh,
            actual_feedin_kwh = EXCLUDED.actual_feedin_kwh,
            actual_consumption_kwh = EXCLUDED.actual_consumption_kwh;
            -- 注意：预测字段不在UPDATE SET中，保持原值
    """, rows)
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"✅ 已保存{date_str}的实际数据（不更新预测字段）")


# ===== 新增：只保存预测数据（不更新实际字段） =====
def save_predicted_hourly_data(plant_id, target_date, pred_gen, pred_load):
    """
    只保存预测数据，不更新实际字段
    用于保存当天的预测发电和用电
    """
    date_str = f"{target_date['year']}-{target_date['month']:02d}-{target_date['day']:02d}"
    rows = []
    for hour in range(24):
        pg = pred_gen[hour] if hour < len(pred_gen) else None
        pl = pred_load[hour] if hour < len(pred_load) else None
        # 实际字段传入None，但在UPDATE SET中不包含它们
        rows.append((plant_id, date_str, hour, None, None, None, pg, pl))

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    execute_values(cur, """
        INSERT INTO generation_load_hourly 
        (plant_id, date, hour, actual_generation_kwh, actual_feedin_kwh, actual_consumption_kwh, predicted_generation_kwh, predicted_consumption_kwh)
        VALUES %s
        ON CONFLICT (plant_id, date, hour) DO UPDATE SET
            predicted_generation_kwh = EXCLUDED.predicted_generation_kwh,
            predicted_consumption_kwh = EXCLUDED.predicted_consumption_kwh;
            -- 注意：实际字段不在UPDATE SET中，保持原值
    """, rows)
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"✅ 已保存{date_str}的预测数据（不更新实际字段）")


# ===== 新增：只保存15分钟预测数据（不更新实际字段） =====
def save_15min_predicted_data(plant_id, target_date, pred_earning, pred_mode_96):
    """
    只保存15分钟预测数据（预测收益、预测模式）
    不更新实际收益和实际模式
    """
    date_str = f"{target_date['year']}-{target_date['month']:02d}-{target_date['day']:02d}"
    rows = []
    for i in range(96):  # 只处理96个15分钟区间
        t = f"{i // 4:02d}:{(i % 4) * 15:02d}"
        minutes = i * 15

        # 只获取预测数据
        pred_val = pred_earning.get(t)
        pred_mode = pred_mode_96[i] if i < len(pred_mode_96) else None

        # 实际字段设为None，但在UPDATE SET中不包含它们
        rows.append((
            plant_id, date_str, t, minutes,
            pred_val, None, None, None, None, None,  # 实际字段设为None
            None, pred_mode  # actual_mode设为None，predicted_mode正常
        ))

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    execute_values(cur, """
        INSERT INTO income_comparison_table 
        (plant_id, date, "time", time_minutes, predictedearning, actualincome, solarsaving, feedinrevenue, sell, buy, actual_mode, predicted_mode)
        VALUES %s
        ON CONFLICT (plant_id, date, "time") DO UPDATE SET
            predictedearning = EXCLUDED.predictedearning,
            predicted_mode = EXCLUDED.predicted_mode;
            -- 注意：实际字段不在UPDATE SET中，保持原值
    """, rows)
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"✅ 已保存{date_str}的15分钟预测数据")


# ===== 新增：只保存15分钟实际数据（不更新预测字段） =====
def save_15min_actual_data(plant_id, target_date, actual_curve):
    """
    只保存15分钟实际数据（实际收益、电价等）
    不更新预测收益和预测模式
    """
    date_str = f"{target_date['year']}-{target_date['month']:02d}-{target_date['day']:02d}"
    rows = []
    for i in range(96):  # 只处理96个15分钟区间
        t = f"{i // 4:02d}:{(i % 4) * 15:02d}"
        minutes = i * 15

        # 只获取实际数据
        solar = actual_curve.get("Solar Savings", {}).get(t)
        feedin = actual_curve.get("Feed-in-Revenue", {}).get(t)
        sell = actual_curve.get("Selling Price", {}).get(t)
        buy = actual_curve.get("Buying Price", {}).get(t)
        actual_income = (solar or 0) + (feedin or 0) if solar is not None or feedin is not None else None

        # 预测字段设为None，但在UPDATE SET中不包含它们
        rows.append((
            plant_id, date_str, t, minutes,
            None, actual_income, solar, feedin, sell, buy,  # 预测earning设为None
            None, None  # 模式字段设为None
        ))

    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    execute_values(cur, """
        INSERT INTO income_comparison_table 
        (plant_id, date, "time", time_minutes, predictedearning, actualincome, solarsaving, feedinrevenue, sell, buy, actual_mode, predicted_mode)
        VALUES %s
        ON CONFLICT (plant_id, date, "time") DO UPDATE SET
            actualincome = EXCLUDED.actualincome,
            solarsaving = EXCLUDED.solarsaving,
            feedinrevenue = EXCLUDED.feedinrevenue,
            sell = EXCLUDED.sell,
            buy = EXCLUDED.buy;
            -- 注意：预测字段和模式字段不在UPDATE SET中，保持原值
    """, rows)
    conn.commit()
    cur.close()
    conn.close()
    logger.info(f"✅ 已保存{date_str}的15分钟实际数据")


# if __name__ == "__main__":
#     signer = APISignature()
#
#     # 1. 登录（不记录到数据库）
#     logger.info("正在登录...")
#     if not login():
#         logger.error("登录失败，退出")
#         exit(1)
#
#     # 确保数据库的表存在
#     ensure_7day_tables_exist()
#
#     # 2. 加载电站列表
#     df_plants = pd.read_csv("D:/code/接口签名/testfoxessplants.csv")
#
#     # conn = psycopg2.connect(**DB_CONFIG)
#     # df_plants = pd.read_sql("SELECT device_id, plant_id, plant_name FROM plants", conn)
#     # conn.close()
#
#     TODAY = get_current_date()
#     YESTERDAY = get_yesterday_date()
#     yesterday_str = f"{YESTERDAY['year']}-{YESTERDAY['month']:02d}-{YESTERDAY['day']:02d}"
#
#     for _, row in df_plants.iterrows():
#         device_id = row["device_id"]
#         plant_id = row["plant_id"]
#         plant_name = row["plant_name"]
#         logger.info(f"开始处理电站: {plant_name} ({plant_id})")
#
#         # ========== 获取昨日实际数据 ==========
#         try:
#             curve_resp = call_earning_curve(plant_id, YESTERDAY)
#             actual_curve = extract_curve(curve_resp)
#         except Exception as e:
#             logger.error(f"获取昨日收益曲线失败: {e}")
#             actual_curve = {}
#
#         try:
#             raw_resp = call_earning_raw(plant_id, YESTERDAY)
#             actual_gen_96, actual_feedin_96 = [], []
#             if raw_resp and raw_resp.get("result"):
#                 for dev_data in raw_resp.get("result", []):
#                     if dev_data.get("devId") == device_id:
#                         energy = dev_data["raw"]["energy"]
#                         actual_gen_96 = energy.get("generation", [])
#                         actual_feedin_96 = energy.get("feedin", [])
#                         break
#         except Exception as e:
#             logger.error(f"获取昨日原始数据失败: {e}")
#             actual_gen_96, actual_feedin_96 = [], []
#
#         # 关键修改1：昨日实际模式不应该获取，因为API只能获取当天配置
#         # 保留数据库中已有的昨日实际模式，不做更新
#
#         actual_gen_24 = aggregate_96_to_24(actual_gen_96)
#         actual_feedin_24 = aggregate_96_to_24(actual_feedin_96)
#
#         # ========== 获取今日预测数据 ==========
#         try:
#             today_curve_resp = call_earning_curve(plant_id, TODAY)
#             pred_earning = extract_curve(today_curve_resp).get("Predicted Earning", {})
#         except Exception as e:
#             logger.error(f"获取今日收益曲线失败: {e}")
#             pred_earning = {}
#
#         try:
#             forecast_resp = call_forecast_curve(plant_id)
#             pred_gen_24 = [None] * 24
#             pred_load_24 = [None] * 24
#             pred_mode_24_raw = {}
#             if forecast_resp:
#                 res = forecast_resp.get("result", {})
#                 try:
#                     save_7day_forecast(plant_id, TODAY, forecast_resp)
#                 except Exception as e:
#                     logger.error(f"[7D Save Error] {e}", exc_info=True)
#
#                 gen_dict = res.get("generationTempLook", {})
#                 load_dict = res.get("loadTempLook", {})
#                 dispatch_dict = res.get("dispatchTempLook", {})
#                 pred_gen_24 = (gen_dict.get(device_id, [])[:24] + [None] * 24)[:24]
#                 pred_load_24 = (load_dict.get(device_id, [])[:24] + [None] * 24)[:24]
#                 pred_mode_24_raw = dispatch_dict.get(device_id, {})
#         except Exception as e:
#             logger.error(f"获取预测曲线失败: {e}")
#             pred_gen_24 = [None] * 24
#             pred_load_24 = [None] * 24
#             pred_mode_24_raw = {}
#
#         pred_mode_96 = expand_predicted_mode_to_15min(pred_mode_24_raw)
#
#         # ========== 获取今日实际模式（只能获取今天的） ==========
#         today_actual_mode_96 = [None] * 96
#         try:
#             # 只有今天可以获取实际模式
#             sched_list = fetch_all_scheduler_list(device_id)
#             today_actual_mode_96 = scheduler_to_15min_actual(sched_list)[:96]
#             logger.info(f"获取到今日实际模式，共 {sum(1 for m in today_actual_mode_96 if m is not None)} 个非空点")
#         except Exception as e:
#             logger.error(f"获取今日调度器列表失败: {e}")
#             today_actual_mode_96 = [None] * 96
#
#         # ========== 保存数据 ==========
#         try:
#             # 关键修改2：昨日实际模式不更新，只更新其他字段
#             # 使用 ON CONFLICT 的 UPDATE SET 中排除 actual_mode 字段
#             save_15min_data_without_actual_mode(plant_id, YESTERDAY, actual_curve, {}, [None] * 96)
#
#             save_hourly_data(plant_id, YESTERDAY, actual_gen_24, actual_feedin_24, [None] * 24, [None] * 24)
#
#             # 今日数据：实际模式用 today_actual_mode_96，预测模式正常
#             save_15min_data(plant_id, TODAY, {}, pred_earning, today_actual_mode_96, pred_mode_96)
#             save_hourly_data(plant_id, TODAY, [None] * 24, [None] * 24, pred_gen_24, pred_load_24)
#         except Exception as e:
#             logger.error(f"保存数据失败: {e}")
#
#         # ========== 计算并保存预测指标 ==========
#         # 评估昨日预测
#         try:
#             actual_gen, pred_gen = fetch_actual_and_predicted_data(plant_id, yesterday_str, "generation")
#             rmse, mae, nrmse, nmae, mape, r2 = calculate_prediction_metrics(actual_gen, pred_gen, "generation")
#             if rmse is not None:
#                 save_prediction_metric(plant_id, yesterday_str, "generation", rmse, mae, nrmse, nmae, mape, r2)
#
#             actual_load, pred_load = fetch_actual_and_predicted_data(plant_id, yesterday_str, "consumption")
#             rmse, mae, nrmse, nmae, mape, r2 = calculate_prediction_metrics(actual_load, pred_load, "consumption")
#             if rmse is not None:
#                 save_prediction_metric(plant_id, yesterday_str, "consumption", rmse, mae, nrmse, nmae, mape, r2)
#
#         except Exception as e:
#             logger.error(f"评估预测指标失败 ({plant_id}): {e}", exc_info=True)
#
#     # 评估历史7天预测（可选：遍历最近N天）
#     try:
#         today_str = f"{TODAY['year']}-{TODAY['month']:02d}-{TODAY['day']:02d}"
#         eval_date = datetime.strptime(today_str, "%Y-%m-%d") - timedelta(days=7)
#         while eval_date <= datetime.today():
#             run_date_str = eval_date.strftime("%Y-%m-%d")
#             for _, row in df_plants.iterrows():
#                 evaluate_7day_forecast_for_run_date(row["plant_id"], run_date_str)
#             eval_date += timedelta(days=1)
#     except Exception as e:
#         logger.error(f"7天预测评估失败: {e}", exc_info=True)
#
#     logger.info("✅ 所有电站同步与评估完成")
if __name__ == "__main__":
    signer = APISignature()

    # 1. 登录
    logger.info("正在登录...")
    if not login():
        logger.error("登录失败，退出")
        exit(1)

    # 确保数据库的表存在
    ensure_7day_tables_exist()

    # 2. 加载电站列表
    df_plants = pd.read_csv("D:/code/接口签名/testfoxessplants.csv")

    TODAY = get_current_date()
    YESTERDAY = get_yesterday_date()
    yesterday_str = f"{YESTERDAY['year']}-{YESTERDAY['month']:02d}-{YESTERDAY['day']:02d}"

    for _, row in df_plants.iterrows():
        device_id = row["device_id"]
        plant_id = row["plant_id"]
        plant_name = row["plant_name"]
        logger.info(f"开始处理电站: {plant_name} ({plant_id})")

        # ========== A. 获取并保存昨日实际数据 ==========
        logger.info(f"获取{plant_id}的昨日实际数据...")
        try:
            # 获取昨日实际收益曲线
            curve_resp = call_earning_curve(plant_id, YESTERDAY)
            actual_curve = extract_curve(curve_resp)
            # 只保存15分钟实际数据（不更新预测字段）
            save_15min_actual_data(plant_id, YESTERDAY, actual_curve)
        except Exception as e:
            logger.error(f"获取/保存昨日收益曲线失败: {e}")
            actual_curve = {}

        try:
            # 获取昨日实际发电/用电
            raw_resp = call_earning_raw(plant_id, YESTERDAY)
            actual_gen_96, actual_feedin_96 = [], []
            if raw_resp and raw_resp.get("result"):
                for dev_data in raw_resp.get("result", []):
                    if dev_data.get("devId") == device_id:
                        energy = dev_data["raw"]["energy"]
                        actual_gen_96 = energy.get("generation", [])
                        actual_feedin_96 = energy.get("feedin", [])
                        break

            actual_gen_24 = aggregate_96_to_24(actual_gen_96)
            actual_feedin_24 = aggregate_96_to_24(actual_feedin_96)

            # 只保存小时实际数据（不更新预测字段）
            save_actual_hourly_data(plant_id, YESTERDAY, actual_gen_24, actual_feedin_24)
        except Exception as e:
            logger.error(f"获取/保存昨日实际发电用电失败: {e}")

        # ========== B. 获取并保存今日预测数据 ==========
        logger.info(f"获取{plant_id}的今日预测数据...")
        try:
            # 获取今日预测收益
            today_curve_resp = call_earning_curve(plant_id, TODAY)
            pred_earning = extract_curve(today_curve_resp).get("Predicted Earning", {})
        except Exception as e:
            logger.error(f"获取今日收益曲线失败: {e}")
            pred_earning = {}

        try:
            # 获取今日预测发电/用电/模式
            forecast_resp = call_forecast_curve(plant_id)
            pred_gen_24 = [None] * 24
            pred_load_24 = [None] * 24
            pred_mode_24_raw = {}

            if forecast_resp:
                res = forecast_resp.get("result", {})

                # 保存7天预测
                try:
                    save_7day_forecast(plant_id, TODAY, forecast_resp)
                except Exception as e:
                    logger.error(f"[7D Save Error] {e}", exc_info=True)

                # 提取预测数据
                gen_dict = res.get("generationTempLook", {})
                load_dict = res.get("loadTempLook", {})
                dispatch_dict = res.get("dispatchTempLook", {})
                pred_gen_24 = (gen_dict.get(device_id, [])[:24] + [None] * 24)[:24]
                pred_load_24 = (load_dict.get(device_id, [])[:24] + [None] * 24)[:24]
                pred_mode_24_raw = dispatch_dict.get(device_id, {})

            pred_mode_96 = expand_predicted_mode_to_15min(pred_mode_24_raw)

            # 只保存小时预测数据（不更新实际字段）
            save_predicted_hourly_data(plant_id, TODAY, pred_gen_24, pred_load_24)
            # 只保存15分钟预测数据（不更新实际字段）
            save_15min_predicted_data(plant_id, TODAY, pred_earning, pred_mode_96)

        except Exception as e:
            logger.error(f"获取/保存今日预测数据失败: {e}")

        # ========== C. 计算并保存预测指标 ==========
        # 评估昨日预测（对比昨天的预测 vs 昨天的实际）
        logger.info(f"计算{plant_id}的预测指标...")
        try:
            actual_gen, pred_gen = fetch_actual_and_predicted_data(plant_id, yesterday_str, "generation")
            rmse, mae, nrmse, nmae, mape, r2 = calculate_prediction_metrics(actual_gen, pred_gen, "generation")
            if rmse is not None:
                save_prediction_metric(plant_id, yesterday_str, "generation", rmse, mae, nrmse, nmae, mape, r2)

            actual_load, pred_load = fetch_actual_and_predicted_data(plant_id, yesterday_str, "consumption")
            rmse, mae, nrmse, nmae, mape, r2 = calculate_prediction_metrics(actual_load, pred_load, "consumption")
            if rmse is not None:
                save_prediction_metric(plant_id, yesterday_str, "consumption", rmse, mae, nrmse, nmae, mape, r2)

        except Exception as e:
            logger.error(f"评估预测指标失败 ({plant_id}): {e}", exc_info=True)

    # ========== D. 评估7天预测 ==========
    logger.info("评估历史7天预测...")
    try:
        today_str = f"{TODAY['year']}-{TODAY['month']:02d}-{TODAY['day']:02d}"
        # 评估最近14天（确保覆盖7天预测周期）
        eval_date = datetime.strptime(today_str, "%Y-%m-%d") - timedelta(days=14)
        while eval_date <= datetime.today():
            run_date_str = eval_date.strftime("%Y-%m-%d")
            for _, row in df_plants.iterrows():
                evaluate_7day_forecast_for_run_date(row["plant_id"], run_date_str)
            eval_date += timedelta(days=1)
    except Exception as e:
        logger.error(f"7天预测评估失败: {e}", exc_info=True)

    logger.info("✅ 所有电站同步与评估完成")