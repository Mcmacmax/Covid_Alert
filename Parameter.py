import pandas as pd
import numpy as np
import datetime
import pyodbc as db
import os
import glob
from dateutil.relativedelta import relativedelta

def B(dfoutB,data_In,Output_PathB,Tracedate):
    count = 0
    for v in data_In.values:
        Location_Name =v[0]
        #datefrom1 = v[1]
        #dateto1 = v[1]
        datefrom1 = Tracedate
        dateto1 = Tracedate
        daterisk_end = v[1]
        FROM_LAT1 = v[2]
        FROM_LONG1 = v[3]
        ID=v[4]
        print(Location_Name)
        dfout = pd.DataFrame(columns=['TRACE_DATE','ID','Location_Name','daterisk_end','Location_Lat','Location_Long','EMPID','EMPID_LAT','EMPID_LONG','EMPID_CheckIn_Date','REF'])
        ##################################################### 1. Del Data and write from data frame
        """ database connection ={SQL Server Native Client 11.0};"""
        conn = db.connect('Driver={SQL Server Native Client 11.0};'
                            'Server=SBNDCTSREMP;'
                            'Database=SR_APP;'
                            'Trusted_Connection=yes;')
        cursor = conn.cursor()
        SQL =  """
        /* Declare Tracking Date Preriod */

        --------------INPUT FILED---------------
        declare @Location_Name nvarchar(255) =N'"""+str(Location_Name)+"""'
        declare @dateFrom date = '"""+str(datefrom1)+"""'
        declare @dateTo date = '"""+str(dateto1)+"""' 
        declare @LatIn float  = '"""+str(FROM_LAT1)+"""'
        declare @longIn float = '"""+str(FROM_LONG1)+"""'
        declare @daterisk_end date = '"""+str(daterisk_end)+"""'
        declare @ID nvarchar(255) ='"""+str(ID)+"""'


        --------------AUTO CALCUCATE-------------------
        declare @Lat float =   cast(cast(@LatIn as nvarchar) as float)-0.00085
        declare @Lat1 float =  cast(cast(@LatIn as nvarchar) as float)+0.00085
        declare @long float  = cast(cast(@LongIn as nvarchar)as float)-0.00085
        declare @long1 float = cast(cast(@LongIn as nvarchar)as float)+0.00085
        ----------------------------------------------

        /* List All Check-In Transection in Risk Area */

        select 

        @Location_Name Location_Name
        ,cast(getdate() as smalldatetime) Trace_datetime
        ,@Lat Location_Lat
        ,@long Location_Long
        ,MN.EmployeeId TO_EMP
        ,MN.latitude TO_LAT
        ,MN.longitude TO_LONG
        ,MN.CheckinDatetime TO_LOCATIONDATETIME
        ,@daterisk_end daterisk_end
        ,@ID ID
        ,concat(MN.EmployeeId,'_',@ID) REF
        from ( /* QR check in*/
        SELECT TS.[EmployeeId] 
        ,cast(TS.CreatedDateTime as date) [CheckinDate]
        ,TS.CreatedDateTime [CheckinDatetime]
        ,Loc.LocationNameTH 
        ,TS.ShopName
        ,coalesce(Loc.LocationNameTH, case when TS.ShopName = '' then NULL else TS.ShopName end ) LocationName
        ,[UserLat] as [latitude] 
        ,[UserLong] as [longitude] 
        FROM [SR_APP].[dbo].[TB_QR_TimeStamp] TS
        left join [SR_APP].[dbo].[TB_QR_Location] Loc on Loc.LocationId = TS.LocationId
        where cast(TS.CreatedDateTime as date) between @dateFrom and @dateTo
        and cast([UserLat] as float) between @lat and @lat1
        and cast([UserLong] as float) between @long and @long1
        
        union /* PG check in*/
        select  A.[EmployeeId]
        ,cast(A.[CreatedDateTime] as date) as [CheckinDate]
        ,A.[CreatedDateTime] as [CheckinDatetime] 
        ,A.[ShopName] [LocationNameTH]
        ,cast(A.[ShopId] as nvarchar(20)) ShopName
        ,A.[ShopName] [LocationName]
        ,[UserLat] as [latitude] 
        ,[UserLong] as [longitude] 
        from [SR_APP].[dbo].[TB_Checkin_PG] A
        where cast(A.[CreatedDateTime] as date) between @dateFrom and @dateTo
        and cast(A.[UserLat] as float) between @lat and @lat1
        and cast(A.[UserLong] as float) between @long and @long1
        
        union /* Bev App Log */
			
		select  [employee_id]
		,cast([create_date] as date) as [CheckinDate]
		,[create_date] as [CheckinDatetime] 
		,' ' [LocationNameTH]
		,' ' ShopName
		,' ' [LocationName]
		,[latitude] as [latitude] 
		,[longitude] as [longitude] 
		from [SR_APP].[dbo].[TB_SR_Covid_location] 
		where cast([create_date] as date) between @dateFrom and @dateTo
		and cast([latitude] as float) between @lat and @lat1
		and cast([longitude] as float) between @long and @long1

        ) MN
        """
        #print(SQL)
        cursor.execute(SQL)
        data_Out = cursor.fetchall()
        for row in data_Out:
            newrow= {'TRACE_DATE':row[1],'ID':row[9],'Location_Name':row[0],'daterisk_end':row[8],'Location_Lat':row[2],'Location_Long':row[3],'EMPID':row[4],'EMPID_LAT':row[5],'EMPID_LONG':row[6],'EMPID_CheckIn_Date':row[7],'REF':row[10]}
            dfout = dfout.append(newrow, ignore_index=True)
        #print('B Complete ===>> ',count,' : ')
        #Output_Path = r'./'+str(Location_Name)+'.xlsx'
        dfoutB = dfoutB.append(dfout,ignore_index=True)
        #dfoutB.to_excel(Output_Path,index=False)
        #print(dfoutB)
    dfoutB.sort_values(by=['Location_Name'])
    dfoutB.to_excel(Output_PathB,index=False)
    cursor.commit()
    return(dfoutB)

def writeB(df_outB):
    dfobj = pd.DataFrame(df_outB)
    df_write = dfobj.replace(np.nan,0)
    ##################################################### 1. Del Data and write from data frame
    #start_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #print ('DATE',start_datetime)
    """ database connection ={SQL Server Native Client 11.0};"""
    conn = db.connect('Driver={SQL Server Native Client 11.0};'
                        'Server=SBNDCTSREMP;'
                        'Database=TB_SR_Employee;'
                        'Trusted_Connection=yes;')
    cursor = conn.cursor()
    ####sql_del ="delete FROM [TB_SR_Employee].[dbo].[TRACE_EMPLOYEE]"
    ####cursor.execute(sql_del)
    for index, row in df_write.iterrows():
        print(row)
        cursor.execute("""INSERT INTO TB_SR_Employee.dbo.COVID_ALERT_Transaction([TRACE_DATE],[ID],[Location_Name],[daterisk_end],[Location_Lat],[Location_Long],[EMPID],[EMPID_LAT],[EMPID_LONG],[EMPID_CheckIn_Date],[REF]) 
        values(N'%s',N'%s',N'%s',N'%s','%f','%f',N'%s',N'%s',N'%s',N'%s',N'%s')"""%\
            (row[0].strftime('%Y-%m-%d %H:%M:%S'),row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9].strftime('%Y-%m-%d %H:%M:%S'),row[10])
        )   
    cursor.commit()