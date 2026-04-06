from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

VALID_TOKEN = 'mycat'

CITY_CODES = {
    "北京": "101010100",
    "上海": "101020100",
    "广州": "101280101",
    "深圳": "101280601",
    "杭州": "101210101",
    "成都": "101270101",
    "武汉": "101200101",
    "西安": "101110101",
    "南京": "101190101",
    "重庆": "101040100",
    "天津": "101030100",
    "苏州": "101190401",
    "郑州": "101180101",
    "长沙": "101250101",
    "青岛": "101120201",
    "大连": "101070201",
    "宁波": "101210401",
    "厦门": "101230201",
    "福州": "101230101",
    "济南": "101120101",
    "合肥": "101220101",
    "南昌": "101240101",
    "昆明": "101290101",
    "南宁": "101300101",
    "贵阳": "101260101",
    "哈尔滨": "101050101",
    "长春": "101060101",
    "沈阳": "101070101",
    "石家庄": "101090101",
    "太原": "101100101",
    "呼和浩特": "101080101",
    "乌鲁木齐": "101130101",
    "拉萨": "101140101",
    "兰州": "101110501",
    "西宁": "101150101",
    "银川": "101170101",
    "海口": "101310101",
    "三亚": "101310201"
}

class WeatherRequest(BaseModel):
    location: str

@app.post('/weather')
def get_current_weather(request: Request, body: WeatherRequest):
    """
    Weather query API
    - Need Authorization header validation
    - Return weather info with NLP format
    """
    # Validate identity
    auth_header = request.headers.get('Authorization')
    if auth_header != f'Bearer {VALID_TOKEN}':
        raise HTTPException(status_code=403, detail='Invalid authorization header')
    location = body.location

    # Find city code
    city_code = CITY_CODES.get(location)
    if not city_code:
        return {
            'status': 'error',
            'message': f'Please provide {location} corresponding city code to query, currently supported cities:{','.join(CITY_CODES.keys())}'
        }

    # Invoke weather API
    url = f'http://t.weather.itboy.net/api/weather/city/{city_code}'
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        return {'status': 'error', 'message': f'Request weather API failed: {str(e)}'}

    # Resolve weather info
    try:
        forcast = data['data']['forecast'][0]
        weather_type = forcast['type']
        high = forcast['high']
        low = forcast['low']
        temperature = f'{high} / {low}'

        # Return NLP format
        return f'Today the weather of {location} is {weather_type}, temperature is {temperature}. '
    except(KeyError, IndexError) as e:
        return {'status': 'error', 'message': f'Resolve weather info failed: {str(e)}'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8001)