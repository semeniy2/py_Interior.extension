# -*- coding: utf-8 -*-

__title__ = "View Crop"
__doc__ = """Set Two Boundary Points for View Crop
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

from pyrevit import revit, forms
import wpf, os, clr

clr.AddReference('System')
clr.AddReference('RevitAPI')

from System.Windows import Window

from Functions.my_functions import message_ui



doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument


def check_view (): # check if the curent view is not 3d
    view = doc.ActiveView
    if type(view) in [ViewPlan,ViewSection]:
        return True
    else:
        message_ui("To create a crop, select a view in the plan or section.")
        return False

def check_element (): # check if family in the project 
    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DetailComponents).OfClass(FamilySymbol).WhereElementIsElementType().ToElements()
    for i in collector:
        if i.Family.Name == "View Crop":
            return True
    message_ui('"View Crop" family is not loaded into the project')
    return False

def crop_view(): # Creating a view crop family using two points
    view_work =  doc.ActiveView

    view_work.get_Parameter(BuiltInParameter.VIEWER_CROP_REGION).Set(False)
    view_work.get_Parameter(BuiltInParameter.VIEWER_CROP_REGION_VISIBLE).Set(False)

    
    collector = FilteredElementCollector(doc).OwnedByView(view_work.Id).OfCategory(BuiltInCategory.OST_DetailComponents)
    del_el = []
    for i in collector:
        if i.Symbol.Family.Name == "View Crop": del_el.append(i.Id)
    for i in del_el:doc.Delete(i)
    
    doc.Regenerate()
    
    if not view_work.SketchPlane:

        filter_1 = ElementClassFilter(SketchPlane)
        sketch_plane = doc.GetElement(view_work.GetDependentElements (filter_1)[0]).GetPlane()
        view_work.SketchPlane = SketchPlane.Create(doc, sketch_plane)

    else:
        sketch_plane = view_work.SketchPlane.GetPlane()


    point1 = uidoc.Selection.PickPoint()
    point2 = uidoc.Selection.PickPoint()
    
    point_centr = XYZ((point1.X + point2.X)/2, (point1.Y + point2.Y)/2, (point1.Z + point2.Z)/2)


    collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_DetailComponents).OfClass(FamilySymbol).WhereElementIsElementType().ToElements()

    for i in collector:
        if i.Family.Name == "View Crop":
            f = i
            break
    
    
    instance = doc.Create.NewFamilyInstance(point_centr, f, view_work)

    
    x = abs(sketch_plane.Project(point1)[0].U - sketch_plane.Project(point2)[0].U)
    y = abs(sketch_plane.Project(point1)[0].V - sketch_plane.Project(point2)[0].V)
    masw = view_work.get_Parameter(BuiltInParameter.VIEW_SCALE).AsInteger()
    x_min = min(sketch_plane.Project(point1)[0].U, sketch_plane.Project(point2)[0].U) - sketch_plane.Project(view_work.Origin)[0].U - 4/304.8*masw
    x_max = max(sketch_plane.Project(point1)[0].U, sketch_plane.Project(point2)[0].U) - sketch_plane.Project(view_work.Origin)[0].U + 4/304.8*masw
    y_min = min(sketch_plane.Project(point1)[0].V, sketch_plane.Project(point2)[0].V) - sketch_plane.Project(view_work.Origin)[0].V - 4/304.8*masw
    y_max = max(sketch_plane.Project(point1)[0].V, sketch_plane.Project(point2)[0].V) - sketch_plane.Project(view_work.Origin)[0].V + 4/304.8*masw

    if x*304.8 >= 9.9: instance.LookupParameter('Length').Set(x)
    if y*304.8 >= 9.9: instance.LookupParameter('Width').Set(y)
    
    instance.LookupParameter('Scale').Set(masw) 
    view_work.get_Parameter(BuiltInParameter.VIEWER_CROP_REGION).Set(True)
    view_work.get_Parameter(BuiltInParameter.VIEWER_CROP_REGION_VISIBLE).Set(False)
    bbox = BoundingBoxXYZ()
    x1 = x_min
    x2 = x_max
    y1 = y_min
    y2 = y_max 
  
 
    if sketch_plane.YVec.Z == -1:
        y1 = -y_max
        y2 = -y_min
        x1 = -x_max
        x2 = -x_min
    if sketch_plane.YVec.Y == -1:
        y1 = -y_max
        y2 = -y_min
    bbox.Min = XYZ(x1, y1, view_work.CropBox.Min.Z)
    bbox.Max = XYZ(x2, y2, view_work.CropBox.Max.Z)
    view_work.CropBox = bbox

    doc.Regenerate()
    
def mm(mm_in):
    """
    - Преобразуем миилиметры в дюймы
    """
    return mm_in/304.8

def cut_grid(): # Trimming grids to fit within the view boundaries
    
    view_work = doc.ActiveView
    ofset = mm(0.1)*view_work.get_Parameter(BuiltInParameter.VIEW_SCALE).AsInteger()
    
    collector = FilteredElementCollector(doc, view_work.Id).OfCategory(BuiltInCategory.OST_Grids).OfClass(Grid).WhereElementIsNotElementType()
    bbox = view_work.CropBox
    
    for i in collector:
        try:
            line_1 = i.GetCurvesInView(DatumExtentType.Model,view_work)[0]

            if (line_1.GetEndPoint(0).X - line_1.GetEndPoint(1).X) < 0.000001 and (line_1.GetEndPoint(0).Z - line_1.GetEndPoint(1).Z) < 0.000001:
                line_new = Line.CreateBound(XYZ(line_1.GetEndPoint(0).X,bbox.Max.Y + ofset,line_1.GetEndPoint(0).Z), XYZ(line_1.GetEndPoint(1).X,bbox.Min.Y - ofset,line_1.GetEndPoint(1).Z))
            if (line_1.GetEndPoint(0).Y - line_1.GetEndPoint(1).Y) < 0.000001 and (line_1.GetEndPoint(0).Z - line_1.GetEndPoint(1).Z) < 0.000001:
                line_new = Line.CreateBound(XYZ(bbox.Max.X+ofset,line_1.GetEndPoint(0).Y,line_1.GetEndPoint(0).Z), XYZ(bbox.Min.X-ofset,line_1.GetEndPoint(1).Y,line_1.GetEndPoint(1).Z))
            if (line_1.GetEndPoint(0).X - line_1.GetEndPoint(1).X) < 0.000001 and (line_1.GetEndPoint(0).Y - line_1.GetEndPoint(1).Y) < 0.000001:
                line_new = Line.CreateBound(XYZ(line_1.GetEndPoint(0).X,line_1.GetEndPoint(0).Y,bbox.Min.Y+view_work.Origin.Z-ofset), \
                                            XYZ(line_1.GetEndPoint(1).X,line_1.GetEndPoint(1).Y,bbox.Max.Y+view_work.Origin.Z+ofset))
            
        except:
            pass

        try:
            i.SetCurveInView(DatumExtentType.ViewSpecific,view_work,line_new)
        except:
            pass


transaction = Transaction(doc, "View Crop")
try:
    transaction.Start()


    if check_view():
        if check_element():
            
            crop_view()
            cut_grid()
    
   

    transaction.Commit()

except Exception as e:

    transaction.RollBack()
    print (e)