from bokeh.plotting import curdoc, figure
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Range1d, LinearAxis, Whisker, Span, Div
from bokeh.io import show, output_file, save
from bokeh.transform import factor_cmap

class Report():
    models = {"Div": Div, "Span": Span, "Range1d": Range1d}
    layouts = {"column": column, "row": row}
    figure = figure
    def __init__(self, title, file_name = None):
        self.figures = []
        self.file_name = file_name
        self.doc = curdoc()
        self.title = title
        self.doc_root_attached = False
    def add_figure(self, figure):
        self.figures.append(figure)
    def render_to_file(self):
        if self.file_name == None:
            raise "No file_name provided 2nd constructor argument"
        if self.doc_root_attached == False:
            self.doc.add_root(column(*self.figures))
            self.doc_root_attached = True
        output_file(filename=self.file_name, title=self.title)
        save(self.doc)

