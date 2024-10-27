import pygame 

pygame.init()

clock = pygame.time.Clock()
fps = 60

bottom_panel_height = 150
screen_width = 800
screen_height = 400 + bottom_panel_height

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Battle")

background_img = pygame.image.load('C:\\Users\\zanet\\OneDrive\\Desktop\\PyGame\\img\\background\\Background.png').convert_alpha()
panel_img = pygame.image.load('C:\\Users\\zanet\\OneDrive\\Desktop\\PyGame\\img\\Icons\\cobble.png').convert_alpha()  # Replace with your panel image path

def draw_bg():
    # Scale background only to the game area (400 height)
    background_scaled = pygame.transform.scale(background_img, (screen_width, 400))
    screen.blit(background_scaled, (0, 0))

def draw_bottom_panel():
    # Scale the panel image to fit the width of the screen
    panel_scaled = pygame.transform.scale(panel_img, (screen_width, bottom_panel_height))
    # Draw the panel image
    screen.blit(panel_scaled, (0, 400))  # Position it at the bottom

run = True
while run:
    
    clock.tick(fps)
    
    # Draw background
    draw_bg()
    
    # Draw bottom panel
    draw_bottom_panel()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            
    pygame.display.update()       

pygame.quit()
