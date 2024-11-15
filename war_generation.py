# 오른쪽이 끊기는 경우
import pygame

pygame.init()

screen = pygame.display.set_mode((1024, 768))  # 윈도우 크기
clock = pygame.time.Clock()

# 배경 이미지
background = pygame.image.load("background_tile/png/BG.png").convert()
# width = 1280
ground_size = background.get_width()

bgx = 0 # background x

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    """업데이트"""
    #bgx += 10
    point = pygame.mouse.get_pos()

    if point[0] > 1019 and bgx < 251:
        
        bgx += 5
    
    elif point[0] < 5 and bgx > 0:
        bgx -= 5

    """화면에 그리기"""

    # 배경 색
    screen.fill((255, 255, 255))

    # 스프라이트 그리기
    screen.blit(background, dest = (-bgx, 0))

    pygame.display.flip()

    clock.tick(30)

pygame.quit()