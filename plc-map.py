#!/usr/bin/env plcsh
 
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

########## second - way simpler - export sites as a list to javascript for rendering with googlemap
js_prelude="""
function Site (lat,lon,site_id,name,peer_id,peername,nb_nodes) {
  this.lat=lat;
  this.lon=lon;
  this.site_id=site_id;
  this.name=name;
  this.peer_id=peer_id;
  this.peername=peername;
  this.nb_nodes=nb_nodes;
}
"""

def locate_peer (peers,peer_id):
    for peer in peers:
        if peer['peer_id']==peer_id:
            return peer
    return {'peername':'Cannot locate peer'}

def js_site (site,peers):
    # some sites come with lat or lon being None
    lat = site['latitude']
    if not lat:
        lat=0
    lon = site['longitude']
    if not lon:
        lon=0
    # build javascript text
    jstext="new Site("
    jstext += str(lat) + "," + str(lon) + ","
    jstext += str(site['site_id']) + ","
    # needs html encoding for wierd chars
    jstext += '"' + site['name'].encode("utf-8") + '"' + ','
    if not site['peer_id']:
        jstext += '0,""' +','
    else:
        peer=locate_peer(peers,site['peer_id'])
        jstext += str(site['peer_id']) + ',"' + peer['peername'].encode("utf-8") + '"' + ','
    jstext += str(len(site['node_ids']))
    jstext += ')\n'
    return jstext

def make_javascript():
    outputname="/var/www/html/sites/plc-sites.js"
    f=open(outputname,"w")
    f.write(js_prelude)
    columns=['latitude','longitude','site_id','name','peer_id','node_ids']
    f.write("allSites=new Array(\n")
    # writes foreign sites first
    foreign_sites=GetSites({'~peer_id':None},columns)
    peers=GetPeers({})
    local_sites=GetSites({'peer_id':None},columns)
    f.write(",".join([js_site(site,peers) for site in foreign_sites+local_sites]))
    f.write(");")

def main ():
    make_image ()
    make_javascript ()

if __name__ == '__main__':
    main ()
