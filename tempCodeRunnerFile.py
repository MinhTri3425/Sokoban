self.joy_bfs = pygame.Rect(self.joycon_right_center_x - self.dpad_size // 2,
                                algo_center_y - self.dpad_size - self.dpad_spacing,
                                self.dpad_size, self.dpad_size)
        self.joy_dfs = pygame.Rect(self.joycon_right_center_x - self.dpad_size // 2,
                                algo_center_y + self.dpad_spacing,
                                self.dpad_size, self.dpad_size)
        self.joy_astar = pygame.Rect(self.joycon_right_center_x - self.dpad_size - self.dpad_spacing,
                                    algo_center_y - self.dpad_size // 2,
                                    self.dpad_size, self.dpad_size)
        self.joy_stop = pygame.Rect(self.joycon_right_center_x + self.dpad_spacing,
                                    algo_center_y - self.dpad_size // 2,
                                    self.dpad_size, self.dpad_size)