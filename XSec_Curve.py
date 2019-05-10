import arcpy, math

try:
    arcpy.AddMessage("Loading Data...")
    xSecPoints = arcpy.GetParameterAsText(0)
    xSecStartID = arcpy.GetParameterAsText(1)
    xSecEndID= arcpy.GetParameterAsText(2)
    xSecCenterPoints = arcpy.GetParameterAsText(3)
    xSecLineLength = float(arcpy.GetParameterAsText(4))
    deleteAndAppend = str(arcpy.GetParameterAsText(5))
    newPointXSecOut = arcpy.GetParameterAsText(6)

    if(deleteAndAppend == "false" and newPointXSecOut == ""):
    	arcpy.AddError('No Output Specified')
        raise

    if(xSecEndID<xSecStartID):
        temp = xSecStartID
        xSecStartID = xSecEndID
        xSecEndID = temp
        del temp

    xSecPointsStart = r'in_memory\ptsStart'
    xSecPointsEnd = r'in_memory\ptsEnd'
    startMaxAttributes = [0,0,0]
    startMinAttributes =[999999,0,0]
    endMaxAttributes = [0,0,0]
    endMinAttributes =[999999,0,0]
    clRowVal = []
    xSecResultsTable = arcpy.CreateTable_management("in_memory", "xSecResultsTable")
    xSecLineResults = r"in_memory\xsSecResults"
    newXSecPoints = r"in_memory\newXSecPoints"


    arcpy.AddMessage("Selecting cross sections...")
    arcpy.Select_analysis(xSecPoints, xSecPointsStart, "ID = " + str(xSecStartID))
    cursor = arcpy.da.SearchCursor(xSecPointsStart, ['SHAPE@X', 'SHAPE@Y', 'OID@'])
    for row in cursor:
        if row[0] > startMaxAttributes[0]:
            startMaxAttributes = row
        if row[0] < startMinAttributes[0]:
            startMinAttributes = row

    arcpy.Select_analysis(xSecPoints, xSecPointsEnd, "ID = " + str(xSecEndID))
    cursor = arcpy.da.SearchCursor(xSecPointsEnd, ['SHAPE@X', 'SHAPE@Y', 'OID@'])
    for row in cursor:
        if row[0] > endMaxAttributes[0]:
            endMaxAttributes = row
        if row[0] < endMinAttributes[0]:
            endMinAttributes = row

    xa, ya, trash = startMaxAttributes
    xb, yb, trash = startMinAttributes
    xc, yc, trash = endMaxAttributes
    xd, yd, trash = endMinAttributes
    del trash

    arcpy.AddMessage("Doing math...")
    intersectX = ((yc-xc*((yd-yc)/(xd-xc)))-(ya-xa*((yb-ya)/(xb-xa))))/(((yb-ya)/(xb-xa))-((yd-yc)/(xd-xc)))
    intersectY = ya-xa*((yb-ya)/(xb-xa))+intersectX*((yb-ya)/(xb-xa))

    intersect = [intersectX, intersectY]

    with arcpy.da.SearchCursor(xSecCenterPoints, ["ID", "SHAPE@X", "SHAPE@Y"], "ID >= " + str(xSecStartID) + "AND ID <= " + str(xSecEndID)) as cursor:
        arcpy.AddMessage("Casting Lines...")
        for row in cursor:
            m = ((intersectY - row[2]) / (intersectX - row[1]))
            c = 1 / math.sqrt(1 + math.pow(m,2))
            s =  m / math.sqrt(1 + math.pow(m,2))
            if(row[1] > intersectX):
                clRowVal.append([row[0], intersectX, intersectY, row[1] + (xSecLineLength * c), row[2] + (xSecLineLength * s),m,c,s])
            else:
                clRowVal.append([row[0], intersectX, intersectY, row[1] - (xSecLineLength * c), row[2] - (xSecLineLength * s),m,c,s])


    arcpy.AddField_management(xSecResultsTable, "ID", "LONG")
    arcpy.AddField_management(xSecResultsTable, "FROM_X", "DOUBLE")
    arcpy.AddField_management(xSecResultsTable, "FROM_Y", "DOUBLE")
    arcpy.AddField_management(xSecResultsTable, "TO_X", "DOUBLE")
    arcpy.AddField_management(xSecResultsTable, "TO_Y", "DOUBLE")
    arcpy.AddField_management(xSecResultsTable, "m", "DOUBLE")
    arcpy.AddField_management(xSecResultsTable, "c", "DOUBLE")
    arcpy.AddField_management(xSecResultsTable, "s", "DOUBLE")

    fieldNameList = ["ID", "FROM_X", "FROM_Y", "TO_X", "TO_Y", "m","c","s"]

    cursor = arcpy.da.InsertCursor(xSecResultsTable, (fieldNameList))
    for row in clRowVal:
        cursor.insertRow(row)

    arcpy.XYToLine_management(xSecResultsTable,xSecLineResults,
                             "FROM_X","FROM_Y","TO_X",
                             "TO_Y","","ID",xSecPoints)

    arcpy.AddMessage("Generating Points...")
    arcpy.GeneratePointsAlongLines_management(xSecLineResults, newXSecPoints, 'DISTANCE', '1 meters')

    if(deleteAndAppend == "true"):
        arcpy.AddMessage("Deleting and Appending...")
        with arcpy.da.UpdateCursor(xSecPoints, "ID", "ID >= " +str(xSecStartID)+" AND ID <= " + str(xSecEndID)) as cursor:
            for row in cursor:
                cursor.deleteRow()
        arcpy.Append_management(newXSecPoints,xSecPoints, 'NO_TEST')
    if(newPointXSecOut):
            arcpy.AddMessage("Copying features to " + newPointXSecOut)
            arcpy.CopyFeatures_management(newXSecPoints, newPointXSecOut);

    arcpy.RefreshActiveView()

except:
    print(arcpy.GetMessages(2))
