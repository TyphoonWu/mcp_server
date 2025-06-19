import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import axios from 'axios';
import { z } from "zod";


const CMA_CN_API_BASE = "https://weather.cma.cn/api/map/weather/1";
const CMA_CN_API_NOW = "https://weather.cma.cn/api/now";

// Create server instance
const server = new McpServer({
    name: "weather",
    version: "1.0.0",
    capabilities: {
        resources: {},
        tools: {},
    },
});

interface CityInfo {
    stationId: string;     // 站点编号
    cityName: string;      // 城市名
    country: string;       // 国家
    unknown: number;       // 未知
    latitude: number;      // 纬度
    longitude: number;     // 经度
    maxTemp: number;       // 最高温度
    weather: string;       // 天气
    windPower: number;     // 风力 m/s
    windDirection: string; // 风向
    windLevel: string;     // 风级
    minTemp: number;       // 最低温度
    weather2: string;      // 天气2
    windPower2: number;    // 风力2
    windDirection2: string;// 风向2
    windLevel2: string;    // 风级2
    cityCode: string;      // 城市代码
    districtCode: string;  // 区县代码
}

interface data {
    lastUpdate: string; // 最后更新时间
    date: string;       // 日期
    city: any[][];   // 城市信息数组，实际是二维数组
}

interface WeatherResponse {
    msg: string;
    code: number;
    data: data
}

interface Location {
    id: string;
    name: string;
    path: string;
}

interface WeatherNow {
    precipitation: number;
    temperature: number;
    pressure: number;
    humidity: number;
    windDirection: string;
    windDirectionDegree: number;
    windSpeed: number;
    windScale: string;
    feelst: number;
}

interface WeatherAlarm {
    id: string;
    title: string;
    signaltype: string;
    signallevel: string;
    effective: string;
    eventType: string;
    severity: string;
    type: string;
}

interface WeatherData {
    location: Location;
    now: WeatherNow;
    alarm: WeatherAlarm[];
    jieQi: string;
    lastUpdate: string;
}

interface WeatherCityResponse {
    msg: string;
    code: number;
    data: WeatherData
}


// Helper function for making NWS API requests
async function makeNWSRequest<T>(url: string): Promise<T | null> {
    try {
        const response = await axios.get(url, { timeout: 30 * 1000 });
        console.error("HTTP success! status:", response.status);
        // If response.data is already an object, no need to parse
        const data = typeof response.data === "string" ? JSON.parse(response.data) : response.data;
        return data as T;
    } catch (error: any) {
        if (error.code === 'ECONNABORTED') {
            console.error('Error making NWS request timeout');
        } else {
            console.error('Error making NWS request:', error);
        }
        return null;
    }
}

// Helper function to convert array to CityInfo object
function arrayToCityInfo(arr: any[]): CityInfo {
    return {
        stationId: arr[0],
        cityName: arr[1],
        country: arr[2],
        unknown: arr[3],
        latitude: arr[4],
        longitude: arr[5],
        maxTemp: arr[6],
        weather: arr[7],
        windPower: arr[8],
        windDirection: arr[9],
        windLevel: arr[10],
        minTemp: arr[11],
        weather2: arr[12],
        windPower2: arr[13],
        windDirection2: arr[14],
        windLevel2: arr[15],
        cityCode: arr[16],
        districtCode: arr[17]
    };
}

async function getWeatherDataByDate(city: string): Promise<CityInfo | null> {
    const url = CMA_CN_API_BASE;
    const response = await makeNWSRequest<WeatherResponse>(url);
    if (!response || response.code !== 0 || !response.data.city.length) {
        console.error("Failed to fetch weather data for city:", city);
        return null;
    }

    if (city) {
        // 转换数据格式并打印
        const cities = response.data.city.map(cityArray => arrayToCityInfo(cityArray as any[]));

        // 查找匹配的城市
        const cityData = cities.find(c => c.cityName === city);

        if (cityData) {
            console.error("Found matching city:", cityData);
            return cityData;
        } else {
            console.error("City not found:", city);
            return null;
        }
    } else {
        return null;
    }
}

async function getWeatherDataByNow(city: string): Promise<WeatherData | null> {
    const url = CMA_CN_API_BASE;
    const response = await makeNWSRequest<WeatherResponse>(url);
    if (!response || response.code !== 0 || !response.data.city.length) {
        console.error("Failed to fetch weather data for city:", city);
        return null;
    }

    if (city) {
        // 转换数据格式并打印
        const cities = response.data.city.map(cityArray => arrayToCityInfo(cityArray as any[]));

        // 查找匹配的城市
        const cityData = cities.find(c => c.cityName === city);
        const stationId = cityData?.stationId;
        if (!stationId) {
            console.error("City data does not contain stationId:", cityData);
            return null;
        } else {
            console.error("Found stationId for city:", stationId);
        }
        const nowUrl = `${CMA_CN_API_NOW}/${stationId}`;
        const nowResponse = await makeNWSRequest<WeatherCityResponse>(nowUrl);
        if (nowResponse && nowResponse.code === 0) {
            console.error("Found matching city:", nowResponse.data);
            return nowResponse.data;
        } else {
            console.error("City not found:", city);
            return null;
        }
    } else {
        return null;
    }
}


server.tool(
    "get_weather_now",
    "Get current weather forecast for a city name, the name type is string",
    {
        city: z.string().describe("Name of the city, the type is string, the city string does not include string of 省，市，自治区，特别行政区，直辖市"),
    },
    async ({ city }) => {

        const weatherData = await getWeatherDataByNow(city);
        if (!weatherData) {
            return {
                content: [
                    {
                        type: "text",
                        text: "Could not fetch weather data for " + city,
                    },
                ],
                isError: true,
            };
        }

        return {
            content: [
                {
                    type: "text",
                    text: "Fetching current weather forecast for " + city + ":\n" +
                        `City: ${weatherData.location.name}\n` +
                        `Temperature: ${weatherData.now.temperature}°C\n` +
                        `Humidity: ${weatherData.now.humidity}%\n` +
                        `Wind: ${weatherData.now.windDirection} at ${weatherData.now.windSpeed} m/s, ${weatherData.now.windScale}\n` +
                        `Pressure: ${weatherData.now.pressure} hPa\n` +
                        `Precipitation: ${weatherData.now.precipitation} mm\n` +
                        `Last Update: ${weatherData.lastUpdate}\n`
                },
            ],
            isError: false,
        };
    },
);

server.tool(
    "get_weather_date",
    "Get today's weather forecast for a city name, the name type is string",
    {
        city: z.string().describe("Name of the city, the type is string, the city string does not include string of 省，市，自治区，特别行政区，直辖市"),
    },
    async ({ city }) => {

        const weatherData = await getWeatherDataByDate(city);
        if (!weatherData) {
            return {
                content: [
                    {
                        type: "text",
                        text: "Could not fetch weather data for " + city,
                    },
                ],
                isError: true,
            };
        }

        return {
            content: [
                {
                    type: "text",
                    text: "Fetching today's weather forecast for " + city + ":\n" +
                        `City: ${weatherData.cityName}\n` +
                        `Country: ${weatherData.country}\n` +
                        `Max Temp: ${weatherData.maxTemp}°C\n` +
                        `Min Temp: ${weatherData.minTemp}°C\n` +
                        `Weather: ${weatherData.weather}\n` +
                        `Wind power: ${weatherData.windPower}m/s\n` +
                        `Wind Direction: ${weatherData.windDirection}\n` +
                        `Wind Level: ${weatherData.windLevel}\n`,
                },
            ],
            isError: false,
        };
    },
);

async function main() {
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("Weather MCP Server running on stdio");
}

main().catch((error) => {
    console.error("Fatal error in main():", error);
    process.exit(1);
});