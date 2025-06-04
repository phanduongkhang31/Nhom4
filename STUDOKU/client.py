# client.py
import socket
import threading
import json
import tkinter as tk 



class SudokuClient:
    def __init__(self, app_controller, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.socket = None
        self.app_controller = app_controller # Reference to SudokuApp (main.py)
        self.game_ui = None # Reference to the GameScreenUI instance, set by app_controller

        self.is_connected = False
        self.receive_thread = None
        self.player_id = None # Gán bởi server
        self.current_game_id = None

        # Trạng thái bảng game từ server (để client tự kiểm tra hoặc hiển thị)
        self.server_board_state = [[0 for _ in range(9)] for _ in range(9)]
        self.server_fixed_mask = [[False for _ in range(9)] for _ in range(9)]


    def connect(self):
        if self.is_connected:
            print("Đã kết nối rồi.")
            return True
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5) # Timeout cho kết nối
            self.socket.connect((self.host, self.port))
            self.socket.settimeout(None) # Bỏ timeout sau khi kết nối
            self.is_connected = True
            
            self.receive_thread = threading.Thread(target=self._receive_data, daemon=True)
            self.receive_thread.start()
            
            print(f"CLIENT: Đã kết nối tới server {self.host}:{self.port}")
            if self.game_ui:
                self.game_ui.show_message("Kết nối", "Kết nối server thành công!")
                self.game_ui.update_info_display(0,0, "Multiplayer") # Reset UI info
            return True
        except socket.timeout:
            print(f"CLIENT ERROR: Hết thời gian chờ kết nối tới server.")
            if self.game_ui: self.game_ui.show_message("Lỗi", "Hết thời gian chờ kết nối server.", "error")
            self.is_connected = False
            return False
        except Exception as e:
            print(f"CLIENT ERROR: Lỗi kết nối - {e}")
            if self.game_ui: self.game_ui.show_message("Lỗi", f"Không thể kết nối: {e}", "error")
            self.is_connected = False
            return False

    def disconnect(self):
        if self.is_connected and self.socket:
            try:
                self.send_message({'command': 'quit'})
            except Exception as e:
                print(f"CLIENT: Lỗi khi gửi lệnh quit: {e}")
            finally:
                self.is_connected = False # Đặt trước khi close để thread nhận biết
                try:
                    self.socket.shutdown(socket.SHUT_RDWR) # Ngắt cả đọc và ghi
                    self.socket.close()
                except OSError as e: # Có thể đã đóng rồi
                     print(f"CLIENT: Lỗi khi đóng socket: {e}")
                self.socket = None
                if self.receive_thread and self.receive_thread.is_alive():
                    self.receive_thread.join(timeout=1) # Chờ thread kết thúc
                print("CLIENT: Đã ngắt kết nối.")
                if self.game_ui: self.game_ui.show_message("Thông báo", "Đã ngắt kết nối server.")
        self.player_id = None
        self.current_game_id = None


    def send_message(self, message_dict):
        if not self.is_connected or not self.socket:
            print("CLIENT ERROR: Chưa kết nối để gửi tin nhắn.")
            if self.game_ui: self.game_ui.show_message("Lỗi", "Chưa kết nối server.", "error")
            return False
        try:
            json_message = json.dumps(message_dict)
            self.socket.sendall(json_message.encode('utf-8'))
            # print(f"CLIENT SENT: {message_dict}") # DEBUG
            return True
        except Exception as e:
            print(f"CLIENT ERROR: Lỗi gửi dữ liệu: {e}")
            # Có thể server đã đóng kết nối, thử ngắt kết nối client
            self.disconnect()
            return False

    def _receive_data(self):
        buffer = ""
        while self.is_connected and self.socket:
            try:
                data_chunk = self.socket.recv(4096)
                if not data_chunk:
                    print("CLIENT: Server đã đóng kết nối.")
                    self.disconnect() # Xử lý ngắt kết nối sạch sẽ
                    break
                
                buffer += data_chunk.decode('utf-8')
                
                # Xử lý trường hợp nhận được nhiều JSON object trong một lần recv
                while True:
                    try:
                        message_obj, index = json.JSONDecoder().raw_decode(buffer)
                        # print(f"CLIENT RECEIVED: {message_obj}") # DEBUG
                        self._process_message(message_obj)
                        buffer = buffer[index:].lstrip() # Bỏ phần đã xử lý và khoảng trắng đầu
                    except json.JSONDecodeError:
                        # Chưa đủ dữ liệu để parse một JSON object hoàn chỉnh
                        break # Chờ thêm dữ liệu

            except ConnectionResetError:
                print("CLIENT: Kết nối bị reset bởi server.")
                self.disconnect()
                break
            except socket.error as e: # Các lỗi socket khác
                if self.is_connected: # Chỉ in lỗi nếu vẫn đang kỳ vọng kết nối
                    print(f"CLIENT ERROR: Lỗi socket khi nhận dữ liệu: {e}")
                self.disconnect()
                break
            except Exception as e:
                if self.is_connected:
                    print(f"CLIENT ERROR: Lỗi không xác định khi nhận dữ liệu: {e}")
                # Có thể ngắt kết nối ở đây nếu lỗi nghiêm trọng
                # self.disconnect()
                break
        print("CLIENT: Thread nhận dữ liệu đã dừng.")


    def _process_message(self, message):
        command = message.get('command')
        
        if command == 'connected_ack':
            self.player_id = message.get('player_id')
            print(f"CLIENT: Được server gán Player ID: {self.player_id}")
            # Client có thể yêu cầu danh sách game hoặc tạo game mới ở đây

        elif command == 'game_state_update': # Server gửi trạng thái game ban đầu hoặc cập nhật
            self.current_game_id = message.get('game_id')
            self.server_board_state = message.get('board_data')
            self.server_fixed_mask = message.get('fixed_mask')
            # Có thể có thêm thông tin như current_player, opponent_id, v.v.
            if self.game_ui:
                # UI cần được cập nhật với board này
                self.game_ui.reset_ui_for_new_game() # Reset UI cho game mới
                self.game_ui.update_board_display(
                    self.server_board_state,
                    self.server_fixed_mask,
                    pencil_data={} # Multiplayer không dùng pencil của client, mà là của server
                )
                self.game_ui.show_message("Game Multiplayer", f"Đã tham gia Game ID: {self.current_game_id}")
                self.game_ui.update_info_display(0,0, f"MP Game: {self.current_game_id}") # Reset info

        elif command == 'move_accepted': # Nước đi của bạn được chấp nhận
            r, c, num = message.get('row'), message.get('col'), message.get('number')
            self.server_board_state[r][c] = num # Cập nhật board cục bộ
            if self.game_ui:
                # Hiển thị nước đi của bạn (không phải lỗi)
                self.game_ui.update_cell_display(r, c, num, is_fixed=False, is_error=False)

        elif command == 'move_rejected':
            reason = message.get('reason', 'Nước đi không hợp lệ')
            if self.game_ui:
                self.game_ui.show_message("Nước đi bị từ chối", reason, "warning")
                # Có thể cần phục hồi ô đó về trạng thái trước đó từ server_board_state
                

        elif command == 'opponent_moved': # Đối thủ đã đi
            r, c, num = message.get('row'), message.get('col'), message.get('number')
            self.server_board_state[r][c] = num
            if self.game_ui:
                # Hiển thị nước đi của đối thủ với màu khác
                self.game_ui.update_cell_display(r, c, num, is_fixed=False, is_error=False) # Giả sử server đã check
                # Có thể thêm màu riêng cho đối thủ trong update_cell_display

        elif command == 'game_over':
            winner_id = message.get('winner_id')
            reason = message.get('reason', '')
            message_text = f"Game kết thúc! {reason}\n"
            if winner_id == self.player_id:
                message_text += "Bạn đã thắng!"
            elif winner_id:
                message_text += f"Người chơi {winner_id} đã thắng."
            else:
                message_text += "Hòa!" # Hoặc lý do khác
            
            if self.game_ui:
                self.game_ui.show_message("Game Over", message_text)
            self.current_game_id = None # Sẵn sàng cho game mới

        elif command == 'error':
            error_message = message.get('message', 'Lỗi không xác định từ server.')
            if self.game_ui:
                self.game_ui.show_message("Lỗi Server", error_message, "error")
        
        elif command == 'message': # Thông báo chung từ server
            text = message.get('text')
            if self.game_ui: self.game_ui.show_message("Thông báo Server", text)

        

    # --- Các hàm để UI gọi ---
    def request_new_multiplayer_game(self, difficulty="medium"):
        if not self.is_connected: return
        self.send_message({
            'command': 'create_game',
            'difficulty': difficulty,
            'player_id': self.player_id # Gửi player_id để server biết ai tạo
        })

    def request_join_game(self, game_id_to_join):
        if not self.is_connected: return
        self.send_message({
            'command': 'join_game',
            'game_id': game_id_to_join,
            'player_id': self.player_id
        })

    def submit_player_move(self, r, c, number):
        if not self.is_connected or not self.current_game_id:
            if self.game_ui: self.game_ui.show_message("Lỗi", "Không trong game hoặc chưa kết nối.", "error")
            return
        
        # Kiểm tra cơ bản phía client (tùy chọn, server vẫn là nguồn tin cậy)
        if self.server_fixed_mask[r][c]:
            if self.game_ui: self.game_ui.show_message("Thông báo", "Không thể thay đổi ô cố định.", "warning")
            return
        
        self.send_message({
            'command': 'make_move',
            'game_id': self.current_game_id,
            'player_id': self.player_id,
            'row': r,
            'col': c,
            'number': number # Gửi số 0 nếu là xóa
        })

    def set_game_ui(self, ui_instance):
        """Được gọi bởi SudokuApp để gán instance của GameScreenUI."""
        self.game_ui = ui_instance

# Ví dụ cách chạy client (thường sẽ được khởi tạo từ main.py)
if __name__ == '__main__':
    # Phần này chỉ để test client độc lập, không có UI đầy đủ
    class MockAppController: # Để test client mà không cần full SudokuApp
        def show_main_menu(self): pass
    
    class MockGameUI:
        def show_message(self, title, msg, type="info"): print(f"UI MOCK ({type.upper()}) {title}: {msg}")
        def update_board_display(self, board, fixed, pencil_data=None): print(f"UI MOCK: Update board - {board}")
        def update_info_display(self, m, t, d=None): pass
        def reset_ui_for_new_game(self): pass
        def update_cell_display(self, r,c,n, is_fixed, is_error, pencil=None): pass

    print("Chạy Sudoku Client (test mode)...")
    mock_controller = MockAppController()
    client = SudokuClient(app_controller=mock_controller)
    client.set_game_ui(MockGameUI()) # Gán mock UI

    if client.connect():
        # Sau khi kết nối, client có thể gửi yêu cầu tạo/tham gia game
        # client.request_new_multiplayer_game()
        # Hoặc chờ server tự động đưa vào game nếu server có logic đó
        
        # Giữ client chạy để nhận tin nhắn (trong thực tế, main loop của Tkinter sẽ giữ chương trình chạy)
        try:
            while client.is_connected:
                cmd = input("Client cmd (new, join <id>, move <r> <c> <n>, quit): ")
                if cmd.startswith("new"):
                    client.request_new_multiplayer_game()
                elif cmd.startswith("join"):
                    try:
                        _, gid = cmd.split()
                        client.request_join_game(gid)
                    except: print("Sai cú pháp join.")
                elif cmd.startswith("move"):
                    try:
                        _, r,c,n = cmd.split()
                        client.submit_player_move(int(r),int(c),int(n))
                    except: print("Sai cú pháp move.")
                elif cmd == "quit":
                    break
        except KeyboardInterrupt:
            print("Client tắt bởi người dùng.")
        finally:
            client.disconnect()
    else:
        print("Không thể kết nối tới server.")