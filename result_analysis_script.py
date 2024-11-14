import json
import pandas as pd
import requests
import networkx as nx
import os
from qiskit_ibm_runtime import QiskitRuntimeService
import datetime


az_cost_factor  = 0.000016
aws_cost_factor = 0.0000166667

def read_dictionary_from_file(file_path):
    with open(file_path, 'r') as file:
        # Read the content of the file
        content = file.read()
        # Evaluate the content as a dictionary
        dictionary_data = json.loads(content)
        return dictionary_data
    
def quantum_results(job_id,ibmq_token):
    service = QiskitRuntimeService(channel="ibm_quantum", token=ibmq_token)
    # jobs_in_last_three_months = service.jobs(created_after=three_months_ago)
    # print(jobs_in_last_three_months)
    job = service.job(job_id=job_id)
    # print(job)
    metric = job.metrics()
    print("METRIC",metric)
    quantum_usage_sec= metric['usage']['quantum_seconds']
    from dateutil import parser
    metric['timestamps']['finished'] = parser.isoparse(metric['timestamps']['finished'])
    metric['timestamps']['created'] = parser.isoparse(metric['timestamps']['created'])
    total_queue_waittime =  metric['timestamps']['finished']- metric['timestamps']['created']
    # print('quantum_usage_sec',quantum_usage_sec)
    # print('total_queue_waittime',total_queue_waittime.total_seconds())
    dic = {
        'Quantum_Exec_Time':quantum_usage_sec,
        'Quantum_Queue_Time':total_queue_waittime.total_seconds()-quantum_usage_sec,
        'job_id' :  job_id, 
        'ibmq_token' : ibmq_token      
    }
    return dic
# path="output_obj.txt"
def creating_outobject(url):
    # data = read_dictionary_from_file(path)
    # print(data)
    # return 
    print(f"Processing {url}")
    data = None
    csp = 'aws' if 'aws' in url.lower() else 'azure'
    if csp == 'aws':
        with open(url) as f:
            json_data = json.load(f)
            res = {
                "_body": json_data['body'],
                "_metadata": json_data['metadata'],
                "instanceId": json_data['metadata']['deployment_id']
            }
            data = {"output": json.dumps(res), "instanceId": json_data['metadata']['deployment_id']}
    if url.endswith(".json"):
        with open(url) as f:
            data = data or json.load(f)
    else :
        response_API = requests.get(url)
        data = response_API.text
        data = json.loads(data)

        

    # data = json.loads(url)
    # Parse the data into JSON format
    # print(data)
    out_obj=json.loads(data['output'])
    out_obj=out_obj['_metadata']['functions']
    instanceId=data['instanceId']
    out_obj=json.loads(data['output'])
    # print(out_obj['_body'].keys())
    boddy=out_obj['_body']
    boddy['devices'] = boddy['jobs'] if 'jobs' in boddy else None
    # change all instances of key 'id' to key 'job_id'
    if boddy['devices'] != None:
        for i in range(len(boddy['devices'])):
            boddy['devices'][i]['job_id'] = boddy['devices'][i].pop('id')

    # boddy['devices']=[{'device':'ibm_brisbane','job_id' : 'cnnejcgalmrcvvncrb9g',
    # 'qtoken' : '83fbd2a81a2088f83ed2baaa4444ff193a48fb315819591bbc90ac4f00a654004b3d15c2e48a38d939421d40bad5ebd70c56ad4c9cb13676e84a1993b6d223e2'}, {'device':'ibm_brisbane','job_id' : 'cnnejcgalmrcvvncrb9g',
    # 'qtoken' : '83fbd2a81a2088f83ed2baaa4444ff193a48fb315819591bbc90ac4f00a654004b3d15c2e48a38d939421d40bad5ebd70c56ad4c9cb13676e84a1993b6d223e2'}]
    print("Deives", boddy['devices'])
    out_obj=out_obj['_metadata']['functions']
    quantum_list = boddy['devices'] if 'devices' in boddy else None
    out=[]
    for fn in out_obj:
        # temp={}
        for fn_name in fn:
            obj=fn[fn_name]
            # print(obj)
            # print(type(obj['start_delta']))
            start_delta=int(obj['start_delta'])
            end_delta = obj['end_delta']
            mem_before=obj['mem_before']
            mem_after = obj['mem_after']
            net_time=abs(end_delta-start_delta)
            net_mem=abs(mem_after-mem_before)
            payload_size=int(obj['in_payload_bytes'])
            temp={
                'NodeId':fn_name,
                'start_delta':start_delta,
                'end_delta':end_delta,
                'mem_before':mem_before,
                'mem_after':mem_after,
                'net_time':net_time,
                'net_mem':net_mem,
                # measure cost based on azure or aws
                'cost':aws_cost_factor*(net_time/1000)*(net_mem/1073741824) if csp == 'aws' else az_cost_factor*(net_time/1000)*(net_mem/1073741824),
                'inter_function_payload_size':payload_size
            }
            out.append(temp)
    return out,instanceId,quantum_list


def custom_dfs(graph, node, dataframe,result_list, node_to_nodeid,path="",ntime=0,cost=0):

    
    neighbors = list(graph.neighbors(node))
    path+=node+'->'
    nodeId=node_to_nodeid[node]
    # print(nodeId)
    # print(dataframe)
    print("Node Id",nodeId)
    node_data=dataframe.loc[nodeId].to_dict()
    # print(node_data)
    ntime+= node_data['net_time']
    cost+= node_data['cost']
    paths_with_weights = []
    for neighbor in neighbors:
        custom_dfs(graph, neighbor, dataframe, result_list,node_to_nodeid,path, ntime,cost)

    if len(neighbors)==0:
        result_list.append((path, (ntime,cost)))
        # print("We are in last node")
        return [(path, ntime,cost)]
    
    return paths_with_weights

class result_analysis:
    def data_analysis(url_list):
        for url,wf_path,out_path in url_list:
            out,instance_id,quantum_list = creating_outobject(url)
            df = pd.DataFrame.from_dict(out).set_index('NodeId')
            df_grouped = df.groupby('NodeId').agg({
    'start_delta': 'min',
    'end_delta': 'max',
    'mem_before': 'min',
    'mem_after': 'max',
    'net_time': 'sum',
    'net_mem': 'sum',
    'cost': 'sum',
    'inter_function_payload_size': 'sum'
})
            print(df)
            df=df_grouped
            print(df_grouped)
            # dag_path=wf_path+'/'
            dag_path=wf_path
            # os.path.join(wf_path,'dag.json')
            with open(dag_path, 'r') as file:
                data = json.load(file)

            # Create a directed graph
            node_to_nodeid={}
            nodeid_to_node={}
            graph = nx.DiGraph()

            # Add nodes to the graph
            for node in data['Nodes']:
                graph.add_node(node['NodeName'])
                node_to_nodeid[node['NodeName']]=node['NodeId']
                nodeid_to_node[node["NodeId"]]=node['NodeName']

            # Add edges to the graph
            for edge in data['Edges']:
                for source, targets in edge.items():
                    for target in targets:
                        graph.add_edge(source, target)  # Assuming each edge has only one target

            # Print the graph nodes and edges
            # print("Nodes:", graph.nodes(data=False))
            # print("Edges:", graph.edges())
            # print("NodeMap:",node_to_nodeid)
            workflow_name=data['WorkflowName']
            result_list=[]
            custom_dfs(graph, nodeid_to_node['1'], df,result_list,node_to_nodeid)
            # print(node_to_nodeid)
            poller_id = node_to_nodeid['Poller'] if 'Poller' in node_to_nodeid else None
            poller_ex_time = -1 if poller_id==None else df.loc[poller_id]['net_time']/1000
            max_time=max_cost=0
            critical_path=""
            for (path,(time,cost)) in result_list:
                if time>max_time:
                    (critical_path,(max_time,max_cost))=(path,(time,cost))
            max_time=max_time/1000
            start_node_data=df.loc['1'].to_dict()
            # end node should be the highest node id
            end_node_data=df.loc[str(len(data['Nodes']))].to_dict()
            print("End Node Data",end_node_data)
            # end_node_data=df.loc['253'].to_dict()
            start_timestamp=start_node_data['start_delta']
            end_timestamp=end_node_data['end_delta']
            total_workflow_exec_time=(end_timestamp-start_timestamp)/1000
            waiting_time=(total_workflow_exec_time-max_time)
            total_cost=df['cost'].sum()
            total_func_exec_time = df['net_time'].sum()/1000
            inter_function_payload_size = df['inter_function_payload_size'].sum()

            print('For workflow:\t', workflow_name,'\n\t InstanceId:\t',instance_id ,'\n\t\tTotal workflow execution time(2E Workflow Exec. Time):\t',total_workflow_exec_time ,'\n\t\tTotal function execution time:\t',total_func_exec_time, 'seconds\n\t\tTotal funtion exec time(as per critical path):\t',max_time,'seconds\n\t\tTotal waiting time(as per critical path):\t',waiting_time,'seconds\n\t\tCritical Path:\t',critical_path,'\b\b\n\t\tTotal Cost: \t$ ',total_cost)
            results={
                "WorkFlowName":workflow_name,
                "InstanceId":instance_id,
                "TotalCost":format(total_cost, '.20f'),
                "Total_workflow_exec_time_E2E":total_workflow_exec_time,
                "E2E_WF_Exec_Time":max_time,
                "Inter_Function_Time":float(total_func_exec_time),
                "Total_waiting_time":waiting_time,
                "CriticalPath":critical_path,
                "Inter_Function_Payload_Size": str(inter_function_payload_size),
                "PathResults": []
            }
            

            # print(result_list)
            print("\n\nFor each path total execution time and total waiting time")
            for (path,(time,cost)) in result_list:
                time=time/1000
                out={"Path":path,
                     "Total_exec_time":time,
                     "Total waiting time":total_workflow_exec_time-time}
                print("Path:",path,'\tTotal exec time:',time,'sec\tTotal waiting time:',total_workflow_exec_time-time,"sec")
                results["PathResults"].append(out)
            
            print("*****************************************************************************")
            print(quantum_list)
            if quantum_list != None and 'device' in quantum_list[0] and 'job_id' in quantum_list[0] and "-" not in quantum_list[0]['job_id']:
                qresults = []
                for dict in quantum_list:
                    qtoken= dict['qtoken']
                    job_id= dict['job_id']
                    qresults.append(quantum_results(job_id=job_id,ibmq_token=qtoken))
                results["Q_Results"] = qresults
            print("*****************************************************************************")

            if poller_ex_time != -1:
                results["Async_Poller_Time"] = poller_ex_time
                results["Inter_Function_Time_Excluding_Poller"] = (float(total_func_exec_time) - float(poller_ex_time))
                results['Total_Quantum_Queue_Time'] = sum([x['Quantum_Queue_Time'] for x in results["Q_Results"]]) if 'Q_Results' in results else 0
                results['Total_Quantum_Exectime'] = sum([x['Quantum_Exec_Time'] for x in results["Q_Results"]]) if 'Q_Results' in results else 0
                if quantum_list != None:
                    if 'Q_Results' in results:
                        results['Job_Ids'] = ','.join([x['job_id'] for x in results["Q_Results"]]) if 'Q_Results' in results else ''
                    elif 'job_id' in quantum_list[0]:
                        results['Job_Ids'] = ','.join([x['job_id'] for x in quantum_list]) if quantum_list != None else ''
                results
            # result_dir = wf_path + '/Results'
            result_dir = out_path

            
            if not os.path.exists(result_dir):
                os.makedirs(result_dir)
            json_file_path = os.path.join(result_dir, f'processed.json')
            # text_file_path = os.path.join(result_dir, f'{instance_id}.txt')
            
            with open(json_file_path, 'w') as json_file:
                json.dump(results, json_file, indent=4)

            print(f"Results saved to {json_file_path}")

            # with open(text_file_path, 'w') as f:
            #     f.write('For workflow:\t' + workflow_name + '\n\t InstanceId:\t' + instance_id + '\n\t\tTotal workflow execution time:\t' + str(total_workflow_exec_time) + ' seconds\n\t\tTotal funtion exec time(as per critical path):\t' + str(max_time) + ' seconds\n\t\tTotal waiting time(as per critical path):\t' + str(waiting_time) + ' seconds\n\t\tCritical Path:\t' + critical_path + '\b\b\n\t\tTotal Cost: \t$ ' + str(total_cost) + '\n\n\nFor each path total execution time and total waiting time\n')
            #     for (path, (time, cost)) in result_list:
            #         time = time / 1000
            #         f.write("Path:" + str(path) + '\tTotal exec time:' + str(time) + ' sec\tTotal waiting time:' + str(total_workflow_exec_time - time) + " sec\n")


            # print('\n\n')
            # output_file = 'output.xlsx'
            # sheet_name = instance_id[0:30]
            # if not os.path.isfile(output_file):
            # # Create a new workbook and save it if the file does not exist
            #     wb = Workbook()
            #     wb.save(output_file)

            
            # with pd.ExcelWriter(output_file, engine='openpyxl', mode='a') as writer:
            #     # Check if the sheet name already exists in the workbook
            #     if sheet_name in writer.book.sheetnames:
            #         # Get the sheet by name and remove it
            #         std = writer.book[sheet_name]
            #         writer.book.remove(std)
            #     # Write the DataFrame to the sheet
            #     df.to_excel(writer, sheet_name=sheet_name, index=True)

        print("Results stored sucessfully.")
