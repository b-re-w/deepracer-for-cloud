def reward_function(params):
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    speed = params['speed']
    is_left_of_center = params['is_left_of_center']
    closest_waypoints = params['closest_waypoints']
    steps = params['steps']
    progress = params['progress']
    steering_angle = params['steering_angle']
    waypoints = params['waypoints']
    heading = params['heading']
    
    expect_time = 10.0
    expect_steps = 145
    is_offtrack = params['is_offtrack']
    
    # waypoint 분류
    right = [120,121,122,123,124,125,126,127,128,129,130,131,132]
    center_right = [20,21,22,23,24,25,26,27,28,29,30,118,119,133,134]
    left = [7,8,9,10,11,12,13,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,
            85,86,87,88,89,90,100,101,102,103,104,105,106,107,108,109,110,
            139,140,141,142,143,144,145,146,147,148,149,150]
    center_left = [1,2,3,4,5,6,16,17,18,31,32,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,
                   70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,91,92,93,94,95,96,97,98,99,
                   111,112,113,114,115,116,117,135,136,137,138,151,152,153,154]
    
    # 속도 구간
    fast_speed = [2,3,4,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,
                  47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,
                  68,69,70,71,72,73,74,75,76,77,78,79,80,96,97,98,99,100,101,102,103,104,105,106,107,
                  110,111,112,113,114,115,116,117,118,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,
                  152,153,154]
    medium_speed = [1,5,6,7,8,9,10,11,12,13,34,35,36,37,38,39,40,41,42,43,44,45,46,
                    81,82,83,86,87,88,89,90,91,92,93,94,95,108,109,119,120,121,122,
                    141,142,143,144,145,146,147,148,149,150,151]
    slow_speed = [84,85,139,140]
    
    reward = 0.0
    next_point = max(closest_waypoints[0], closest_waypoints[1])
    
    # 오프트랙 패널티
    if is_offtrack:
        reward -= 200
        return float(reward)
    
    # === 1. 위치 보상 ===
    else:
        if next_point in right:
            if (not is_left_of_center) and 0.25 < (distance_from_center/track_width) < 0.48:
                reward += 10
            elif (not is_left_of_center) and (distance_from_center/track_width) <= 0.25:
                reward += 5  # 중간 보상
            else:
                reward += 0.1
        elif next_point in left:
            if (is_left_of_center) and 0.25 < (distance_from_center/track_width) < 0.48:
                reward += 10
            elif (is_left_of_center) and (distance_from_center/track_width) <= 0.25:
                reward += 5  # 중간 보상
            else:
                reward += 0.1
        elif next_point in center_right:
            if (not is_left_of_center) and (distance_from_center/track_width <= 0.25):
                reward += 10
            elif (is_left_of_center) and (distance_from_center/track_width <= 0.25):
                reward += 3
            else:
                reward += 0.1
        elif next_point in center_left:
            if (is_left_of_center) and (distance_from_center/track_width <= 0.25):
                reward += 10
            elif (not is_left_of_center) and (distance_from_center/track_width <= 0.25):
                reward += 3
            else:
                reward += 0.1
    
        # === 2. 속도 보상 개선 (범위 기반) ===
        if next_point in fast_speed:
            if speed >= 2.5:  # 2.5 이상이면 좋은 보상
                reward += 8 + (speed - 2.5) * 4  # 더 빠를수록 더 큰 보상
            elif speed >= 2.0:
                reward += 4
            else:
                reward += 0.5
        elif next_point in medium_speed:
            if 1.5 <= speed <= 2.5:  # 적정 속도 범위
                reward += 8
            elif speed > 2.5:
                reward += 2  # 너무 빠르면 낮은 보상
            else:
                reward += 1
        elif next_point in slow_speed:
            if speed <= 1.5:
                reward += 8
            elif speed <= 2.0:
                reward += 4
            else:
                reward += 0.5  # 너무 빠르면 낮은 보상
        
        # === 3. 미래 경로 예측 보상 ===
        # 3-5 waypoint 앞을 미리 보고 준비하는 행동에 보상
        total_waypoints = len(waypoints)
        if total_waypoints > 0:
            future_points = [
                (next_point + 1) % total_waypoints, 
                (next_point + 2) % total_waypoints, 
                (next_point + 3) % total_waypoints
            ]
            upcoming_slow = any(fp in slow_speed + medium_speed for fp in future_points)
            
            if upcoming_slow and speed <= 2.0:  # 미리 감속하는 행동
                reward += 5
            elif upcoming_slow and speed > 2.5:  # 감속하지 않으면 패널티
                reward *= 0.5
        
        # === 4. 조향 안정성 보상 ===
        # 급격한 조향 변화 방지
        if abs(steering_angle) <= 10:  # 부드러운 조향
            reward += 2
        elif abs(steering_angle) <= 20:
            reward += 1
        
        # === 5. 진행률 기반 보상 ===
        if (steps % 50) == 0 and progress >= (steps / expect_steps) * 100:
            reward += 5
        
        # === 6. 완주 보상 ===
        if progress == 100:
            if steps < expect_time * 15:
                reward += 100 * (expect_time * 15 / steps)
            else:
                reward += 50
    
    return float(reward)
