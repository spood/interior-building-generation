import squarify_module
import Image, ImageDraw
import random
import xml.etree.ElementTree as ET

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
                        roomSizes[room] = roomWidth * roomHeight
        
        for room in self.building.optionalRooms:
            if( random.randrange(0,2) == 1):
                for roomTemplate in self.possibleRooms:
                    if(roomTemplate.type == room):
                        roomWidth = random.randrange( roomTemplate.minWidth, roomTemplate.maxWidth)
                        roomHeight = random.randrange( roomTemplate.minHeight, roomTemplate.maxHeight)
                        roomSizes[room] = roomWidth * roomHeight
            
        return roomSizes

XMLreader = XMLBuildingTemplateReader("example_format.xml")
buildings = XMLreader.loadBuildings()
rooms = XMLreader.loadRooms()

# use the house template (at 0), and give it all the rooms we obtained from the XML
house_maker = GenerateBuilding(buildings[0], rooms)
values = house_maker.generateRooms()

x = 0
y = 0
width = 700
height = 433

values = squarify_module.normalize_sizes(values, width, height)

# returns a list of rectangles
rects = squarify_module.squarify(values, x, y, width, height)

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
        print rectX, rectY
        if(rectX < 10):
            draw.rectangle( [ (rectX-10, rectCentreY-20), (rectX + 10, rectCentreY+20) ], outline="#000000")
        if(rectX >= 690):
            draw.rectangle( [ (rectX-10, rectCentreY-20), (rectX + 10, rectCentreY+20) ], outline="#000000")
        
        if(rectY < 10):
            draw.rectangle( [ (rectCentreX-20, rectY-10), (rectCentreX + 20, rectY+10) ], outline="#000000")
        if(rectY >= 420):
            draw.rectangle( [ (rectCentreX-20, rectY-10), (rectCentreX + 20, rectY+10) ], outline="#000000")
   
img.save("img.png", "PNG")



