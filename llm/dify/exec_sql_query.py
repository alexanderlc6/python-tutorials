import re
import json

# Dify Chatflow: SQL生成逻辑
def main(input_string: str) -> dict:
    # 使用正则表达式查找并提取被 ```json 和 ``` 包裹的内容
    pattern_match = re.search(r'```json\s*([\s\S]*?)\s*```', input_string)

    if not pattern_match:
        raise ValueError('No valid JSON found in the input string.')

    # 提取匹配到的JSON字符串，并去除前后空白
    json_content = pattern_match.group(1).strip()
    # 尝试解析JSON字符串
    try:
        # 将提取的JSON字符串解析为Python字典
        parsed_json = json.loads(json_content)
    except json.JSONDecodeError as err:
        raise ValueError(f'Resolve JSON failed: {err}')

    return {
        'result': parsed_json
    }

# Dify Chatflow:迭代内部的代码执行
def main(args: dict) -> dict:
    # 提取输入字典的字段
    title = args.get('title', '')
    sql = args.get('sql', '')
    return {
        'title': title,
        'sql': sql
    }

# LLM结果生成ECharts格式数据
import re
import json

def main(args: str) -> dict:
    default_output = {
        'results': '',
        'ECharts': '0',
        'chartType':'',
        'chartTitle': '',
        'chartData': '',
        'chartXAxis':''
    }

    try:
        # 使用正则表达式提取被 ```json 和 ``` 包裹的内容
        match = re.search(r'```json\s*([\s\S]*?)\s*```', args)
        if not match:
            raise ValueError('No valid JSON found in the input string.')

        # 提取 JSON 字符串
        json_str = match.group(1).strip()

        # 将 JSON 字符串解析为 Python 字典
        result_dict = json.loads(json_str)
    except Exception as e:
        # 如果解析失败，打印错误信息并返回默认输出
        print(f'Error parsing JSON: {e}')
        return default_output

    # 检查是否包含 ECharts 字段
    if 'ECharts' not in result_dict:
        result_dict['ECharts'] = 0
    # 根据 ECharts 的值动态检查图表相关字段
    if result_dict['ECharts'] == '1':
        required_chat_fields = ['chartType', 'chartTitle', 'chartData', 'chartXAxis']
        for field in required_chat_fields:
            if field not in result_dict:
                # 自动补全缺失字段为空字符串
                result_dict[field] = ''

    # 构造返回值
    return {
        'results': str(result_dict.get('results', '')),
        'ECharts': str(result_dict.get('ECharts', '0')),
        'chartType': str(result_dict.get('chartType', '')),
        'chartTitle': str(result_dict.get('chartTitle', '')),
        'chartData': str(result_dict.get('chartData', '')),
        'chartXAxis': str(result_dict.get('chartXAxis', ''))
    }

