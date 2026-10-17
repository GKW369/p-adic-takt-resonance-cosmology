            # ==================================================================
            # !!! TARGET ZONE: PERFORMANCE-OPTIMIERTE HOCHFREQUENZ-KUGEL !!!
            # ==================================================================
            local_y, local_x = np.indices((180, 320))
            lc_x, lc_y = 160, 90
            
            dx_local = local_x - lc_x
            dy_local = local_y - lc_y
            quad_local = (dx_local * dx_local) + (dy_local * dy_local)
            
            mask_takt = np.isin(quad_local % self.control_base, allowed_24_list)
            mask_prim = (quad_local % self.primorial_base) <= self.invariant_limit
            local_sphere_mask = (quad_local < 350) & (mask_takt | mask_prim)
            
            s_y, s_x = np.where(local_sphere_mask)
            
            if len(s_x) > 0:
                z_sphere = 20
                sc_depth = (z_sphere * 1000) // 1414
                denom_s = sc_depth + 156
                
                rx = s_x - lc_x
                ry = s_y - lc_y
                
                p_xl = ((rx * 8 - 12) * 1000) // denom_s
                p_xr = ((rx * 8 + 12) * 1000) // denom_s
                p_y = ((ry * 8) * 1000) // denom_s
                
                o_xl = (p_xl + self.stereo_engine.width // 2) % self.stereo_engine.width
                o_xr = (p_xr + self.stereo_engine.width // 2) % self.stereo_engine.width
                o_y = (p_y + self.stereo_engine.height // 2) % self.stereo_engine.height
                
                self.stereo_engine.left_eye_buffer[o_y, o_xl] = 1
                self.stereo_engine.right_eye_buffer[o_y, o_xr] = 1
            # ==================================================================

            # Uhr-Engine weitertakten
            self.clock_engine.evolve_clock_one_takt()
            
            # Flacker-Schutz (Coherence Hold)
            active_nodes = int(np.sum(self.stereo_engine.left_eye_buffer))
            if active_nodes > 2:
                self.last_valid_view = self.stereo_engine.left_eye_buffer * 255
                bw_scene = self.last_valid_view.copy()
            else:
                bw_scene = self.last_valid_view.copy()
            
            # Diagnostik
            end_time = time.perf_counter()
            dt = end_time - start_time
            fps = 1.0 / dt if dt > 0 else 999.0
            
            # HUD-Anzeige
            cv2.putText(bw_scene, f"FPS: {fps:.1f} | NODES: {active_nodes:,} | HOLOGRAPHIC RECONSTRUCTION ACTIVE", 
                        (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2, cv2.LINE_AA)
            cv2.putText(bw_scene, f"VECTORS: X_SHIFT: {self.pos_x_offset} | Y_SHIFT: {self.pos_y_offset} | Z_TACT: {self.pos_z_offset}", 
                        (30, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 200, 1, cv2.LINE_AA)
            
            cv2.imshow(window_name, bw_scene)
            
            # Tasten-Abfrage und Flug-Steuerung (IndentationError behoben!)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC-Taste
                print("[ GAME ] Universum über ESC sicher geschlossen.")
                break
            elif key == ord('w') or key == ord('W'):
                self.pos_z_offset = (self.pos_z_offset + 1) % self.depth
            elif key == ord('s') or key == ord('S'):
                self.pos_z_offset = (self.pos_z_offset - 1) % self.depth
            elif key == ord('a') or key == ord('A'):
                self.pos_x_offset = (self.pos_x_offset - 1) % self.width
            elif key == ord('d') or key == ord('D'):
                self.pos_x_offset = (self.pos_x_offset + 1) % self.width
            elif key == ord('q') or key == ord('Q'):
                self.pos_y_offset = (self.pos_y_offset - 1) % self.height
            elif key == ord('e') or key == ord('E'):
                self.pos_y_offset = (self.pos_y_offset + 1) % self.height

if __name__ == "__main__":
    game = PTRC3DGameEngine()
    game.run_interactive_loop()
            # ==================================================================
            # !!! TARGET ZONE: PERFORMANCE-OPTIMIERTE HOCHFREQUENZ-KUGEL !!!
            # ==================================================================
            local_y, local_x = np.indices((180, 320))
            lc_x, lc_y = 160, 90
            
            dx_local = local_x - lc_x
            dy_local = local_y - lc_y
            quad_local = (dx_local * dx_local) + (dy_local * dy_local)
            
            mask_takt = np.isin(quad_local % self.control_base, allowed_24_list)
            mask_prim = (quad_local % self.primorial_base) <= self.invariant_limit
            local_sphere_mask = (quad_local < 350) & (mask_takt | mask_prim)
            
            s_y, s_x = np.where(local_sphere_mask)
            
            if len(s_x) > 0:
                z_sphere = 20
                sc_depth = (z_sphere * 1000) // 1414
                denom_s = sc_depth + 156
                
                rx = s_x - lc_x
                ry = s_y - lc_y
                
                p_xl = ((rx * 8 - 12) * 1000) // denom_s
                p_xr = ((rx * 8 + 12) * 1000) // denom_s
                p_y = ((ry * 8) * 1000) // denom_s
                
                o_xl = (p_xl + self.stereo_engine.width // 2) % self.stereo_engine.width
                o_xr = (p_xr + self.stereo_engine.width // 2) % self.stereo_engine.width
                o_y = (p_y + self.stereo_engine.height // 2) % self.stereo_engine.height
                
                self.stereo_engine.left_eye_buffer[o_y, o_xl] = 1
                self.stereo_engine.right_eye_buffer[o_y, o_xr] = 1
            # ==================================================================

            # Uhr-Engine weitertakten
            self.clock_engine.evolve_clock_one_takt()
            
            # Flacker-Schutz (Coherence Hold)
            active_nodes = int(np.sum(self.stereo_engine.left_eye_buffer))
            if active_nodes > 2:
                self.last_valid_view = self.stereo_engine.left_eye_buffer * 255
                bw_scene = self.last_valid_view.copy()
            else:
                bw_scene = self.last_valid_view.copy()
            
            # Diagnostik
            end_time = time.perf_counter()
            dt = end_time - start_time
            fps = 1.0 / dt if dt > 0 else 999.0
            
            # HUD-Anzeige
            cv2.putText(bw_scene, f"FPS: {fps:.1f} | NODES: {active_nodes:,} | HOLOGRAPHIC RECONSTRUCTION ACTIVE", 
                        (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2, cv2.LINE_AA)
            cv2.putText(bw_scene, f"VECTORS: X_SHIFT: {self.pos_x_offset} | Y_SHIFT: {self.pos_y_offset} | Z_TACT: {self.pos_z_offset}", 
                        (30, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.7, 200, 1, cv2.LINE_AA)
            
            cv2.imshow(window_name, bw_scene)
            
            # Tasten-Abfrage und Flug-Steuerung (IndentationError behoben!)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC-Taste
                print("[ GAME ] Universum über ESC sicher geschlossen.")
                break
            elif key == ord('w') or key == ord('W'):
                self.pos_z_offset = (self.pos_z_offset + 1) % self.depth
            elif key == ord('s') or key == ord('S'):
                self.pos_z_offset = (self.pos_z_offset - 1) % self.depth
            elif key == ord('a') or key == ord('A'):
                self.pos_x_offset = (self.pos_x_offset - 1) % self.width
            elif key == ord('d') or key == ord('D'):
                self.pos_x_offset = (self.pos_x_offset + 1) % self.width
            elif key == ord('q') or key == ord('Q'):
                self.pos_y_offset = (self.pos_y_offset - 1) % self.height
            elif key == ord('e') or key == ord('E'):
                self.pos_y_offset = (self.pos_y_offset + 1) % self.height

if __name__ == "__main__":
    game = PTRC3DGameEngine()
    game.run_interactive_loop()
