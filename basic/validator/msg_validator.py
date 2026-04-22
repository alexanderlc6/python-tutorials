"""
消息格式验证测试脚本
用于验证Go程序从各消息队列消费的数据是否符合预期JSON结构
Author: Alex Lu
Date: 2026-03-02 18:22
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """验证错误异常"""
    pass


@dataclass
class FieldRule:
    """字段验证规则"""
    name: str
    required: bool
    field_type: type
    nested_rules: Optional[List['FieldRule']] = None
    # 对于数值类型的范围限制
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    # 对于字符串的正则或格式验证
    format_pattern: Optional[str] = None


class MessageValidator:
    """消息格式验证器"""

    def __init__(self):
        self.errors: List[str] = []

    def validate(self, data: Dict, rules: List[FieldRule], path: str = "") -> bool:
        """
        递归验证数据是否符合规则

        Args:
            data: 待验证的数据
            rules: 字段规则列表
            path: 当前字段路径（用于错误定位）

        Returns:
            bool: 验证是否通过
        """
        is_valid = True

        for rule in rules:
            current_path = f"{path}.{rule.name}" if path else rule.name
            value = data.get(rule.name)

            # 检查必填字段
            if rule.required and value is None:
                self.errors.append(f"[必填字段缺失] {current_path}: 该字段为必填项")
                is_valid = False
                continue

            # 如果字段不存在且非必填，跳过
            if value is None and not rule.required:
                continue

            # 类型验证
            if value is not None:
                if rule.field_type == dict and not isinstance(value, dict):
                    self.errors.append(f"[类型错误] {current_path}: 期望类型为 object，实际为 {type(value).__name__}")
                    is_valid = False
                elif rule.field_type == list and not isinstance(value, list):
                    self.errors.append(f"[类型错误] {current_path}: 期望类型为 array，实际为 {type(value).__name__}")
                    is_valid = False
                elif rule.field_type in (str, int, float) and not isinstance(value, rule.field_type):
                    self.errors.append(
                        f"[类型错误] {current_path}: 期望类型为 {rule.field_type.__name__}，实际为 {type(value).__name__}")
                    is_valid = False

            # 嵌套对象验证
            if rule.field_type == dict and isinstance(value, dict) and rule.nested_rules:
                nested_valid = self.validate(value, rule.nested_rules, current_path)
                is_valid = is_valid and nested_valid

            # 数组元素验证
            if rule.field_type == list and isinstance(value, list) and rule.nested_rules:
                for idx, item in enumerate(value):
                    if isinstance(item, dict):
                        item_path = f"{current_path}[{idx}]"
                        item_valid = self.validate(item, rule.nested_rules, item_path)
                        is_valid = is_valid and item_valid

        # 检查是否有额外未定义的字段（可选，根据需求开启）
        # rule_names = {r.name for r in rules}
        # for key in data.keys():
        #     if key not in rule_names:
        #         self.errors.append(f"[未知字段] {path}.{key}: 未在规范中定义的字段")

        return is_valid

    def get_errors(self) -> List[str]:
        """获取所有验证错误"""
        return self.errors

    def clear_errors(self):
        """清空错误列表"""
        self.errors = []


class TestConfig:
    """测试配置"""
    # Go服务接口地址
    TRIGGER_URL = "http://10.2.92.46:8298/triggerValidateMsgFormat"

    # 超时设置（秒）
    TIMEOUT = 30

    # 重试次数
    MAX_RETRIES = 3


class MessageTemplate:
    """消息模板定义 - 基于附件txt中的规范"""

    # 设备相关数据（Master Data）规则
    DEVICE_MASTER_DATA_RULES = [
        FieldRule("messageId", True, str),  # UUID v4
        FieldRule("serialNumber", True, str),
        FieldRule("address", False, dict, nested_rules=[
            FieldRule("country", False, str),  # 默认HU
            FieldRule("zipCode", True, str),  # 必填
            FieldRule("city", True, str),  # 必填
            FieldRule("street", True, str),  # 必填
            FieldRule("streetType", False, str),
            FieldRule("streetCode", False, str),
            FieldRule("streetCodeSupplement", False, str),
            FieldRule("building", False, str),
            FieldRule("stairway", False, str),
            FieldRule("door", False, str),
            FieldRule("floor", False, str),
            FieldRule("latitude", False, str),
            FieldRule("longitude", False, str),
            FieldRule("landRegistryNumber", False, str),
        ]),
        FieldRule("brand", True, str),  # 必须与config_req.conf中的CN字段一致
        FieldRule("model", True, str),
        FieldRule("nominalPower", True, int),  # 单位：W
        FieldRule("acVoltageMin", True, int),  # 单位：V
        FieldRule("acVoltageMax", True, int),  # 单位：V
        FieldRule("installationDate", True, str),  # YYYY-MM-DD
        FieldRule("removalDate", False, str),  # YYYY-MM-DD，可选
    ]

    # 测量数据（Measurement Data）规则
    MEASUREMENT_DATA_RULES = [
        FieldRule("messageId", True, str),  # UUID v4
        FieldRule("serialNumber", True, str),
        FieldRule("readOutTs", True, str),  # ISO 8601格式
        FieldRule("obisCode", True, str),
        FieldRule("data", True, list, nested_rules=[
            FieldRule("timestamp", True, str),  # ISO 8601格式
            FieldRule("value", True, str),  # 数值字符串，4位小数截断
        ]),
    ]

    # 消息类型映射
    MESSAGE_TYPES = {
        "device_master": {
            "name": "设备主数据",
            "rules": DEVICE_MASTER_DATA_RULES,
            "exchange_pattern": "<BRAND>.master-data",
            "routing_key": "<BRAND>",
            "queues": ["mqtt", "rabbitmq", "webhook", "kafka"]  # 可能的数据源
        },
        "measurement": {
            "name": "测量数据",
            "rules": MEASUREMENT_DATA_RULES,
            "exchange_pattern": "<BRAND>.measurement-data",
            "routing_key": "<BRAND>",
            "queues": ["mqtt", "rabbitmq", "webhook", "kafka"]
        }
    }


class MessageFormatTester:
    """消息格式测试器"""

    def __init__(self):
        self.validator = MessageValidator()
        self.session = requests.Session()
        self.session.timeout = TestConfig.TIMEOUT

    def trigger_validation(self) -> Dict[str, Any]:
        """
        触发Go接口进行验证

        Returns:
            dict: 接口返回的数据，包含从各队列消费的消息
        """
        try:
            logger.info(f"正在触发验证接口: {TestConfig.TRIGGER_URL}")
            response = self.session.get(TestConfig.TRIGGER_URL)
            response.raise_for_status()

            result = response.json()
            logger.info(f"接口响应状态: {response.status_code}")
            return result

        except requests.exceptions.ConnectionError as e:
            logger.error(f"连接失败: 无法连接到 {TestConfig.TRIGGER_URL} - {str(e)}")
            raise
        except requests.exceptions.Timeout:
            logger.error(f"请求超时: 接口在 {TestConfig.TIMEOUT} 秒内未响应")
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"响应解析失败: 返回的不是有效JSON - {str(e)}")
            raise

    def validate_single_message(self, message: Dict, msg_type: str, source: str) -> bool:
        """
        验证单条消息

        Args:
            message: 消息内容
            msg_type: 消息类型（device_master 或 measurement）
            source: 消息来源（mqtt/rabbitmq/webhook/kafka）

        Returns:
            bool: 验证是否通过
        """
        self.validator.clear_errors()

        type_info = MessageTemplate.MESSAGE_TYPES.get(msg_type)
        if not type_info:
            logger.error(f"未知的消息类型: {msg_type}")
            return False

        logger.info(f"验证 [{type_info['name']}] 来自 [{source.upper()}] 的消息...")

        is_valid = self.validator.validate(message, type_info["rules"])

        if is_valid:
            logger.info(f"✅ [{source.upper()}] {type_info['name']} 验证通过")
        else:
            logger.error(f"❌ [{source.upper()}] {type_info['name']} 验证失败:")
            for error in self.validator.get_errors():
                logger.error(f"   - {error}")

        return is_valid

    def detect_message_type(self, message: Dict) -> Optional[str]:
        """
        自动检测消息类型

        Args:
            message: 消息内容

        Returns:
            str: 消息类型标识，或None（无法识别）
        """
        # 通过关键字段判断消息类型
        if "nominalPower" in message or "installationDate" in message:
            return "device_master"
        elif "obisCode" in message or "readOutTs" in message:
            return "measurement"
        elif "data" in message and isinstance(message.get("data"), list):
            # 可能是测量数据，但缺少关键字段
            if message.get("data") and "timestamp" in message["data"][0]:
                return "measurement"

        return None

    def run_test(self):
        """运行完整测试流程"""
        logger.info("=" * 60)
        logger.info("消息格式验证测试开始")
        logger.info(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("=" * 60)

        try:
            # 1. 触发Go接口获取数据
            result = self.trigger_validation()

            # 2. 解析返回结果
            if not isinstance(result, dict):
                logger.error("接口返回格式错误: 期望JSON对象")
                return False

            # 3. 检查是否有消费到的消息
            messages_found = False
            total_checks = 0
            passed_checks = 0

            # 遍历各消息源（mqtt, rabbitmq, webhook, kafka）
            for source in ["mqtt", "rabbitmq", "webhook", "kafka"]:
                source_data = result.get(source)

                if not source_data:
                    logger.warning(f"[{source.upper()}] 未返回数据或为空")
                    continue

                messages_found = True

                # 确保是列表格式
                if not isinstance(source_data, list):
                    source_data = [source_data]

                logger.info(f"\n--- 检查 [{source.upper()}] 消息源 ({len(source_data)} 条消息) ---")

                for idx, message in enumerate(source_data):
                    total_checks += 1

                    # 自动检测消息类型
                    msg_type = self.detect_message_type(message)

                    if not msg_type:
                        logger.warning(f"  消息 #{idx + 1}: 无法自动识别消息类型，尝试两种规则验证...")
                        # 尝试两种验证，只要有一种通过即可
                        device_valid = self.validate_single_message(message, "device_master", f"{source}-{idx + 1}")
                        self.validator.clear_errors()
                        measure_valid = self.validate_single_message(message, "measurement", f"{source}-{idx + 1}")

                        if device_valid or measure_valid:
                            passed_checks += 1
                        else:
                            logger.error(f"  消息 #{idx + 1}: 不符合任何已知消息格式")
                    else:
                        if self.validate_single_message(message, msg_type, f"{source}-{idx + 1}"):
                            passed_checks += 1

            # 4. 输出测试总结
            logger.info("\n" + "=" * 60)
            logger.info("测试总结")
            logger.info("=" * 60)

            if not messages_found:
                logger.warning("⚠️  未从任何消息源获取到数据")
                return False

            logger.info(f"总验证次数: {total_checks}")
            logger.info(f"通过次数: {passed_checks}")
            logger.info(f"失败次数: {total_checks - passed_checks}")
            logger.info(f"成功率: {passed_checks / total_checks * 100:.2f}%" if total_checks > 0 else "N/A")

            if passed_checks == total_checks:
                logger.info("✅ 所有消息格式验证通过！")
                return True
            else:
                logger.error("❌ 部分消息格式验证失败，请检查上述错误详情")
                return False

        except Exception as e:
            logger.error(f"测试执行异常: {str(e)}")
            import traceback
            logger.debug(traceback.format_exc())
            return False


def generate_sample_messages():
    """
    生成示例消息（用于测试验证逻辑本身）
    """
    # 有效的设备主数据示例
    valid_device = {
        "messageId": "67231151-ea92-4efe-a0a9-e7604669dc09",
        "serialNumber": "13548965",
        "address": {
            "country": "HU",
            "zipCode": "8956",
            "city": "ExampleCity",
            "street": "Example",
            "streetType": "utca",
            "latitude": "46.530936",
            "longitude": "18.814042"
        },
        "brand": "LANDIS",
        "model": "E550",
        "nominalPower": 5000,
        "acVoltageMin": 180,
        "acVoltageMax": 270,
        "installationDate": "2024-10-13"
    }

    # 无效的示例（缺少必填字段）
    invalid_device = {
        "messageId": "67231151-ea92-4efe-a0a9-e7604669dc09",
        "serialNumber": "13548965",
        "brand": "LANDIS",
        # 缺少 model, nominalPower 等必填字段
    }

    # 有效的测量数据示例
    valid_measurement = {
        "messageId": "67231151-ea92-4efe-a0a9-e7604669dc09",
        "serialNumber": "21231e32132eqw21312312",
        "readOutTs": "2024-11-18T15:50:32Z",
        "obisCode": "9.7.0",
        "data": [
            {
                "timestamp": "2024-11-18T15:20:44Z",
                "value": "150"
            },
            {
                "timestamp": "2024-11-18T15:25:14Z",
                "value": "154"
            }
        ]
    }

    return {
        "valid_device": valid_device,
        "invalid_device": invalid_device,
        "valid_measurement": valid_measurement
    }


def run_self_test():
    """运行自测，验证验证器逻辑正确"""
    logger.info("\n" + "=" * 60)
    logger.info("运行验证器自测...")
    logger.info("=" * 60)

    samples = generate_sample_messages()
    tester = MessageFormatTester()
    validator = MessageValidator()

    # 测试有效设备数据
    logger.info("\n测试1: 有效的设备主数据")
    validator.clear_errors()
    is_valid = validator.validate(samples["valid_device"], MessageTemplate.DEVICE_MASTER_DATA_RULES)
    assert is_valid == True, "有效数据应该验证通过"
    assert len(validator.get_errors()) == 0, "有效数据不应该有错误"
    logger.info("✅ 通过")

    # 测试无效设备数据
    logger.info("\n测试2: 缺少必填字段的设备数据")
    validator.clear_errors()
    is_valid = validator.validate(samples["invalid_device"], MessageTemplate.DEVICE_MASTER_DATA_RULES)
    assert is_valid == False, "无效数据应该验证失败"
    errors = validator.get_errors()
    assert len(errors) > 0, "应该有错误信息"
    logger.info(f"✅ 通过，捕获到 {len(errors)} 个错误")
    for err in errors:
        logger.info(f"   - {err}")

    # 测试有效测量数据
    logger.info("\n测试3: 有效的测量数据")
    validator.clear_errors()
    is_valid = validator.validate(samples["valid_measurement"], MessageTemplate.MEASUREMENT_DATA_RULES)
    assert is_valid == True, "有效测量数据应该验证通过"
    logger.info("✅ 通过")

    logger.info("\n✅ 所有自测通过，验证器工作正常")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="消息格式验证测试工具")
    parser.add_argument("--self-test", action="store_true", help="运行自测模式，验证验证器逻辑")
    parser.add_argument("--url", type=str, default=TestConfig.TRIGGER_URL, help="Go服务接口地址")

    args = parser.parse_args()

    # 更新配置
    if args.url:
        TestConfig.TRIGGER_URL = args.url

    if args.self_test:
        run_self_test()
    else:
        tester = MessageFormatTester()
        success = tester.run_test()
        sys.exit(0 if success else 1)