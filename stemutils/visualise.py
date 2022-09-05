import hyperspy.api as hs
from stemutils.io import *
import ncempy.io
from matplotlib import widgets
import numpy as np
import matplotlib.pyplot as plt

class RectangleSelector(widgets.RectangleSelector):
    def get_lims(self, scale = 1):
        extent = self.extents
        return np.asarray(extent)*scale


def line_select_callback(eclick, erelease):
    'eclick and erelease are the press and release events'
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
    print(" The button you used were: %s %s" % (eclick.button, erelease.button))


def toggle_selector(event):
    print(' Key pressed.')
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print(' RectangleSelector deactivated.')
        toggle_selector.RS.set_active(False)
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print(' RectangleSelector activated.')
        toggle_selector.RS.set_active(True)


        
def draw_rectangle_selector(im):
    fig, current_ax = plt.subplots()                 # make a new plotting range
    plt.imshow(im)
    print("\n      click  -->  release")

    # drawtype is 'box' or 'line' or 'none'
    toggle_selector.RS = RectangleSelector(current_ax, line_select_callback,
                                           drawtype='box', useblit=True,
                                           button=[1, 3],  # don't use middle button
                                           minspanx=5, minspany=5,
                                           spancoords='pixels',
                                           interactive=True)
    plt.connect('key_press_event', toggle_selector)
    plt.show()
    return toggle_selector





def add_annotation_markers(file):
    '''
    Finds and plots the annotations from dm3/dm4 file metadata as hyperspy markers
    
    file (str): path to dm3/dm4 file
    
    returns: hyperspy.signal with annotations
    '''
    
    
    p3 = hs.load(file)
    
    dm4file = ncempy.io.dm.fileDM(file)

    tag_dict = dm4file.allTags

    keys = list(dm4file.allTags.keys())

    text_ann_keys = [k for k in keys if k.find('AnnotationType') != -1 and np.all(dm4file.allTags[k] == 13)]

    txt = []
    pos = []

    for text_ann_k in text_ann_keys:

        txt.append(tag_dict[text_ann_k.strip('AnnotationType') + 'Text'])

        txt_rect = tag_dict[text_ann_k.strip('AnnotationType') + 'Rectangle']

        pos.append(txt_rect)


    for i, t in enumerate(txt):
        c = pos[i]
        lx, rx = p3.axes_manager[0].scale * c[1], p3.axes_manager[0].scale * c[3]
        ly, ry = p3.axes_manager[1].scale * c[0], p3.axes_manager[1].scale * c[2]
        px= np.mean((lx,rx))
        py = np.mean((ly,ry))

        m = hs.plot.markers.text(px,py, t, color = 'red', fontsize = 20, ha = 'center')
        p3.add_marker(m, permanent=True)


    box_ann_keys = [k for k in keys if k.find('AnnotationType') != -1 and np.all(dm4file.allTags[k] == 5)]

    rec_coords = []

    for box_ann_k in box_ann_keys:

        rec_coords.append(tag_dict[box_ann_k.strip('AnnotationType') + 'Rectangle'])

    for c in rec_coords:
        lx, rx = p3.axes_manager[0].scale * c[1], p3.axes_manager[0].scale * c[3]
        ly, ry = p3.axes_manager[1].scale * c[0], p3.axes_manager[1].scale * c[2]
        m = hs.plot.markers.rectangle(lx,ly,rx,ry, color = 'red')
        p3.add_marker(m, permanent=True)
    
    return p3
