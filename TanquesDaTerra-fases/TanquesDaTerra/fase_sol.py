import pygame
import os
import random
from tank_sol import TankSol
from obstacles import Obstacle
from camera import Camera

def iniciar_fase_sol(screen):
    pygame.init()
    clock = pygame.time.Clock()
    sw, sh = screen.get_size()

    # — Vertical offsets —
    BG_VERTICAL_SHIFT    = 260
    TANK_VERTICAL_SHIFT  = 250
    ENEMY_VERTICAL_SHIFT = 250

    # — Game parameters —
    SPAWN_MARGIN   = 20
    ENEMY_SPEED    = 2
    ENEMY_SCALE    = 1.5
    FLAME_SCALE    = 2.5
    FLAME_DAMAGE   = 20
    FLAME_INTERVAL = 1.0
    KILL_TARGET    = 15
    # Spawn 1 new enemy per death
    WAVE_KILL      = 1

    kill_count = 0
    death_since_spawn = 0

    base = os.path.dirname(__file__)
    cam = Camera(level_width=1600, level_height=sh)

    # — Load background —
    layer_files = ['Hills Layer 01.png','Hills Layer 02.png','Hills Layer 03.png',
                   'Hills Layer 04.png','Hills Layer 05.png','Hills Layer 06.png']
    parallax_factors = [0.2,0.35,0.5,0.7,0.9,1.1]
    bg_dir = os.path.join(base,'assets','sol_bg')
    bg_layers = [(pygame.image.load(os.path.join(bg_dir,f)).convert_alpha(),fac)
                 for f,fac in zip(layer_files,parallax_factors)]

    # — Calculate floors —
    ground_idx  = layer_files.index('Hills Layer 05.png')
    ground_surf = bg_layers[ground_idx][0]
    floor_base  = sh - ground_surf.get_height()
    floor_bg    = floor_base + BG_VERTICAL_SHIFT
    floor_tank  = floor_base + TANK_VERTICAL_SHIFT
    floor_enemy = floor_base + ENEMY_VERTICAL_SHIFT

    # — Load HUD and effects —
    hud_dir = os.path.join(base,'assets','hud')
    hud_tank_100 = pygame.image.load(os.path.join(hud_dir,'vida100.png')).convert_alpha()
    hud_tank_60  = pygame.image.load(os.path.join(hud_dir,'vida60.png')).convert_alpha()
    hud_tank_20  = pygame.image.load(os.path.join(hud_dir,'vida20.png')).convert_alpha()
    hud_enemy    = pygame.image.load(os.path.join(hud_dir,'vidaenemy.png')).convert_alpha()
    bullet_base  = pygame.image.load(os.path.join(hud_dir,'balatanque.png')).convert_alpha()
    bullet_left  = pygame.transform.flip(bullet_base,True,False)
    bullet_right = bullet_base
    flame_base   = pygame.image.load(os.path.join(hud_dir,'chamas.png')).convert_alpha()
    fw, fh       = flame_base.get_size()
    flame_img    = pygame.transform.scale(flame_base,(int(fw*FLAME_SCALE),int(fh*FLAME_SCALE)))
    flame_left   = pygame.transform.flip(flame_img,True,False)
    flame_right  = flame_img

    # — Instantiate tank —
    tmp = TankSol(0,0)
    tank_y = floor_tank - tmp.image.get_height()
    tank   = TankSol(100,tank_y)

    # — Spawn enemies —
    def spawn_enemies(n=3):
        enemies=[]
        for _ in range(n):
            side = random.choice(['left','right'])
            if side=='left':
                ex = -SPAWN_MARGIN - random.randint(0,SPAWN_MARGIN)
                dir_mult = 1
            else:
                ex = 1600 + SPAWN_MARGIN + random.randint(0,SPAWN_MARGIN)
                dir_mult = -1
            o = Obstacle(ex, floor_enemy,40,60,'inimigo',sprite_name='inimigo_sol1')
            if hasattr(o,'image') and o.image:
                iw, ih = o.image.get_size()
                size = (int(iw*ENEMY_SCALE),int(ih*ENEMY_SCALE))
                scaled = pygame.transform.scale(o.image,size)
                o.image_left  = scaled
                o.image_right = pygame.transform.flip(scaled,True,False)
            o.dir = dir_mult
            o.speed = ENEMY_SPEED
            o.touch_timer = 0.0
            img = o.image_left if o.dir<0 else o.image_right
            o.rect = img.get_rect()
            o.rect.x = ex
            o.rect.y = floor_enemy - img.get_height()
            enemies.append(o)
        return enemies

    obstacles = spawn_enemies()

    # — Main loop —
    while True:
        dt = clock.tick(60)/1000.0
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit();exit()
            if e.type==pygame.KEYDOWN and e.key==pygame.K_ESCAPE:
                return

        # Update tank
        keys = pygame.key.get_pressed()
        tank.handle_input(keys)
        tank.update()

        # Update enemies
        for o in obstacles:
            move_dir = 1 if o.rect.centerx < tank.rect.centerx else -1
            o.rect.x += move_dir * o.speed
            # Define flame rect centered on sprite
            if o.dir < 0:
                fx = o.rect.left - flame_left.get_width()
            else:
                fx = o.rect.right
            # vertical center
            fy_center = o.rect.centery - (flame_img.get_height() // 2)
            flame_rect = pygame.Rect(fx, fy_center, flame_img.get_width(), flame_img.get_height())
            # Damage only if tank collides flame_rect
            if tank.rect.colliderect(flame_rect):
                o.touch_timer += dt
                if o.touch_timer >= FLAME_INTERVAL:
                    tank.health -= FLAME_DAMAGE
                    o.touch_timer -= FLAME_INTERVAL
            else:
                o.touch_timer = 0.0

        # Projectile collisions
        for b in list(tank.bullets):
            for o in list(obstacles):
                if b.rect.colliderect(o.rect):
                    o.take_damage(TankSol.DAMAGE)
                    tank.bullets.remove(b)
                    if o.health<=0:
                        obstacles.remove(o)
                        kill_count+=1; death_since_spawn+=1
                    break

        # Spawn after one kill
        if death_since_spawn>=WAVE_KILL:
            obstacles.extend(spawn_enemies(1))
            death_since_spawn=0

        # End condition
        if tank.health<=0 or kill_count>=KILL_TARGET:
            return

        cam.update(tank.rect)

        # Draw background
        sky = bg_layers[0][0].get_at((0,0)); screen.fill(sky)
        for surf,fac in bg_layers:
            w=surf.get_width();off=int(cam.offset*fac)%w; y=floor_bg-surf.get_height()
            screen.blit(surf,(-off,y));screen.blit(surf,(w-off,y))

        # Draw enemies, flames, HUD
        for o in obstacles:
            img = o.image_left if o.dir<0 else o.image_right
            screen.blit(img, o.rect.move(-cam.offset,0))
            # Draw flame effect only when tank is in flame_rect
            if o.dir<0:
                fx = o.rect.left - flame_left.get_width()
                fy = o.rect.y + o.rect.height//4
                flame_rect = pygame.Rect(fx, fy, flame_left.get_width(), flame_left.get_height())
                if tank.rect.colliderect(flame_rect):
                    screen.blit(flame_left, (fx - cam.offset, fy))
            else:
                fx = o.rect.right
                fy = o.rect.y + o.rect.height//4
                flame_rect = pygame.Rect(fx, fy, flame_right.get_width(), flame_right.get_height())
                if tank.rect.colliderect(flame_rect):
                    screen.blit(flame_right, (fx - cam.offset, fy))
            # HUD inimigo
            hud_x=o.rect.centerx-hud_enemy.get_width()//2-cam.offset
            hud_y=o.rect.y-hud_enemy.get_height()-5
            screen.blit(hud_enemy,(hud_x,hud_y))

        # Draw bullets
        for b in tank.bullets:
            bi = bullet_right if b.dx>0 else bullet_left
            screen.blit(bi,(b.rect.x-cam.offset,b.rect.y))

        # Draw tank & HUD
        tank_img = tank.image_left if tank.facing=='left' else tank.image_right
        screen.blit(tank_img,tank.rect.move(-cam.offset,0))
        if tank.health>60: th=hud_tank_100
        elif tank.health>20:th=hud_tank_60
        elif tank.health>0: th=hud_tank_20
        else: th=None
        if th:
            tx=tank.rect.centerx-th.get_width()//2-cam.offset; ty=tank.rect.y-th.get_height()-5
            screen.blit(th,(tx,ty))

        pygame.display.flip()
