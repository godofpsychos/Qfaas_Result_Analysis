import os
import json
import csv

base_dir = '.'  
output_csv = 'processed_data.csv'

data = []

for dirpath, dirnames, filenames in os.walk(base_dir):
    for filename in filenames:
        if filename == 'processed.json':
            json_path = os.path.join(dirpath, filename)
            experiment_name = os.path.basename(dirpath)  
            with open(json_path, 'r') as json_file:
                try:
                    json_data = json.load(json_file)
                    
                    row = {
                        "experiment": experiment_name,
                        "Cost": json_data.get("TotalCost"),
                        "Function Execution time (Total_workflow_exec_time_E2E)": json_data.get("Total_workflow_exec_time_E2E"),
                        "Async. Poller Time (Async_Poller_Time)": json_data.get("Async_Poller_Time"),
                        "Quantum Queue Time (Total_Quantum_Queue_Time)": json_data.get("Total_Quantum_Queue_Time"),
                        "Quantum HW/Sim. Exec Time (Total_Quantum_Exectime)": json_data.get("Total_Quantum_Exectime"),
                        "Inter-func. Time Excluding Polling (Inter_Function_Time_Excluding_Poller)": json_data.get("Inter_Function_Time_Excluding_Poller"),
                        "Inter-func. time (Inter_Function_Time)": json_data.get("Inter_Function_Time"),
                        "E2E WF Exec. Time (E2E_WF_Exec_Time)": json_data.get("E2E_WF_Exec_Time"),
                        "Inter-func. payload size": '',  
                        "Quantum Job ID (Job_Ids)": json_data.get("Job_Ids"),
                    }
                    
                    data.append(row)  
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from {json_path}")

with open(output_csv, 'w', newline='') as csv_file:
    
    fieldnames = [
        "experiment",
        "Cost",
        "Function Execution time (Total_workflow_exec_time_E2E)",
        "Async. Poller Time (Async_Poller_Time)",
        "Quantum Queue Time (Total_Quantum_Queue_Time)",
        "Quantum HW/Sim. Exec Time (Total_Quantum_Exectime)",
        "Inter-func. Time Excluding Polling (Inter_Function_Time_Excluding_Poller)",
        "Inter-func. time (Inter_Function_Time)",
        "E2E WF Exec. Time (E2E_WF_Exec_Time)",
        "Inter-func. payload size",
        "Quantum Job ID (Job_Ids)"
    ]
    
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for row in data:
        writer.writerow(row)

print(f'Data has been written to {output_csv}')
