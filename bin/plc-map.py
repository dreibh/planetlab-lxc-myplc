#!/usr/bin/env plcsh
 
# this is a very rustic script for generating png maps from a model
# the model is expected in /var/www/html/sites/map.png
# and the output is located in the same dir as livemap.png
#
# this has many drawbacks, as it needs a cylindric projection map
# (there's almost no such map out there) and manual calibration
# you want to use the kml-based googlemap applet instead

import Image, ImageDraw

####### first - rustic - linear positioning on a map
def circle (image, percentX, percentY, radiusX, radiusY, colorIn, colorOut):

    imageX, imageY = image.size
    centerX = int(imageX*percentX)
    centerY = int(imageY*percentY)
    x = max (0, min (centerX,imageX))
    y = max (0, min (centerY,imageY))

    x1 = x - radiusX
    x2 = x + radiusX
    y1 = y - radiusY
    y2 = y + radiusY

    draw = ImageDraw.Draw (image)
    draw.chord((x1,y1,x2,y2), 0, 360, fill=colorIn, outline=colorOut )
    del draw

latitude={'top':65.,
          'bottom': 35.5}
longitude={'left':-11.,
           'right':58.}
    
def render_site (site, image, sx, sy, cIn, cOut):
    if site['longitude'] is not None and site['latitude'] is not None:
        px=float(longitude['left']-site['longitude'])/float(longitude['left']-longitude['right'])
        py=float(latitude['top']-site['latitude'])/float(latitude['top']-latitude['bottom'])
        if (px<0 or py<0 or px>1 or py>1):
            return
        
        circle(image,px,py,sx,sy,cIn,cOut)
    
def make_image():
    path = '/var/www/html/sites/'
    original = path + 'map.png'
    live = path + 'livemap.png'

    # map characteristics, in degrees.
    # latitude : positive is north
    # longitude : positive is east 

    # circle radius in pixels
    sxLocal,syLocal=7,7
    # circle in and out colors
    cInLocal , cOutLocal = '#566b8a','#bbbbbb'

    # same for federating / foreign sites
    sxForeign,syForeign=6,6
    cInForeign , cOutForeign = '#acb3a4', '#444444'
 
    image = Image.open(original)

    for site in GetSites({'~peer_id':None,'enabled':True}):
        render_site (site, image, sxForeign, syForeign, cInForeign , cOutForeign)
    # local sites go last to be more visible
    for site in GetSites({'peer_id':None,'enabled':True}):
        render_site (site, image, sxLocal, syLocal, cInLocal , cOutLocal)
        
    image.save (live)

def main ():
    make_image ()

if __name__ == '__main__':
    main ()
