package main

import (
	"bufio"
	"math/rand"
	"os"
	"strings"
	"time"
)

type LetterAttempt struct {
	Letter byte   `json:"letter"`
	Status string `json:"status"`
}

type WordAttempt struct {
	Letters    []LetterAttempt `json:"letters"`
	FinishTurn bool            `json:"finishTurn"`
}

func GenerateWord() (string, error) {
	wordsFile, err := os.Open("./palabras.txt")
	if err != nil {
		return "", err
	}
	defer wordsFile.Close()

	var palabras []string
	escaner := bufio.NewScanner(wordsFile)
	for escaner.Scan() {
		palabras = append(palabras, strings.TrimSpace(escaner.Text()))
	}

	if err := escaner.Err(); err != nil {
		return "", err
	}

	rand.Seed(time.Now().UnixNano())
	return palabras[rand.Intn(len(palabras))], nil
}

func ProcessAttempt(word string, attemptWord string) WordAttempt {
	result := WordAttempt{Letters: []LetterAttempt{}, FinishTurn: false}
	var status string
	incorrectFlag := false
	for i := 0; i < len(attemptWord); i++ {
		if attemptWord[i] == word[i] {
			status = "correct"
		} else if strings.Contains(word, string(attemptWord[i])) {
			status = "amarillo"
			incorrectFlag = true
		} else {
			status = "incorrecto"
			incorrectFlag = true
		}
		result.Letters = append(result.Letters, LetterAttempt{Letter: attemptWord[i], Status: status})
	}

	if !incorrectFlag {
		result.FinishTurn = true
	}

	return result
}

