ip_address = 'localhost' # Enter your IP Address here
project_identifier = 'P3B' # Enter the project identifier i.e. P3A or P3B

# SERVO TABLE CONFIGURATION
short_tower_angle = 315 # enter the value in degrees for the identification tower 
tall_tower_angle = 90 # enter the value in degrees for the classification tower
drop_tube_angle = 180 # enter the value in degrees for the drop tube. clockwise rotation from zero degrees

# BIN CONFIGURATION
# Configuration for the colors for the bins and the lines leading to those bins.
# Note: The line leading up to the bin will be the same color as the bin 

bin1_offset = 0.3 # offset in meters
bin1_color = [1,1,1] # e.g. [1,0,0] for red
bin1_metallic = False

bin2_offset = 0.3
bin2_color = [1,1,0]
bin2_metallic = False

bin3_offset = 0.3
bin3_color = [0,0,1]
bin3_metallic = False

bin4_offset = 0.3
bin4_color = [1,0,1]
bin4_metallic = False
#--------------------------------------------------------------------------------
import sys
sys.path.append('../')
from Common.simulation_project_library import *

hardware = False
if project_identifier == 'P3A':
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    configuration_information = [table_configuration, None] # Configuring just the table
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
else:
    table_configuration = [short_tower_angle,tall_tower_angle,drop_tube_angle]
    bin_configuration = [[bin1_offset,bin2_offset,bin3_offset,bin4_offset],[bin1_color,bin2_color,bin3_color,bin4_color],[bin1_metallic,bin2_metallic, bin3_metallic,bin4_metallic]]
    configuration_information = [table_configuration, bin_configuration]
    QLabs = configure_environment(project_identifier, ip_address, hardware,configuration_information).QLabs
    table = servo_table(ip_address,QLabs,table_configuration,hardware)
    arm = qarm(project_identifier,ip_address,QLabs,hardware)
    bot = qbot(0.1,ip_address,QLabs,project_identifier,hardware)
#--------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------

#   Aarib 
#   Function dispenses random container onto servo table
def dispense_container():
    rand_container_num = random.randint(1,6)                                                                    ##  Generate random number between 1-6 to dispense a random container
    properties = table.dispense_container(rand_container_num, True)                                             ##  Container properties are determined and stored
    print(f"The Material is: {properties[0]}, The mass is: {properties[1]}, The binID is: {properties[2]}\n")
    
    return(properties)                                                                                          ##  returns container properties as list


#   Hareem
#   Function checks whether container should be loaded using 3 pre-determined conditions         
def should_container_load(num_of_containers, total_container_mass, container_properties):
    
    current_binID = container_properties[-1][2]     ##  Sets new bindID to the next containers bin location
    new_binID = container_properties[-2][2]         ##  Sets current bindID to container 1 bin location
    
    if (current_binID == new_binID) and (total_container_mass < 90) and (num_of_containers < 3):    ##  Checks if bindID is same as previous
            return True                                                                             ##  total weight less than 90 and                                               
    else:                                                                                           ##  number of containers less than 3
            return False


#   Hareem  
#   Function Loads and positions containers using Q-arm onto Q-bot
def load_container(container_properties):
    num_of_containers = 0
    total_container_mass = 0

    arm.home()
    arm.rotate_elbow(-35)           ## Loads container on Q-bot
    arm.rotate_shoulder(50)
    time.sleep(0.5)
    arm.control_gripper(45)
    time.sleep(0.5)
    arm.rotate_shoulder(-42)
    arm.rotate_base(-88)
    time.sleep(0.5)
    arm.move_arm(0.019, -0.61, 0.515)  ## Postions container 1 
    time.sleep(0.5)
    arm.control_gripper(-45)
    time.sleep(0.5)
    arm.rotate_shoulder(-20)
    arm.home()

    num_of_containers += 1                                      ##  Adds 1 container to counter once loaded
    total_container_mass += container_properties[-1][1]         ##  Calculates total mass from container properties
    container_properties.append(dispense_container())           ##  Dispenses another container and appends properties into nested list

    print(f"The total mass of all container is {total_container_mass}")
    print(f"The number of containers dispensed is: {num_of_containers}\n")
    
    while should_container_load(num_of_containers, total_container_mass, container_properties):  ## Determines if necessary conditions are met to load containers                                                                                   
        qbot_loading(num_of_containers)  ##  Loads container

        num_of_containers += 1
        total_container_mass += container_properties[-1][1]
        container_properties.append(dispense_container())

        print(f"The total mass of all container is {total_container_mass}")
        print(f"The number of containers dispensed is: {num_of_containers}")


#   Hareem
#   Function loads new containers in different positions
def qbot_loading(num_of_containers):
    arm.home()
    arm.rotate_elbow(-35)
    arm.rotate_shoulder(50)
    time.sleep(0.5)
    arm.control_gripper(45)
    time.sleep(0.5)
    arm.rotate_shoulder(-42)
    arm.rotate_base(-88)
    time.sleep(0.5)

    if num_of_containers == 1:              ## Positions container 2
        arm.move_arm(0.019, -0.51, 0.515)
    elif num_of_containers == 2:            ## Positions container 3
        arm.move_arm(0.019, -0.45, 0.515)
        
    time.sleep(0.5)
    arm.control_gripper(-45)
    time.sleep(0.5)
    arm.rotate_shoulder(-20)
    arm.home()

    
#   Aarib
#   Function returns Q-bot to home postion    
def return_home(bot_home_position):
    print("Returning Home\n")
    current_position = bot.position()                                 ## Sets current postion of Q-bot 
    current_position = [round(elem, 1) for elem in current_position]  ## Rounds position to one decimal place
    current_position = [str(elem) for elem in current_position]       ## Converts back to string
    
    while bot_home_position != current_position:                            ## Uses current and home position of q-bot to go home
        current_position = bot.position()                                   ## Updates position as Q-bot moves
        current_position = [round(elem, 1) for elem in current_position]    
        current_position = [str(elem) for elem in current_position]         

        line_follow()
            
    bot.stop()
    bot.forward_distance(0.03)
    print("Arrived at home postion\n")

#   Aarib 
#   Function transfers container into corresponding bins
def transfer_container(container_properties):
    
    bot.activate_line_following_sensor()        ##  Activate sensors to locate bins
    bot.activate_color_sensor()
    
    target_binID = container_properties[-2][2]  ##  Sets Target bindID to container 1 bin location
   
    if target_binID == "Bin01":                 ##  Set bin numbers equal to their corresponding 
        dropoff_location = [1,1,1]              ##  RGB values which is the Dropoff location
        print("The target bin is: Bin1\n")
        
    elif target_binID == "Bin02":
        dropoff_location = [1,1,0]
        print("The target bin is: Bin2\n")
        
    elif target_binID == "Bin03":
        dropoff_location = [0,0,1]
        print("The target bin is: Bin3\n")
        
    elif target_binID == "Bin04":
        dropoff_location = [1,0,1]
        print("The target bin is: Bin4\n")

    color_coordinates = bot.read_color_sensor()         ##  Sets color coordinates as color sensor reading
                                                    
    while color_coordinates[0] != dropoff_location:     ##  Bot follows line until color coordinates is equal to correct bin
        
        color_coordinates = bot.read_color_sensor()     ##  Updates color coordinates as q-bot moves
        line_follow()
        
    if color_coordinates[0] == dropoff_location:
        time.sleep(0.5)
        bot.forward_distance(0.1)
        print("Depositing Shortly\n")
        deposit_container(dropoff_location, color_coordinates)  ##  Deposits container using dropoff location 
        bot.deactivate_color_sensor()                           ##  and bin color coordinates
        
        

#   Aarib
#   Function allows Q-bot to follow the yellow line path
def line_follow():
    
    if (bot.line_following_sensors() == [1,1]):     ## Go striaght if directly on yellow line
        bot.set_wheel_speed([0.07, 0.07])           
    elif (bot.line_following_sensors() == [0,1]):   ## Turn left
        bot.set_wheel_speed([0.07, 0.04])
    elif (bot.line_following_sensors() == [1,0]):   ## Turn Right
        bot.set_wheel_speed([0.04, 0.07])
    elif (bot.line_following_sensors() == [0,0]):   ## Turn left until back on yellow line
        bot.set_wheel_speed([0.07, 0.04])


#   Hareem        
#   Function dumps container using stepper motor
def bot_dump():
    bot.activate_stepper_motor()  ##  Activating stepper motor
    bot.rotate_hopper(43)
    time.sleep(0.5)
    bot.rotate_hopper(30)
    time.sleep(0.5)
    bot.rotate_hopper(30)
    time.sleep(0.5)
    bot.rotate_hopper(0)
    time.sleep(1)
    bot.deactivate_stepper_motor()


#  Hareem
#  Function deposits containers and postions Q-bot for each bin
def deposit_container(dropoff_location, color_coordinates):

    if dropoff_location == [1,1,1]:
        print("depositing at Bin 1")
                    
    elif dropoff_location == [1,1,0]:
        print("depositing at Bin 2")
                
    elif dropoff_location == ([0,0,1]):
        print("depositing at bin 3")
   
    elif dropoff_location == [1,0,1]:
        print("depositing at bin 4")
        
    bot.rotate(80)              ##  Positioning Q-bot for dump
    time.sleep(1)
    bot.forward_distance(0.15)
    bot.rotate(-80)
    time.sleep(1)
    bot_dump()                  ##  Dump containers
        
    time.sleep(1)               ##  Returns Q-bot to yellow line
    bot.rotate(-80)
    time.sleep(0.5)
    bot.forward_distance(0.15)
    time.sleep(0.5)
    bot.rotate(80)
        
#   Aarib
#   Function goes through program in sequence
def main():
    automate_recycling = True

    container_properties = []
    container_properties.append(dispense_container())   ##  Dispenses and appends container properties into nested list

    bot_home_position = bot.position()                                  ##  Sets current postion as home position
    bot_home_position = [round(elem, 1) for elem in bot_home_position]  ##  Rounds to one decimal
    bot_home_position = [str(elem) for elem in bot_home_position]       ##  Converts back to string

    while automate_recycling:                   
        load_container(container_properties)                    
        transfer_container(container_properties)                
        return_home(bot_home_position)              ##  Return Q-bot home using home position
        
main()





#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
    

    

