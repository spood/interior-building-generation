import squarify_module
import Image, ImageDraw
import random
import xml.etree.ElementTree as ET
import numpy
import itertools
import math
import copy

imgVar = 0

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
        
class Room:
    def __init__(self, type, x, y, width, height, furniture):
        self.type = type
        self.x = x
        self.y = y
        self.width = width
        self.height = height
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
    
def drawBuilding(floor, width, height, rooms):
    img = Image.new("RGB", (width * tile_size + tile_size + 20, height * tile_size + tile_size + 20), "white")
    draw = ImageDraw.Draw(img)
    for w in range(width):
        for h in range(height):
            if( floor[w][h] == 1):
                pointX = (w*tile_size) + (tile_size / 2)
                pointY = (h*tile_size) + (tile_size / 2)
                draw.rectangle( [ (pointX,pointY ), (pointX + tile_size, pointY + tile_size) ], outline="#000000")
                #draw.text( (pointX + tile_size/2, pointY + tile_size/2), str(w) + "," + str(h), fill="#000000")
            if (floor[w][h] == -1):
                pointX = (w*tile_size) + (tile_size / 2)
                pointY = (h*tile_size) + (tile_size / 2)
                draw.rectangle( [ (pointX,pointY ), (pointX + tile_size, pointY + tile_size) ], outline="#FF0000")
                #draw.text( (pointX + tile_size/2, pointY + tile_size/2), str(w) + "," + str(h), fill="#000000")
    for room in rooms:
        #for w,h in room.tiles:
        #    draw.rectangle( [ (w * tile_size,h * tile_size ), (w * tile_size + tile_size, h * tile_size + tile_size) ], outline="#000000")
        draw.text( (room.x * tile_size + room.width * tile_size/2, room.y * tile_size + room.height * tile_size/2), room.type, fill="#000000")
    global imgVar
    img.save( str(imgVar) + ".png", "PNG")
    imgVar += 1
        
def removeTile(position, rooms):
    for room in rooms:
        if position in room.tiles:
            print "remove",position
            room.tiles.remove(position)
            
def removeDoubleRows(floor, width, height, generatedRooms):
    # remove any double rows that crop up from converting float to int
    for room in generatedRooms:
        # check left side of room if a wall is there
        newX = room.x
        for h in range(room.y, room.y + room.height):
            if(room.x > 0):
                if(floor[ room.x - 1][h] == 1):
                    print room.type,"found left side-",room.x-1,h
                    if( (room.x,h) in room.tiles and (room.x-1,h) not in room.tiles):
                        if(room.y != h and room.y + room.height != h and floor[room.x-2][h] != 1 and floor[room.x+1][h] != 1):
                            floor[room.x][h] = 0
                            removeTile( (room.x,h),generatedRooms )
                        room.tiles.append( (room.x-1,h) )
                        newX = room.x-1
                if(floor[ room.x + 1][h] == 1):
                    print room.type,"found left side+",room.x+1,h
                    if( (room.x,h) in room.tiles):
                        print "height",room.y,room.height,h
                        if(room.y != h and room.y + room.height != h and floor[room.x+2][h] != 1 ):
                            floor[room.x][h] = 0
                            removeTile( (room.x,h),generatedRooms )
                        #increasedWidth = True
        #if(newX != room.x):
        #    room.x = newX
        #    room.width += 1
        # check right side of room if a wall is there
        increasedWidth = False
        for h in range(room.y, room.y + room.height):
            if(room.x + room.width < width):
                if(floor[ room.x + room.width + 1][h] == 1):
                    print room.type,"found right side",room.x + room.width + 1,h, "with x pos",room.x,"width",room.width
                    if( (room.x + room.width,h) in room.tiles and (room.x + room.width+1,h) not in room.tiles):
                        if(room.y != h and room.y + room.height != h and floor[room.x+room.width+2][h] != 1 and floor[room.x+room.width-1][h] != 1):
                            floor[room.x+room.width][h] = 0
                            removeTile( (room.x+room.width,h),generatedRooms )
                        room.tiles.append( (room.x+room.width+1,h) )
                        increasedWidth = True
                if(floor[ room.x + room.width - 1][h] == 1):
                    print room.type,"found right side-1",room.x + room.width - 1,h, "with x pos",room.x,"width",room.width,"y",room.y,"h",h
                    if( (room.x + room.width,h) in room.tiles):
                        if(room.y != h and room.y + room.height != h and floor[room.x+room.width-2][h] != 1):
                            floor[room.x+room.width][h] = 0
                            removeTile( (room.x+room.width,h),generatedRooms )
                        #increasedWidth = True
        #if(increasedWidth):
        #    room.width += 1
        # check top side of room if a wall is there
        newY = room.y
        for w in range(room.x, room.x + room.width):
            if(room.y > 0):
                if(w == 18):
                    print "comparing",w,room.y-1
                if(floor[w][room.y - 1] == 1):
                    print room.type,"found top side",w,room.y - 1,room.x,room.x+room.width
                    if( (w,room.y) in room.tiles and (w,room.y - 1) not in room.tiles):
                        if(room.x != w and room.x + room.width != w  and floor[w][room.y-2] != 1 and floor[w][room.y+1] != 1):
                            floor[w][room.y] = 0
                            removeTile( (w,room.y),generatedRooms )
                        room.tiles.append( (w,room.y-1) )
                        newY = room.y -1
                if(floor[w][room.y + 1] == 1):
                    if( (w,room.y) in room.tiles ):
                        if(room.x != w and room.x + room.width != w and floor[w][room.y+2] != 1):
                            floor[w][room.y] = 0
                            removeTile( (w,room.y),generatedRooms )
                        #increasedHeight = True
        #if(newY != room.y):
        #    room.y = newY
        #    room.height += 1
        # check bottom side of room if a wall is there
        increasedHeight = False
        for w in range(room.x, room.x + room.width):
            if(room.y + room.height < height):
                if(floor[w][room.y+room.height + 1] == 1):
                    print room.type,"found bottom side",w,room.y+room.height + 1, "room.x",room.x,"w",w
                    if( (w,room.y+room.height) in room.tiles and (w,room.y+room.height + 1) not in room.tiles):
                        if(room.x != w and room.x + room.width != w and floor[w][room.y+room.height+2] != 1 and floor[w][room.y+room.height-1] != 1):
                            floor[w][room.y+room.height] = 0
                            removeTile( (w,room.y+room.height),generatedRooms )
                        room.tiles.append( (w,room.y+room.height+1) )
                        increasedHeight = True
                if(floor[w][room.y+room.height - 1] == 1):
                    print room.type,"found bottom side",w,room.y - 1
                    if( (w,room.y+room.height) in room.tiles ):
                        if(room.x != w and room.x + room.width != w and floor[w][room.y+room.height-2] != 1):
                            floor[w][room.y+room.height] = 0
                            removeTile( (w,room.y+room.height),generatedRooms )
                        #increasedHeight = True
        #if(increasedHeight):
        #    room.height += 1

def pathTouchesRooms(path,rooms):
    for room in rooms:
        inRoom = False
        for pos in path:
            if pos in room.tiles:
                inRoom = True
                continue
        if inRoom == False:
            return False
    return True
    
def distance(p1,p2):
    return math.hypot(p2[0]-p1[0], p2[1]-p1[1])
    
def calculateCorridorPath(floor, width, height, rooms, startRoom):
    roomsNotTouchingStartRoom = []
    for room in rooms:
        inRoom = False
        for pos in room.tiles:
            if pos in startRoom.tiles:
                inRoom = True
                floor[pos[0]][pos[1]] = 0
        if inRoom == False:
            roomsNotTouchingStartRoom.append(room)
    for room in roomsNotTouchingStartRoom:
        print "not touching",room.type
            
    for w in range(0,width+1):
        print "remove",w,0
        floor[w][0] = 0
        removeTile((w,0),rooms)
        floor[w][height] = 0
        removeTile((w,height),rooms)
            
    for h in range(0,height+1):
        print "remove",0,h
        floor[0][h] = 0
        removeTile((0,h),rooms)
        floor[width][h] = 0
        removeTile((width,h),rooms)
        
    #floor[13][8] = 1
    # get start point (the spot closest to the centre of the floor, from the start room)
    floorMid = (width/2,height/2)
    closestPos = None
    closestDist = 999999
    lastPos = None
    for pos in startRoom.tiles:
        dist = distance(pos,floorMid)
        if(dist < closestDist):
            lastPos = closestPos
            closestPos = pos
            closestDist = dist
    
    startPoint = closestPos
    floor[lastPos[0]][lastPos[1]] = 1
    availablePaths = []
    path = [startPoint]
    stack = [path]
    firstRun = True
    # pathfinding
    while(len(stack) > 0):
        path = stack.pop()
        pos = path.pop()
        # did we find an exit
        if( floor[pos[0]][pos[1]] == 1 ):
            if( pos[0] == 1 or pos[0] == width or pos[1] == 1 or pos[1] == height-1):
                print "found exit at",pos[0],pos[1]
                foundPath = []
                foundPath.append( (pos[0],pos[1]) )
                for w in range(width):
                    for h in range(height):
                        if floor[w][h] == -1:
                            foundPath.append( (w,h) )
                
                # if it touches every square
                if(pathTouchesRooms(foundPath,roomsNotTouchingStartRoom)):
                    print "this path can work", imgVar
                    availablePaths.append(foundPath)
                drawBuilding(floor,width+1,height+1, rooms)
        # search for available squares around each tile
        if( ((floor[pos[0]][pos[1]] != 0) and (floor[pos[0]][pos[1]] != -1)) or firstRun):
            firstRun = False
            floor[pos[0]][pos[1]] = -1
            newpath = list(path)
            newpath.append( (pos[0] + 1, pos[1]) )
            stack.append(newpath)
            newpath = list(path)
            newpath.append( (pos[0] - 1, pos[1]) )
            stack.append(newpath)
            newpath = list(path)
            newpath.append( (pos[0], pos[1] + 1) )
            stack.append(newpath)
            newpath = list(path)
            newpath.append( (pos[0], pos[1] - 1) )
            stack.append(newpath)
            
    # return shortest path
    availablePaths.sort(key=len)
    return availablePaths[0]
    
def applyCorridorPath(floor, rooms, corridorPath, startRoom):
    startPos = corridorPath[ len(corridorPath)-1]
    print startPos
    for x,y in corridorPath:
        # TODO update the tiles for each room affected...
        floor[x][y] = 0
        if( (x,y) not in startRoom.tiles):
            if (x-1,y) not in corridorPath:
                floor[x-1][y] = 1
            if (x+1,y) not in corridorPath:
                floor[x+1][y] = 1
            if (x,y-1) not in corridorPath:
                floor[x][y-1] = 1
            if (x,y+1) not in corridorPath:
                floor[x][y+1] = 1
        
    
#random.seed(6)
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
floor = [[[0] for ni in range(height+1)] for mi in range(width+1)]
for w in range(width):
    for h in range(height):
        floor[w][h] = 0

values = squarify_module.normalize_sizes(values, widthtotal, heighttotal)

# returns a list of rectangles
rects = squarify_module.padded_squarify(values, x, y,widthtotal, heighttotal)

img = Image.new("RGB", (widthtotal + tile_size + 20, heighttotal + tile_size + 20), "white")
draw = ImageDraw.Draw(img)

startRoom = None
generatedRooms = []
# place rooms
for rect in rects:
    drawBuilding(floor, width, height, generatedRooms)
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
        
    roomFurniture = []
    for roomTemplate in house_maker.possibleRooms:
        if(roomTemplate.type == rect['name']):
            roomFurniture = list(roomTemplate.furniture)
    newRoom = Room(rect['name'], rectX, rectY, rectWidth, rectHeight, roomFurniture)
    newRoom.tiles = []
    generatedRooms.append( newRoom );
    
    # top side
    for w in range(0,rectWidth):
        floor[rectX + w][rectY] = 1
        newRoom.tiles.append( (rectX + w, rectY) )
    # bottom side
    for w in range(0,rectWidth):
        floor[rectX + w][rectY + rectHeight] = 1
        newRoom.tiles.append( (rectX + w, rectY + rectHeight) )
    # left side
    for h in range(0,rectHeight+1):
        floor[rectX][rectY + h] = 1
        newRoom.tiles.append( (rectX, rectY + h) )
    # right side
    for h in range(0,rectHeight+1):
        floor[rectX + rectWidth][rectY + h] = 1
        newRoom.tiles.append( (rectX + rectWidth, rectY + h) )
    #print rectX, rectY
    #draw.rectangle( [ (rectX, rectY), (rectX + rectWidth, rectY + rectHeight) ], outline="#000000")
    removeDoubleRows(floor, width, height, generatedRooms)
    # draw front door
    if(rect['name'] == "livingRoom"):
        startRoom = newRoom
        if(rectX < 3):
            draw.rectangle( [ (rectX*tile_size, rectCentreY*tile_size), (tile_size, rectCentreY*tile_size+tile_size) ], outline="#000000")
        if(rectX >= width-3):
            draw.rectangle( [ (rectX*tile_size, rectCentreY*tile_size), (tile_size, rectCentreY*tile_size+tile_size) ], outline="#000000")
        
        if(rectY < 3):
            draw.rectangle( [ (rectCentreX*tile_size, rectY*tile_size), (rectCentreX*tile_size+tile_size, tile_size) ], outline="#000000")
        if(rectY >= height-3):
            draw.rectangle( [ (rectCentreX*tile_size0, rectY*tile_size), (rectCentreX*tile_size+tile_size, tile_size) ], outline="#000000")
    #if(len(generatedRooms) == 7):
    #    break




export_TMX(floor, width, height)

drawBuilding(floor, width, height, generatedRooms)

corridorPath = calculateCorridorPath(copy.deepcopy(floor), width-1, height-1, generatedRooms, startRoom)

applyCorridorPath(floor,rooms,corridorPath, startRoom)

drawBuilding(floor, width, height, generatedRooms)
