package main

import (
	"encoding/json"
	"fmt"
	"net"
	"sync"
	"time"
)

type Message struct {
	Type    string      `json:"type"`
	Content interface{} `json:"content"`
}

type User struct {
	Name     string        `json:"name"`
	Turn     int           `json:"turn"`
	Score    int           `json:"score"`
	Attempts []WordAttempt `json:"attempts"`
}

type GameStatus struct {
	Status string            `json:"status"`
	Users  map[net.Conn]User `json:"users"`
}

var (
	users      = make(map[net.Conn]User)
	mutex      sync.Mutex
	word       string
	gameStatus = "Starting"
)

func sendMessage(conn net.Conn, message Message) {
	encoder := json.NewEncoder(conn)
	err := encoder.Encode(message)
	if err != nil {
		fmt.Println("Error al enviar el mensaje:", err)
	}
}

func broadcast(message Message) {
	for conn := range users {
		sendMessage(conn, message)
	}
}

func sendStatus() {
	intervalo := time.Second
	ticker := time.NewTicker(intervalo)

	for {
		select {
		case <-ticker.C:
			usersStatus := []User{}
			for _, user := range users {
				usersStatus = append(usersStatus, user)
			}
			broadcast(Message{Type: "GameStatus", Content: usersStatus})
			fmt.Println("enviando: ", usersStatus)
		}
	}
}

func handleConnection(conn net.Conn, endTurnChan chan string) {

	var msg Message
	fmt.Println("Nueva conexión:", conn.RemoteAddr())
	decoder := json.NewDecoder(conn)

	user := User{Name: "", Score: 0, Attempts: []WordAttempt{}}
	mutex.Lock()
	users[conn] = user
	mutex.Unlock()

	for {
		err := decoder.Decode(&msg)
		if err != nil {
			fmt.Println("Error al decodificar el mensaje:", err)
			return
		}
		switch msg.Type {
		case "Register":
			name, ok := msg.Content.(string)
			fmt.Println(name)
			if !ok {
				fmt.Println("Error al obtener el contenido del mensaje Login")
				return
			}
			mutex.Lock()
			user := users[conn]
			user.Name = name
			users[conn] = user
			mutex.Unlock()
			sendMessage(conn, Message{Type: "RegisterResponse", Content: "Usuario creado correctamente"})
		case "Attempt":
			content, ok := msg.Content.(string)
			if !ok {
				fmt.Println("Error al obtener el contenido del mensaje Attempt")
				return
			}

			result := ProcessAttempt(word, content)

			mutex.Lock()
			user := users[conn]
			user.Turn++
			user.Score += result.Score
			users[conn] = user
			mutex.Unlock()

			if result.CorrectWord {
				endTurnChan <- users[conn].Name
				return
			}

			sendMessage(conn, Message{Type: "AttemptResponse", Content: result})
		default:
			fmt.Println("Tipo de mensaje no reconocido:", msg.Type)
		}
	}
}

func main() {
	listener, err := net.Listen("tcp", ":8080")
	if err != nil {
		fmt.Println("Error al iniciar el servidor:", err)
		return
	}
	defer listener.Close()

	var players int
	fmt.Print("Cantidad de jugadores: ")
	fmt.Scanf("%d", &players)

	endTurnChan := make(chan string)

	for i := 0; i < players; i++ {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Println("Error al aceptar la conexión:", err)
			continue
		}

		go handleConnection(conn, endTurnChan)
	}

	word, _ = GenerateWord()
	fmt.Println("Palabra: ", word)

	go sendStatus()
	winner := <-endTurnChan

	fmt.Println("El ganador es: ", winner)
	broadcast(Message{Type: "EndTurn", Content: winner})
}
