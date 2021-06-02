from model.hero import *
from model.map import Map
from model.parameters import Parameters
from model.state import State
from model.abilites import AbilityType
from model.teams import Teams
import json
import datetime
import random
import time


file = open("debug.txt", "w")
file.write("hyita " + '\n')


game = json.loads(input())
game_map = Map(game)  # карта игрового мира
game_params = Parameters(game)  # параметры игры
game_teams = Teams(game)  # моя команда

timestart = datetime.datetime.now().second
step = 0

while True:
    try:
        """ Получение состояния игры """
        state = State(input(), game_teams, game_params)

        my_buildings = state.my_buildings()
        my_squads = state.my_squads()
        # сортируем по остаточному пути
        my_squads.sort(key=lambda c: c.way.left, reverse=False)

        enemy_buildings = state.enemy_buildings()
        enemy_squads = state.enemy_squads()

        neutral_buildings = state.neutral_buildings()

        forges_buildings = state.forges_buildings()

        step += 1
        """ Играем за мага """
        if game_teams.my_her.hero_type == HeroType.Mag:
            # 1 проверяем доступность абилки Чума
            if state.ability_ready(AbilityType.Plague):
                file.write("1\n")
                print(game_teams.my_her.plague(enemy_buildings[0].id))
                enemy_buildings[0].buff_mask | 4
                timefirstplague = datetime.datetime.now().second
            # 2 захватываем нейтральные башни до 50 хода
            if step < 20:
                file.write("2.2\n")
                for i in range (0, len(my_buildings)):
                    for neutral_building in neutral_buildings:
                        distance = game_map.towers_distance(my_buildings[i].id, neutral_building.id)
                        if (distance < 3) and my_buildings[i].creeps_count > 15:    
                            print(game_teams.my_her.move(my_buildings[i].id, neutral_building.id, 0.65))
                            my_buildings[0].creeps_count -= 0.65 * my_buildings[i].creeps_count
            

            # 3 захватываем нейтральные башни этой тактикой начиная с 51 хода
            if step > 51:
                file.write("3\n")
                for i in range (0, len(my_buildings)):
                    if my_buildings[i].creeps_count > 11:
                        for neutral_building in neutral_buildings:
                            distance = game_map.towers_distance(my_buildings[i].id, neutral_building.id)
                            if (distance < 5 and len(neutral_buildings) > 6):
                                print(game_teams.my_her.move(my_buildings[i].id, neutral_building.id, 0.9))
                                my_buildings[i].creeps_count -= 0.9 * my_buildings[i].creeps_count
                                break
                            # 3.1 если нейтральных башен мало или они далеко тогда отправляем из двух башен отряд
                            elif len(neutral_buildings) < 4 and i + 1 <  len(my_buildings):
                                file.write("3.1\n")
                                print(game_teams.my_her.move(my_buildings[i].id, neutral_building.id, 0.5))
                                print(game_teams.my_her.move(my_buildings[i + 1].id, neutral_building.id, 0.5))
                                my_buildings[i].creeps_count -= 0.5 * my_buildings[i].creeps_count  
                                my_buildings[i + 1].creeps_count -= 0.5 * my_buildings[i + 1].creeps_count  
                                break
                            elif (my_buildings[i].creeps_count > 10 and len(my_buildings) > 4):
                                print(game_teams.my_her.move(my_buildings[i].id, neutral_building.id, 0.7))
                                my_buildings[i].creeps_count -= 0.7 * my_buildings[i].creeps_count
                                break

            # 4 проверяем доступность абилки Обмен башнями
            if state.ability_ready(AbilityType.Build_exchange):
                file.write("4\n")
                if len(my_buildings) > 4:
                    k = 0
                    for my_building in my_buildings:
                        if k == 0:
                            if my_building.creeps_count < 5:
                                for enemy_building in enemy_buildings:
                                    if enemy_building.creeps_count > 18 and enemy_building.buff_mask & 4 != 4:
                                        print(game_teams.my_her.exchange(enemy_building.id, my_building.id))
                                        k = 1
                                        break

            for j in range  (0, len(enemy_buildings)):
                k = 0
                list1 = []
                for i in range  (0, len(my_buildings)):
                    distance = game_map.towers_distance(my_buildings[i].id, enemy_buildings[j].id)
                    if distance < 5 and my_buildings[i].creeps_count > 5:
                        k += 1
                        list1.append(str(i))
                if  k >= 2 :
                    print(game_teams.my_her.move(my_buildings[int(list1[0])].id, enemy_buildings[j].id, 0.8))
                    print(game_teams.my_her.move(my_buildings[int(list1[1])].id, enemy_buildings[j].id, 0.8))
                    my_buildings[int(list1[0])].creeps_count -= 0.8 * my_buildings[int(list1[0])].creeps_count
                    my_buildings[int(list1[1])].creeps_count -= 0.8 * my_buildings[int(list1[1])].creeps_count
                
            # 5 Upgrade башни
            for my_building in my_buildings:
                if my_building.level.id <= len(game_params.tower_levels) - 1:
                    # Если хватает стоимости на upgrade
                    update_coast = game_params.get_tower_level(my_building.level.id + 1).update_coast
                    if update_coast < my_building.creeps_count:
                        print(game_teams.my_her.upgrade_tower(my_building.id))
                        my_building.creeps_count -= update_coast
                        file.write("5\n")
    
            # 6 атакуем башню neutral
            if step % 5 == 0 and len(neutral_buildings) > 0:
                file.write("6\n")
                for i in range (0, len(my_buildings)):
                        if my_buildings[i].creeps_count > 13:
                            print(game_teams.my_her.move(my_buildings[i].id, neutral_buildings[0].id, 0.8))
                            my_buildings[i].creeps_count -= 0.8 * my_buildings[i].creeps_count
                            if (i + 1 < len(my_buildings)):
                                if my_buildings[i + 1].creeps_count > 10:
                                    print(game_teams.my_her.move(my_buildings[i + 1].id, neutral_buildings[0].id, 0.5))
                                    my_buildings[i + 1].creeps_count -= 0.7 * my_buildings[i + 1].creeps_count
                                    break

            # 7 атакуем башню противника
            if step % 3 == 0 or len(neutral_buildings) < 2:
                file.write("7\n")
                for i in range (0, len(my_buildings)):
                    if (i + 1 < len(my_buildings)):
                        if my_buildings[i].creeps_count > 10 and my_buildings[i + 1].creeps_count > 10:
                            if (len(enemy_buildings) > 2):
                                print(game_teams.my_her.move(my_buildings[i].id, enemy_buildings[2].id, 0.75))
                                print(game_teams.my_her.move(my_buildings[i + 1].id, enemy_buildings[2].id, 0.75))
                                my_buildings[i].creeps_count -= 0.75 * my_buildings[i].creeps_count
                                my_buildings[i + 1].creeps_count -= 0.75 * my_buildings[i + 1].creeps_count
                                break
            # 7.1 ускорение
            if len(my_squads) > 4:
                if state.ability_ready(AbilityType.Speed_up):
                    location = game_map.get_squad_center_position(my_squads[2])
                    print(game_teams.my_her.speed_up(location))  
            # 7.2 поменяла башню и отправила туда солдат                        
            if step % 14 == 0:
                file.write("7.2\n")
                for i in range (0, len(my_buildings)):
                    for j in range (0, len(my_buildings)):
                        if my_buildings[i].creeps_count > 10 and my_buildings[j].creeps_count < 5:
                                print(game_teams.my_her.move(my_buildings[i].id, my_buildings[j].id, 0.2))
                                my_buildings[j].creeps_count += 0.2 * my_buildings[i].creeps_count
                                my_buildings[i].creeps_count -= 0.2 * my_buildings[i].creeps_count
                                break
                if state.ability_ready(AbilityType.Build_exchange):
                        k = 0
                        for my_building in my_buildings:
                            if k == 0:
                                if my_building.creeps_count < 10:
                                    for enemy_building in enemy_buildings:
                                        if enemy_building.buff_mask & 4 != 4:
                                            print(game_teams.my_her.exchange(enemy_building.id, my_building.id))
                                            k = 1
                                            break                                    

            # 8 когда нейтральных башен не осталось начинаем атаковать вражеские
            if step % 3 != 0:
                file.write("8\n")
                if len(neutral_buildings) < 2:
                    if (len(my_buildings) > 1):
                        for i in range (0, len(my_buildings)):
                            for j in range  (0, len(enemy_buildings)):
                                distance = game_map.towers_distance(my_buildings[i].id, enemy_buildings[j].id)
                                if (i + 1 < len(my_buildings) and distance < 5):
                                    if (my_buildings[i].creeps_count + my_buildings[i + 1].creeps_count - 5 > enemy_buildings[j].creeps_count):
                                            print(game_teams.my_her.move(my_buildings[i].id, enemy_buildings[j].id, 0.75))
                                            print(game_teams.my_her.move(my_buildings[i + 1].id, enemy_buildings[j].id, 0.75))
                                            my_buildings[i].creeps_count -= 0.75 * my_buildings[i].creeps_count
                                            my_buildings[i + 1].creeps_count -= 0.75 * my_buildings[i + 1].creeps_count    
                    else:
                        file.write("8.2\n")
                        for j in range  (0, len(enemy_buildings)):
                            distance = game_map.towers_distance(my_buildings[0].id, enemy_buildings[j].id)
                            if distance < 5 and enemy_buildings[j].creeps_count < my_buildings[0].creeps_count:
                                print(game_teams.my_her.move(my_buildings[0].id, enemy_buildings[j].id, 0.8))
                            else:
                                if enemy_buildings[j].creeps_count < my_buildings[0].creeps_count:
                                    print(game_teams.my_her.move(my_buildings[0].id, enemy_buildings[j].id, 0.7)) 

            # 9 проверяем доступность абилки Чума
            if datetime.datetime.now().second - timefirstplague > 25 and len(enemy_buildings) > 3:
                file.write("9\n")
                for i in range (2, len(enemy_buildings)):
                    print(game_teams.my_her.plague(enemy_buildings[i].id))
                    enemy_buildings[i].buff_mask | 4
                    break

            # 10  Атакуем башню противника
            if  len(my_buildings) > 2 and step % 2 == 0:
                file.write("10\n")
                # определяем расстояние между башнями
                distance = game_map.towers_distance(my_buildings[0].id, enemy_buildings[0].id)
                # определяем сколько тиков идти до нее со стандартной скоростью
                ticks = distance / game_params.creep.speed
                # определяем прирост башни в соответствии с ее уровнем
                enemy_creeps = 0
                if enemy_buildings[0].creeps_count >= enemy_buildings[0].level.player_max_count:
                    # если текущее количество крипов больше чем положено по уровню
                    enemy_creeps = enemy_buildings[0].creeps_count
                else:
                    # если меньше - будет прирост
                    grow_creeps = ticks / enemy_buildings[0].level.creep_creation_time
                    enemy_creeps = enemy_buildings[0].creeps_count + grow_creeps
                    if enemy_creeps >= enemy_buildings[0].level.player_max_count:
                        enemy_creeps = enemy_buildings[0].level.player_max_count
                # определяем количество крипов с учетом бонуса защиты
                enemy_defence = enemy_creeps * (1 + enemy_buildings[0].DefenseBonus)
                # если получается в моей башне крипов больше + 10 на червя - идем на врага всей толпой
                if enemy_defence + 10 < my_buildings[0].creeps_count:
                    file.write("10.1\n")
                    print(game_teams.my_her.move(my_buildings[0].id, enemy_buildings[0].id, 0.8))
        
            # 11  Пополняю свои башни если в них мало людей      
            if step > 50 and step % 29 == 0:
                file.write("11\n")
                for i in range (0, len(my_buildings)):
                    for j in range (0, len(my_buildings)):
                        if my_buildings[i].creeps_count > 20 and my_buildings[j].creeps_count < 5:
                                print(game_teams.my_her.move(my_buildings[i].id, my_buildings[j].id, 0.3))
                                my_buildings[j].creeps_count += 0.2 * my_buildings[i].creeps_count
                                my_buildings[i].creeps_count -= 0.2 * my_buildings[i].creeps_count
                                break


    except Exception as e:
        print(str(e))
    finally:
        """ Требуется для получения нового состояния игры  """
        print("end")
