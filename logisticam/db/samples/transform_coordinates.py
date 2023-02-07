# %%
import sys
import sqlite3
import numpy as np

database = sqlite3.connect(sys.argv[1])


def transform_coordinates(camera, trans_mat, cam_pose_world) :
    global database
    
    # get all coordinates from database
    cursor = database.cursor()
    nrows = cursor.execute(f"""SELECT Detections.*
        FROM Detections INNER JOIN Frames ON Detections.frame=Frames.id
        WHERE Frames.created_by={camera};""")
    rows = cursor.fetchall()
    print(f"Fetched {nrows} detections from camera {camera}")

    # convert to numpy array
    rows = np.asarray(rows, dtype=np.int64)
    # for mixed column types, try instead:
    # rows = np.fromiter(rows, count=nrows, dtype=('i4,i4,i4'))

    # extract x,y,z positions
    from_cam_position = rows[:,2:]
    print("relative: ", rows[1])
    
    # negative z because cam vertical points down
    from_cam_position[:,2] = -from_cam_position[:,2]

    # transform coordinates and add offset of camera position
    world_position = np.transpose(np.matmul(trans_mat, np.transpose(from_cam_position))) + 100*cam_pose_world  # in cm
    
    # replace original data with transformed coordinates
    rows[:,2:] = world_position
    print("absolute: ", rows[1])
    
    print(f"Updating {len(rows)} detections from camera {camera}...", end=" ", flush=True)
    for row in rows :
        cursor.execute(f"""UPDATE Detections
            SET pos_x={row[2]}, pos_y={row[3]}, pos_z={row[4]}
            WHERE frame={row[0]} AND nb={row[1]};""")
    print("done!\n")
    
    database.commit()
    cursor.close()


# %% 
# LOCAL 5.470 : CAMERA ID 1

# world coordinates of camera and cups
local_origin=np.asarray([44.40,43.23,0])
cam_pose_world=np.asarray([0.1,1.70,2.74]) + local_origin
t1_pose_world=np.asarray([0.83,1.65,2.32]) + local_origin
t2_pose_world=np.asarray([0.52,2.26,2.07]) + local_origin
t3_pose_world=np.asarray([0.83,2.26,2.44]) + local_origin

# world coordinates of cups with respect to camera
world_vec1=t1_pose_world-cam_pose_world
world_vec2=t2_pose_world-cam_pose_world
world_vec3=t3_pose_world-cam_pose_world

world_basis=np.transpose(np.asarray([world_vec1,world_vec2,world_vec3]))

# coordinates of cups in camera basis
cam_vec1=np.asarray([0.38,0.76,0.11])
cam_vec2=np.asarray([-0.29,0.89,0.30])
cam_vec3=np.asarray([-0.14,0.98,-0.12])

# negative z because cam vertical points down
cam_vec1[2]=-cam_vec1[2]
cam_vec2[2]=-cam_vec2[2]
cam_vec3[2]=-cam_vec3[2]

cam_basis=np.transpose(np.asarray([cam_vec1,cam_vec2,cam_vec3]))

# transformation matrix
trans_mat=np.matmul(world_basis, np.linalg.inv(cam_basis))

transform_coordinates(1, trans_mat, cam_pose_world)


# %% 
# LOCAL 5.461 : CAMERA ID 2

# world coordinates of camera and cups
# world frame (bottom right of 5th floor, switch x and y, change sign of new x and add local origin offset)
local_origin=np.asarray([44.08,43.23,0])
cam_pose_world=np.asarray([-0.25,1.59,2.74]) + local_origin
t1_pose_world=np.asarray([-0.55,1.65,2.32])  + local_origin
t2_pose_world=np.asarray([-0.54,2.26,2.07])  + local_origin
t3_pose_world=np.asarray([-0.86,2.26,2.44])  + local_origin

# world coordinates of cups with respect to camera
world_vec1=t1_pose_world-cam_pose_world
world_vec2=t2_pose_world-cam_pose_world
world_vec3=t3_pose_world-cam_pose_world

world_basis=np.transpose(np.asarray([world_vec1,world_vec2,world_vec3]))

# coordinates of cups in camera basis
cam_vec1=np.asarray([-0.08,0.46,0.21])
cam_vec2=np.asarray([0.41,0.84,0.27])
cam_vec3=np.asarray([0.25,0.89,-0.15])

# negative z because cam vertical points down
cam_vec1[2]=-cam_vec1[2]
cam_vec2[2]=-cam_vec2[2]
cam_vec3[2]=-cam_vec3[2]

cam_basis=np.transpose(np.asarray([cam_vec1,cam_vec2,cam_vec3]))

# transformation matrix
trans_mat=np.matmul(world_basis, np.linalg.inv(cam_basis))

transform_coordinates(2, trans_mat, cam_pose_world)


# %% 
# LOCAL 5.462 : CAMERA ID 3

# world coordinates of camera and cups
local_origin=np.asarray([44.08,34.75,0])
cam_pose_world=np.asarray([-0.13,-1.89,2.68]) + local_origin
t1_pose_world=np.asarray([0.06,-2.61,2.32]) + local_origin
t2_pose_world=np.asarray([0.35,-2.92,2.07]) + local_origin
t3_pose_world=np.asarray([0.67,-2.92,2.44]) + local_origin

# world coordinates of cups with respect to camera
world_vec1=t1_pose_world-cam_pose_world
world_vec2=t2_pose_world-cam_pose_world
world_vec3=t3_pose_world-cam_pose_world

world_basis=np.transpose(np.asarray([world_vec1,world_vec2,world_vec3]))

# coordinates of cups in camera basis
cam_vec1=np.asarray([0.31,0.82,-0.03])
cam_vec2=np.asarray([0.25,1.33,-0.07])
cam_vec3=np.asarray([0.03,1.31,-0.49])

# negative z because cam vertical points down
cam_vec1[2]=-cam_vec1[2]
cam_vec2[2]=-cam_vec2[2]
cam_vec3[2]=-cam_vec3[2]

cam_basis=np.transpose(np.asarray([cam_vec1,cam_vec2,cam_vec3]))

# transformation matrix
trans_mat=np.matmul(world_basis, np.linalg.inv(cam_basis))

transform_coordinates(3, trans_mat, cam_pose_world)


# %% 
# LOCAL corridor : CAMERA ID 5

# world coordinates of camera and cups
local_origin=np.asarray([44.08,35.07,0]) 
cam_pose_world=np.asarray([-0.36,1.75,2.73]) + local_origin

#t1_pose_world=np.asarray([0.06,-2.61,2.32]) + local_origin
#t2_pose_world=np.asarray([0.35,-2.92,2.07]) + local_origin
#t3_pose_world=np.asarray([0.67,-2.92,2.44]) + local_origin
#
#
## world coordinates of cups with respect to camera
#world_vec1=t1_pose_world-cam_pose_world
#world_vec2=t2_pose_world-cam_pose_world
#world_vec3=t3_pose_world-cam_pose_world
#
#world_basis=np.transpose(np.asarray([world_vec1,world_vec2,world_vec3]))
#
#
## coordinates of cups in camera basis
#cam_vec1=np.asarray([0.31,0.82,-0.03])
#cam_vec2=np.asarray([0.25,1.33,-0.07])
#cam_vec3=np.asarray([0.03,1.31,-0.49])
#
## negative z because cam vertical points down
#cam_vec1[2]=-cam_vec1[2]
#cam_vec2[2]=-cam_vec2[2]
#cam_vec3[2]=-cam_vec3[2]
#
#cam_basis=np.transpose(np.asarray([cam_vec1,cam_vec2,cam_vec3]))
#
#
# transformation matrix
#trans_mat=np.matmul(world_basis, np.linalg.inv(cam_basis))
trans_mat=np.identity(3)

transform_coordinates(5, trans_mat, cam_pose_world)
