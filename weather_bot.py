import os
import asyncio
import json
from datetime import datetime
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取心知天气API密钥
API_KEY = os.getenv("SENIVERSE_API_KEY")
if not API_KEY:
    print("错误: 请在.env文件中设置有效的SENIVERSE_API_KEY")
    exit(1)

# 基础URL
BASE_URL = "https://api.seniverse.com/v3"

# 获取当前天气
async def get_current_weather(city, lang="zh-Hans", unit="c"):
    """
    获取指定城市的当前天气
    
    参数:
        city (str): 城市名称
        lang (str): 返回结果的语言，默认为简体中文
        unit (str): 温度单位，c为摄氏度，f为华氏度
        
    返回:
        dict: 包含天气信息的字典
    """
    url = f"{BASE_URL}/weather/now.json"
    params = {
        "key": API_KEY,
        "location": city,
        "language": lang,
        "unit": unit
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # 心知天气API返回的数据结构
        result_data = data["results"][0]
        now = result_data["now"]
        
        # 格式化返回数据
        result = {
            "城市": result_data["location"]["name"],
            "天气": now["text"],
            "温度": f"{now['temperature']}°C",
            "体感温度": f"{now.get('feels_like', 'N/A')}°C",
            "湿度": f"{now.get('humidity', 'N/A')}%",
            "风向": now.get("wind_direction", "N/A"),
            "风速": f"{now.get('wind_speed', 'N/A')}km/h",
            "更新时间": result_data["last_update"]
        }
        return result
    except requests.exceptions.RequestException as e:
        return {"错误": f"获取天气数据失败: {str(e)}"}

# 获取天气预报
async def get_weather_forecast(city, days=3, lang="zh-Hans", unit="c"):
    """
    获取指定城市的天气预报
    
    参数:
        city (str): 城市名称
        days (int): 预报天数，最多15天
        lang (str): 返回结果的语言，默认为简体中文
        unit (str): 温度单位，c为摄氏度，f为华氏度
        
    返回:
        dict: 包含天气预报信息的字典
    """
    url = f"{BASE_URL}/weather/daily.json"
    params = {
        "key": API_KEY,
        "location": city,
        "language": lang,
        "unit": unit,
        "days": min(days, 15)  # 心知天气API支持最多15天预报
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # 心知天气API返回的数据结构
        result_data = data["results"][0]
        daily_forecasts = result_data["daily"]
        
        # 处理预报数据
        forecasts = {}
        for item in daily_forecasts:
            date = item["date"]
            
            forecast_item = {
                "白天天气": item["text_day"],
                "夜间天气": item["text_night"],
                "最高温度": f"{item['high']}°C",
                "最低温度": f"{item['low']}°C",
                "降水概率": f"{item.get('precip', 'N/A')}",
                "风向": item.get("wind_direction", "N/A"),
                "风速": f"{item.get('wind_speed', 'N/A')}km/h",
                "风力等级": item.get("wind_scale", "N/A"),
                "湿度": f"{item.get('humidity', 'N/A')}%"
            }
            forecasts[date] = forecast_item
            
        return {"城市": result_data["location"]["name"], "预报": forecasts}
    except requests.exceptions.RequestException as e:
        return {"错误": f"获取天气预报失败: {str(e)}"}

# 获取空气质量
async def get_air_quality(city, lang="zh-Hans"):
    """
    获取指定城市的空气质量
    
    参数:
        city (str): 城市名称
        lang (str): 返回结果的语言，默认为简体中文
        
    返回:
        dict: 包含空气质量信息的字典
    """
    url = f"{BASE_URL}/air/now.json"
    params = {
        "key": API_KEY,
        "location": city,
        "language": lang
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # 心知天气API返回的数据结构
        result_data = data["results"][0]
        air = result_data["air"]
        
        # AQI指数对应的描述
        aqi_desc = {
            "优": "空气质量令人满意，基本无空气污染",
            "良": "空气质量可接受，但某些污染物可能对极少数异常敏感人群健康有较弱影响",
            "轻度污染": "易感人群症状有轻度加剧，健康人群出现刺激症状",
            "中度污染": "进一步加剧易感人群症状，可能对健康人群心脏、呼吸系统有影响",
            "重度污染": "心脏病和肺病患者症状显著加剧，运动耐受力降低，健康人群普遍出现症状",
            "严重污染": "健康人群运动耐受力降低，有明显强烈症状，提前出现某些疾病"
        }
        
        result = {
            "城市": result_data["location"]["name"],
            "空气质量指数": f"{air['city']['aqi']}",
            "空气质量": f"{air['city']['quality']} ({aqi_desc.get(air['city']['quality'], '未知')})",
            "PM2.5": f"{air['city'].get('pm25', 'N/A')}",
            "PM10": f"{air['city'].get('pm10', 'N/A')}",
            "二氧化硫(SO2)": f"{air['city'].get('so2', 'N/A')}",
            "二氧化氮(NO2)": f"{air['city'].get('no2', 'N/A')}",
            "一氧化碳(CO)": f"{air['city'].get('co', 'N/A')}",
            "臭氧(O3)": f"{air['city'].get('o3', 'N/A')}",
            "更新时间": result_data["last_update"]
        }
        return result
    except requests.exceptions.RequestException as e:
        return {"错误": f"获取空气质量数据失败: {str(e)}"}

# 并发获取城市的天气信息
async def get_city_weather_info(city):
    """
    并发获取城市的天气信息，包括当前天气、天气预报和空气质量
    
    参数:
        city (str): 城市名称
        
    返回:
        dict: 包含所有天气信息的字典
    """
    # 并发调用多个函数获取不同的天气数据
    current_weather_task = asyncio.create_task(get_current_weather(city))
    forecast_task = asyncio.create_task(get_weather_forecast(city, days=3))
    air_quality_task = asyncio.create_task(get_air_quality(city))
    
    # 等待所有任务完成
    current_weather = await current_weather_task
    forecast = await forecast_task
    air_quality = await air_quality_task
    
    # 合并结果
    return {
        "当前天气": current_weather,
        "天气预报": forecast,
        "空气质量": air_quality
    }

# 并发获取多个城市的天气
async def get_multiple_cities_weather(cities):
    """
    并发获取多个城市的天气信息，包括当前天气、天气预报和空气质量
    
    参数:
        cities (list): 城市名称列表
        
    返回:
        dict: 包含多个城市天气信息的字典
    """
    # 为每个城市创建完整的天气信息获取任务
    tasks = [get_city_weather_info(city) for city in cities]
    results = await asyncio.gather(*tasks)
    
    return dict(zip(cities, results))

# 格式化输出天气信息
def format_weather_info(data):
    """
    格式化天气信息为易读的字符串
    
    参数:
        data (dict): 天气数据字典
        
    返回:
        str: 格式化后的字符串
    """
    if "错误" in data:
        return f"获取天气信息失败：{data['错误']}"
        
    output = []
    
    # 当前天气
    if "当前天气" in data:
        current = data["当前天气"]
        output.append("=== 当前天气 ===")
        for key, value in current.items():
            output.append(f"{key}: {value}")
    
    # 天气预报
    if "天气预报" in data and "预报" in data["天气预报"]:
        output.append("\n=== 天气预报 ===")
        for date, forecast in data["天气预报"]["预报"].items():
            output.append(f"\n{date}:")
            for key, value in forecast.items():
                output.append(f"  {key}: {value}")
    
    # 空气质量
    if "空气质量" in data:
        output.append("\n=== 空气质量 ===")
        for key, value in data["空气质量"].items():
            if key != "城市":  # 城市名已经在当前天气中显示
                output.append(f"{key}: {value}")
    
    return "\n".join(output)

# 主函数
async def main():
    while True:
        print("\n=== 欢迎使用天气预报机器人 ===")
        print("1. 获取单个城市的详细天气信息")
        print("2. 获取多个城市的天气信息")
        print("3. 退出程序")
        print("=" * 35)
        
        choice = input("\n请输入选项(1-3): ").strip()
        
        if choice == "3":
            print("\n感谢使用天气预报机器人，再见！")
            break
            
        elif choice == "1":
            city = input("\n请输入城市名称（如：北京）: ").strip()
            if not city:
                print("\n错误：城市名称不能为空！")
                continue
                
            print(f"\n正在获取 {city} 的详细天气信息...\n")
            try:
                result = await get_city_weather_info(city)
                print(format_weather_info(result))
            except Exception as e:
                print(f"\n发生错误：{str(e)}")
        
        elif choice == "2":
            cities_input = input("\n请输入城市名称，多个城市用逗号分隔（如：北京,上海,广州）: ").strip()
            if not cities_input:
                print("\n错误：城市名称不能为空！")
                continue
                
            cities = [city.strip() for city in cities_input.split(",") if city.strip()]
            if not cities:
                print("\n错误：未输入有效的城市名称！")
                continue
                
            print(f"\n正在获取 {', '.join(cities)} 的天气信息...\n")
            try:
                results = await get_multiple_cities_weather(cities)
                for city, result in results.items():
                    print(f"\n【{city}】")
                    print("-" * 50)
                    print(format_weather_info(result))
                    print("-" * 50)
            except Exception as e:
                print(f"\n发生错误：{str(e)}")
        
        else:
            print("\n无效的选项！请输入1-3之间的数字。")
        
        input("\n按回车键继续...")

# 运行主函数
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程序已被用户中断。感谢使用！")
    except Exception as e:
        print(f"\n程序发生错误：{str(e)}")