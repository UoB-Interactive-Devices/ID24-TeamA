import numpy as np
import cv2

# ---------------------------------------------------------------------------------------------------------------------
# GLOBAL VARIABLES
# ---------------------------------------------------------------------------------------------------------------------
# PROJECTOR_ELEVATION (cm): the height of the projector above the projection plane. should be ~(0.7 * table_width).
PROJECTOR_ELEVATION = 115
# TABLE_WIDTH (cm): the width of the projection surface in cm.
TABLE_WIDTH = 120
# TABLE_DEPTH (cm): the depth of the projection surface in cm.
TABLE_DEPTH = 60
# VOXEL_size (cm): the underlying geometry representation is voxels, the w/h/d is the same for each voxel
VOXEL_SIZE = 5
# PROJECTOR_WIDTH (pixels): the resolution width
PROJECTOR_WIDTH = 1920
# PROJECTOR_HEIGHT (pixels): the resolution width
PROJECTOR_DEPTH = 1080
# ---------------------------------------------------------------------------------------------------------------------

def get_grid():
    width_voxels = int(TABLE_WIDTH / VOXEL_SIZE)
    depth_voxels = int(TABLE_DEPTH / VOXEL_SIZE)
    pixels_per_voxel_width = int(PROJECTOR_WIDTH / width_voxels)
    pixels_per_voxel_depth = int(PROJECTOR_DEPTH / depth_voxels)

    im = np.zeros([1080, 1920, 3], dtype=np.uint8)

    for y in range(0, depth_voxels):
        for x in range(0, width_voxels):
            start_x = x * pixels_per_voxel_width
            start_y = y * pixels_per_voxel_depth
            end_x = start_x + pixels_per_voxel_width
            end_y = start_y + pixels_per_voxel_depth

            cv2.rectangle(im, (start_x, start_y), (end_x, end_y), [255, 255, 255], 2)
    return im


def convert_voxel_to_world_cm(x, y, z):
    voxel_x_cm = x * VOXEL_SIZE
    voxel_y_cm = y * VOXEL_SIZE
    voxel_z_cm = z * VOXEL_SIZE
    return voxel_x_cm, voxel_y_cm, voxel_z_cm


class Face:
    def __init__(self, bl, br, tl, tr):
        self.bl_world = bl
        self.br_world = br
        self.tl_world = tl
        self.tr_world = tr

        self.bl_pix, self.br_pix, self.tl_pix, self.tr_pix = self.compute_projection()
    def compute_projection(self):
        bl_pix = rasterize_point_from_world_to_pixel(self.bl_world)
        br_pix = rasterize_point_from_world_to_pixel(self.br_world)
        tl_pix = rasterize_point_from_world_to_pixel(self.tl_world)
        tr_pix = rasterize_point_from_world_to_pixel(self.tr_world)


        return bl_pix, br_pix, tl_pix, tr_pix


class Block:

    def __init__(self, voxels_occupied, projection_size):
        # will create a mask of where the model casts "shadows" from the projectors perspective
        # self.buffer = get_grid()
        self.buffer = np.zeros([1080, 1920, 3], dtype=np.uint8)
        for voxel in voxels_occupied:
            # compute faces, given each voxel is a (x,y,z) triple, we can convert a voxel to 6 faces
            # the constructor will automatically compute the pixel projections
            faces = []
            voxel_x_cm, voxel_y_cm, voxel_z_cm = convert_voxel_to_world_cm(voxel[0], voxel[1], voxel[2])

            # bot
            faces.append(Face(
                np.array([voxel_x_cm, voxel_y_cm, voxel_z_cm]),
                np.array([voxel_x_cm + VOXEL_SIZE, voxel_y_cm, voxel_z_cm]),
                np.array([voxel_x_cm, voxel_y_cm, voxel_z_cm + VOXEL_SIZE]),
                np.array([voxel_x_cm + VOXEL_SIZE, voxel_y_cm, voxel_z_cm + VOXEL_SIZE]),
            ))
            # top
            faces.append(Face(
                np.array([voxel_x_cm, voxel_y_cm + VOXEL_SIZE, voxel_z_cm]),
                np.array([voxel_x_cm + VOXEL_SIZE, voxel_y_cm + VOXEL_SIZE, voxel_z_cm]),
                np.array([voxel_x_cm, voxel_y_cm + VOXEL_SIZE, voxel_z_cm + VOXEL_SIZE]),
                np.array([voxel_x_cm + VOXEL_SIZE, voxel_y_cm + VOXEL_SIZE, voxel_z_cm + VOXEL_SIZE]),
            ))
            faces.append(Face(
                np.array([voxel_x_cm, voxel_y_cm, voxel_z_cm]),
                np.array([voxel_x_cm, voxel_y_cm, voxel_z_cm + VOXEL_SIZE]),
                np.array([voxel_x_cm, voxel_y_cm + VOXEL_SIZE, voxel_z_cm]),
                np.array([voxel_x_cm, voxel_y_cm + VOXEL_SIZE, voxel_z_cm + VOXEL_SIZE]),
            ))
            faces.append(Face(
                np.array([voxel_x_cm + VOXEL_SIZE, voxel_y_cm, voxel_z_cm]),
                np.array([voxel_x_cm + VOXEL_SIZE, voxel_y_cm, voxel_z_cm + VOXEL_SIZE]),
                np.array([voxel_x_cm + VOXEL_SIZE, voxel_y_cm + VOXEL_SIZE, voxel_z_cm]),
                np.array([voxel_x_cm + VOXEL_SIZE, voxel_y_cm + VOXEL_SIZE, voxel_z_cm + VOXEL_SIZE]),
            ))
            faces.append(Face(
                np.array([voxel_x_cm, voxel_y_cm, voxel_z_cm]),
                np.array([voxel_x_cm + VOXEL_SIZE, voxel_y_cm, voxel_z_cm]),
                np.array([voxel_x_cm + VOXEL_SIZE, voxel_y_cm + VOXEL_SIZE, voxel_z_cm]),
                np.array([voxel_x_cm + VOXEL_SIZE, voxel_y_cm, voxel_z_cm]),
            ))
            faces.append(Face(
                np.array([voxel_x_cm, voxel_y_cm, voxel_z_cm + VOXEL_SIZE]),
                np.array([voxel_x_cm + VOXEL_SIZE, voxel_y_cm, voxel_z_cm + VOXEL_SIZE]),
                np.array([voxel_x_cm + VOXEL_SIZE, voxel_y_cm + VOXEL_SIZE, voxel_z_cm + VOXEL_SIZE]),
                np.array([voxel_x_cm + VOXEL_SIZE, voxel_y_cm, voxel_z_cm + VOXEL_SIZE]),
            ))

            # update buffer
            for face in faces:
                a3 = np.array([[face.tl_pix, face.bl_pix, face.br_pix, face.tr_pix]], dtype=np.int32)
                # for testing, colour based on normal vec of face
                normal = np.cross((face.tr_world - face.tl_world), (face.bl_world - face.tl_world))
                col = 255 * (normal / np.linalg.norm(normal))
                col = [255, 255, 255]
                # col = [np.random.randint(10, 255), np.random.randint(10, 255), np.random.randint(10, 255)]

                # update frame buffer
                cv2.fillPoly(
                        self.buffer,
                        a3,
                        col
                    )


    def get_buffer(self):
        return self.buffer


def rasterize_point_from_world_to_pixel(world_point):
    # will project a world point to the table from the perspective of the projector then convert to pixel coordinates
    # if the point is out of bounds, -1 will be returned. currently no error checking for negative rasterizations
    # compute ray from projector to point
    ray_origin = world_point
    ray_direction = world_point - np.array([(TABLE_WIDTH / 2) - 2, PROJECTOR_ELEVATION, TABLE_DEPTH])
    # solve for point at y = 0, (x,y,z) = origin + (t * direction) so find t such that origin_y + direction_y = 0
    t_solution = -ray_origin[1] / ray_direction[1]
    projected_point = ray_origin + (t_solution * ray_direction)

    # convert point to pixels, compute ratio of world space them apply to screen space
    x_ratio = projected_point[0] / TABLE_WIDTH
    z_ratio = projected_point[2] / TABLE_DEPTH
    x_pixels = min(PROJECTOR_WIDTH, max(0, int(x_ratio * PROJECTOR_WIDTH)))
    z_pixels = min(PROJECTOR_DEPTH, max(0, int(z_ratio * PROJECTOR_DEPTH)))

    #if x_ratio < 0 or z_ratio < 0 or x_ratio > 1 or z_ratio > 1:
        #print(
            #f"ERROR: projection out of bounds for point {world_point}, it projects to pixel ({x_pixels},{z_pixels}) on the projector")

    return np.array([x_pixels, z_pixels])


# takes in a voxel binary array then computes a shadow map based on the locations
# this is a very slow approach and could be done with a dynamic masking algorithm each time a new block is added/removed
# but due to time constraints and the simplicity of the scene, it should be fine.
def update_blocks(occupied_voxels):
    temp = Block(occupied_voxels, [PROJECTOR_WIDTH, PROJECTOR_DEPTH])
    mask = temp.get_buffer()
    return mask


def main():
    voxel_grid = np.zeros((int(TABLE_WIDTH / VOXEL_SIZE), 50, int(TABLE_DEPTH / VOXEL_SIZE)))

    # from tl to br
    # voxel_grid[5:10, 0:5, 10:16] = 1
    # voxel_grid[15:22, 0:2, 0:1] = 1
    # voxel_grid[8:17, 0:8, 7:9] = 1
    voxel_grid[0:4, 0:4, 0:4] = 1
    curr_x = 0
    curr_z = 0

    indices = np.transpose((voxel_grid == 1).nonzero())

    # for each voxel filled
    buffer = update_blocks(indices)

    cv2.namedWindow("res", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("res", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty("res", cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
    cv2.imshow("res", buffer)

    exit_program = False

    # main loop
    while not exit_program:
        k = cv2.waitKey(33)
        if k == 27:  # Esc key to stop
            exit_program = True

        if k == 119: # Up
            voxel_grid.fill(0)
            curr_z -= 1
            voxel_grid[curr_x:curr_x + 4, 0:4, curr_z:curr_z + 4] = 1
            indices = np.transpose((voxel_grid == 1).nonzero())
            buffer = update_blocks(indices)
            cv2.imshow("res", buffer)

        if k == 115:  # Down
            voxel_grid.fill(0)
            curr_z += 1
            voxel_grid[curr_x:curr_x + 4, 0:4, curr_z:curr_z + 4] = 1
            indices = np.transpose((voxel_grid == 1).nonzero())
            buffer = update_blocks(indices)
            cv2.imshow("res", buffer)

        if k == 97: # Left
            voxel_grid.fill(0)
            curr_x -= 1
            voxel_grid[curr_x:curr_x + 4, 0:4, curr_z:curr_z + 4] = 1
            indices = np.transpose((voxel_grid == 1).nonzero())
            buffer = update_blocks(indices)
            cv2.imshow("res", buffer)

        if k == 100: # Right
            voxel_grid.fill(0)
            curr_x += 1
            voxel_grid[curr_x:curr_x + 4, 0:4, curr_z:curr_z + 4] = 1
            indices = np.transpose((voxel_grid == 1).nonzero())
            buffer = update_blocks(indices)
            cv2.imshow("res", buffer)

        if k == 116: # t key pressed
            # compute voxel grid
            voxel_grid.fill(0)
            voxel_grid[curr_x:curr_x + 4, 0:4, curr_z:curr_z + 4] = 1
            indices = np.transpose((voxel_grid == 1).nonzero())
            buffer = update_blocks(indices)

            # load tex and grid
            grid = get_grid()
            tex = cv2.imread(r"C:\Users\georg\Documents\InteractiveDevices\textures\lizard_skin.jpg")
            tex = cv2.resize(tex, (1920, 1080))

            # use buffer as mask to blend between grid and tex
            masked_tex = cv2.bitwise_and(buffer, tex)
            masked_grid = cv2.bitwise_and(cv2.bitwise_not(buffer), grid)
            blended_res = cv2.add(masked_grid, masked_tex)

            cv2.imshow("res", blended_res)

        if k == 105: # i key pressed
            # compute voxel grid
            voxel_grid.fill(0)
            voxel_grid[7:8, 0:6, 4:5] = 1
            indices = np.transpose((voxel_grid == 1).nonzero())
            buffer = update_blocks(indices)

            # load tex and grid
            grid = get_grid()
            tex = cv2.imread(r"C:\Users\georg\Documents\InteractiveDevices\textures\lizard_skin.jpg")
            tex = cv2.resize(tex, (1920, 1080))

            # use buffer as mask to blend between grid and tex
            masked_tex = cv2.bitwise_and(buffer, tex)
            masked_grid = cv2.bitwise_and(cv2.bitwise_not(buffer), grid)
            blended_res = cv2.add(masked_grid, masked_tex)

            # show info panel
            # load info image
            info_image = cv2.imread(r"C:\Users\georg\Documents\InteractiveDevices\textures\info.png")
            info_height, info_width, _ = np.shape(info_image)

            info_pos_x, info_pos_y = 500, 100
            blended_res[info_pos_y:info_pos_y + info_height, info_pos_x:info_pos_x + info_width] = info_image

            cv2.imshow("res", blended_res)


def start_projection():
    grid = get_grid()
    cv2.namedWindow("proj", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("proj", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setWindowProperty("proj", cv2.WND_PROP_ASPECT_RATIO, cv2.WINDOW_KEEPRATIO)
    cv2.imshow("proj", grid)
    cv2.waitKey(1)
    
def update_projection(voxel_grid):
    print('updating')
    # compute voxel grid
    indices = np.transpose((voxel_grid == 1).nonzero())
    for i in indices:
        i[2] = 12 - i[2]
    print(indices)
    buffer = update_blocks(indices)

    # load tex and grid
    grid = get_grid()
    tex = cv2.imread(r"C:\Users\purci\OneDrive\Documents\GitHub\ID24-TeamA\software\lizard_skin.jpg")
    tex = cv2.resize(tex, (1920, 1080))

    # use buffer as mask to blend between grid and tex
    masked_tex = cv2.bitwise_and(buffer, tex)
    masked_grid = cv2.bitwise_and(cv2.bitwise_not(buffer), grid)
    blended_res = cv2.add(masked_grid, masked_tex)
    cv2.imshow("proj", blended_res)
    cv2.waitKey(1)




