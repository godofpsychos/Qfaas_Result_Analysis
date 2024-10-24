from result_analysis_script import result_analysis
import csv,json,os

def list_dir(path):
    directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    return directories

# result_analysis.data_analysis("path to outputs","path to dag","path to store results")
# result_analysis.data_analysis([('/home/tarunpal/Desktop/temp/Qfaas_Result_Analysis/output/test/results.json',"/home/tarunpal/Desktop/temp/Qfaas_Result_Analysis/dags/test/dag.json","/home/tarunpal/Desktop/temp/Qfaas_Result_Analysis/Processed_results/test")])
dags_folder_path="/home/tarunpal/Desktop/temp/Qfaas_Result_Analysis/dags"
output_folder_path="/home/tarunpal/Desktop/temp/Qfaas_Result_Analysis/output"
processed_result_path="/home/tarunpal/Desktop/temp/Qfaas_Result_Analysis/Processed_results"

dir_in_dags= list_dir(dags_folder_path)
dir_in_output= list_dir(output_folder_path)
dir_in_processed=list_dir(processed_result_path)

# for name in dir_in_dags:
#     if name in dir_in_output:
#         if name in dir_in_processed:
#             continue
#         else :
#             os.makedirs(processed_result_path+'/'+name)
    
#     else :
#         print("Please make dir available for ",name," in output folder")

# dir_in_processed=list_dir(processed_result_path)
# for name in  dir_in_output:
#     if name in dir_in_dags:
#         if name in dir_in_processed:
#             continue
#         else :
#             os.makedirs(processed_result_path+'/'+name)
    
#     else :
#         print("Please make dir available for ",name," in dag folder")

# dir_in_processed=list_dir(processed_result_path)
# anylysis_list = []
# for name in dir_in_dags:
#     if name in dir_in_output and name in dir_in_processed:
#         anylysis_list.append((output_folder_path+'/'+name+'/results.json',dags_folder_path+'/'+name+'/dag.json',processed_result_path+'/'+name))
        
# result_analysis.data_analysis(anylysis_list)


#building CSV From results
list_dict = []
for name in dir_in_processed:
    json_path= processed_result_path+'/'+name+'/processed.json'
    with open(json_path, 'r') as file:
        data = json.load(file)
        l=name.split('-')
        data["Experiment type"] = l[0] if len(l)>0 else "NA"
        data["Experiment Subtype"] = l[1] if len(l)>1 else "NA"
    list_dict.append(data)

def flatten_dict(d, all_fields):
    flat_dict = {field: "NA" for field in all_fields}  # Initialize with "NA"
    
    for key, value in d.items():
        if key in flat_dict:  # Only process keys that are in all_fields
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    # Check if the constructed key is in all_fields
                    flat_key = f"{key}_{sub_key}"
                    if flat_key in flat_dict:
                        flat_dict[flat_key] = sub_value
            elif isinstance(value, list):
                if key == 'Q_Results':
                    listtt =[]
                    for dictt in value:
                        strr = f"{dictt["job_id"]}->use:{dictt["quantum_usage_sec"]},wait:{dictt["total_queue_waittime"]}"
                        listtt.append(strr)
                    strrr = ','.join(listtt)
                    flat_dict[key]=strrr
                # Only store list values if the key is in all_fields
                else:
                    flat_dict[key] = ', '.join(value)  # Join list items into a string
            else:
                flat_dict[key] = value  # Directly assign value if it's in all_fields
    print(flat_dict)
    return flat_dict

# Define all possible fields for the CSV
all_fields = ["Experiment type","Experiment Subtype","WorkFlowName","InstanceId","Total_workflow_exec_time_E2E","TotalFuntionExecutionTimeWithCritical","TotalFuntionExecutionTime","Total_waiting_time","TotalCost","Q_Results","Poller_ex_time","Exec_time_excluding_poller"]

# Flatten the data
flattened_data = [flatten_dict(item, all_fields) for item in list_dict]

# Specify the CSV file path
csv_file_path = '/home/tarunpal/Desktop/temp/Qfaas_Result_Analysis/output_with_na.csv'

# Writing to CSV
with open(csv_file_path, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=all_fields)
    writer.writeheader()  # Write the header
    writer.writerows(flattened_data)  # Write the data

print(f'Data written to {csv_file_path}')
