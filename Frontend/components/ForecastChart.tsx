"use client";

import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";
import { format, parseISO } from "date-fns";
import { Forecast } from "@/types";

interface ForecastChartProps {
    data: Forecast[];
}

export default function ForecastChart({ data }: ForecastChartProps) {
    if (!data || data.length === 0) {
        return (
            <div className="h-[300px] flex items-center justify-center border border-dashed border-gray-300 rounded-lg text-gray-500">
                No forecast data available to display.
            </div>
        );
    }

    // Pre-process data for chart
    const chartData = data.map((item) => ({
        date: item.date, // Keep string for now, format in tickFormatter
        yieldIndex: item.yield_index,
    }));

    return (
        <div className="h-[300px] w-full p-4 bg-white rounded-lg border border-gray-200 shadow-sm">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">Yield Index Forecast (30 Days)</h3>
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                        <linearGradient id="colorYield" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#16a34a" stopOpacity={0.8} />
                            <stop offset="95%" stopColor="#16a34a" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <XAxis
                        dataKey="date"
                        tickFormatter={(str) => format(parseISO(str), "MMM d")}
                        style={{ fontSize: '12px' }}
                    />
                    <YAxis style={{ fontSize: '12px' }} />
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <Tooltip
                        labelFormatter={(str) => format(parseISO(str), "PPP")}
                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    />
                    <Legend />
                    <Area
                        type="monotone"
                        dataKey="yieldIndex"
                        stroke="#16a34a"
                        fillOpacity={1}
                        fill="url(#colorYield)"
                        name="Yield Index"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
