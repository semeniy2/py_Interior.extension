# -*- coding: utf-8 -*-

__title__ = "Select \nby Image"
__doc__ = """Select elements of the same family.
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *


from pyrevit import revit, forms
import wpf, os, clr

clr.AddReference('System')
clr.AddReference('RevitAPI')

from System.Windows import Window, Thickness
from System.Windows.Controls import Image, ListBoxItem, StackPanel, TextBlock, Orientation
from System.Windows.Media import RenderOptions, BitmapScalingMode
from System.Windows.Media.Imaging import BitmapImage

import clr
import System
from System.IO import MemoryStream, SeekOrigin
from System import Uri

from Functions.my_functions import message_ui



doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

PATH_SCRIPT = os.path.dirname(__file__)

class select_type_ui(Window):

    def __init__(self, el_in):

        path_xaml_file = os.path.join(PATH_SCRIPT, 'Select by Image.xaml')
        wpf.LoadComponent(self, path_xaml_file)

        self.dic_listbox = dict()

        self.el_in = el_in
        
        all_types = self.get_list_type(el_in)

        self.change_listbox(all_types)

        self.ShowDialog()


    def get_list_type(self, el_in):
        el_filter = ElementClassFilter(FamilySymbol)
        dic_temp = dict()

        for i in el_in[0].Symbol.Family.GetDependentElements(el_filter):
            dic_temp[doc.GetElement(i).get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()] = doc.GetElement(i)

        all_types = [dic_temp[i] for i in sorted(dic_temp.keys())]

        return all_types

    def change_listbox(self, list_of_types):
        listbox = self.UI_Listbox

        listbox.Items.Clear()

        
        x = 0

        for i in list_of_types:


            image = Image()
            image.Source = self.get_image_from_FamilySymbol(i)
            image.Width = 120
            image.Height = 90
            RenderOptions.SetBitmapScalingMode(image, BitmapScalingMode.HighQuality)

            self.dic_listbox[x] = i
            x += 1

            stack_2 = StackPanel()
            stack_2.Orientation  = Orientation.Horizontal
            stack_2.Children.Add(image)

            stack_text = StackPanel()
            stack_text.Margin = Thickness(20, 0, 0, 0)
            stack_text.Orientation  = Orientation.Vertical

            stack_2.Children.Add(stack_text)

            text = TextBlock()
            text.Margin = Thickness(0, 5, 0, 0)
            text.Text = i.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_NAME).AsString()
            text2 = TextBlock()
            text2.Margin = Thickness(0, 10, 0, 0)
            text2.Text = i.get_Parameter(BuiltInParameter.ALL_MODEL_DESCRIPTION).AsString()

            stack_text.Children.Add(text)
            stack_text.Children.Add(text2)
            try:
                text3 = TextBlock()
                text3.Text = "Dimensions: " + i.LookupParameter("Width").AsValueString()+" x "+ i.LookupParameter("Height_").AsValueString()
                stack_text.Children.Add(text3)
            except:
                pass



            listboxit = ListBoxItem()
            listboxit.Content = stack_2

            listbox.Items.Add(listboxit)


    
    def get_image_from_FamilySymbol (self, el_in):
        try:
            image_element = doc.GetElement(el_in.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_IMAGE).AsElementId()).GetImage()
            memory_stream = MemoryStream()
            image_element.Save(memory_stream, System.Drawing.Imaging.ImageFormat.Png)

            # Создаем BitmapImage из потока
            bitmap_image = BitmapImage()
            memory_stream.Seek(0, SeekOrigin.Begin)  
            bitmap_image.BeginInit()
            bitmap_image.StreamSource = memory_stream
            bitmap_image.EndInit()

            return bitmap_image


        except:
            bitmap = BitmapImage()
            bitmap.BeginInit()
            path_file = os.path.dirname(__file__)
            path_images = os.path.join(path_file,'images', 'no_image.jpg')
            bitmap.UriSource = Uri(path_images)
            bitmap.EndInit()

            return bitmap
    
    def UI_ListBox_SelectionChanged(self, sender, e):
        self.Close()
 
        for i in self.el_in:
            i.Symbol = self.dic_listbox[sender.SelectedIndex]




        




      



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
    return True




transaction = Transaction(doc, "Select by Image")
try:
    transaction.Start()

    select_el = [doc.GetElement(i) for i in __revit__.ActiveUIDocument.Selection.GetElementIds()]

    if cheсk_family(select_el):
        select_type_ui(select_el)
    else:
        message_ui("To run the script, you need to select \nelements from the same family")
        

    # wind_ui()
    
   

    transaction.Commit()

except Exception as e:

    transaction.RollBack()
    print (e)