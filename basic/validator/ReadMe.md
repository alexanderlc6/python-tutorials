## 脚本功能说明
### 核心特性
#### 双业务场景支持
* 设备主数据（Device Master Data）：验证 nominalPower, installationDate 等字段
* 测量数据（Measurement Data）：验证 obisCode, readOutTs, data 数组等字段

#### 严格报文字段验证
* ✅ 必填字段检查（required）
* ✅ 数据类型检查（string/integer/object/array）
* ✅ 嵌套对象递归验证（如 address 对象内的字段）
* ✅ 数组元素结构验证（如 data 数组中的每个对象）

#### 多消息源支持
* 自动检查 mqtt, rabbitmq, webhook, kafka 四个数据源
* 自动识别消息类型（通过关键字段判断）
#### 详细的错误输出
* 字段路径追踪（如 address.zipCode）
* 具体的错误类型（必填缺失、类型错误等）
* 支持未知字段检测（可选）

## 使用方式
```python
# 正常运行测试（连接Go服务）
python test_message_format.py

# 指定不同的接口地址
python test_message_format.py --url http://localhost:8089/triggerValidateMsgFormat

# 运行自测（验证验证器逻辑本身）
python test_message_format.py --self-test
```

## 预期接口返回格式
脚本期望Go接口返回如下JSON结构：
```json
{
  "mqtt": [
    {"messageId": "...", "brand": "...", ...},
    {"messageId": "...", "obisCode": "...", ...}
  ],
  "rabbitmq": [...],
  "webhook": [...],
  "kafka": [...]
}
```

如果接口返回的是其他格式（如直接返回布尔值），脚本会相应调整解析逻辑。您可以根据实际接口返回格式调整 trigger_validation 方法的解析部分。

### 输出示例
```text
2024-03-02 10:30:00 - INFO - 消息格式验证测试开始
2024-03-02 10:30:00 - INFO - 正在触发验证接口: http://10.2.92.46:8298/triggerValidateMsgFormat
2024-03-02 10:30:01 - INFO - --- 检查 [RABBITMQ] 消息源 (2 条消息) ---
2024-03-02 10:30:01 - INFO - ✅ [RABBITMQ-1] 设备主数据 验证通过
2024-03-02 10:30:01 - ERROR - ❌ [RABBITMQ-2] 测量数据 验证失败:
2024-03-02 10:30:01 - ERROR -    - [必填字段缺失] data[0].value: 该字段为必填项
2024-03-02 10:30:01 - INFO - 成功率: 75.00%
```