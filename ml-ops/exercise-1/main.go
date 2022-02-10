package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os/exec"
)

func main(){
	http.HandleFunc("/predict", predict)
	log.Fatalln(http.ListenAndServe("localhost:8080", nil))
}


func launch(request []byte) ([]byte, error){
	cmd := exec.Command("python3", "model.py")


	in, err := cmd.StdinPipe()
	if err != nil {
		return nil, fmt.Errorf("failed to get stdin pipt: %w", err)
	}

	_, err = in.Write(request)
	if err != nil {
		return nil, fmt.Errorf("failed to write to stdin, %w", err)
	}

	err = in.Close()
	if err != nil {
		return nil, fmt.Errorf("failed to close stdin, %w", err)
	}

	out, err := cmd.CombinedOutput()
	if err != nil {
		log.Println("Cmd failed: ", string(out))
		return out, fmt.Errorf("failed to run command: %w", err)

	}
	return out, nil
}



func predict(w http.ResponseWriter, r *http.Request){

	buf, err := ioutil.ReadAll(r.Body)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	w.Header().Set("Content-Type", "application/json")

	response, err := launch(buf)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	_, err = w.Write(response)
	if err != nil {
		log.Println("couldn't sent response", err)
	}

}