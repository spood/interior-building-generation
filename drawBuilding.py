import squarify_module
import Image, ImageDraw
import random
import xml.etree.ElementTree as ET
import numpy
import itertools
import math

class BuildingTemplate:
    
    def __init__(self, type, minFloors, maxFloors, minDoors, maxDoors, requiredRooms, optionalRooms):
        self.type = type
        self.minFloors = minFloors
        self.maxFloors = maxFloors
        self.minDoors = minDoors
        self.maxDoors = maxDoors
        self.requiredRooms = requiredRooms
        self.optionalRooms = optionalRooms

class RoomTemplate:
    
    def __init__(self, type, minWidth, maxWidth, minHeight, maxHeight, minWindows, maxWindows, furniture):
        self.type = type
        self.minWidth = minWidth
        self.maxWidth = maxWidth
        self.minHeight = minHeight
        self.maxHeight = maxHeight
        self.minWindows = minWindows
        self.maxWindows = maxWindows
        self.furniture = furniture
        
class XMLBuildingTemplateReader:

    def __init__(self, xmlpath):
        self.tree = ET.parse(xmlpath)
        self.root = self.tree.getroot()

    def loadRooms(self):
        roomTemplates = []
        for rooms in self.root.findall( 'rooms/room' ):
            type = rooms.attrib[ 'type' ]
            minWidth = int(rooms.find('minWidth').text)
            maxWidth = int(rooms.find('maxWidth').text)
            minHeight = int(rooms.find('minHeight').text)
            maxHeight = int(rooms.find('maxHeight').text)
            minWindows = int(rooms.find('minWindows').text)
            maxWindows = int(rooms.find('maxWindows').text)
            furnitures = []
            for furniture in rooms.findall('furniture'):
                furnitures.append(furniture.text)
            roomTemplates.append( RoomTemplate(type, minWidth, maxWidth, minHeight, maxHeight, minWindows, maxWindows, furniture) )
        
        return roomTemplates
        
    def loadBuildings(self):
        buildingTemplates = []
        # get all the buildings
        for building in self.root.findall( 'buildings/building' ):
            type = building.attrib[ 'type' ]
            minFloors =  building.find('minFloors').text
            maxFloors =  building.find('maxFloors').text
            minDoors =  building.find('minDoors').text
            maxDoors =  building.find('maxDoors').text
            requiredRooms = []
            optionalRooms = []
            for requiredRoom in building.findall('requiredRoom'):
                requiredRooms.append(requiredRoom.text)
            for optionalRoom in building.findall('optionalRoom'):
                optionalRooms.append(optionalRoom.text)
                
            buildingTemplates.append( BuildingTemplate(type, minFloors, maxFloors, minDoors, maxDoors, requiredRooms, optionalRooms) )

        return buildingTemplates
        

class GenerateBuilding:

    def __init__(self, buildingTemplate, roomTemplates):
        self.building = buildingTemplate
        self.possibleRooms = roomTemplates
        
    def generateRooms(self):
        roomSizes = {}
        # generate required rooms for the building
        for room in self.building.requiredRooms:
            for roomTemplate in self.possibleRooms:
                if(roomTemplate.type == room):
                    roomWidth = random.randrange( roomTemplate.minWidth, roomTemplate.maxWidth)
                    roomHeight = random.randrange( roomTemplate.minHeight, roomTemplate.maxHeight)
                    roomSizes[room] = roomWidth * roomHeight
                    # generate a second room randomly
                    if( random.randrange(0,2) == 1):
                        roomWidth = random.randrange( roomTemplate.minWidth, roomTemplate.maxWidth)
                        roomHeight = random.randrange( roomTemplate.minHeight, roomTemplate.maxHeight)
                        roomSizes[room + "2"] = roomWidth * roomHeight
        
        for room in self.building.optionalRooms:
            if( random.randrange(0,2) == 1):
                for roomTemplate in self.possibleRooms:
                    if(roomTemplate.type == room):
                        roomWidth = random.randrange( roomTemplate.minWidth, roomTemplate.maxWidth)
                        roomHeight = random.randrange( roomTemplate.minHeight, roomTemplate.maxHeight)
                        roomSizes[room] = roomWidth * roomHeight
            
        return roomSizes


def export_TMX(floorplan, width, height):
    root = ET.Element('map')
    root.attrib['version'] = "1.0"
    root.attrib['orientation'] = "orthogonal"
    root.attrib['width'] = "25"
    root.attrib['height'] = "20"
    root.attrib['tilewidth'] = "32"
    root.attrib['tileheight'] = "32"

    tileset = ET.Element('tileset')
    root.append(tileset)

    tileset.attrib['firstgid'] = "1"
    tileset.attrib['name'] = "black"
    tileset.attrib['tilewidth'] = "32"
    tileset.attrib['tileheight'] = "32"
    
    tilesetimg = ET.Element('image')
    tileset.append(tilesetimg)
    tilesetimg.attrib['source'] = "black_tile.png"
    tilesetimg.attrib['width'] = "32"
    tilesetimg.attrib['height'] = "32"
    
    layer = ET.Element('layer')
    root.append(layer)
    layer.attrib['name'] = "Tile Layer 1"
    layer.attrib['width'] = "25"
    layer.attrib['height'] = "20"
    
    data = ET.Element('data')
    layer.append(data)
    
    for h in range(height):
        for w in range(width):
            tile = ET.Element('tile')
            data.append(tile)
            tile.attrib['gid'] = str(floorplan[w][h])
    
    tmxOutput = open("tmxOutput.tmx", 'w')
    ET.ElementTree(root).write(tmxOutput)
    tmxOutput.close()
        
random.seed(0)
XMLreader = XMLBuildingTemplateReader("example_format.xml")
buildings = XMLreader.loadBuildings()
rooms = XMLreader.loadRooms()

house_maker = GenerateBuilding(buildings[0], rooms)
values = house_maker.generateRooms()

x = 0
y = 0
width = 25
height = 20
tile_size = 32

widthtotal = width * tile_size
heighttotal = height * tile_size

# wtf python how do i make 2d array
floor = [[[0] for ni in range(height+1)] for mi in range(width)]
for w in range(width):
    for h in range(height):
        floor[w][h] = 0

values = squarify_module.normalize_sizes(values, widthtotal, heighttotal)

# returns a list of rectangles
rects = squarify_module.squarify(values, x, y,widthtotal, heighttotal)

img = Image.new("RGB", (widthtotal + tile_size + 20, heighttotal + tile_size + 20), "white")
draw = ImageDraw.Draw(img)


# draw rooms
for rect in rects:
    rectX = int( round(rect['x'] / tile_size))
    rectY = int( round(rect['y'] / tile_size))
    rectWidth = int( round(rect['dx'] / tile_size))
    rectHeight = int( round(rect['dy'] / tile_size))
    rectCentreX = int(math.ceil(rectX + (rectWidth / 2)))
    rectCentreY = int(math.ceil(rectY + (rectHeight / 2)))
    
    while(rectX + rectWidth >= width):
        rectWidth -= 1
    while(rectY + rectHeight >= height):
        rectHeight -= 1
    
    # top side
    for w in range(0,rectWidth+1):
        floor[rectX + w][rectY] = 1
    # bottom side
    for w in range(0,rectWidth+1):
        floor[rectX + w][rectY + rectHeight] = 1
    # left side
    for h in range(0,rectHeight+1):
        floor[rectX][rectY + h] = 1
    # right side
    for h in range(0,rectHeight+1):
        floor[rectX + rectWidth][rectY + h] = 1
    #print rectX, rectY
    #draw.rectangle( [ (rectX, rectY), (rectX + rectWidth, rectY + rectHeight) ], outline="#000000")
    draw.text( (rectCentreX * tile_size, rectCentreY * tile_size), rect['name'], fill="#000000")
    # draw front door
    if(rect['name'] == "livingRoom"):
        if(rectX < 3):
            draw.rectangle( [ (rectX*tile_size, rectCentreY*tile_size), (tile_size, rectCentreY*tile_size+tile_size) ], outline="#000000")
        if(rectX >= width-3):
            draw.rectangle( [ (rectX*tile_size, rectCentreY*tile_size), (tile_size, rectCentreY*tile_size+tile_size) ], outline="#000000")
        
        if(rectY < 3):
            draw.rectangle( [ (rectCentreX*tile_size, rectY*tile_size), (rectCentreX*tile_size+tile_size, tile_size) ], outline="#000000")
        if(rectY >= height-3):
            draw.rectangle( [ (rectCentreX*tile_size0, rectY*tile_size), (rectCentreX*tile_size+tile_size, tile_size) ], outline="#000000")

# remove any double rows that crop up from converting float to int
# idgaf about nested ifs
for w in range(width-2):
    for h in range(height-2):
        if( floor[w][h] == 1):
            if( floor[w+1][h] == 1):
                if( floor[w+2][h] == 0):
                    if(floor[w][h-1] == 1 or floor[w][h+1] == 1):
                        floor[w+1][h] = 0
                        floor[w][h] = 1
            if( floor[w][h+1] == 1):
                if( floor[w][h+2] == 0):
                    if(floor[w-1][h] == 1 or floor[w+1][h] == 1):
                        floor[w][h+1] = 0
                        floor[w][h] = 1
                        
for w in range(width-2):
    for h in range(height-2):
        if( floor[w][h] == 1):
            if( floor[w+1][h] == 1):
                if( floor[w+2][h] == 0):
                    if(floor[w][h-1] == 1 or floor[w][h+1] == 1):
                        floor[w+1][h] = 0
                        floor[w][h] = 1
            if( floor[w][h+1] == 1):
                if( floor[w][h+2] == 0):
                    if(floor[w-1][h] == 1 or floor[w+1][h] == 1):
                        floor[w][h+1] = 0
                        floor[w][h] = 1

export_TMX(floor, width, height)
                        
for w in range(width):
    for h in range(height):
        if( floor[w][h] == 1):
            pointX = (w*tile_size) + (tile_size / 2)
            pointY = (h*tile_size) + (tile_size / 2)
            draw.rectangle( [ (pointX,pointY ), (pointX + tile_size, pointY + tile_size) ], outline="#000000")
img.save("img.png", "PNG")



