from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import calendar
from dowhy import gcm
import networkx as nx
import openpyxl
import os
from django.conf import settings
from FormAPI.utils.ReportAnalysis.Industry_utils import Prelim_calculation
# import typing_extensions

db_settings = settings.DATABASES['default']

def get_connection_url(database_name):
    package = "mysql+pymysql"
    database_connection_url = f"{package}://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
    return database_connection_url

def get_db_connection(database_name):
    database_connection_url = get_connection_url(database_name)
    connect_args = {'charset': 'latin1'}
    # connect_args = {'ssl': {'ttls': True}}
    engine = create_engine(database_connection_url,
                            echo=False, connect_args=connect_args)
    db_conn = engine.connect()

    dbSession = sessionmaker(bind=engine)
    db_session = dbSession()

    return db_session, db_conn

def get_connection_url2(database_name):
    package = "mysql+pymysql"
    user_name = db_settings['USER']
    password = db_settings['PASSWORD']
    database_name = database_name
    host_name = db_settings['HOST']
    port = db_settings['PORT']

    database_connection_url = package + "://" + user_name + ":" + password + "@" + host_name + ":" + port + "/" + database_name
    
    #example -> 'mysql+pymysql://root:manoj123@127.0.0.1:3306/app_reviews'

    return database_connection_url


def get_db_connection2(database_name):
    database_connection_url = get_connection_url(database_name)

    # connect_args = {'ssl': {'ttls': True}}
    # engine = create_engine(database_connection_url, echo=False, connect_args=connect_args)

    connect_args = {'charset': 'latin1'}
    engine = create_engine(database_connection_url,
                               echo=False, connect_args=connect_args)
    
    db_conn = engine.connect()

    dbSession = sessionmaker(bind=engine)
    db_session = dbSession()

    return db_session, db_conn

# #### Transform Dataframe to club all graph parameters by date

def fetch_data(player_id, parameter_list, date, db_conn):
    par_str = str(parameter_list).replace("[", "(").replace("]", ")")
    main_df = pd.read_sql(text(f"SELECT * FROM main_data where parameter_id in {par_str} and player_id = {player_id} and start_date <= '{str(date)}';"), db_conn)
    par_df = pd.read_sql(text(f"SELECT parameter_id, unit, verbal_name FROM parameter where parameter_id in {par_str};"), db_conn)
    par_df.fillna("", inplace= True)
    filter_main_df = main_df[['player_id', 'parameter_id', 'start_date', 'value']].copy()
    filter_main_df['start_date'] = pd.to_datetime(filter_main_df["start_date"]).dt.date
    
    filter_main_df = filter_main_df.loc[filter_main_df['start_date'] <= date]
    filter_main_df['Metric'] = filter_main_df['parameter_id']
    transformed_df = filter_main_df.pivot_table(index= 'start_date', columns= ['Metric'], values= 'value', aggfunc= 'first')
    transformed_df = transformed_df.reset_index()
    transformed_df.sort_values('start_date', inplace= True)
    # max_date = transformed_df['start_date'].max()
    transformed_df = transformed_df[transformed_df['start_date'].isin(transformed_df['start_date'].iloc[-13:])]
    # transformed_df['Year'] = (transformed_df["start_date"]).apply(lambda x: x.year)
    # transformed_df['month'] =  (transformed_df["start_date"]).apply(lambda x: x.month)
    transformed_df = transformed_df.interpolate(method = "spline", order = 2, axis = 0).fillna(method = "bfill", axis = 0)
    # transformed_df.fillna(0, inplace = True)
    return transformed_df, par_df

def fetch_pf_data(players, parameter_list, date, db_conn):
    par_str = str(parameter_list).replace("[", "(").replace("]", ")")
    main_df = pd.read_sql(text(f"SELECT * FROM main_data where parameter_id in {par_str} and player_id in {tuple(players)} and start_date <= '{str(date)}';"), db_conn)
    par_df = pd.read_sql(text(f"SELECT parameter_id, unit, verbal_name FROM parameter where parameter_id in {par_str};"), db_conn)
    player_df = pd.read_sql(text(f"SELECT player_id, player_name from player where player_id in {tuple(players)};"), db_conn)
    par_df.fillna("", inplace= True)
    filter_main_df = main_df[['player_id', 'parameter_id', 'start_date', 'value']].copy()
    filter_main_df['start_date'] = pd.to_datetime(filter_main_df["start_date"]).dt.date

    filter_main_df = filter_main_df.loc[filter_main_df['start_date'] <= date]
    transformed_df = filter_main_df.pivot_table(index= 'start_date', columns= ['player_id'], values= 'value', aggfunc= 'first')
    transformed_df = transformed_df.reset_index()
    transformed_df.sort_values('start_date', inplace= True)
    transformed_df = transformed_df[transformed_df['start_date'].isin(transformed_df['start_date'].iloc[-13:])]
    # transformed_df['Year'] = (transformed_df["start_date"]).apply(lambda x: x.year)
    # transformed_df['month'] =  (transformed_df["start_date"]).apply(lambda x: x.month)
    transformed_df = transformed_df.interpolate(method = "spline", order = 2, axis = 0).fillna(method = "bfill", axis = 0)
    transformed_df.fillna(0, inplace = True)
    return transformed_df, par_df, player_df


# #### Aggregate and Transform Data by the Specified Periodicity


# ### Define Graph and apply GCM


class Node:
    def __init__(self, id: int):
        self.id = id
        self.children = []
    
    def add_child(self, child_node):
        self.children.append(child_node)
        
def convert_to_percentage(value_dictionary):
    total_absolute_sum = np.sum([abs(v) for v in value_dictionary.values()])
    return {k: abs(v) / total_absolute_sum * 100 for k, v in value_dictionary.items()}

def CPGR(series):
    total_return = series.iloc[-1]/series.iloc[0] - 1
    # no_of_periods = len(series) - 1
    # CPGR = (1 + total_return)**(1 / no_of_periods) - 1
    CPGR = total_return * 100
    return float(f"{CPGR: .2f}")

def intrinsic_contribution(causal_strength, causal_contribution, Node, curr_contribution):
    param_id = Node.id
    # current node uniquely identifies it's contribution to parent in causal_strength where it's first element in the tuple key (Node.id, ....)
    Node_to_parent = causal_strength.get(param_id, 100)
    abs_nodal_contribution = Node_to_parent * curr_contribution/100
    causal_contribution[param_id] = abs_nodal_contribution
    curr_contribution = abs_nodal_contribution
    if Node.children:
        for the_node in Node.children:
            intrinsic_contribution(causal_strength, causal_contribution, the_node, curr_contribution)
    else:
        return
    
def find_causal_node(causal_strength, Node: Node, Nodal_map):
    if Node.children:
        children_ids = [Child_node.id for Child_node in Node.children]
        children_causal_strength = dict(filter(lambda item: item[0] in children_ids, causal_strength.items()))
        Max_strength_node = max(children_causal_strength, key= children_causal_strength.get)
        Strongest_node = Nodal_map[Max_strength_node]
        return find_causal_node(causal_strength, Strongest_node, Nodal_map)
    else:
        return Node



class Industry_report:
    def __init__(self, report_name, ind_id):
        self.report_name = report_name
        self.industry_id = ind_id
        self.pages = {}
        self.tot_player = None
        self.players = []

    def Add_page(self, Page_no, Graph_name: str):
        # self.page_no = Page_no
        if Page_no not in self.pages:
            self.pages[Page_no] = {}
        if Graph_name not in self.pages[Page_no]:
            self.pages[Page_no][Graph_name] = Graph(Graph_name) 

class Graph:
    def __init__(self, Graph_name):
        self.Graph_name = Graph_name
        self.sub_graphs = {}
    
    def add_sub_graph(self, sub_graphs):
        for sub_graph_name, info in sub_graphs.items():
            self.sub_graphs[sub_graph_name] = info


def read_rep_structure():
    Reports_wb = openpyxl.load_workbook(os.path.join(settings.BASE_DIR, './FormAPI/utils/ReportAnalysis/Report_Structure.xlsx'))
    All_sheets = Reports_wb.sheetnames
    All_sheets.remove("Players")
    Players_df = pd.DataFrame(Reports_wb["Players"].values)
    Players_df = Players_df.set_axis(Players_df.iloc[0], axis= 1)
    Players_df = Players_df[1:]
    ind_reports = {}
    ind_players = {}
    # ind_structures = {}

    for worksheet in All_sheets:
        ind_graphs_df = pd.DataFrame(Reports_wb[worksheet].values)
        ind_graphs_df = ind_graphs_df.set_axis(ind_graphs_df.iloc[0], axis = 1)
        ind_graphs_df = ind_graphs_df[1:]
        # print("industry_sheet", ind_graphs_df)
        Industry_info = Players_df.loc[Players_df["Industry"].apply(str) == str(worksheet)]
        # print("********",Industry_info)
        ind_players[worksheet] = Industry_info["Player_id"].to_list()

        ind_id = ind_graphs_df["Industry_id"].unique()[0]
        ind_reports[worksheet] = Industry_report(worksheet, ind_id)
        ind_reports[worksheet].players = ind_players[worksheet]
        ind_reports[worksheet].tot_player = Industry_info["Tot_player"].unique()[0]

        for key, data_df in ind_graphs_df.groupby(["Page_no", "Parent_graph", "Sub_graph"]):
            Page_no, Parent_graph, Sub_graph_name = key
            ind_reports[worksheet].Add_page(Page_no, Parent_graph)
            curr_page = ind_reports[worksheet].pages[Page_no]
            target_child_dict = {}
            for target_id, children in data_df[["target_id", "child_id"]].dropna().groupby("target_id"):
                child_list = list(children['child_id'])
                target_child_dict[target_id] = child_list

            sub_graph = {}
            sub_graph[Sub_graph_name] = {"root parameter": data_df["root_parameter"].unique()[0], "linkage tree": {}}
            linkage_tree = sub_graph[Sub_graph_name]["linkage tree"]

            for target_id, nodes_list in target_child_dict.items():
                linkage_tree[target_id] = []
                for child_id in nodes_list:
                    linkage_tree[target_id].append((child_id, target_id))
                    
            curr_page[Parent_graph].add_sub_graph(sub_graph)

    return ind_reports
    
# Report_structures_df = pd.read_excel("Report_Structure.xlsx", sheet_name= "Foodtech")


# causal_graph = []
def get_causal_node(linkage_tree, transformed_df, root_node, Nodes_map):
    causal_strengths = {}
    for target_id, sub_tree in linkage_tree.items():
        causal_graph = nx.DiGraph(sub_tree)
        scm = gcm.StructuralCausalModel(causal_graph)
        gcm.auto.assign_causal_mechanisms(scm, transformed_df)
        gcm.fit(scm, transformed_df)
        arrow_strengths = gcm.arrow_strength(scm, target_node= target_id)
        causal_strengths.update(convert_to_percentage(arrow_strengths))
        
    intrinsic_causal_contribution = {}
    modified_strength = {my_key[0]: val for my_key, val in causal_strengths.items()}
    intrinsic_contribution(modified_strength, intrinsic_causal_contribution, root_node, 100)
    causal_node = find_causal_node(modified_strength, root_node, Nodes_map)
    return causal_node, modified_strength

# contributing_param = parameter_list.copy()
# contributing_param.remove(371)

def Platforms_inference(transformed_df, Nodes_map, causal_node, par_df, all_players, pl_name_dict):
    tot_player = all_players.pop()
    # root_parameter = par_df["parameter_id"].iloc[0] 
    unit = par_df["unit"].iloc[0].strip()
    par_name = par_df["verbal_name"].iloc[0].strip()
    par_name = par_name[0].title() + par_name[1:]
    tot_player_CPGR = CPGR(transformed_df[tot_player])
    impact_pl_CPGR = CPGR(transformed_df[causal_node.id])
    curr_level = float("{:.1f}".format(transformed_df[tot_player].iloc[-1]))
    curr_period = transformed_df['start_date'].iloc[-1].strftime("%b'%y") 
    Total_market = transformed_df[all_players].iloc[-1].sum()
    Market_share = {pl_id: float("{:.2f}".format(transformed_df[pl_id].iloc[-1] * 100/Total_market)) for pl_id in all_players}
    threshold_change = 1 # expressed in % 
    inference = ""
    # Market Share Inference
    max_share_pl = max(Market_share, key = Market_share.get)
    inference += f"{pl_name_dict[max_share_pl].title()} had the highest market share at {Market_share[max_share_pl]}% in {curr_period}"
    if tot_player_CPGR >= threshold_change:
        inference += f". {par_name} grew by {str(tot_player_CPGR)}% YoY to reach {curr_level} {unit} for {curr_period}" 
        if impact_pl_CPGR > 0:
            inference += f" driven by {str(impact_pl_CPGR)}% rise for {pl_name_dict[causal_node.id]}"
        # find one node with the highest impact -> causal_node
    elif - threshold_change < tot_player_CPGR < threshold_change:
        if tot_player_CPGR > 0:
            inference += f"{par_name} stayed within a narrow range increasing only slightly by {str(tot_player_CPGR)}% YoY as of {curr_period}"
        else:
            inference += f"{par_name} stayed within a narrow range decreasing only slightly by {str(abs(tot_player_CPGR))}% YoY as of {curr_period}"
    else:
        inference += f". {par_name} fell by {str(abs(tot_player_CPGR))}% YoY to reach {curr_level} {unit} for {curr_period}"
        if impact_pl_CPGR < 0:
            inference += f" due to a {str(abs(impact_pl_CPGR))}% decline for {pl_name_dict[causal_node.id].title()}"
    return inference

def simple_inference(transformed_df, root_parameter, par_df):
    par_name_map = par_df.set_index("parameter_id")["verbal_name"].to_dict()
    unit = par_df["unit"].iloc[0].strip()
    root_node_CPGR = CPGR(transformed_df[root_parameter])
    par_name = par_name_map[root_parameter].strip()
    par_name = par_name[0].title() + par_name[1:]
    curr_period = transformed_df['start_date'].iloc[-1].strftime("%b'%y") 
    curr_level = float("{:.1f}".format(transformed_df[root_parameter].iloc[-1]))
    threshold_change = 1 # expressed in % 
    inference = ""
    if root_node_CPGR >= threshold_change:
        inference += f"{par_name} grew by {str(root_node_CPGR)}% YoY to reach {curr_level} {unit} for {curr_period}"
        # find one node with the highest impact -> causal_node
    elif - threshold_change < root_node_CPGR < threshold_change:
        if root_node_CPGR > 0:
            inference += f"{par_name} stayed within a narrow range increasing only slightly by {str(root_node_CPGR)}% YoY as of {curr_period}"
        else:
            inference += f"{par_name} stayed within a narrow range decreasing only slightly by {str(abs(root_node_CPGR))}% YoY as of {curr_period}"
    else:
        inference += f"{par_name} fell by {str(abs(root_node_CPGR))}% YoY to reach {curr_level} {unit} for {curr_period}"
    return inference

def causal_inference(transformed_df, Nodes_map, modified_strength, root_node, causal_node, par_df):
    par_name_map = par_df.set_index("parameter_id")["verbal_name"].to_dict()
    unit = par_df["unit"].iloc[0].strip()
    root_node_CPGR = CPGR(transformed_df[root_node.id])
    root_par_name = par_name_map[root_node.id].strip()
    root_par_name = root_par_name[0].title() + root_par_name[1:]
    causal_node_CPGR = CPGR(transformed_df[causal_node.id])
    curr_level = float("{:.1f}".format(transformed_df[root_node.id].iloc[-1]))
    curr_period = transformed_df['start_date'].iloc[-1].strftime("%b'%y") 
    threshold_change = 1 # expressed in % 
    inference = ""
    if root_node_CPGR >= threshold_change:
        inference += f"{root_par_name} grew by {str(root_node_CPGR)}% YoY to reach {curr_level} {unit} for {curr_period}" 
        if causal_node_CPGR > 0:
            inference += f" driven by {str(causal_node_CPGR)}% rise in {par_name_map[causal_node.id]}"
        # else:
        #     inference += f"driven by a {str(abs(causal_node_CPGR))}% decline in {par_name_map[causal_node.id]}"
        # find one node with the highest impact -> causal_node
    elif - threshold_change < root_node_CPGR < threshold_change:
        if root_node_CPGR > 0:
            inference += f"{root_par_name} stayed within a narrow range increasing only slightly by {root_node_CPGR}% YoY as of {curr_period}"
        else:
            inference += f"{root_par_name} stayed within a narrow range decreasing only slightly by {str(abs(root_node_CPGR))}% YoY as of {curr_period}"
        # if significant but offsetting change was observed in two or more variables find the two variables with highest var attribution
        threshold = 2                 # threshold to indicate significant change in child nodes
        first_node = causal_node
        first_node_CPGR = causal_node_CPGR
        del modified_strength[first_node.id]
        if first_node_CPGR > threshold:
            second_node = find_causal_node(modified_strength, root_node, Nodes_map)
            while CPGR(transformed_df[second_node.id]) >= threshold:
                del modified_strength[second_node.id]
                second_node = find_causal_node(modified_strength, root_node, Nodes_map)
            inference += f" as {par_name_map[first_node.id]} rose by {first_node_CPGR} but {par_name_map[second_node.id]} fell by {CPGR(transformed_df[second_node.id])}"
        elif first_node_CPGR < - threshold:
            second_node = find_causal_node(modified_strength, root_node, Nodes_map)
            while CPGR(transformed_df[second_node.id]) <= - threshold:
                del modified_strength[second_node.id]
                second_node = find_causal_node(modified_strength, root_node, Nodes_map)
            inference += f" as {par_name_map[second_node.id]} rose by {CPGR(transformed_df[second_node.id])} but {par_name_map[first_node.id]} fell by {first_node_CPGR}"
    else:
        inference += f"{root_par_name} fell by {str(abs(root_node_CPGR))}% YoY to reach {curr_level} {unit} for {curr_period}"
        if causal_node_CPGR < 0:
            inference += f" due to a {str(abs(causal_node_CPGR))}% decline in {par_name_map[causal_node.id]}"
        # else:
        #     inference += f"{str(causal_node_CPGR)}% rise in {par_name_map[causal_node.id]}"
    return inference
    # print(inference)

def report_graphs(ind_report, player_id, date, db_conn, db_session):
    ind_id = ind_report.industry_id
    pages = ind_report.pages
    df_rows = []
    for page_no, page_graphs  in pages.items():
        for Parent_graph, Graph_Object in page_graphs.items():
            Sub_graphs = Graph_Object.sub_graphs
            for sub_graph_name, graph_info in Sub_graphs.items():
                if (ind_report.tot_player == player_id) and (sub_graph_name == "Platforms"):
                    print(graph_info)
                    inference = Platform_analysis(graph_info, ind_report, date, db_conn)
                elif sub_graph_name == "Platforms":
                    continue
                else:
                    try:
                        inference = causal_analysis(graph_info, player_id, date, db_conn)
                    except KeyError as e:
                        print("Data Absent :", e.args[0])
                        continue
                root_parameter = graph_info["root parameter"]
                cols_dict = {"Industry_id": ind_id, "Player_id": player_id, "start_date": str(date), "Page_no": page_no, "Parent_graph": Parent_graph,
                             "Sub_graph": sub_graph_name, "root_parameter": root_parameter, "Inference": inference}
                df_rows.append(cols_dict)

    data_df = pd.DataFrame(df_rows)
    cur = db_conn.connection.cursor()
    cur.execute(f"delete from report_inference where Player_id = {player_id} and start_date = '{str(date)}';")
    # db_conn.connection.commit()
    data_df.to_sql(name = "report_inference", con = db_conn, if_exists = "append", index= False)
    db_conn.connection.commit()
    db_session.commit()


def causal_analysis(graph_info, player_id, date, db_conn):
    root_parameter = graph_info["root parameter"]
    linkage_tree = graph_info["linkage tree"]
    # print(root_parameter, linkage_tree)
    if linkage_tree:
        parameter_list = []
        Nodes_map = {}

        for target_id, sub_tree in linkage_tree.items():
            parameter_list.append(target_id)
            Nodes_map[target_id] = Node(target_id)
            for node_pairs in sub_tree:
                child_parameter = node_pairs[0]
                parameter_list.append(child_parameter)
                Nodes_map[child_parameter] = Node(child_parameter)
                Nodes_map[target_id].add_child(Nodes_map[child_parameter])
        # print(Nodes_map)
        root_node = Nodes_map[root_parameter]
        transformed_df, par_df = fetch_data(player_id, parameter_list, date, db_conn)
        causal_node, modified_strength = get_causal_node(linkage_tree, transformed_df, root_node, Nodes_map)
        inference = causal_inference(transformed_df, Nodes_map, modified_strength, root_node, causal_node, par_df)
    else:
        transformed_df, par_df = fetch_data(player_id, [root_parameter], date, db_conn)    
        inference = simple_inference(transformed_df, root_parameter, par_df)
    return inference

def Platform_analysis(grpah_info, ind_report, date, db_conn):
    tot_player = ind_report.tot_player
    Players = ind_report.players
    root_parameter = grpah_info["root parameter"]
    all_players = Players.copy()
    all_players.append(tot_player)
    # defining linkage tree & nodal map for players
    linkage_tree = {tot_player: []}
    Nodes_map = {}
    Nodes_map[tot_player] = Node(tot_player)
    root_node = Nodes_map[tot_player]
    for player in Players: 
        linkage_tree[tot_player].append((player, tot_player))
        Nodes_map[player] = Node(player)
        root_node.add_child(Nodes_map[player])
        
    transformed_df, par_df, player_df = fetch_pf_data(all_players, [root_parameter], date, db_conn)
    print(transformed_df.columns)
    pl_name_dict = player_df.set_index("player_id")["player_name"].to_dict()
    causal_node, modified_strength = get_causal_node(linkage_tree, transformed_df, root_node, Nodes_map)
    inference = Platforms_inference(transformed_df, Nodes_map, causal_node, par_df, all_players, pl_name_dict)

    return inference


# ### 1) Execute Preliminary Calculations for Sector


def Generate_report_insights(industry_id):
    database_name = db_settings['NAME']
    db_session, db_conn = get_db_connection(database_name)

    ind_reports = read_rep_structure()
    tot_player = ind_reports[str(industry_id)].tot_player

    try:
        Industry_aggregate = Prelim_calculation(industry_id)
        Industry_aggregate(tot_player, db_conn, db_session)
    except ValueError as e:
        print(str(e))
    # ### 2) Generate Report Inferences
    database_name = db_settings['NAME']
    db_session, db_conn = get_db_connection(database_name)

    # month, year = map(int, input("Enter Period in the format mm-yyyy: ").split("-"))
    curr_date = date.today()
    curr_month = curr_date.month
    curr_year = curr_date.year
    if curr_month == 1:
        year = curr_year - 1
        month = 12
    else:
        year = curr_year
        month = curr_month - 1
    for_date = date(year, month, 1)
    report_graphs(ind_reports[str(industry_id)], tot_player, for_date, db_conn, db_session)




