# Squarified Treemap Layout
# Implements algorithm from Bruls, Huizing, van Wijk, "Squarified Treemaps"
#   (but not using their pseudocode)

def normalize_sizes(sizes, dx, dy):
    total_size = sum(sizes.values())
    total_area = dx * dy
    for k,v in sizes.iteritems():
        sizes[k] = float(v)
        sizes[k] = v * total_area / total_size
    #sizes = map(float, sizes)
    #sizes = map(lambda size: size * total_area / total_size, sizes)
    return sizes

def layoutrow(sizes, x, y, dx, dy):
    # generate rects for each size in sizes
    # dx >= dy
    # they will fill up height dy, and width will be determined by their area
    # sizes should be pre-normalized wrt dx * dy (i.e., they should be same units)
    covered_area = sum(sizes.values())
    width = covered_area / dy
    rects = []
    for key,value in sizes.iteritems():
        rects.append({'x': x, 'y': y, 'dx': width, 'dy': value / width, "name": key})
        y += value / width
    return rects

def layoutcol(sizes, x, y, dx, dy):
    # generate rects for each size in sizes
    # dx < dy
    # they will fill up width dx, and height will be determined by their area
    # sizes should be pre-normalized wrt dx * dy (i.e., they should be same units)
    covered_area = sum(sizes.values())
    height = covered_area / dx
    rects = []
    for key,value in sizes.iteritems():
        rects.append({'x': x, 'y': y, 'dx': value / height, 'dy': height, "name": key})
        x += value / height
    return rects

def layout(sizes, x, y, dx, dy):
    return layoutrow(sizes, x, y, dx, dy) if dx >= dy else layoutcol(sizes, x, y, dx, dy)

def leftoverrow(sizes, x, y, dx, dy):
    # compute remaining area when dx >= dy
    covered_area = sum(sizes.values())
    width = covered_area / dy
    leftover_x = x + width
    leftover_y = y
    leftover_dx = dx - width
    leftover_dy = dy
    return (leftover_x, leftover_y, leftover_dx, leftover_dy)

def leftovercol(sizes, x, y, dx, dy):
    # compute remaining area when dx >= dy
    covered_area = sum(sizes.values())
    height = covered_area / dx
    leftover_x = x
    leftover_y = y + height
    leftover_dx = dx
    leftover_dy = dy - height
    return (leftover_x, leftover_y, leftover_dx, leftover_dy)

def leftover(sizes, x, y, dx, dy):
    return leftoverrow(sizes, x, y, dx, dy) if dx >= dy else leftovercol(sizes, x, y, dx, dy)

def worst_ratio(sizes, x, y, dx, dy):
    return max([max(rect['dx'] / rect['dy'], rect['dy'] / rect['dx']) for rect in layout(sizes, x, y, dx, dy)])

def squarify(sizes, x, y, dx, dy):
    # sizes should be pre-normalized wrt dx * dy (i.e., they should be same units)
    # or dx * dy == sum(sizes)
    # sizes should be sorted biggest to smallest
    
    # converts to float
    for values in sizes.itervalues():
        values = float(values)
    #sizes = map(float, sizes)
    
    if len(sizes) == 0:
        return []
    
    if len(sizes) == 1:
        return layout(sizes, x, y, dx, dy)
    
    # figure out where 'split' should be
    i = 1
    while i < len(sizes) and worst_ratio( slicedictbefore(sizes, i), x, y, dx, dy) >= worst_ratio(slicedictbefore(sizes, i+1), x, y, dx, dy):
        i += 1
    current = slicedictbefore(sizes,i)
    remaining = slicedictafter(sizes,i)
    
    (leftover_x, leftover_y, leftover_dx, leftover_dy) = leftover(current, x, y, dx, dy)
    return layout(current, x, y, dx, dy) + \
            squarify(remaining, leftover_x, leftover_y, leftover_dx, leftover_dy)

    
# equivalent to [:t]
def slicedictbefore(d, t):
    newDict = {}
    iteration = 0;
    for k,v in d.iteritems():
        if (iteration > t):
            break
        newDict[k] = float(v)
        iteration += 1
    return newDict
    
# equivalent to [t:]
def slicedictafter(d, t):
    newDict = {}
    iteration = 0;
    for k,v in d.iteritems():
        if (iteration <= t):
            iteration += 1
            continue
        newDict[k] = float(v)
    return newDict