# -*- coding: utf-8 -*-

from mine import *
import random
import time

if __name__ == '__main__':
    mc = Minecraft()

    playerPos = mc.player.getPos()
    direction = mc.player.getDirection()
    print(direction.x, direction.y, direction.z)
    print(round(direction.x), round(direction.y), round(direction.z))
    for i in range(20):
        mc.setBlock(playerPos.x + 3, playerPos.y, playerPos.z, random.randint(0, 255), 0)
        time.sleep(i * 0.1)
    print('Ça, c\'est de la... Maaaaagie !!!!')
