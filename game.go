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
	Letters     []LetterAttempt `json:"letters"`
	Score       int
	CorrectWord bool `json:"finishTurn"`
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
	occurrences := []byte{}
	result := WordAttempt{Letters: []LetterAttempt{}, CorrectWord: false}
	var status string
	incorrectFlag := false
	for i := 0; i < len(attemptWord); i++ {
		if attemptWord[i] == word[i] {
			status = "correct"
			occurrences = append(occurrences, attemptWord[i])
		} else if strings.Contains(word, string(attemptWord[i])) {
			status = "yellow"
			occurrences = append(occurrences, attemptWord[i])
			incorrectFlag = true
		} else {
			status = "incorrect"
			incorrectFlag = true
		}
		result.Letters = append(result.Letters, LetterAttempt{Letter: attemptWord[i], Status: status})
	}

	if !incorrectFlag {
		result.CorrectWord = true
	}

	return result
}
