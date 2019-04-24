import arcpy, math

# xSecPoints = arcpy.GetParameterAsText(0)
# xSecStartID = arcpy.GetParameterAsText(1)
# xSecEndID= arcpy.GetParameterAsText(2)
# x_sec_center_points = arcpy.GetParameterAsText(3)

xSecPoints = r"E:\Trinity_River\Trinity_Cleanup\XsecTEST\T1_Transect_Points_Z_WSE.shp"
xSecStartID = 485
xSecEndID= 523
xSecCenterPoints = r"E:\Trinity_River\Trinity_Cleanup\XsecTEST\T1_Q2002.shp"

xSecPointsStart = r'in_memory\ptsStart'
xSecPointsEnd = r'in_memory\ptsEnd'
startMaxAttributes = [0,0]
startMinAttributes =[999999,0]
endMaxAttributes = [0,0]
endMinAttributes =[999999,0]

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
point = arcpy.Point(intersectX, intersectY)

pointGeometry = arcpy.PointGeometry(point)
arcpy.CopyFeatures_management(pointGeometry, "test2")

clRowVal = []

with arcpy.da.SearchCursor(xSecCenterPoints, ["SHAPE@X", "SHAPE@Y","ID"], "ID >= " + str(xSecStartID) + "AND ID <= " + str(xSecEndID)) as cursor:
    for row in cursor:
        clRowVal.append([row[0],row[1],row[2]])

for row in clRowVal:
    row.append((intersectY-row[1])/(intersectX-row[0]))
