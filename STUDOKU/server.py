# server.py
import socket
import threading
import json
import uuid # For generating unique game IDs and player IDs
from sudoku_logic import SudokuGenerator
import traceback # Để in chi tiết lỗi

HOST = '0.0.0.0' # Nghe trên tất cả các interface
PORT = 5555
MAX_PLAYERS_PER_GAME = 2 # Ví dụ: game 1v1

class SudokuGameMultiplayer:
    def __init__(self, game_id, difficulty="medium", created_by_player_id=None):
        self.game_id = game_id
        self.difficulty = difficulty
        self.generator = SudokuGenerator()
        self.puzzle_board, self.solution_board = self.generator.generate_puzzle(difficulty)
        
        # --- DEBUG INIT ---
        print(f"\nDEBUG SERVER: New SudokuGameMultiplayer CREATED: ID={game_id}, Difficulty={difficulty}, CreatedBy={created_by_player_id}")
        print(f"  Initial Puzzle Board (sent to clients as board_data in game_state_update):")
        for i, row_data in enumerate(self.puzzle_board): print(f"    Row {i}: {row_data}")
        print(f"  Solution Board (used for checking victory):")
        for i, row_data in enumerate(self.solution_board): print(f"    Row {i}: {row_data}")
        # --- END DEBUG INIT ---

        self.current_board_state = [row[:] for row in self.puzzle_board]
        self.fixed_mask = [[(self.puzzle_board[r][c] != 0) for c in range(9)] for r in range(9)]
        
        self.players = {} # player_id -> client_socket object
        self.player_states = {} # player_id -> {'score': 0, ...}
        self.current_turn_player_id = None # Ai đang đến lượt
        self.game_started = False
        self.created_by = created_by_player_id
        self.game_over = False
        self.winner = None
        print(f"  Initial current_board_state (server's tracking board):")
        for i, row_data in enumerate(self.current_board_state): print(f"    Row {i}: {row_data}")
        print("-" * 30)


    def add_player(self, player_id, client_socket):
        print(f"DEBUG SERVER (Game {self.game_id}): Attempting to add player {player_id}. Current players: {len(self.players)}/{MAX_PLAYERS_PER_GAME}")
        if len(self.players) < MAX_PLAYERS_PER_GAME and player_id not in self.players:
            self.players[player_id] = client_socket
            self.player_states[player_id] = {'score': 0, 'moves_made': 0} 
            print(f"SERVER: Player {player_id} đã tham gia game {self.game_id}. Tổng: {len(self.players)}")
            
            if len(self.players) == MAX_PLAYERS_PER_GAME:
                print(f"DEBUG SERVER (Game {self.game_id}): Max players reached. Starting game.")
                self.start_game()
            return True
        print(f"DEBUG SERVER (Game {self.game_id}): Failed to add player {player_id}. Room full or player already joined.")
        return False

    def remove_player(self, player_id):
        print(f"DEBUG SERVER (Game {self.game_id}): Attempting to remove player {player_id}.")
        if player_id in self.players:
            del self.players[player_id]
            if player_id in self.player_states: # Kiểm tra trước khi xóa
                del self.player_states[player_id]
            print(f"SERVER: Player {player_id} đã rời game {self.game_id}.")
            if not self.players: 
                self.game_over = True 
                print(f"DEBUG SERVER (Game {self.game_id}): No players left. Game marked as over.")
                return True 
            if self.game_started and not self.game_over and len(self.players) == 1:
                self.winner = list(self.players.keys())[0]
                self.game_over = True
                print(f"DEBUG SERVER (Game {self.game_id}): Player left mid-game. Winner by default: {self.winner}")
                self.broadcast_game_over()
            return False # Player removed, but game not necessarily empty
        print(f"DEBUG SERVER (Game {self.game_id}): Player {player_id} not found for removal.")
        return False


    def start_game(self):
        print(f"DEBUG SERVER (Game {self.game_id}): start_game called. game_started={self.game_started}, num_players={len(self.players)}")
        if not self.game_started and len(self.players) == MAX_PLAYERS_PER_GAME:
            self.game_started = True
            self.current_turn_player_id = list(self.players.keys())[0] 
            print(f"SERVER: Game {self.game_id} bắt đầu! Lượt của {self.current_turn_player_id}.")
            self.broadcast_game_state() 
        else:
            print(f"DEBUG SERVER (Game {self.game_id}): start_game conditions not met.")


    def make_move(self, player_id, r, c, number):
        print(f"\nDEBUG SERVER (Game {self.game_id}): make_move CALLED by Player {player_id}")
        print(f"  Move details: row={r}, col={c}, number={number}")
        print(f"  Game state BEFORE move: game_over={self.game_over}, current_turn={self.current_turn_player_id}")

        if self.game_over:
            print(f"  Move REJECTED: Game {self.game_id} is already over.")
            return False, "Game đã kết thúc."
        if player_id != self.current_turn_player_id:
            print(f"  Move REJECTED: Not player {player_id}'s turn (current is {self.current_turn_player_id}).")
            return False, "Không phải lượt của bạn."
        
        if r < 0 or r >= 9 or c < 0 or c >= 9:
            print(f"  Move REJECTED: Invalid coordinates ({r},{c}).")
            return False, "Tọa độ không hợp lệ."
        if self.fixed_mask[r][c]:
            print(f"  Move REJECTED: Cell ({r},{c}) is fixed.")
            return False, "Không thể thay đổi ô cố định."
        if not (0 <= number <= 9): 
            print(f"  Move REJECTED: Invalid number {number}.")
            return False, "Số không hợp lệ."

        print(f"  Board state BEFORE applying number to current_board_state[{r}][{c}]:")
        print(f"    Value at ({r},{c}) was: {self.current_board_state[r][c]}")


        # CHÍNH SÁCH NƯỚC ĐI SAI: Hiện tại đang từ chối nước đi sai ngay
        is_correct_move = (number == 0 or number == self.solution_board[r][c]) 
        if not is_correct_move: 
            self.player_states[player_id]['score'] -=1 
            print(f"  Move REJECTED: Incorrect number {number} for cell ({r},{c}). Expected {self.solution_board[r][c]}.")
            return False, "Nước đi không chính xác."

        self.current_board_state[r][c] = number
        self.player_states[player_id]['moves_made'] += 1
        print(f"  Board state AFTER applying number to current_board_state[{r}][{c}]:")
        # for i, row_d in enumerate(self.current_board_state): print(f"    Row {i}: {row_d}") # Có thể làm log dài
        print(f"    Value at ({r},{c}) is now: {self.current_board_state[r][c]}")

        print(f"  Comparing current_board_state with SOLUTION board for game {self.game_id}:")
        # for i, row_d in enumerate(self.solution_board): print(f"    Row {i}: {row_d}") # Có thể làm log dài
        
        board_complete, board_correct = self.generator.check_board_state(
            self.current_board_state, 
            self.solution_board       
        )
        print(f"  Result from check_board_state: complete={board_complete}, correct={board_correct}")

        if board_complete and board_correct:
            self.winner = player_id
            self.game_over = True
            print(f"  !!! GAME OVER (Game {self.game_id}) !!! Winner determined: {self.winner}. Broadcasting game over.")
            self.broadcast_game_over() 
        else:
            player_ids_list = list(self.players.keys())
            if not player_ids_list: # Không còn người chơi nào
                print(f"  No players left in game {self.game_id} after move. Marking game over.")
                self.game_over = True # Sẽ được dọn dẹp bởi handle_client
            elif self.current_turn_player_id in player_ids_list:
                current_idx = player_ids_list.index(self.current_turn_player_id)
                self.current_turn_player_id = player_ids_list[(current_idx + 1) % len(player_ids_list)]
                print(f"  Game {self.game_id} continues. Next turn: {self.current_turn_player_id}")
                self.broadcast_move(player_id, r, c, number)
            else: # Người chơi hiện tại không còn trong danh sách (có thể đã disconnect)
                if player_ids_list: # Nếu còn người chơi khác
                    self.current_turn_player_id = player_ids_list[0]
                    print(f"  Current turn player {self.current_turn_player_id} left. Next turn set to {self.current_turn_player_id}.")
                    # Không broadcast_move vì người đi đã không còn, nhưng cần thông báo lượt cho người mới
                    self.broadcast_message({'command':'message', 'text': f'Đối thủ đã rời. Đến lượt bạn!'}, to_player_id=self.current_turn_player_id)
                else: # Không còn ai
                    print(f"  No players left and current turn player also gone in game {self.game_id}. Marking game over.")
                    self.game_over = True

        print("-" * 30)
        return True, "Nước đi được chấp nhận."

    def broadcast_message(self, message_dict, to_player_id=None):
        """Gửi tin nhắn tới một hoặc tất cả người chơi trong game."""
        try:
            json_message = json.dumps(message_dict)
            # print(f"DEBUG SERVER (Game {self.game_id}): Broadcasting to {'player ' + to_player_id if to_player_id else 'ALL'}: {json_message}")
            encoded_message = json_message.encode('utf-8')
            if to_player_id and to_player_id in self.players:
                try:
                    self.players[to_player_id].sendall(encoded_message)
                except Exception as e_send_single:
                    print(f"SERVER ERR (broadcast to {to_player_id} in game {self.game_id}): {e_send_single}")
                    # self.remove_player(to_player_id) # Cân nhắc xóa player nếu gửi lỗi
            else: 
                for pid_loop, sock_loop in list(self.players.items()): 
                    try:
                        sock_loop.sendall(encoded_message)
                    except Exception as e_send_all:
                        print(f"SERVER ERR (broadcast to {pid_loop} in game {self.game_id} during all_broadcast): {e_send_all}")
                        # self.remove_player(pid_loop) # Cân nhắc xóa player nếu gửi lỗi
        except json.JSONDecodeError as e_json:
            print(f"SERVER CRITICAL ERROR: JSON encoding failed for message: {message_dict} - Error: {e_json}")
        except Exception as e_broadcast_general:
            print(f"SERVER CRITICAL ERROR: General error in broadcast_message for game {self.game_id}: {e_broadcast_general}")


    def broadcast_game_state(self):
        print(f"DEBUG SERVER (Game {self.game_id}): Broadcasting initial game state to {len(self.players)} players.")
        for pid_broadcast in self.players:
            state_msg = {
                'command': 'game_state_update',
                'game_id': self.game_id,
                'board_data': self.puzzle_board, 
                'fixed_mask': self.fixed_mask,
                'current_turn': self.current_turn_player_id,
                'your_turn': (pid_broadcast == self.current_turn_player_id),
                'players_in_game': list(self.players.keys()) # Thêm thông tin người chơi
            }
            self.broadcast_message(state_msg, to_player_id=pid_broadcast)

    def broadcast_move(self, mover_id, r, c, number):
        print(f"DEBUG SERVER (Game {self.game_id}): Broadcasting move by {mover_id} ({r},{c},{number}). Next turn: {self.current_turn_player_id}")
        self.broadcast_message({
            'command': 'move_accepted', 'row':r, 'col':c, 'number':number
        }, to_player_id=mover_id)

        for pid_broadcast in self.players:
            if pid_broadcast != mover_id:
                self.broadcast_message({
                    'command': 'opponent_moved',
                    'mover_id': mover_id, 'row': r, 'col': c, 'number': number,
                    'next_turn': self.current_turn_player_id
                }, to_player_id=pid_broadcast)
            if pid_broadcast == self.current_turn_player_id: # Sau khi đối thủ đi, thông báo cho người có lượt
                 self.broadcast_message({'command':'message', 'text': 'Đến lượt bạn!'}, to_player_id=pid_broadcast)


    def broadcast_game_over(self):
        print(f"DEBUG SERVER (Game {self.game_id}): Broadcasting GAME OVER. Winner: {self.winner}")
        msg = {
            'command': 'game_over',
            'game_id': self.game_id,
            'winner_id': self.winner,
            'reason': f"Player {self.winner} đã hoàn thành bảng!" if self.winner else "Game kết thúc do đối thủ rời đi hoặc hòa."
        }
        self.broadcast_message(msg)


class SudokuServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {} 
        self.games = {}   
        self.generator = SudokuGenerator() 

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"SERVER: Đang lắng nghe trên {self.host}:{self.port}")

            while True:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    player_id = str(uuid.uuid4()) 
                    self.clients[client_socket] = player_id
                    print(f"SERVER: Kết nối mới từ {client_address}, Player ID: {player_id}")
                    
                    client_socket.sendall(json.dumps({'command':'connected_ack', 'player_id':player_id}).encode('utf-8'))

                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, player_id), daemon=True)
                    client_thread.start()
                except OSError as e_accept: # Nếu server_socket đã bị đóng
                    if self.server_socket and self.server_socket.fileno() == -1: # Socket closed
                        print("SERVER: Server socket closed, stopping accept loop.")
                        break
                    print(f"SERVER ERROR: Lỗi khi chấp nhận kết nối: {e_accept}")
                except Exception as e_accept_general: 
                    print(f"SERVER ERROR: Lỗi không xác định khi chấp nhận kết nối: {e_accept_general}")
                    traceback.print_exc()
                    break 

        except OSError as e_bind: 
            print(f"SERVER CRITICAL ERROR: Không thể bind tới {self.host}:{self.port} - {e_bind}")
        except KeyboardInterrupt:
            print("SERVER: Nhận KeyboardInterrupt, đang tắt server...")
        finally:
            print("SERVER: Bắt đầu quá trình dọn dẹp và đóng server...")
            # Thông báo cho các client đang kết nối rằng server sắp tắt
            for client_sock_in_clients in list(self.clients.keys()): # list() để tạo bản sao
                try:
                    client_sock_in_clients.sendall(json.dumps({'command':'message', 'text':'Server đang tắt...'}).encode('utf-8'))
                except Exception as e_send_shutdown:
                    print(f"SERVER WARN: Không thể gửi tin nhắn server tắt cho client: {e_send_shutdown}")
            
            # Đóng tất cả các game đang hoạt động
            for game_id_loop, game_obj_loop in list(self.games.items()):
                 print(f"SERVER: Dọn dẹp game {game_id_loop}...")
                 game_obj_loop.broadcast_message({'command':'message', 'text':f'Game {game_id_loop} bị hủy do server tắt.'})
                 # Có thể thêm logic dọn dẹp game cụ thể hơn nếu cần
            self.games.clear()

            # Đóng socket của server
            if self.server_socket:
                print("SERVER: Đang đóng server socket...")
                try:
                    self.server_socket.close()
                except Exception as e_close_server_socket:
                    print(f"SERVER ERROR: Lỗi khi đóng server socket: {e_close_server_socket}")
            print("SERVER: Đã đóng.")


    def handle_client(self, client_socket, player_id):
        buffer = ""
        player_current_game_id = None
        print(f"DEBUG SERVER: handle_client started for Player {player_id}")

        try:
            while True:
                try:
                    data_chunk = client_socket.recv(4096)
                except ConnectionAbortedError: # Client đột ngột hủy kết nối
                    print(f"SERVER WARN: ConnectionAbortedError for player {player_id}. Client might have closed abruptly.")
                    break
                except OSError as e_recv: # Socket có thể đã bị đóng
                    if e_recv.winerror == 10038 or e_recv.errno == 9: # WSAENOTSOCK or EBADF
                         print(f"SERVER WARN: Socket error (likely closed) on recv for player {player_id}: {e_recv}")
                    else:
                         print(f"SERVER ERROR: OSError on recv for player {player_id}: {e_recv}")
                    break

                if not data_chunk:
                    print(f"SERVER: Player {player_id} đã ngắt kết nối (no data_chunk).")
                    break 
                
                buffer += data_chunk.decode('utf-8')
                # print(f"DEBUG SERVER (Player {player_id}): Buffer content: '{buffer[:100]}...'") # Log buffer nếu cần

                while True: 
                    try:
                        message, index = json.JSONDecoder().raw_decode(buffer)
                        print(f"SERVER RECEIVED from {player_id}: {message}") 
                        
                        command = message.get('command')
                        game_id_req = message.get('game_id') 

                        if command == 'create_game':
                            difficulty = message.get('difficulty', 'medium')
                            new_game_id = str(uuid.uuid4())[:8] 
                            print(f"DEBUG SERVER: Player {player_id} creating game {new_game_id} with difficulty {difficulty}")
                            game = SudokuGameMultiplayer(new_game_id, difficulty, created_by_player_id=player_id)
                            game.add_player(player_id, client_socket)
                            self.games[new_game_id] = game
                            player_current_game_id = new_game_id
                            client_socket.sendall(json.dumps({
                                'command':'message',
                                'text': f"Game {new_game_id} đã được tạo. Chờ người chơi khác..."
                            }).encode('utf-8'))
                            # Nếu game bắt đầu ngay với 1 người (ví dụ chế độ chờ đặc biệt)
                            # if MAX_PLAYERS_PER_GAME == 1: game.start_game()

                        elif command == 'join_game':
                            print(f"DEBUG SERVER: Player {player_id} attempting to join game {game_id_req}")
                            if game_id_req in self.games:
                                game = self.games[game_id_req]
                                if not game.game_started and len(game.players) < MAX_PLAYERS_PER_GAME : # Chỉ cho join nếu game chưa bắt đầu và còn chỗ
                                    if game.add_player(player_id, client_socket):
                                        player_current_game_id = game_id_req
                                        print(f"DEBUG SERVER: Player {player_id} successfully joined game {game_id_req}. Current players in game: {len(game.players)}")
                                    else: # add_player trả về False
                                        print(f"DEBUG SERVER: Player {player_id} failed to join game {game_id_req} (add_player returned False).")
                                        client_socket.sendall(json.dumps({'command':'error', 'message':'Lỗi khi tham gia phòng. Có thể đã đầy hoặc bạn đã ở trong phòng.'}).encode('utf-8'))
                                else:
                                    error_msg_join = "Phòng đã bắt đầu hoặc đã đầy." if game.game_started else "Phòng đã đầy."
                                    print(f"DEBUG SERVER: Player {player_id} cannot join game {game_id_req}: {error_msg_join}")
                                    client_socket.sendall(json.dumps({'command':'error', 'message': error_msg_join}).encode('utf-8'))
                            else:
                                print(f"DEBUG SERVER: Player {player_id} tried to join non-existent game {game_id_req}")
                                client_socket.sendall(json.dumps({'command':'error', 'message':'Game ID không tồn tại.'}).encode('utf-8'))
                        
                        elif command == 'make_move':
                            print(f"DEBUG SERVER: Player {player_id} attempting make_move in game {player_current_game_id}")
                            if player_current_game_id and player_current_game_id in self.games:
                                game = self.games[player_current_game_id]
                                r_mv,c_mv,num_mv = message.get('row'), message.get('col'), message.get('number')
                                try:
                                    success, reason = game.make_move(player_id, r_mv,c_mv,num_mv)
                                    if not success:
                                        client_socket.sendall(json.dumps({'command':'move_rejected', 'reason':reason}).encode('utf-8'))
                                except Exception as e_make_move_call:
                                    print(f"SERVER CRITICAL ERROR during game.make_move for game {player_current_game_id}, player {player_id}: {e_make_move_call}")
                                    traceback.print_exc()
                                    client_socket.sendall(json.dumps({'command':'error', 'message':'Lỗi server khi xử lý nước đi.'}).encode('utf-8'))
                                    # Cân nhắc break ở đây nếu lỗi nghiêm trọng
                            else:
                                print(f"DEBUG SERVER: Player {player_id} tried make_move but not in a valid game (current_game_id: {player_current_game_id}).")
                                client_socket.sendall(json.dumps({'command':'error', 'message':'Bạn không ở trong game nào hoặc game không hợp lệ.'}).encode('utf-8'))

                        elif command == 'quit': 
                            print(f"SERVER: Player {player_id} sent quit command.")
                            break 

                        buffer = buffer[index:].lstrip()
                    except json.JSONDecodeError:
                        # print(f"DEBUG SERVER (Player {player_id}): Incomplete JSON in buffer, waiting for more data. Buffer: '{buffer[:100]}...'")
                        break 
                    except Exception as e_process_msg:
                        print(f"SERVER ERROR: Lỗi khi xử lý message từ {player_id}. Message: {message if 'message' in locals() else 'N/A'}. Error: {e_process_msg}")
                        traceback.print_exc()
                        # Cân nhắc break nếu lỗi nghiêm trọng
                        buffer = "" # Xóa buffer để tránh lỗi lặp lại với dữ liệu hỏng
                        break 
                
                if command == 'quit': # Nếu lệnh quit được xử lý bên trong, thoát vòng lặp ngoài
                    break

        except ConnectionResetError:
            print(f"SERVER: Player {player_id} ngắt kết nối đột ngột (ConnectionResetError).")
        except Exception as e_handle_client_outer:
            print(f"SERVER CRITICAL ERROR in outer loop of handle_client for {player_id}: {e_handle_client_outer}")
            traceback.print_exc()
        finally:
            print(f"SERVER: Bắt đầu dọn dẹp cho Player {player_id}.")
            
            # Xử lý rời game
            if player_current_game_id and player_current_game_id in self.games:
                game = self.games[player_current_game_id]
                print(f"SERVER: Player {player_id} is leaving game {player_current_game_id}.")
                if game.remove_player(player_id): # Nếu game rỗng sau khi player rời
                    print(f"SERVER: Game {player_current_game_id} rỗng, xóa game.")
                    if player_current_game_id in self.games: # Kiểm tra lại trước khi del
                        del self.games[player_current_game_id]
            
            if client_socket in self.clients:
                 del self.clients[client_socket] # Xóa client khỏi danh sách quản lý chung
                 print(f"SERVER: Player {player_id} (socket) removed from active clients list.")

            try:
                client_socket.shutdown(socket.SHUT_RDWR) # Thử shutdown trước khi close
            except OSError: # Bỏ qua lỗi nếu socket đã đóng
                pass
            except Exception as e_shutdown:
                print(f"SERVER WARN: Lỗi khi shutdown socket cho player {player_id}: {e_shutdown}")

            try:
                client_socket.close()
                print(f"SERVER: Socket cho Player {player_id} đã đóng.")
            except Exception as e_close:
                 print(f"SERVER ERROR: Lỗi khi đóng socket cho player {player_id}: {e_close}")
            print(f"SERVER: Kết thúc dọn dẹp cho Player {player_id}.")


if __name__ == "__main__":
    server = SudokuServer(HOST, PORT)
    server.start()