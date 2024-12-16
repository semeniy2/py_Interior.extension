# -*- coding: utf-8 -*-

from Autodesk.Revit.DB import (BuiltInCategory,
                               BuiltInParameter,
                               ElementId,
                               FilteredElementCollector,
                               ViewSection,
                               ViewPlan,
                               BoundingBoxXYZ,
                               ElementClassFilter,
                               SketchPlane,
                               XYZ,
                               Grid,
                               DatumExtentType,
                               Line,
                               )





sender  = __eventsender__
args    = __eventargs__

doc = args.GetDocument()

modified_el_ids     = args.GetModifiedElementIds()
deleted_el_ids      = args.GetDeletedElementIds()
new_el_ids          = args.GetAddedElementIds()

modified_el = [doc.GetElement(e_id) for e_id in modified_el_ids]


def check_el(dic_in): 

    if "Вид план, разрез" in dic_in:
        el = dic_in["Вид план, разрез"]
        if el.Category:
            if el.Category.Id in [ElementId(BuiltInCategory.OST_Views)]:
                if not el.IsTemplate:
                    if type(el) in (ViewPlan, ViewSection):
                        return True
        return False

    elif "Подрезка вида" in dic_in:
        el_in = dic_in["Подрезка вида"]
        if el_in.get_Parameter(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM):
            if el_in.get_Parameter(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM).AsValueString() == "DI_PD_Подрезка вида: подрезка вида":
                return True
        return False

def change_el(el_in): 

    el_in
    view = doc.GetElement(el_in.OwnerViewId)


    filter_1 = ElementClassFilter(SketchPlane)
    for i in view.GetDependentElements (filter_1):
        if doc.GetElement(i).Name == view.Name:
            sketch_plane = doc.GetElement(i).GetPlane()
            break
    
    if sketch_plane:
        

        masw = view.get_Parameter(BuiltInParameter.VIEW_SCALE).AsInteger()
        pos = el_in.Location.Point
        gor = el_in.LookupParameter('Length').AsDouble()
        ver = el_in.LookupParameter('Width').AsDouble()
        x_min = sketch_plane.Project(pos)[0].U - gor/2 - 4/304.8*masw - sketch_plane.Project(view.Origin)[0].U
        x_max = sketch_plane.Project(pos)[0].U + gor/2 + 4/304.8*masw - sketch_plane.Project(view.Origin)[0].U
        y_min = sketch_plane.Project(pos)[0].V - ver/2 - 4/304.8*masw - sketch_plane.Project(view.Origin)[0].V
        y_max = sketch_plane.Project(pos)[0].V + ver/2 + 4/304.8*masw - sketch_plane.Project(view.Origin)[0].V

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
    
        bbox.Min = XYZ(x1, y1, view.CropBox.Min.Z)
        bbox.Max = XYZ(x2, y2, view.CropBox.Max.Z)

        view.CropBox = bbox

        doc.Regenerate()

        ofset = 0.015*masw

        collector = FilteredElementCollector(doc, view.Id).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
        bbox = view.CropBox

        for i in collector:
            try:
                line_1 = i.GetCurvesInView(DatumExtentType.Model,view)[0]

                if (line_1.GetEndPoint(0).X - line_1.GetEndPoint(1).X) < 0.000001 and (line_1.GetEndPoint(0).Z - line_1.GetEndPoint(1).Z) < 0.000001:
                    line_new = Line.CreateBound(XYZ(line_1.GetEndPoint(0).X,bbox.Max.Y + ofset,line_1.GetEndPoint(0).Z), XYZ(line_1.GetEndPoint(1).X,bbox.Min.Y - ofset,line_1.GetEndPoint(1).Z))
                if (line_1.GetEndPoint(0).Y - line_1.GetEndPoint(1).Y) < 0.000001 and (line_1.GetEndPoint(0).Z - line_1.GetEndPoint(1).Z) < 0.000001:
                    line_new = Line.CreateBound(XYZ(bbox.Max.X+ofset,line_1.GetEndPoint(0).Y,line_1.GetEndPoint(0).Z), XYZ(bbox.Min.X-ofset,line_1.GetEndPoint(1).Y,line_1.GetEndPoint(1).Z))
                if (line_1.GetEndPoint(0).X - line_1.GetEndPoint(1).X) < 0.000001 and (line_1.GetEndPoint(0).Y - line_1.GetEndPoint(1).Y) < 0.000001:
                    line_new = Line.CreateBound(XYZ(line_1.GetEndPoint(0).X,line_1.GetEndPoint(0).Y,bbox.Min.Y+view.Origin.Z-ofset), \
                                                XYZ(line_1.GetEndPoint(1).X,line_1.GetEndPoint(1).Y,bbox.Max.Y+view.Origin.Z+ofset))
            except:pass

            try:i.SetCurveInView(DatumExtentType.ViewSpecific,view,line_new)
            except:pass

def view_crop(view): 

    collector = FilteredElementCollector(doc,view.Id).OfCategoryId(ElementId(BuiltInCategory.OST_DetailComponents)).WhereElementIsNotElementType().ToElements()
    el_out = []
    for i in collector:
        if i.get_Parameter(BuiltInParameter.ELEM_FAMILY_AND_TYPE_PARAM).AsValueString() == "View Crop: View Crop":
            el_out.append(i)
    return el_out





try:
    
    active_view = doc.ActiveView
    
    if active_view:

        if type(active_view) in [ViewPlan,ViewSection]:

            view_crop_el = view_crop(active_view)

            if view_crop_el:                                       

                for el in modified_el:

                    if el.Id == active_view.Id:                                                  

                        
                        masw = el.get_Parameter(BuiltInParameter.VIEW_SCALE).AsInteger()
                        for i in view_crop_el:
                        
                            i.LookupParameter("Scale").Set(masw)                            
                    
                    else:                                                   
                        for i in view_crop_el:
                            if i.Id == el.Id:       
                                change_el(i)                           


        
      
    
except:
    import traceback
    print(traceback.format_exc())
    pass




