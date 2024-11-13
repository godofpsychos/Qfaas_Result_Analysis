from result_analysis_script import result_analysis
import csv,json,os

def list_dir(path):
    directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    return directories

# result_analysis.data_analysis("path to outputs","path to dag","path to store results")
# result_analysis.data_analysis([('/home/tarunpal/Desktop/temp/Qfaas_Result_Analysis/output/test/results.json',"/home/tarunpal/Desktop/temp/Qfaas_Result_Analysis/dags/test/dag.json","/home/tarunpal/Desktop/temp/Qfaas_Result_Analysis/Processed_results/test")])
pwd = os.getcwd()
dags_folder_path=f"{pwd}/dags"
output_folder_path=f"{pwd}/output"
processed_result_path=f"{pwd}/Processed_results"

dir_in_dags= list_dir(dags_folder_path)
dir_in_output= list_dir(output_folder_path)
dir_in_processed=list_dir(processed_result_path)

for name in dir_in_dags:
    if name in dir_in_output:
        if name in dir_in_processed:
            continue
        else :
            os.makedirs(processed_result_path+'/'+name)
    
    else :
        print("Please make dir available for ",name," in output folder")

dir_in_processed=list_dir(processed_result_path)
for name in  dir_in_output:
    if name in dir_in_dags:
        if name in dir_in_processed:
            continue
        else :
            os.makedirs(processed_result_path+'/'+name)
    
    else :
        print("Please make dir available for ",name," in dag folder")

dir_in_processed=list_dir(processed_result_path)
anylysis_list = []
for name in dir_in_dags:
    if name in dir_in_output and name in dir_in_processed:
        anylysis_list.append((output_folder_path+'/'+name+'/results.json',dags_folder_path+'/'+name+'/dag.json',processed_result_path+'/'+name))

result_analysis.data_analysis(anylysis_list)


#building CSV From results
# list_dict = []
# for name in dir_in_processed:
#     json_path= processed_result_path+'/'+name+'/processed.json'
#     with open(json_path, 'r') as file:
#         data = json.load(file)
#         l=name.split('-')
#         data["Experiment type"] = l[0] if len(l)>0 else "NA"
#         data["Experiment Subtype"] = l[1] if len(l)>1 else "NA"
#     list_dict.append(data)

# def flatten_dict(d, all_fields):
#     flat_dict = {field: "NA" for field in all_fields}  # Initialize with "NA"
    
#     for key, value in d.items():
#         if key in flat_dict:  # Only process keys that are in all_fields
#             if isinstance(value, dict):
#                 for sub_key, sub_value in value.items():
#                     # Check if the constructed key is in all_fields
#                     flat_key = f"{key}_{sub_key}"
#                     if flat_key in flat_dict:
#                         flat_dict[flat_key] = sub_value
#             elif isinstance(value, list):
#                 if key == 'Q_Results':
#                     listtt =[]
#                     print("Value",value)
#                     for dictt in value:
#                         strr = f"{dictt['job_id']}->use:{dictt['Quantum_Exec_Time']},wait:{dictt['Quantum_Queue_Time']}"
#                         listtt.append(strr)
#                     strrr = ','.join(listtt)
#                     flat_dict[key]=strrr
#                 # Only store list values if the key is in all_fields
#                 else:
#                     flat_dict[key] = ', '.join(value)  # Join list items into a string
#             else:
#                 flat_dict[key] = value  # Directly assign value if it's in all_fields
#     print(flat_dict)
#     return flat_dict

# # Define all possible fields for the CSV
# all_fields = ["Experiment type","Experiment Subtype","WorkFlowName","InstanceId","Total_workflow_exec_time_E2E","TotalFuntionExecutionTimeWithCritical","TotalFuntionExecutionTime","Total_waiting_time","TotalCost","Q_Results","Poller_ex_time","Exec_time_excluding_poller"]

# # Flatten the data
# flattened_data = [flatten_dict(item, all_fields) for item in list_dict]

# # Specify the CSV file path
# csv_file_path = f"{pwd}/output_with_na.csv"

# # Writing to CSV
# with open(csv_file_path, mode='w', newline='') as file:
#     writer = csv.DictWriter(file, fieldnames=all_fields)
#     writer.writeheader()  # Write the header
#     writer.writerows(flattened_data)  # Write the data

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
                        "Inter-func. payload size": json_data.get("Inter_Function_Payload_Size"), 
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

print(f'Data written to {output_csv}')
