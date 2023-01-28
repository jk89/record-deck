from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d, LinearAxis, Whisker, Span, Div
from bokeh.io import show, output_file, save
from bokeh.transform import factor_cmap
from colour import Color
import utils
class Report():
    models = {"Div": Div, "Span": Span, "Range1d": Range1d, "ColumnDataSource": ColumnDataSource}
    layouts = {"column": column, "row": row}
    figure = figure
    Color = Color
    def __init__(self, *args): # title, file_name = None
        self.figures = []
        self.doc = curdoc()
        #self.doc.theme = 'night_sky'
        self.doc_root_attached = False
        # args could be (title, file_name) or (title, file_name_pattern, file_descriptor)
        if len(args) == 2:
            self.title = args[0]
            self.file_name = args[1]
        elif len(args) == 3:
            self.title = args[0]
            self.file_name = None
            self.file_name_pattern = args[1]
            self.file_descriptor = args[2]
        else:
            raise "Constructor needs args of (title, file_name) or (title, file_name_pattern, file_descriptor)"
    def add_figure(self, figure):
        self.figures.append(figure)
    def render_to_file(self):
        if self.doc_root_attached == False:
            self.doc.add_root(column(*self.figures))
            self.doc_root_attached = True
        
        if self.file_name != None:
            print("here")
            #we should use the file name provided directly
            output_file(filename=self.file_name, title=self.title)
            save(self.doc)
            return None
        elif self.file_name_pattern != None or self.file_descriptor != None:
            print("here2")
            # we should save a random file name and keep the details within an id file
            rid = utils.random_id()
            report_file_name = (self.file_name_pattern + ".html") % (rid)
            report_id_file_name = (self.file_name_pattern + ".id") % (rid)

            with open(report_id_file_name, "w") as fid:
                fid.write(self.file_descriptor)

            output_file(filename=report_file_name, title=self.title)
            save(self.doc)
            return report_file_name
        else:
            raise "Bad arguments"

"""
from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d, LinearAxis, Whisker, Span, Div
from bokeh.io import show, output_file, save
from bokeh.transform import factor_cmap
from colour import Color
import utils

class Report():
    models = {"Div": Div, "Span": Span, "Range1d": Range1d, "ColumnDataSource": ColumnDataSource}
    layouts = {"column": column, "row": row}
    figure = figure
    Color = Color
    def __init__(self, title, file_name = None, run_ids=None):
        self.figures = []
        self.file_name = file_name
        self.doc = curdoc()
        self.title = title
        self.doc_root_attached = False
        self.run_ids = run_ids
    def add_figure(self, figure):
        self.figures.append(figure)
    def render_to_file(self):
        if self.doc_root_attached == False:
            self.doc.add_root(column(*self.figures))
            self.doc_root_attached = True
        if self.file_name != None:
            raise "No file_name provided 2nd constructor argument"
        rid = utils.random_id()
        file_id_file = "./datasets/data/calibration-data/combination-report-%s.id" % (rid)
        file_short = "./datasets/data/calibration-data/combination-report-%s.html" % (rid)
        with open(file_id_file, "w") as fid:
            fid.write(self.file_name)
        output_file(filename=file_short, title=self.title)
        save(self.doc)
        return file_short


print ( )
"""