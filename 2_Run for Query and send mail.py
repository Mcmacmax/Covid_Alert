import pandas as pd
import numpy as np
import datetime
import pyodbc as db
import os
import glob
from dateutil.relativedelta import relativedelta
from Parameter import B as B
from Parameter import writeB as WB
from Email import send_mail as email

start_datetime = datetime.datetime.now()
print (start_datetime,'execute')

today = datetime.datetime.now().strftime('%Y-%m-%d')
today2 = datetime.datetime.now().strftime('%d-%m-%Y')
Date = datetime.datetime.now() - relativedelta(days=1)
Tracedate = Date.strftime('%Y-%m-%d')
Tracedate2 = Date.strftime('%d-%m-%Y')
print(Tracedate)

########## DATA TO P'KAJORN #######
"""database connection ={SQL Server Native Client 11.0};"""
conn = db.connect('Driver={SQL Server Native Client 11.0};'
                    'Server=SBNDCBIPBST02;'	
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
####เพิ่มรหัสพี่ขจรและตัวเองเข้าไปก่อนส่ง#####
data_Out = data_Out.append({'employee_id': '11027745'}, ignore_index=True)
data_Out = data_Out.append({'employee_id': '70032204'}, ignore_index=True)
data_Out = data_Out.append({'employee_id': '70047231'}, ignore_index=True)
Output = r'./CovidAlert.xlsx'
data_Out.to_excel(Output,index=False)

################################################  STEP 6 ########################################################
#SEND EMAIL
email(Output,today2,Tracedate2)
print("Finish send Mail")

end_datetime = datetime.datetime.now()
print ('---Start---',start_datetime)
print('---complete---',end_datetime)
DIFFTIME = end_datetime - start_datetime 
DIFFTIMEMIN = DIFFTIME.total_seconds()
print('Time_use : ',round(DIFFTIMEMIN,2), ' Seconds')
#except:
    #print("NO TRACEABILITY")