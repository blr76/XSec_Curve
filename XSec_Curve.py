import arcpy, os

# xSecPoints = arcpy.GetParameterAsText(0)
# xSecStartID = arcpy.GetParameterAsText(1)
# xSecEndID= arcpy.GetParameterAsText(2)
# x_sec_center_points = arcpy.GetParameterAsText(3)

xSecPoints = r"E:\Trinity_River\Trinity_Cleanup\XsecTEST\T1_Transect_Points_Z_WSE.shp"
xSecStartID = 507
xSecEndID= 499
xSecCenterPoints = r"E:\Trinity_River\Trinity_Cleanup\XsecTEST\T1_Q2002.shp"

sumStatsTblStartID = r'in_memory\statTblStart'
sumStatsTblEndID = r'in_memory\statTblEnd'
xSecPointsStart = r'in_memory\ptsStart'
xSecPointsEnd = r'in_memory\ptsEnd'

arcpy.Select_analysis(xSecPoints, xSecPointsStart, "ID = " + str(xSecStartID))
arcpy.Select_analysis(xSecPoints, xSecPointsEnd, "ID = " + str(xSecEndID))

# arcpy.Statistics_analysis(xSecPointsStart, sumStatsTblStartID, [["POINT_X", "MAX"], ["POINT_X","MIN"]], "FID")
# arcpy.Statistics_analysis(xSecPointsEnd, sumStatsTblEndID, [["POINT_X", "MAX"], ["POINT_X","MIN"]])


cursor = arcpy.da.SearchCursor(sumStatsTblStartID, ['MAX_POINT_X', 'MIN_POINT_X'])
for row in cursor:
    print(row)
