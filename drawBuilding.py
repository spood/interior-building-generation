import squarify_module
import Image, ImageDraw
import random
import xml.etree.ElementTree as ET
import numpy
import itertools

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

        
def perp( a ) :
    b = numpy.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b

# line segment a given by endpoints a1, a2
# line segment b given by endpoints b1, b2
# return 
def seg_intersect(a1,a2, b1,b2) :
    da = a2-a1
    db = b2-b1
    dp = a1-b1
    dap = perp(da)
    denom = numpy.dot( dap, db)
    num = numpy.dot( dap, dp )
    # hah!
    if(denom < 0.0001):
        denom = 0.0001
    return (num / denom)*db + b1
        
def lineIntersectsRect(line, rect, margin=10):
    #if(line[0] > rect['x'] - margin and line[2] < rect['x'] + rect['dx'] + margin ):
    #    return True
    #if(line[1] > rect['y'] - margin and line[3] < rect['y'] + rect['dy'] + margin ):
    #    return True
    return False
        
def getCorridor(rects, livingRoomRect):
    corridor = Image.new("RGB", (width + 20, height + 20), "white")
    corridorDraw = ImageDraw.Draw(corridor)
    lines = []
    for rect in rects:
        if(rect['name'] == "livingRoom"):
            continue
        rectX = rect['x']
        rectY = rect['y']
        rectWidth = rect['dx']
        rectHeight = rect['dy']
        # top line
        top_line = (rectX, rectY, rectX + rectWidth,rectY)
        corridorDraw.line(top_line, fill=0)
        lines.append(top_line)
        
        # bottom line
        bottom_line = (rectX, rectY + rectHeight, rectX + rectWidth,rectY + rectHeight)
        corridorDraw.line(bottom_line, fill=0)
        lines.append(bottom_line)
        
        # left line
        left_line = (rectX, rectY, rectX, rectY + rectHeight)
        corridorDraw.line(left_line, fill=0)
        lines.append(left_line)
        
        # right line
        right_line = (rectX + rectWidth, rectY, rectX + rectWidth,rectY + rectHeight)
        corridorDraw.line(right_line, fill=0)
        lines.append(right_line)
    
    lineCombinations = itertools.combinations(lines, 2)
    for lineComb in lineCombinations:

        p1 = numpy.array( [lineComb[0][0], lineComb[0][1]])
        p2 = numpy.array( [lineComb[0][2], lineComb[0][3]])
        
        p3 = numpy.array( [lineComb[1][0], lineComb[1][1]])
        p4 = numpy.array( [lineComb[1][2], lineComb[1][3]])
        intersection = seg_intersect( p1, p2, p3, p4)
        
        if( numpy.isfinite(intersection[0]) and numpy.isfinite(intersection[1]) ):
            print intersection
            corridorDraw.ellipse((intersection[0]-5, intersection[1]-5, intersection[0]+5, intersection[1]+5), fill=(255,0,0))


            
    corridor.save("corridor.png", "PNG")
        
random.seed(0)
XMLreader = XMLBuildingTemplateReader("example_format.xml")
buildings = XMLreader.loadBuildings()
rooms = XMLreader.loadRooms()

house_maker = GenerateBuilding(buildings[0], rooms)
values = house_maker.generateRooms()

x = 0
y = 0
width = 700
height = 433

values = squarify_module.normalize_sizes(values, width, height)

# returns a list of rectangles
rects = squarify_module.squarify(values, x, y, width, height)

# get the living room rect so we can generate a corridor to it
for rect in rects:
    if(rect['name'] == "livingRoom"):
        getCorridor(rects, rect)

img = Image.new("RGB", (width + 20, height + 20), "white")
draw = ImageDraw.Draw(img)


# draw rooms
for rect in rects:
    rectX = rect['x']
    rectY = rect['y']
    rectWidth = rect['dx']
    rectHeight = rect['dy']
    rectCentreX = rectX + (rectWidth / 2)
    rectCentreY = rectY + (rectHeight / 2)
    draw.rectangle( [ (rectX, rectY), (rectX + rectWidth, rectY + rectHeight) ], outline="#000000")
    draw.text( (rectCentreX, rectCentreY), rect['name'], fill="#000000")
    # draw front door
    if(rect['name'] == "livingRoom"):
        if(rectX < 10):
            draw.rectangle( [ (rectX-10, rectCentreY-20), (rectX + 10, rectCentreY+20) ], outline="#000000")
        if(rectX >= width-10):
            draw.rectangle( [ (rectX-10, rectCentreY-20), (rectX + 10, rectCentreY+20) ], outline="#000000")
        
        if(rectY < 10):
            draw.rectangle( [ (rectCentreX-20, rectY-10), (rectCentreX + 20, rectY+10) ], outline="#000000")
        if(rectY >= height-10):
            draw.rectangle( [ (rectCentreX-20, rectY-10), (rectCentreX + 20, rectY+10) ], outline="#000000")
   
img.save("img.png", "PNG")



