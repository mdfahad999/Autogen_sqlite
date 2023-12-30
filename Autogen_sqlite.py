
import sqlite3


class SQLiteDB:
    def __init__(self, db_file=None):
        self.conn=None
        self.cursor = None
        if db_file:
            self.connect_with_db_file(db_file)

    def __enter__(self):
        return self

    def __exit__(self,exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def connect_with_db_file(self, db_file):
        self.conn = sqlite3.connect(db_file)
        self.cursor =self.conn.cursor()


    def connect_with_url(self, url):
        raise NotImplementedError("SQLite does not support connection via URL")

    def upsert(self, table_name, _dict):
        columns =', '.join(_dict.keys())
        placeholder =', '.join('?'*len(_dict))
        sql=f"INSERT OR REPLACE INTO {table_name} {{columns}}  VALUES {{placeholder}}"
        self.cursor.execute(sql, list(_dict.values()))
        self.conn.commit()

    def delete(self, table_name,_id):
        sql=f'DELETE FROM {table_name} WHERE id = ?'
        self.cursor.execute(sql,(_id))
        self.conn.commit()

    def get(self, table_name, _id):
        sql =f'SELECT * FROM {table_name} WHERE id =?'
        self.cursor.execute(sql,(_id))
        return self.cursor.fetchone()

    def get_all(self, table_name):
        sql = 'SELECT * FORM {}'.format(table_name)
        return self.cursor.execute(sql).fetchall()

    def run_sql(self, sql):
        print('\n\n----- ENtered into the run_sql --------\n\n')
        return self.cursor.execute(sql).fetchall()

    def get_table_definitions(self, table_name):
        sql =f"SELECT sql FROM sqlite_master  WHERE type='table'  AND name=? " 
        self.cursor.execute(sql,(table_name,))
        return self.cursor.fetchone()[0]
    
    def get_all_table_names(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type= 'table'")
        return [row[0]  for row in self.cursor.fetchall()]
    
    def get_table_definitions_for_prompt(self):
        table_names = self.get_all_table_names()
        table_definitions = [self.get_table_definitions(table_name) for table_name in table_names]
        return '\n'.join(table_definitions)
    
#pwd

import os
import sys
from typing import Any , Dict
import openai

os.environ['OPENAI_API_TYPE'] = 'azure'
os.environ['OPENAI_API_VERSION'] = '2023-03-15-preview'
os.environ['OPENAI_API_BASE'] = 'https://###################'
os.environ['OPENAI_API_KEY'] = '..........'


assert os.environ.get('OPENAI_API_KEY')

openai.api_key = os.environ.get('OPENAI_API_KEY')

def safe_get(data, dot_chained_keys):
    keys =dot_chained_keys.split('.')
    for key in keys:
        try:
            if isinstance(data, list):
                data = data[int(key)]
            else:
                data = data[key]
        except(KeyError, TypeError, IndexError):
            return None
    return data

def response_parser(response:Dict[str, Any]):
    return safe_get(response,'choices.0.message.content')

def llm(prompt, model ='gpt-4-16k'):
    response =openai.ChatCompletion.create(model=model, engine ='gpt416k', temperature=0, messages=[{'role':'user','content':prompt}])

    return response_parser(response)


def add_cap_ref(prompt:str, prompt_suffix, cap_ref, cap_ref_content):

    new_prompt =f"""{prompt} {prompt_suffix} \n\n {cap_ref} \n\n {cap_ref_content}"""
    return new_prompt


####Here is the new cell

db_path ='db/DataBase21345589.db'
prompt ='what is the total budget?'

SQLITE_TABLE_DEFINITIONS_CAP_REF = 'TABLE_DEFINITIONS'
SQLITE_SQL_QUERY_CAP_REF = 'SQL_QUERY'

TABLE_FORMAT_CAP_REF ='TABLE_RESPONSE_FORMAT'

SQL_DELIMETER='SQLite'

with SQLiteDB()  as db:
    db.connect_with_db_file(db_path)
    Masked =db.get_all('Masked')
    print('Masked Table', db.get_table_definitions('Masked'))

    table_definitions = db.get_table_definitions_for_prompt()

    prompt = add_cap_ref(prompt, f"USE these {SQLITE_TABLE_DEFINITIONS_CAP_REF}  to satisfy  the database query",SQLITE_TABLE_DEFINITIONS_CAP_REF,table_definitions )
    prompt = add_cap_ref(prompt,f"Respond in this format {TABLE_FORMAT_CAP_REF}",TABLE_FORMAT_CAP_REF,f"<explanation of the sql query>{SQL_DELIMETER}<sql query exclusively as  raw text>")

    prompt_response = llm(prompt)

    print('\n\n---------\n\n')
    print('SQL QUERY:', prompt_response)

    print('REFINED QUERY \n\n ', prompt_response.split(SQL_DELIMETER)[1].strip('<').strip('>'))

    result = db.run_sql(prompt_response.split(SQL_DELIMETER)[1].strip('<').strip('>'))

    print(result)


###########################################################################################
#!pip install pyautogen~=0.1.0
# 
openai.api_key =os.environ['OPENAI_API_KEY']
openai.api_base =os.environ['OPENAI_API_BASE']
openai.api_version =os.environ['OPENAI_API_VERSION']
openai.api_type =os.environ['OPENAI_API_TYPE']

config_list =[
    {
      "model" : "GPT4-32K-Digital",
      "api_key": os.environ.get("OPENAI_API_KEY"),
      "api_type":"azure"  ,
      "api_base": os.environ['OPENAI_API_BASE'],
      "api_version":os.environ['OPENAI_API_VERSION']
    }
]

config_list

import autogen

import json

db_path ='db/DataBase21345589.db'

prompt ='what is the total budget?'


SQLITE_TABLE_DEFINITIONS_CAP_REF = 'TABLE_DEFINITIONS'
SQLITE_SQL_QUERY_CAP_REF = 'SQL_QUERY'

TABLE_FORMAT_CAP_REF ='TABLE_RESPONSE_FORMAT'

SQL_DELIMETER='SQLite'


def write_file(content):
    print('\n\n----Entered into write_file -------\n\n')
    my_object = {"Result":content}

    with open('output.json','w') as f:
        json.dumps(my_object, f)

with SQLiteDB()  as db:
    db.connect_with_db_file(db_path)
    Masked =db.get_all('Masked')
    print('Masked Table', db.get_table_definitions('Masked'))

    table_definitions = db.get_table_definitions_for_prompt()

    prompt = add_cap_ref(prompt, f"USE these {SQLITE_TABLE_DEFINITIONS_CAP_REF}  to satisfy  the database query",SQLITE_TABLE_DEFINITIONS_CAP_REF,table_definitions )
    
    
    gpt4_config = {
        #"seed": 42,  # change the seed for different trials
        "use_cache":False,
        "temperature": 0,
        "config_list": config_list,
        "request_timeout": 120,
        "functions":[
            {
                "name":"run_sql",
                "description":"Run a SQL QUERY against the sqlite database",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "sql":{
                            "type":"string",
                            "description":"The SQL query to run",
                        }
                    },
                    "required":["sql"],
                },
            },
            {
                "name":"write_file",
                "description":"use  to write a reponse to file on the filesystem",
                "parameters":{
                    "type":"object",
                    "properties":{
                        "content":{
                            "type":"string",
                            "description":"The response of the file to write",
                        }
                    },
                    "required":["reponse"],
                },
            }
    

        ]
    }

    function_map_write_file ={'write_file':write_file}

    function_map ={'run_sql':db.run_sql,'write_file':write_file}


    def is_termination_msg(content):

        have_content =content.get('content',None) is not None
        if have_content and 'APPROVED' in content['content']:
            return True
        return False
    
    COMPLETE_PROMPT ='If everything looks good , respond with APPROVED'

    USER_PROXY_PROMPT ="""A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin. """ +COMPLETE_PROMPT

    DATA_ENGINEER_PROMPT ="As a Data Engineer  . YOu follow an approved plan. Generate the initial SQL based on the requirements provided. Send it to the Sr Data Analyst  for review"+COMPLETE_PROMPT


    SR_DATA_ANALYST_PROMPT ='Sr Data Analyst. You follow an approved plan. You rin the correct syntax sqllite sql query, generate the response , and send it to the product Manager for final results.'+COMPLETE_PROMPT

    PRODUCT_MANAGER_PROMPT ="Product Manager, validate the response to make sure it's correct and save responseby using write_file function"+COMPLETE_PROMPT


    user_proxy = autogen.UserProxyAgent(
    name="Admin",
    system_message=USER_PROXY_PROMPT,
    code_execution_config=False,
    human_input_mode ='NEVER',
    is_termination_msg =is_termination_msg
    )

    engineer = autogen.AssistantAgent(
        name="Engineer",
        llm_config=gpt4_config,
        system_message=DATA_ENGINEER_PROMPT,
        human_input_mode ='NEVER',
        is_termination_msg =is_termination_msg

    )
    sr_data_analyst = autogen.AssistantAgent(
        name="Sr_Data_Analyst",
        llm_config=gpt4_config,
        system_message=SR_DATA_ANALYST_PROMPT,
        human_input_mode ='NEVER',
        is_termination_msg =is_termination_msg,
        function_map=function_map

    )
    product_manager= autogen.AssistantAgent(
        name="Product_manager",
        system_message=PRODUCT_MANAGER_PROMPT,
        llm_config=gpt4_config,
        human_input_mode ='NEVER',
        function_map=function_map,
        is_termination_msg =is_termination_msg
    )
    
    groupchat = autogen.GroupChat(agents=[user_proxy, engineer, sr_data_analyst, product_manager], messages=[], max_round=50)
    manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=gpt4_config)


    result =user_proxy.initiate_chat(manager, message=prompt)

