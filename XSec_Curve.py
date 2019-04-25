import arcpy, math

# xSecPoints = arcpy.GetParameterAsText(0)
# xSecStartID = arcpy.GetParameterAsText(1)
# xSecEndID= arcpy.GetParameterAsText(2)
# x_sec_center_points = arcpy.GetParameterAsText(3)

xSecPoints = r"E:\Trinity_River\Trinity_Cleanup\XsecTEST\T1_Transect_Points_Z_WSE.shp"
xSecStartID = 485
xSecEndID= 523
xSecCenterPoints = r"E:\Trinity_River\Trinity_Cleanup\XsecTEST\T1_Q2002.shp"
xSecLineLength = 200

xSecPointsStart = r'in_memory\ptsStart'
xSecPointsEnd = r'in_memory\ptsEnd'
startMaxAttributes = [0,0]
startMinAttributes =[999999,0]
endMaxAttributes = [0,0]
endMinAttributes =[999999,0]
clRowVal = []
xSecResultsTable = arcpy.CreateTable_management("in_memory", "xSecResultsTable")
xSecResults = r"in_memory\xsSecResults"

arcpy.Select_analysis(xSecPoints, xSecPointsStart, "ID = " + str(xSecStartID))
cursor = arcpy.da.SearchCursor(xSecPointsStart, ['POINT_X', 'POINT_Y'])
for row in cursor:
    if row[0] > startMaxAttributes[0]:
        startMaxAttributes = row
    if row[0] < startMinAttributes[0]:
        startMinAttributes = row

arcpy.Select_analysis(xSecPoints, xSecPointsEnd, "ID = " + str(xSecEndID))
cursor = arcpy.da.SearchCursor(xSecPointsEnd, ['POINT_X', 'POINT_Y'])
for row in cursor:
    if row[0] > endMaxAttributes[0]:
        endMaxAttributes = row
    if row[0] < endMinAttributes[0]:
        endMinAttributes = row

xa, ya = startMaxAttributes
xb, yb = startMinAttributes
xc, yc = endMaxAttributes
xd, yd = endMinAttributes

intersectX = ((yc-xc*((yd-yc)/(xd-xc)))-(ya-xa*((yb-ya)/(xb-xa))))/(((yb-ya)/(xb-xa))-((yd-yc)/(xd-xc)))
intersectY = ya-xa*((yb-ya)/(xb-xa))+intersectX*((yb-ya)/(xb-xa))

intersect = [intersectX, intersectY]

##DEBUG##
point = arcpy.Point(intersectX, intersectY)
pointGeometry = arcpy.PointGeometry(point)
arcpy.CopyFeatures_management(pointGeometry, "test2")
##DEBUG##

with arcpy.da.SearchCursor(xSecCenterPoints, ["ID", "SHAPE@X", "SHAPE@Y"], "ID >= " + str(xSecStartID) + "AND ID <= " + str(xSecEndID)) as cursor:
    for row in cursor:
        m = ((intersectY - row[2]) / (intersectX - row[1]))
        c = 1 / math.sqrt(1 + math.pow(m,2))
        s =  m / math.sqrt(1 + math.pow(m,2))
        clRowVal.append([row[0], intersectX, intersectY, row[1] + (xSecLineLength * c), row[2] + (xSecLineLength * s)])

arcpy.AddField_management(xSecResultsTable, "ID", "LONG")
arcpy.AddField_management(xSecResultsTable, "FROM_X", "DOUBLE")
arcpy.AddField_management(xSecResultsTable, "FROM_Y", "DOUBLE")
arcpy.AddField_management(xSecResultsTable, "TO_X", "DOUBLE")
arcpy.AddField_management(xSecResultsTable, "TO_Y", "DOUBLE")

fieldNameList = ["ID", "FROM_X", "FROM_Y", "TO_X", "TO_Y"]

cursor = arcpy.da.InsertCursor(xSecResultsTable, (fieldNameList))
for row in clRowVal:
    cursor.insertRow(row)

arcpy.XYToLine_management(xSecResultsTable,xSecResults,
                         "FROM_X","FROM_Y","TO_X",
                         "TO_Y","","",xSecPoints)
