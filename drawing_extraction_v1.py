import fitz,sys
file_name = sys.argv[1]
doc = fitz.open(file_name)
header = "Header"  # text in header
footer = "Page %i of %i"  # text in footer
for page in doc:
    page.insert_text((50, 50), header)  # insert header
    page.insert_text(  # insert footer 50 points above page bottom
        (50, page.rect.height - 50),
        footer % (page.number + 1, doc.page_count),
    )
page1 = doc[0]
list_of_annotation = [a for a in page1.annots()]
content_and_loc = []
for so in list_of_annotation:
    txt = so.info['content']
    location = so.rect
#     x0,y0,x1,y1 = location.x0,location.y0,location.x1,location.y1
#     new_loc = fitz.Rect(y0,x0,y1,x1)
    r = so.rotation
    content_and_loc.append((txt,location,r))
    
page = doc[0]
paths = page.get_drawings() 

# find_same = []
# nearby = []
find_in_boundary = []
for path in paths:
    i_rect = path['rect'].irect
    a,b,c,d = i_rect
    for t in content_and_loc:
#         print(t)
        a1,b1,c1,d1 = t[-2]
        
#         if a == a1 and b ==b1 and c == c1 and d ==d1:
#             find_same.append((path,t))
#         # Find near proximity
#         if ((a-a1)**2+(b-b1)**2)**1/2<10:
#             nearby.append((path,t))
        if a >=a1 and b>=b1 and c<=c1 and d<=d1:
            find_in_boundary.append(path)
            
            
# import fitz
# doc = fitz.open("B145-79-41-102-1112.pdf")
page = doc[0]
paths = page.get_drawings()  # extract existing drawings
# this is a list of "paths", which can directly be drawn again using Shape
# -------------------------------------------------------------------------
#
# define some output page with the same dimensions
outpdf = fitz.open()
outpage = outpdf.new_page(width=page.rect.height, height=page.rect.width)
shape = outpage.new_shape()  # make a drawing canvas for the output page

# --------------------------------------
for path in paths:

#     if (path not in nearby_paths) and (path not in find_in_boundary):
    if path not in find_in_boundary:
        for item in path["items"]:  # these are the draw commands
            if item[0] == "l":  # line
                shape.draw_line(item[1], item[2])
            elif item[0] == "re":  # rectangle
                shape.draw_rect(item[1])
            elif item[0] == "qu":  # quad
                shape.draw_quad(item[1])
            elif item[0] == "c":  # curve
                shape.draw_bezier(item[1], item[2], item[3], item[4])
            else:
                raise ValueError("unhandled drawing", item)
        # ------------------------------------------------------
        # all items are drawn, now apply the common properties
        # to finish the path
        # ------------------------------------------------------
        if not path["fill"] is None:
            shape.finish(
                fill=(0,0,0),  # fill color
                color=(0,0,0),  # line color
                dashes=path["dashes"],  # line dashing
                even_odd=path.get("even_odd", True),  # control color of overlaps
                closePath=path["closePath"],  # whether to connect last and first point
                lineJoin=path["lineJoin"],  # how line joins should look like
                lineCap=max(path["lineCap"]),  # how line ends should look like
                width=path["width"],  # line width
                stroke_opacity=1,#path.get("stroke_opacity", 1),  # same value for both
                fill_opacity=1#path.get("fill_opacity", 1),  # opacity parameters,

                )
        else:
            shape.finish(
                fill=path["fill"],  # fill color
                color=(0,0,0),  # line color
                dashes=path["dashes"],  # line dashing
                even_odd=path.get("even_odd", True),  # control color of overlaps
                closePath=path["closePath"],  # whether to connect last and first point
                lineJoin=path["lineJoin"],  # how line joins should look like
                lineCap=max(path["lineCap"]),  # how line ends should look like
                width=path["width"],  # line width
                stroke_opacity= 1,#path.get("stroke_opacity", 1),  # same value for both
                fill_opacity=1 #path.get("fill_opacity", 1),  # opacity parameters,

                )
    
#         shape.finish(
#             fill=path["fill"],  # fill color
#             color=path["color"],  # line color
#             dashes=path["dashes"],  # line dashing
#             even_odd=path.get("even_odd", True),  # control color of overlaps
#             closePath=path["closePath"],  # whether to connect last and first point
#             lineJoin=path["lineJoin"],  # how line joins should look like
#             lineCap=max(path["lineCap"]),  # how line ends should look like
#             width=path["width"],  # line width
#             stroke_opacity=path.get("stroke_opacity", 1),  # same value for both
#             fill_opacity=path.get("fill_opacity", 1),  # opacity parameters,

#             )
    
# Overlay the text information
for c in content_and_loc:
    text,rec,r = c
    outpage.insert_textbox(rec,text,rotate=270)
# all paths processed - commit the shape to its page
shape.commit()
outpage.set_rotation(270)
outpdf.save(file_name.split[".pdf"][0]+"mode.pdf")
