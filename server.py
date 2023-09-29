import socket
import pickle
import time
  
s = socket.socket()
host = ""
port = 9999
matrix = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

playerOne = 1
playerTwo = 2

playerConn = list()
playerAddr = list()
playerName = list()


def validate_input(x, y, conn):
    if x < 1 or x > 3 or y < 1 or y > 3:
        print("\nOut of bound! Enter again...\n")
        conn.send("Error".encode())
        return False
    elif matrix[x - 1][y - 1] != 0:
        print("\nAlready entered! Try again...\n")
        conn.send("Error".encode())
        return False
    return True


def get_input(currentPlayer, playerName):
    print(playerName + "'s Turn")
    send_common_msg(playerName + "'s Turn")

    conn = playerConn[currentPlayer - 1]
    failed = 1

    while failed:
        try:
            conn.send("Input".encode())
            data = conn.recv(2048 * 10)
            conn.settimeout(20)
            dataDecoded = data.decode().split(",")
            x = int(dataDecoded[0])
            y = int(dataDecoded[1])

            if validate_input(x, y, conn):
                matrix[x - 1][y - 1] = currentPlayer
                failed = 0
                send_common_msg("Matrix")
                send_common_msg(str(matrix))
        except:
            conn.send("Error".encode())
            print("Error occurred! Try again..")


def check_rows():
    for i in range(3):
        if matrix[i][0] == matrix[i][1] == matrix[i][2] != 0:
            return matrix[i][0]
    return 0


def check_columns():
    for i in range(3):
        if matrix[0][i] == matrix[1][i] == matrix[2][i] != 0:
            return matrix[0][i]
    return 0


def check_diagonals():
    if matrix[0][0] == matrix[1][1] == matrix[2][2] != 0:
        return matrix[0][0]
    if matrix[0][2] == matrix[1][1] == matrix[2][0] != 0:
        return matrix[0][2]
    return 0


def check_winner():
    result = check_rows()
    if result == 0:
        result = check_columns()
    if result == 0:
        result = check_diagonals()
    return result


def start_server():
    try:
        s.bind((host, port))
        print("Tic Tac Toe server started \nBinding to port", port)
        s.listen(2)
        accept_players()
    except socket.error as e:
        print("Server binding error:", e)


def accept_players():
    try:
        welcome = "Welcome to Tic Tac Toe Server"
        for i in range(2):
            conn, addr = s.accept()
            conn.send(welcome.encode())
            name = conn.recv(2048 * 10).decode()
            playerConn.append(conn)
            playerAddr.append(addr)
            playerName.append(name)
            print("Player {} - {} [{}:{}]".format(i + 1, name, addr[0], str(addr[1])))
            conn.send("Hi {}, you are player {}".format(name, str(i + 1)).encode())

        start_game()
        s.close()
    except socket.error as e:
        print("Player connection error", e)
    except:
        print("Error occurred")


def send_common_msg(text):
    playerConn[0].send(text.encode())
    playerConn[1].send(text.encode())
    time.sleep(1)


def start_game():
    result = 0
    i = 0
    while result == 0 and i < 9:
        if (i % 2 == 0):
            get_input(playerOne, playerName[0])
        else:
            get_input(playerTwo, playerName[1])
        result = check_winner()
        i = i + 1

    if result == playerOne:
        lastmsg = playerName[0] + " is the winner"
    elif result == playerTwo:
        lastmsg = playerName[1] + " is the winner"
    else:
        lastmsg = "Draw"

    send_common_msg("Game Over")
    send_common_msg(lastmsg)
    time.sleep(10)
    for conn in playerConn:
        conn.close()


start_server()
