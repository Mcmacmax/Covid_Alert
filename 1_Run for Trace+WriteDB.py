import pandas as pd
import numpy as np
import datetime
import pyodbc as db
import os
import glob
from dateutil.relativedelta import relativedelta
from Parameter import B as B
from Parameter import writeB as WB
from Log import log as log

start_datetime = datetime.datetime.now()
print (start_datetime,'execute')

today = datetime.datetime.now().strftime('%Y-%m-%d')
today2 = datetime.datetime.now().strftime('%d-%m-%Y')
Date = datetime.datetime.now() - relativedelta(days=0) #ข้อมูลคนเช็คอินวันไหน
Tracedate = Date.strftime('%Y-%m-%d')
Tracedate2 = Date.strftime('%d-%m-%Y')
print(Tracedate)

#จุดเสีย่งจาก DATABASE
"""database connection ={SQL Server Native Client 11.0};"""
conn = db.connect('Driver={SQL Server Native Client 11.0};'
                    'Server=SBNDCTSREMP;'	
                    'Database=SR_APP;'
                    'Trusted_Connection=yes;')
cursor = conn.cursor()
dfout = pd.DataFrame(columns=['place','daterisk_end','lat','lng','id'])
SQL = """ 
    declare @date date = cast((getdate()-6) as date)
	declare @today date = cast(getdate() as date)
    select 
    place
    ,daterisk_end
    ,daterisk
    ,lat
    ,lng
    ,p_name_t
    ,a_name_t
    ,t_name_t
    ,id
    ,category
    from [SR_APP].[dbo].[TB_SR_Covid_Risk_Location]
    where daterisk_end between @date and @today
    order by daterisk desc
""" 
cursor.commit()
#print(SQL)
cursor.execute(SQL)
data_Out = cursor.fetchall()
for row in data_Out:
    newrow= {'place':row[0],'daterisk_end':row[1],'lat':row[3],'lng':row[4],'id':row[8]}
    dfout = dfout.append(newrow, ignore_index=True)
data_In = dfout
print(data_In)

#try:
#B
#dfoutB = pd.DataFrame(columns=['Location_Name','TRACE_DATE','Location_Lat','Location_Long','EMPID','EMPID_LAT','EMPID_LONG','EMPID_CheckIn_Date'])
dfoutB = pd.DataFrame(columns=['TRACE_DATE','ID','Location_Name','daterisk_end','Location_Lat','Location_Long','EMPID','EMPID_LAT','EMPID_LONG','EMPID_CheckIn_Date','REF'])
Output_PathB = r'./Ouput'+str(today)+'.xlsx'
df_outB = B(dfoutB,data_In,Output_PathB,Tracedate)
print(df_outB)

###################Write B to SQL ################
df_WB = WB(df_outB)
print('Complte Write B to DATABASE')

'''
########## DATA TO P'KAJORN #######
"""database connection ={SQL Server Native Client 11.0};"""
conn = db.connect('Driver={SQL Server Native Client 11.0};'
                    'Server=SBNDCTSREMP;'	
                    'Database=TB_SR_Employee;'
                    'Trusted_Connection=yes;')
cursor = conn.cursor()
dfout1 = pd.DataFrame(columns=['employee_id'])

SQL = """ 
declare @date date = dateadd(day, -1, cast(getdate() as date))

SELECT distinct A.[EMPID],A.Location_Name
FROM [TB_SR_Employee].[dbo].[COVID_ALERT_Transaction] A
left join (select * from [TB_SR_Employee].[dbo].[COVID_ALERT_Transaction] where cast([EMPID_CheckIn_Date] as date) <> @date) B on A.REF = B.REF
where cast(A.[EMPID_CheckIn_Date] as date) = @date and B.[EMPID] is null 
""" 

cursor.commit()
#print(SQL)
cursor.execute(SQL)
data_Out = cursor.fetchall()
for row in data_Out:
    newrow= {'employee_id':row[0]}
    dfout1 = dfout1.append(newrow, ignore_index=True)
data_Out = dfout1
Output = r'./CovidAlert.xlsx'
data_Out.to_excel(Output,index=False)

################################################  STEP 6 ########################################################
#SEND EMAIL
email(Output,today2,Tracedate2)
print("Finish send Mail")
'''
end_datetime = datetime.datetime.now()
print ('---Start---',start_datetime)
print('---complete---',end_datetime)
DIFFTIME = end_datetime - start_datetime 
DIFFTIMEMIN = DIFFTIME.total_seconds()
print('Time_use : ',round(DIFFTIMEMIN,2), ' Seconds')

log()

#except:
    #print("NO TRACEABILITY")