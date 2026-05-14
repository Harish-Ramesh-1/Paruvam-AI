GRID_SIZE = 0.1

def get_cell_id(lat, lon):
    lat_cell = int(lat / GRID_SIZE)
    lon_cell = int(lon / GRID_SIZE)

    return f"{lat_cell}_{lon_cell}"
