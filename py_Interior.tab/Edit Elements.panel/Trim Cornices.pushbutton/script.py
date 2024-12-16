# -*- coding: utf-8 -*-

__title__ = "Trim Cornices"
__doc__ = """Select Corniсes to trim
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *


import  clr
import math

clr.AddReference('System')
clr.AddReference('RevitAPI')


import clr

from Functions.my_functions import message_ui



doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument



def trim_cornices(el_in):
    cornices_normal = []
    cornices_flip = []
    for i in el_in:
        if i.FacingFlipped:
            cornices_flip.append(i)
        else:
            cornices_normal.append(i)
    
    dict_cornices_flip = dict()
    dict_cornices_normal = dict()



    if len(cornices_flip)>1:
        temp_cornices_flip = cornices_flip[:]
        temp_cornices_flip_2 = cornices_flip[:]

        n=1

        while temp_cornices_flip:

            temp_array = [temp_cornices_flip[0]]
            temp_cornices_flip_2.remove(temp_cornices_flip[0])

            if len(temp_cornices_flip)>1:

                for i in temp_cornices_flip[1:]:
                    if temp_array[-1].Location.Curve.Tessellate()[1].DistanceTo(i.Location.Curve.Tessellate()[0]) < 0.0001:
                        temp_array.append(i)
                        temp_cornices_flip_2.remove(i)
                    elif temp_array[0].Location.Curve.Tessellate()[0].DistanceTo(i.Location.Curve.Tessellate()[1]) < 0.0001:
                        temp_array.insert(0,i)
                        temp_cornices_flip_2.remove(i)
                
            
            dict_cornices_flip[n] = temp_array
            temp_cornices_flip = temp_cornices_flip_2[:]
            temp_array = []
            n+=1


    elif len(cornices_flip) == 1:
        dict_cornices_flip[1] = cornices_flip



    if len(cornices_normal)>1:
        temp_cornices_normal = cornices_normal[:]
        temp_cornices_normal_2 = cornices_normal[:]

        n=1

        while temp_cornices_normal:


            temp_array = [temp_cornices_normal[0]]
            temp_cornices_normal_2.remove(temp_cornices_normal[0])

            if len(temp_cornices_normal)>1:

                for i in temp_cornices_normal[1:]:
                  
                    if temp_array[-1].Location.Curve.Tessellate()[1].DistanceTo(i.Location.Curve.Tessellate()[0]) < 0.0001:
                        temp_array.append(i)
                        temp_cornices_normal_2.remove(i)
                    elif temp_array[0].Location.Curve.Tessellate()[0].DistanceTo(i.Location.Curve.Tessellate()[1]) < 0.0001:
                        temp_array.insert(0,i)
                        temp_cornices_normal_2.remove(i)
                
            
            dict_cornices_normal[n] = temp_array
            temp_cornices_normal = temp_cornices_normal_2[:]
            temp_array = []
            n+=1


    elif len(cornices_normal) == 1:
        dict_cornices_normal[1] = cornices_normal

    


    if dict_cornices_normal:
        for i in dict_cornices_normal.keys():
            if len(dict_cornices_normal[i])>1:

                x=1
                for i1 in dict_cornices_normal[i][:-1]:

                    try: 
                        i1.LookupParameter("Control Lines").Set(0)
                        dict_cornices_normal[i][x].LookupParameter("Control Lines").Set(0)
                        i1.LookupParameter("sa_CL_end").Set(1000/304.8)
                        dict_cornices_normal[i][x].LookupParameter("sa_CL_start").Set(1000/304.8)
                    except:
                        pass
                
                    temp_norm = i1.GetTotalTransform().BasisZ

                    temp_corn = i1.HandOrientation.AngleOnPlaneTo(dict_cornices_normal[i][x].HandOrientation, temp_norm)

                    i1.LookupParameter("Angle end").Set(temp_corn/2)
                    dict_cornices_normal[i][x].LookupParameter("Angle start").Set(temp_corn/2)
                    x +=1

                if dict_cornices_normal[i][0].Location.Curve.Tessellate()[0].DistanceTo(dict_cornices_normal[i][-1].Location.Curve.Tessellate()[1]) < 0.0001:
                    try: 
                        dict_cornices_normal[i][0].LookupParameter("sa_CL_end").Set(1000/304.8)
                        dict_cornices_normal[i][-1].LookupParameter("sa_CL_start").Set(1000/304.8)
                    except:
                        pass
                
                    temp_norm = dict_cornices_normal[i][-1].GetTotalTransform().BasisZ

                    temp_corn = dict_cornices_normal[i][-1].HandOrientation.AngleOnPlaneTo(dict_cornices_normal[i][0].HandOrientation, temp_norm)

                    dict_cornices_normal[i][-1].LookupParameter("Angle end").Set(temp_corn/2)
                    dict_cornices_normal[i][0].LookupParameter("Angle start").Set(temp_corn/2)


    if dict_cornices_flip:
        for i in dict_cornices_flip.keys():
            if len(dict_cornices_flip[i])>1:

                x=1
                for i1 in dict_cornices_flip[i][:-1]:

                    try: 
                        i1.LookupParameter("Control Lines").Set(0)
                        dict_cornices_flip[i][x].LookupParameter("Control Lines").Set(0)
                        i1.LookupParameter("sa_CL_end").Set(1000/304.8)
                        dict_cornices_flip[i][x].LookupParameter("sa_CL_start").Set(1000/304.8)
                    except:
                        pass
                
                    temp_norm = i1.GetTotalTransform().BasisZ

                    temp_corn = i1.HandOrientation.AngleOnPlaneTo(dict_cornices_flip[i][x].HandOrientation, temp_norm)

                    i1.LookupParameter("Angle end").Set(- temp_corn/2)
                    dict_cornices_flip[i][x].LookupParameter("Angle start").Set(-temp_corn/2)
                    x +=1

                if dict_cornices_flip[i][0].Location.Curve.Tessellate()[0].DistanceTo(dict_cornices_flip[i][-1].Location.Curve.Tessellate()[1]) < 0.0001:
                    try: 
                        dict_cornices_flip[i][0].LookupParameter("sa_CL_end").Set(1000/304.8)
                        dict_cornices_flip[i][-1].LookupParameter("sa_CL_start").Set(1000/304.8)
                    except:
                        pass
                
                    temp_norm = dict_cornices_flip[i][-1].GetTotalTransform().BasisZ

                    temp_corn = dict_cornices_flip[i][-1].HandOrientation.AngleOnPlaneTo(dict_cornices_flip[i][0].HandOrientation, temp_norm)

                    dict_cornices_flip[i][-1].LookupParameter("Angle end").Set(-temp_corn/2)
                    dict_cornices_flip[i][0].LookupParameter("Angle start").Set(-temp_corn/2)
        
    if dict_cornices_normal and dict_cornices_flip:
        for i in dict_cornices_normal.keys():
            for i1 in dict_cornices_flip.keys():
                if dict_cornices_normal[i][0].Location.Curve.Tessellate()[0].DistanceTo(dict_cornices_flip[i1][0].Location.Curve.Tessellate()[0]) < 0.0001:
                    try: 
                        dict_cornices_normal[i][0].LookupParameter("Control Lines").Set(0)
                        dict_cornices_flip[i1][0].LookupParameter("Control Lines").Set(0)
                        dict_cornices_normal[i][0].LookupParameter("sa_CL_start").Set(1000/304.8)
                        dict_cornices_flip[i1][0].LookupParameter("sa_CL_start").Set(1000/304.8)
                    except:
                        pass
                    temp_norm = dict_cornices_normal[i][0].GetTotalTransform().BasisZ

                    temp_corn = dict_cornices_normal[i][0].HandOrientation.AngleOnPlaneTo(dict_cornices_flip[i1][0].HandOrientation, temp_norm)

                    dict_cornices_normal[i][0].LookupParameter("Angle start").Set(math.pi/2-temp_corn/2)
                    dict_cornices_flip[i1][0].LookupParameter("Angle start").Set(math.pi/2-temp_corn/2)

                if dict_cornices_normal[i][-1].Location.Curve.Tessellate()[1].DistanceTo(dict_cornices_flip[i1][-1].Location.Curve.Tessellate()[1]) < 0.0001:
                    try: 
                        dict_cornices_normal[i][-1].LookupParameter("Control Lines").Set(0)
                        dict_cornices_flip[i1][-1].LookupParameter("Control Lines").Set(0)
                        dict_cornices_normal[i][-1].LookupParameter("sa_CL_end").Set(1000/304.8)
                        dict_cornices_flip[i1][-1].LookupParameter("sa_CL_end").Set(1000/304.8)
                    except:
                        pass
                    temp_norm = dict_cornices_normal[i][-1].GetTotalTransform().BasisZ

                    temp_corn = dict_cornices_normal[i][-1].HandOrientation.AngleOnPlaneTo(dict_cornices_flip[i1][-1].HandOrientation, temp_norm)

                    dict_cornices_normal[i][-1].LookupParameter("Angle end").Set(-math.pi/2+temp_corn/2)
                    dict_cornices_flip[i1][-1].LookupParameter("Angle end").Set(-math.pi/2+temp_corn/2)

def cheсk_family(el_in):
    try: 
        first_element_Id = el_in[0].Symbol.Family.Id
    except:
        return False
    for i in el_in:
        try:
            if i.Symbol.Family.Id != first_element_Id:
                return False
        except:
            return False
    try:
        x = i.LookupParameter("Angle start").AsValueString()
        y = i.LookupParameter("Angle end").AsValueString()
        return True
    except:
        return False



transaction = Transaction(doc, "Trim Cornices")
try:
    transaction.Start()

    select_el = [doc.GetElement(i) for i in __revit__.ActiveUIDocument.Selection.GetElementIds()]

    if cheсk_family(select_el):
        trim_cornices(select_el)
    else:
        message_ui("The selected elements cannot be trimmed.")
        

    transaction.Commit()

except Exception as e:

    transaction.RollBack()
    print (e)