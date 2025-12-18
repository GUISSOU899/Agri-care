"use client";

import { Forecast, IrrigationRecommendation } from "@/types";
import { format, parseISO } from "date-fns";
import { Download } from "lucide-react";

interface IrrigationTableProps {
    data: IrrigationRecommendation[];
}

export default function IrrigationTable({ data }: IrrigationTableProps) {
    const handleExportCSV = () => {
        if (!data || data.length === 0) return;

        const headers = ["Date", "Irrigation (mm)", "Comment"];
        const rows = data.map((row) => [
            row.date,
            row.irrigation_mm.toString(),
            row.comment || "",
        ]);

        const csvContent =
            "data:text/csv;charset=utf-8," +
            [headers.join(","), ...rows.map((e) => e.join(","))].join("\n");

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", "irrigation_plan.csv");
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    if (!data || data.length === 0) {
        return (
            <div className="h-[300px] flex items-center justify-center border border-dashed border-gray-300 rounded-lg text-gray-500">
                No irrigation data available.
            </div>
        );
    }

    return (
        <div className="w-full bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden flex flex-col">
            <div className="p-4 border-b border-gray-200 flex justify-between items-center bg-gray-50">
                <h3 className="text-lg font-semibold text-gray-800">Irrigation Recommendations</h3>
                <button
                    onClick={handleExportCSV}
                    className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition"
                >
                    <Download size={16} />
                    Export CSV
                </button>
            </div>
            <div className="overflow-auto max-h-[300px]">
                <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50 sticky top-0">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Date
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Irrigation (mm)
                            </th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                Comment
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                        {data.map((row, idx) => (
                            <tr key={idx} className="hover:bg-gray-50 transition">
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                    {format(parseISO(row.date), "PPP")}
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium text-blue-600">
                                    {row.irrigation_mm} mm
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                                    {row.comment || "-"}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
