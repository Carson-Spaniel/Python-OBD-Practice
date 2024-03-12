import pygame
import obd
import time
import random
import math

DEV = True

# # Print out the commands
# for command_name in obd.commands.__dict__.values():
#     print(command_name)

# Initialize Pygame
pygame.init()

# Screen dimensions for a landscape 3.5-inch display
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 480
FPS = 30

# Colors
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (180, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Fonts
font_large = pygame.font.Font("./digital-7.ttf", 120)
font_medium = pygame.font.Font("./digital-7.ttf", 48)
font_small = pygame.font.Font("./digital-7.ttf", 36)

connect = False

if not DEV:
    for i in range(3):
        print('\nAttempting to connect...')

        # Connect to the OBD-II adapter
        connection = obd.OBD(portstr='COM5')

        # Print a message indicating connection
        if connection.is_connected():
            print("Connected to OBD-II adapter. Ready to log data.")
            connect = True
            break
        else:
            print("Could not connect to OBD-II adapter.")

    if not connect:
        print('Failed. Exiting...')
        exit()

# Function to calculate MPG
def calculate_mpg(speed, maf):
    if speed == 0:
        return 0
    gph = (maf / 14.7) * 0.746  # grams per hour to gallons per hour
    if DEV:
        mpg = speed / gph
    else:
        speed.to('mile/hour') / gph
    return round(mpg,1)

# Function to save max horsepower data to a file
def save_rpm(RPM_MAX, SHIFT):
    with open("RPM.txt", "w") as file:
        file.write(f"{RPM_MAX},{SHIFT}")

# Function to load max horsepower data from a file
def load_rpm():
    try:
        with open("RPM.txt", "r") as file:
            data = file.read().split(",")
            max = int(data[0])
            shift = int(data[1])
    except Exception as e:
        print(e)
        max = 8000
        shift = 6500

    return max, shift

RPM_MAX,SHIFT = load_rpm()

# Function to calculate horsepower
def calculate_horsepower(torque, rpm):
    return (torque * rpm) / 5252

# Function to draw text on screen
def draw_text(screen, text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

# Function to display Chevrolet logo animation
def display_logo(screen):
    logo = pygame.image.load("chevy.jpg").convert_alpha()
    logo_rect = logo.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    # Animation variables
    rotation_angle = 0
    scale = 0.2
    animation_duration = 5  # 5 seconds
    start_time = time.time()

    while time.time() - start_time < animation_duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        screen.fill(BLACK)

        # Rotate and scale the logo
        rotated_logo = pygame.transform.rotozoom(logo, rotation_angle, scale)
        rotated_rect = rotated_logo.get_rect(center=logo_rect.center)
        screen.blit(rotated_logo, rotated_rect)

        draw_text(screen, "Developed by Carson Spaniel", font_small, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)

        pygame.display.flip()

        scale += 0.004

        pygame.time.Clock().tick(FPS)

# Main function for the Pygame interface
def main():
    global RPM_MAX
    global SHIFT
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Horsepower and RPM Display")
    clock = pygame.time.Clock()

    pages = ["RPM", "MPG", "Both"] #, "Off"
    current_page = 0

    # Load the last visited page
    try:
        with open("last_visited_page.txt", "r") as file:
            current_page = int(file.read())
            if current_page < 0 or current_page >= len(pages):
                current_page = 0
    except FileNotFoundError:
        current_page = 0

    logging = True

    if not DEV:
        # Display Chevrolet logo for 5 seconds
        display_logo(screen)

    if DEV:
        rpm = 650
        fuel_level = random.randint(0,100)
        speed = 10
        maf = 6
    while logging:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    # Check top left corner for page change
                    if event.pos[0] < SCREEN_WIDTH // 10 and event.pos[1] < SCREEN_HEIGHT // 10:
                        current_page = (current_page - 1) % len(pages)
                    # Check top right corner for page change
                    elif event.pos[0] > SCREEN_WIDTH - SCREEN_WIDTH // 10 and event.pos[1] < SCREEN_HEIGHT // 10:
                        current_page = (current_page + 1) % len(pages)
                    else:
                        if pages[current_page] == "RPM":
                            # Check for collision with increase rectangle
                            if event.pos[0] < SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.1 and event.pos[0] > SCREEN_WIDTH * 0.2+25 and event.pos[1] < SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and event.pos[1] > SCREEN_HEIGHT*.3:
                                RPM_MAX += 100  # Increase RPM_MAX by 100

                                if RPM_MAX > 50000:
                                    RPM_MAX = 50000

                                # Save the new max horsepower data
                                save_rpm(RPM_MAX,SHIFT)

                            # Check for collision with decrease rectangle
                            elif event.pos[0] < SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.1 and event.pos[0] > SCREEN_WIDTH * 0.2+25 and event.pos[1] < SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and event.pos[1] > SCREEN_HEIGHT-SCREEN_HEIGHT*.3:
                                RPM_MAX -= 100  # Decrease RPM_MAX by 100
                                if RPM_MAX == 0:
                                    RPM_MAX = 100

                                if SHIFT > RPM_MAX:
                                    SHIFT = RPM_MAX

                                # Save the new max horsepower data
                                save_rpm(RPM_MAX,SHIFT)

                            # Check for collision with increase rectangle
                            elif event.pos[0] < SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.1 and event.pos[0] > SCREEN_WIDTH * 0.7-25 and event.pos[1] < SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and event.pos[1] > SCREEN_HEIGHT*.3:
                                SHIFT += 100  # Increase SHIFT by 100

                                if SHIFT > RPM_MAX:
                                    SHIFT = RPM_MAX

                                # Save the new max horsepower data
                                save_rpm(RPM_MAX,SHIFT)

                            # Check for collision with decrease rectangle
                            elif event.pos[0] < SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.1 and event.pos[0] > SCREEN_WIDTH * 0.7-25 and event.pos[1] < SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.1 and event.pos[1] > SCREEN_HEIGHT-SCREEN_HEIGHT*.3:
                                SHIFT -= 100  # Decrease SHIFT by 100

                                if SHIFT == 0:
                                    SHIFT = 100

                                # Save the new max horsepower data
                                save_rpm(RPM_MAX,SHIFT)

        if DEV:
            rpm = random.randint(max(0,rpm-20), min(rpm+27,RPM_MAX))
            speed = random.randint(max(0,speed-1), min(speed+1,80))
            maf = random.randint(max(1,maf-1), min(maf+1,80))
            mpg = calculate_mpg(speed, maf)
            if fuel_level<=0:
                fuel_level=100
            fuel_level -= .1
        else:
            # Query for RPM and Torque
            response_rpm = connection.query(obd.commands.RPM)
            response_fuel_level = connection.query(obd.commands.FUEL_LEVEL)
            speed_response = connection.query(obd.commands.SPEED)  # Vehicle speed
            maf_response = connection.query(obd.commands.MAF)      # Mass Air Flow

            if speed_response.success and maf_response.success:
                speed = speed_response.value.to('mile/hour')
                maf = maf_response.value.to('gram/second')
                mpg = calculate_mpg(speed.magnitude, maf.magnitude)

            if not response_rpm.is_null():
                rpm = round(response_rpm.value.magnitude,0)

            if not response_fuel_level.is_null():
                fuel_level = response_fuel_level.value.magnitude

        # Clear the screen
        screen.fill(BLACK)

        # if rpm > SHIFT - (200):
        #     screen.fill(PURPLE)

        # Draw page buttons
        draw_text(screen, "<", font_medium, WHITE, SCREEN_WIDTH*.05, SCREEN_HEIGHT * .05)
        draw_text(screen, ">", font_medium, WHITE, SCREEN_WIDTH -SCREEN_WIDTH*.05, SCREEN_HEIGHT * .05)

        # Draw page indicators (circles)
        circle_radius = 5
        circle_spacing = 10

        # Calculate total width occupied by circles
        total_circle_width = (len(pages)) * (2 * circle_radius + circle_spacing) + circle_spacing + (2*circle_radius)

        # Calculate starting position to center horizontally
        start_x = (SCREEN_WIDTH - total_circle_width) // 2
        circle_x = start_x + circle_radius + circle_spacing
        circle_y = SCREEN_HEIGHT - circle_radius - circle_spacing

        # Calculate the percentage of RPM relative to RPM_MAX
        rpm_percentage = min(1.0, rpm / RPM_MAX)  # Ensure it's between 0 and 1
        
        # Calculate the height of the filled portion based on percentage
        filled_height = math.floor((SCREEN_HEIGHT*.88) * rpm_percentage)

        # Draw the filled portion
        color = GREEN if rpm<SHIFT else RED
        pygame.draw.rect(screen, color, (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT - filled_height, SCREEN_WIDTH * 0.2, filled_height))
        
        # Draw the shift line
        shiftLineColor = RED if rpm<SHIFT else BLACK
        shift_line_y = SCREEN_HEIGHT - (SHIFT / RPM_MAX) * SCREEN_HEIGHT*.88
        pygame.draw.line(screen, shiftLineColor, (SCREEN_WIDTH * 0.8, shift_line_y), (SCREEN_WIDTH, shift_line_y), 5)

        pygame.draw.line(screen, BLACK, (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT*.12+2), (SCREEN_WIDTH, SCREEN_HEIGHT*.12+2), 4)
        pygame.draw.line(screen, BLACK, (SCREEN_WIDTH * 0.8+2, SCREEN_HEIGHT*.12), (SCREEN_WIDTH * 0.8+2, SCREEN_HEIGHT), 4)

        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT*.12), (SCREEN_WIDTH, SCREEN_HEIGHT*.12), 2)
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT*.12), (SCREEN_WIDTH * 0.8, SCREEN_HEIGHT), 2)

        # Calculate the height of the filled portion based on percentage
        fuel_height = math.floor((SCREEN_HEIGHT*.8) * fuel_level/100)

        # Draw the filled portion
        if fuel_level > 75:
            fuel_color = GREEN
        elif fuel_level <=75 and fuel_level > 50:
            fuel_color = YELLOW
        elif fuel_level <=50 and fuel_level > 30:
            fuel_color = ORANGE
        else:
            fuel_color = RED
        
        draw_text(screen, f"{round(fuel_level,1)}%", font_medium, WHITE, SCREEN_WIDTH*.1, SCREEN_HEIGHT*.15)
        pygame.draw.rect(screen, fuel_color, (0, SCREEN_HEIGHT - fuel_height, SCREEN_WIDTH * 0.2, fuel_height))

        pygame.draw.line(screen, BLACK, (0, SCREEN_HEIGHT*.2+2), (SCREEN_WIDTH*.2, SCREEN_HEIGHT*.2+2), 4)
        pygame.draw.line(screen, BLACK, (SCREEN_WIDTH * 0.2-2, SCREEN_HEIGHT*.2), (SCREEN_WIDTH * 0.2-2, SCREEN_HEIGHT), 4)

        pygame.draw.line(screen, WHITE, (0, SCREEN_HEIGHT*.2), (SCREEN_WIDTH*.2, SCREEN_HEIGHT*.2), 2)
        pygame.draw.line(screen, WHITE, (SCREEN_WIDTH * 0.2, SCREEN_HEIGHT*.2), (SCREEN_WIDTH * 0.2, SCREEN_HEIGHT), 2)

        for i, page in enumerate(pages):
            if page != 'Off':
                color = WHITE if i == current_page else BLACK
                pygame.draw.circle(screen, WHITE, (circle_x, circle_y), circle_radius + 4)
                pygame.draw.circle(screen, BLACK, (circle_x, circle_y), circle_radius + 2)
                pygame.draw.circle(screen, color, (circle_x, circle_y), circle_radius)
                circle_x += 2 * (circle_radius + circle_spacing)

        # Draw page indicators (circles)
        circle_radius = 22
        circle_spacing = 5

        total_circle_width = 12 * (2 * circle_radius + 2 * circle_spacing)

        # Calculate starting position to center horizontally
        start_x = (SCREEN_WIDTH - total_circle_width) // 2
        circle_x = start_x + circle_radius + circle_spacing
        circle_y = circle_radius + circle_spacing

        # Colors for each light
        light_colors = [GREEN, GREEN, GREEN, GREEN, RED, RED, RED, RED, PURPLE, PURPLE, PURPLE, PURPLE]

        for i in range(12):
            color = light_colors[i]

            pygame.draw.circle(screen, WHITE, (circle_x, circle_y), circle_radius )
            pygame.draw.circle(screen, BLACK, (circle_x, circle_y), circle_radius -1)
            
            if rpm > SHIFT - ((12 - i) * 200):
                pygame.draw.circle(screen, color, (circle_x, circle_y), circle_radius)
                
            circle_x += 2 * (circle_radius + circle_spacing)

        if pages[current_page] == "RPM":
            # Draw RPM section
            draw_text(screen, "RPM", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 20)
            draw_text(screen, str(rpm), font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 +20)
            draw_text(screen, "Max", font_small, WHITE, SCREEN_WIDTH*.28, SCREEN_HEIGHT // 2)
            draw_text(screen, str(RPM_MAX), font_medium, WHITE, SCREEN_WIDTH*.28, SCREEN_HEIGHT // 2 +40)
            draw_text(screen, "Shift", font_small, WHITE, SCREEN_WIDTH*.72, SCREEN_HEIGHT // 2)
            draw_text(screen, str(SHIFT), font_medium, WHITE, SCREEN_WIDTH*.72, SCREEN_HEIGHT // 2 +40)

            pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH * 0.2+25, SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
            pygame.draw.rect(screen, RED, (SCREEN_WIDTH * 0.2+25, SCREEN_HEIGHT-SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))

            draw_text(screen, "+", font_medium, BLACK, SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.05, SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)
            draw_text(screen, "-", font_medium, BLACK, SCREEN_WIDTH * 0.2+25+SCREEN_WIDTH*.05, SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)

            pygame.draw.rect(screen, GREEN, (SCREEN_WIDTH * 0.7-25, SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))
            pygame.draw.rect(screen, RED, (SCREEN_WIDTH * 0.7-25, SCREEN_HEIGHT-SCREEN_HEIGHT*.3, SCREEN_WIDTH * 0.1, SCREEN_HEIGHT*.1))

            draw_text(screen, "+", font_medium, BLACK, SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.05, SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)
            draw_text(screen, "-", font_medium, BLACK, SCREEN_WIDTH * 0.7-25+SCREEN_WIDTH*.05, SCREEN_HEIGHT-SCREEN_HEIGHT*.3+SCREEN_HEIGHT*.05)


        elif pages[current_page] == "MPG":
            # Draw Horsepower section
            draw_text(screen, "Instant MPG", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 20)
            draw_text(screen, str(round(mpg, 2)), font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2+20)

        elif pages[current_page] == "Both":
            # Draw RPM and Horsepower on separate lines
            draw_text(screen, "RPM", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4)
            draw_text(screen, "Instant MPG", font_medium, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40)
            draw_text(screen, f"{rpm}", font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4 + 60)
            draw_text(screen, str(round(mpg, 2)), font_large, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)

        elif pages[current_page] == "Off":
            screen.fill(BLACK)

        with open("last_visited_page.txt", "w") as file:
            file.write(str(current_page))

        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

        sleep = .05
        if DEV:
            sleep = .1
        
        time.sleep(sleep)

    print("Logging stopped.")

    if not DEV:
        # Close the connection
        connection.close()

if __name__ == "__main__":
    main()