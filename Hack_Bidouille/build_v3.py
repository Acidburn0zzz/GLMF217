# -*- coding: utf-8 -*-

from mine import *
import sys
import os
from collections import OrderedDict


SHIFT = 20
REPOSITORY = 'instructions'
BLOC_DIRECTION = {
    'TORCH' : {'E' : 1, 'W' : 2, 'S' : 3, 'N' : 4, 'U' : 5},
    'STAIRS' : {'E' : 0, 'W' : 1, 'S' : 2, 'N' : 3},
}


def error(errorCode, msg):
    print('ERREUR')
    for line in msg:
        print(line)
    exit(errorCode)


def readFile(filename):
    data = {}
    state = None
    nLevel = None
    loop = { 
        'start' : [],
        'end'   : [],
        'it'    : []
    }
    start_loop = None
    save_level = False
    save_end_level = None

    with open(filename, 'r') as fic:
        while True:
            line = fic.readline()
            if line == '':
                break
            else:
                line = ' '.join(line.split()).rstrip()
                if line == '':
                    continue
                if line[0:2] == '--':
                    line = line.upper()
                    if line == '-- GLOBAL':
                        if state is None:
                            state = 'GLOBAL'
                        else:
                            error(3, (
                                'Fichier MIF (Minecraft Instruction File) mal formé',
                                '-- GLOBAL doit être en première position'
                            ))
                    elif line == '-- BLOCKS':
                        if state == 'GLOBAL':
                            state = 'BLOCKS'
                            if 'WIDTH' not in data['GLOBAL'] or 'HEIGHT' not in data['GLOBAL']:
                                error(5, (
                                    'Fichier MIF (Minecraft Instruction File) mal formé',
                                    'height et width obligatoires dans -- GLOBAL'
                                ))
                        else:
                            error(5, (
                                'Fichier MIF (Minecraft Instruction File) mal formé',
                                '-- BLOCKS doit être après -- GLOBAL'
                            ))
                    elif line == '-- LEVELS':
                        if state == 'BLOCKS':
                            state = 'LEVELS'
                        else:
                            error(6, (
                                'Fichier MIF (Minecraft Instruction File) mal formé',
                                '-- LEVELS doit être après -- BLOCKS'
                            ))
                elif line.upper().startswith('% START LOOP'):
                    start_loop = ' '.join(line.split())[13:]
                    save_level = True
                elif line.upper().startswith('% END LOOP'):
                    if start_loop is None:
                        error(12, (
                            'Fichier MIF (Minecraft Instruction File) mal formé',
                            'Fin de boucle sans boucle'
                        ))
                    loop['start'].append(start_loop[1])
                    loop['end'].append(save_end_level)
                    loop['it'].append(int(start_loop[0]))
                    start_loop = None
                elif line[0] == '*' and state == 'LEVELS':
                    level = line[2:].upper()
                    if not level.startswith('LEVEL '):
                        error(8, (
                            'Fichier MIF (Minecraft Instruction File) mal formé',
                            'La définition d\'un niveau commence par * Level'
                        ))
                    multiLevel = level.split('..')
                    print(multiLevel)
                    if len(multiLevel) == 2:
                        endLevel = int(multiLevel[1])
                    else:
                        endLevel = int(line[8:])
                    if nLevel is None or endLevel > nLevel:
                        nLevel = endLevel
                    else:
                        error(9, (
                            'Fichier MIF (Minecraft Instruction File) mal formé',
                            'Numéro de niveau ' + str(line[8:]) + ' incompatible avec le précédent (' + str(nLevel) + ')'
                        ))
                    if 'LEVELS' not in data:
                        data['LEVELS'] = OrderedDict()
                    if level not in data['LEVELS']:
                        data['LEVELS'][level] = []
                    if save_level:
                        save_level = False
                        start_loop = (start_loop, level)
                    save_end_level = level
                elif '=' in line:
                    if state == 'GLOBAL' or state == 'BLOCKS':
                        var = line.replace(' ', '').split('=')
                        if state not in data:
                            data[state] = {}
                        if var[0].upper() in data[state]:
                            error(11, (
                                'Fichier MIF (Minecraft Instruction File) mal formé',
                                'Block ' + var[0].upper() + ' (' + var[1].upper() + ') déjà défini'
                        ))
                        data[state][var[0].upper()] = var[1].upper()
                    else:
                        error(4, (
                            'Fichier MIF (Minecraft Instruction File) mal formé',
                            'Assignation d\'une valeur à l\'extérieur d\'un bloc -- GLOBAL ou -- BLOCKS'
                        ))
                else:
                    if len(line) != int(data['GLOBAL']['WIDTH']):
                        error(7, (
                            'Fichier MIF (Minecraft Instruction File) mal formé',
                            'La longueur d\'un niveau a été définie à ' + data['GLOBAL']['WIDTH'] + ' et n\'a pas été respectée :',
                            'La ligne ' + line + ' a une taille de ' + str(len(line)) 
                        ))
                    data['LEVELS'][level].append(line)
                    if len(data['LEVELS'][level]) > int(data['GLOBAL']['HEIGHT']):
                        error(7, (
                            'Fichier MIF (Minecraft Instruction File) mal formé',
                            'La largeur d\'un niveau a été définie à ' + data['GLOBAL']['HEIGHT'] + ' et n\'a pas été respectée :',
                            'Le niveau a une largeur de ' + str(len(data['LEVELS'][level])) 
                        ))

    return data, loop        


def createBlocks(pos, depX, depY, depZ, level, blocks):
    torchesBuffer = []
    for line in level:
        for bloc in line:
            if bloc not in blocks:
                error(1, (
                    'Fichier MIF (Minecraft Instruction File) mal formé',
                    'Le type de bloc "' + bloc + '" n\'est pas défini'
                ))

            blocDir = blocks[bloc].split('~')
            if len(blocDir) == 2:
                specialBloc = getattr(block, blocDir[0])
                if blocDir[0].startswith('STAIRS'):
                    blocDir[0] = 'STAIRS'
                specialBloc.data = BLOC_DIRECTION[blocDir[0]][blocDir[1]]
                if blocDir[0] == 'TORCH' or blocDir[0] == 'STAIRS':
                    torchesBuffer.append((pos[0] + depX, pos[1] + depY, pos[2] - depZ, specialBloc.id, specialBloc.data))
                else:
                    mc.setBlock(pos[0] + depX, pos[1] + depY, pos[2] - depZ, specialBloc)
            else:
                mc.setBlock(pos[0] + depX, pos[1] + depY, pos[2] - depZ, getattr(block, blocks[bloc]))
            depZ += 1
        depX += 1
        depZ = 0
    for torch in torchesBuffer:
        mc.setBlock(torch[0], torch[1], torch[2], torch[3], torch[4])
    depY += 1
    depX = 0

    return depX, depY, depZ


def build(pos, data, loop):
    print('START :', loop['start'])
    print('END :', loop['end'])
    print('IT :', loop['it'])
    depX, depY, depZ = 0, 0, 0
    in_loop = False
    it_loop = 0
    execute_loop = False

    buffer_blocks = []
    for level in data['LEVELS']:
        if level in loop['start']:
            in_loop = True
            it_loop = loop['it'][loop['start'].index(level)]
        if in_loop:
            buffer_blocks.append(data['LEVELS'][level])
        if level in loop['end']:
            in_loop = False
            execute_loop = True
        multiLevel = level.split('..')
        if len(multiLevel) == 2:
            start = int(multiLevel[0][6:])
            end = int(multiLevel[1])
        else:
            start = end = 1
        for n in range(start, end + 1):
            depX, depY, depZ = createBlocks(pos, depX, depY, depZ, data['LEVELS'][level], data['BLOCKS'])            
        if execute_loop:
            execute_loop = False
            for it in range(it_loop - 1):
                for n in range(len(buffer_blocks)):
                    depX, depY, depZ = createBlocks(pos, depX, depY, depZ, buffer_blocks[n], data['BLOCKS'])            
            buffer_blocks = []
            it_loop = 0

def getInstructions():
    if len(sys.argv) != 2:
        error(1, (
            'Il faut indiquer un et un seul paramètre !',
            'Exemple : build tower'
        ))

    filename = REPOSITORY + '/' + sys.argv[1] + '.mif'
    if not os.path.isfile(filename):
        print('ERREUR')
        error(2, ('Le fichier {} n\'existe pas !'.format(filename),))

    return filename


if __name__ == '__main__':
    mc = Minecraft()
    filename = getInstructions()
    data, loop = readFile(filename)

    playerPos = mc.player.getPos()
    direction = mc.player.getDirection()
    build((playerPos.x + round(direction.x) * SHIFT, playerPos.y, playerPos.z + round(direction.z) * SHIFT), data, loop)
