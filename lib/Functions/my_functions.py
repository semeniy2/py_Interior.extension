# -*- coding: utf-8 -*-

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

from pyrevit import revit, forms
import wpf, os, clr

clr.AddReference('System')
clr.AddReference('RevitAPI')

from System.Windows import Window


class message_ui(Window):

    def __init__(self, text):

        PATH_SCRIPT = os.path.dirname(__file__)

        base_path = os.path.dirname(PATH_SCRIPT)  
        new_path = os.path.join(base_path, "UI")

        path_xaml_file = os.path.join(new_path, 'Message.xaml')
        wpf.LoadComponent(self, path_xaml_file)

        self.text.Content = text

        self.ShowDialog()